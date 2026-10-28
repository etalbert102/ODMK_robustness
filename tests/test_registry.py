import copy

import pytest

from odmk.constants import (
    DIMENSION_ORDER,
    POINT_ESTIMATE_DIMENSIONS,
    VARIANCE_DIMENSION,
)
from odmk.exceptions import RegistryError
from odmk.registry import build_manifest, load_registry, validate_registry
from odmk.utils import project_root


def test_registry_expands_to_frozen_universe() -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    assert len(manifest) == 16
    assert manifest["specification_id"].tolist() == [f"ODMK-{i:02d}" for i in range(1, 17)]
    assert manifest["point_estimate_id"].nunique() == 8
    assert manifest["is_baseline"].sum() == 1
    assert bool(manifest.iloc[0]["is_baseline"])
    assert list(manifest.columns[2:6]) == list(DIMENSION_ORDER)


def test_every_point_construction_has_both_variance_options() -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    counts = manifest.groupby("point_estimate_id")["d08_variance_estimation"].nunique()
    assert counts.eq(2).all()


def test_point_estimate_dimensions_are_named_independently_of_variance() -> None:
    assert DIMENSION_ORDER == (*POINT_ESTIMATE_DIMENSIONS, VARIANCE_DIMENSION)
    assert POINT_ESTIMATE_DIMENSIONS == (
        "d01_analytic_sample",
        "d03_outcome_construction",
        "d04_main_predictor_construction",
    )


def test_registry_rejects_unknown_lifecycle_status() -> None:
    registry = copy.deepcopy(load_registry(project_root() / "specification_freeze.yaml"))
    registry["status"] = "unknown"
    with pytest.raises(RegistryError, match="Registry status"):
        validate_registry(registry)
