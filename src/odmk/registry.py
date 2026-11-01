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
    FROZEN_BASELINE_CELL,
    FROZEN_DIMENSION_OPTIONS,
    FROZEN_REGISTRY_STATUS,
    POINT_ESTIMATE_DIMENSIONS,
    REGISTRY_REVISION,
)
from .exceptions import RegistryError


def load_registry(path: Path) -> dict[str, Any]:
    """Load the YAML registry and enforce every frozen structural invariant."""

    registry = yaml.safe_load(path.read_text(encoding="utf-8"))
    validate_registry(registry)
    return registry


def validate_registry(registry: dict[str, Any]) -> None:
    """Reject a registry that differs from the approved ODMK design contract.

    Raises:
        RegistryError: If paper identity, revision, status, focal quantity,
            dimension names or options, baseline choices, fixed survey rules,
            structural anchors, or required outputs differ from revision 7.
    """

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
        expected_options = FROZEN_DIMENSION_OPTIONS[name]
        if tuple(options) != expected_options:
            raise RegistryError(
                f"{name} options must equal the frozen revision-{REGISTRY_REVISION} choices: "
                f"{expected_options}"
            )
        expected_baseline = FROZEN_BASELINE_CELL[name]
        if definition.get("baseline") != expected_baseline:
            raise RegistryError(
                f"{name} baseline must equal the frozen choice {expected_baseline!r}"
            )
    construction = registry.get("cell_construction", {})
    if tuple(construction.get("order", ())) != DIMENSION_ORDER:
        raise RegistryError("Cell-construction order differs from the dimension order")
    if construction.get("expected_specifications") != 16:
        raise RegistryError("Registry must specify 16 cells")
    if construction.get("distinct_point_estimate_constructions") != 8:
        raise RegistryError("Registry must specify eight point-estimate constructions")
    if not construction.get("full_factorial"):
        raise RegistryError("Registry must request a full factorial")
    if construction.get("baseline_cell") != FROZEN_BASELINE_CELL:
        raise RegistryError(
            f"Baseline cell must equal the frozen revision-{REGISTRY_REVISION} baseline"
        )


def build_manifest(registry: dict[str, Any]) -> pd.DataFrame:
    """Expand the four binary decisions into stable, baseline-first cell IDs.

    The three named point-estimate dimensions define eight estimands. The
    variance dimension creates two inferential cells for each estimand.

    Returns:
        A deterministic baseline-first table with stable specification and
        point-estimate IDs, all four option columns, and ``is_baseline``.
    """

    dimensions = registry["dimensions"]
    option_lists = [list(dimensions[name]["options"]) for name in DIMENSION_ORDER]
    baseline = registry["cell_construction"]["baseline_cell"]
    combinations = list(product(*option_lists))

    # Put the all-baseline combination first, then order the remaining rows by
    # which choices differ from baseline. This makes stable IDs reproducible.
    combinations.sort(
        key=lambda values: tuple(
            values[index] != baseline[name]
            for index, name in enumerate(DIMENSION_ORDER)
        )
    )

    point_keys: dict[tuple[str, ...], str] = {}
    rows: list[dict[str, str | bool]] = []
    for index, values in enumerate(combinations, start=1):
        options = dict(zip(DIMENSION_ORDER, values, strict=True))

        # d08 changes only uncertainty, so its two rows share one point-estimate
        # ID. The other three choices define the eight distinct comparisons.
        point_key = tuple(options[name] for name in POINT_ESTIMATE_DIMENSIONS)
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
