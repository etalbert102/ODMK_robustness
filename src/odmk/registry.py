"""Read, validate, and expand the frozen specification registry."""

from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from .constants import (
    DIMENSION_ORDER,
    EXPECTED_DATA_SHA256,
    FROZEN_REGISTRY_STATUS,
    REGISTRY_REVISION,
)
from .exceptions import RegistryError


def load_registry(path: Path) -> dict[str, Any]:
    registry = yaml.safe_load(path.read_text(encoding="utf-8"))
    validate_registry(registry)
    return registry


def validate_registry(registry: dict[str, Any]) -> None:
    if registry.get("paper_id") != "ODMK":
        raise RegistryError("Registry paper_id must be ODMK")
    if registry.get("revision") != REGISTRY_REVISION:
        raise RegistryError(f"Registry revision must be {REGISTRY_REVISION}")
    if registry.get("status") != FROZEN_REGISTRY_STATUS:
        raise RegistryError(f"Registry status must be {FROZEN_REGISTRY_STATUS!r}")
    if registry.get("fixed", {}).get("data_sha256") != EXPECTED_DATA_SHA256:
        raise RegistryError("Registry data hash differs from the canonical public-use file")
    dimensions = registry.get("dimensions", {})
    if tuple(dimensions) != DIMENSION_ORDER:
        raise RegistryError(f"Dimensions must appear in frozen order: {DIMENSION_ORDER}")
    for name in DIMENSION_ORDER:
        definition = dimensions[name]
        options = definition.get("options", {})
        if len(options) != 2 or definition.get("baseline") not in options:
            raise RegistryError(f"{name} must have two options including its baseline")
    construction = registry.get("cell_construction", {})
    if tuple(construction.get("order", ())) != DIMENSION_ORDER:
        raise RegistryError("Cell-construction order differs from the dimension order")
    if construction.get("expected_specifications") != 16:
        raise RegistryError("Registry must specify 16 cells")
    if construction.get("distinct_point_estimate_constructions") != 8:
        raise RegistryError("Registry must specify eight point-estimate constructions")
    if not construction.get("full_factorial"):
        raise RegistryError("Registry must request a full factorial")


def build_manifest(registry: dict[str, Any]) -> pd.DataFrame:
    dimensions = registry["dimensions"]
    option_lists = [list(dimensions[name]["options"]) for name in DIMENSION_ORDER]
    baseline = registry["cell_construction"]["baseline_cell"]
    combinations = list(product(*option_lists))
    combinations.sort(key=lambda values: tuple(values[i] != baseline[name] for i, name in enumerate(DIMENSION_ORDER)))

    point_keys: dict[tuple[str, str, str], str] = {}
    rows: list[dict[str, str | bool]] = []
    for index, values in enumerate(combinations, start=1):
        options = dict(zip(DIMENSION_ORDER, values, strict=True))
        point_key = values[:3]
        if point_key not in point_keys:
            point_keys[point_key] = f"ODMK-P{len(point_keys) + 1:02d}"
        rows.append(
            {
                "specification_id": f"ODMK-{index:02d}",
                "point_estimate_id": point_keys[point_key],
                **options,
                "is_baseline": options == baseline,
            }
        )
    manifest = pd.DataFrame(rows)
    if len(manifest) != 16 or manifest["point_estimate_id"].nunique() != 8:
        raise RegistryError("Expanded registry has the wrong number of cells")
    if manifest["is_baseline"].sum() != 1 or not bool(manifest.iloc[0]["is_baseline"]):
        raise RegistryError("The single baseline cell must be first")
    return manifest
