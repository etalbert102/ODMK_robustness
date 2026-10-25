import numpy as np
import pytest

from odmk.constants import EXPECTED_DATA_SHA256
from odmk.engine import run_manifest
from odmk.exceptions import ODMKError
from odmk.registry import build_manifest, load_registry
from odmk.utils import project_root
from odmk.validation import validate_full_results


def test_synthetic_engine_exercises_all_16_cells(synthetic_derived) -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    results = run_manifest(
        synthetic_derived, manifest, scope="synthetic", source_hash="synthetic-fixture"
    )
    validation = validate_full_results(
        results,
        manifest,
        expected_source_hash="synthetic-fixture",
        expected_taylor_df=6,
    )
    assert validation["successful_cells"] == 16
    assert validation["failed_cells"] == 0
    assert validation["point_estimate_invariance"] is True
    assert validation["point_estimate_invariance_status"] == "verified"
    assert set(results["denominator_degrees_of_freedom"]) == {6, 49}


def test_variance_choice_cannot_change_point_estimates(synthetic_derived) -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    results = run_manifest(
        synthetic_derived, manifest, scope="synthetic", source_hash="synthetic-fixture"
    )
    for _, pair in results.groupby("point_estimate_id"):
        assert len(pair) == 2
        for field in ("asian_mean", "white_mean", "asian_minus_white_difference"):
            assert np.allclose(pair[field], pair[field].iloc[0], rtol=0, atol=1e-12)


def test_synthetic_scope_rejects_canonical_hash(synthetic_derived) -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    with pytest.raises(ODMKError, match="canonical HINTS"):
        run_manifest(
            synthetic_derived, manifest, scope="synthetic", source_hash=EXPECTED_DATA_SHA256
        )


def test_baseline_scope_runs_only_one_cell(synthetic_derived) -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    results = run_manifest(
        synthetic_derived, manifest, scope="baseline", source_hash="synthetic-fixture"
    )
    assert results["specification_id"].tolist() == ["ODMK-01"]


def test_approved_scope_requires_production_authorization(synthetic_derived) -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    with pytest.raises(ODMKError, match="authorization"):
        run_manifest(
            synthetic_derived, manifest, scope="approved", source_hash="synthetic-fixture"
        )


def test_validation_retains_failed_registered_cell(synthetic_derived) -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    results = run_manifest(
        synthetic_derived, manifest, scope="synthetic", source_hash="synthetic-fixture"
    )
    failed_index = results.index[-1]
    results.loc[failed_index, "status"] = "failed"
    results.loc[failed_index, "failure_category"] = "CellEstimationError"
    results.loc[failed_index, "failure_reason"] = "registered test failure"
    identity = {
        "paper_id",
        "registry_revision",
        "source_data_sha256",
        "specification_id",
        "point_estimate_id",
        "is_baseline",
        "d01_analytic_sample",
        "d03_outcome_construction",
        "d04_main_predictor_construction",
        "d08_variance_estimation",
        "all_option_labels",
        "focal_term",
        "status",
        "failure_category",
        "failure_reason",
    }
    for column in set(results.columns) - identity:
        results.loc[failed_index, column] = np.nan
    validation = validate_full_results(results, manifest)
    assert validation["failed_cells"] == 1
    assert validation["point_estimate_pairs_checked"] == 7
    assert validation["point_estimate_invariance"] is None
    assert validation["point_estimate_invariance_status"] == "partially_verified"


def test_validation_rejects_result_that_differs_from_frozen_manifest(synthetic_derived) -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    results = run_manifest(
        synthetic_derived, manifest, scope="synthetic", source_hash="synthetic-fixture"
    )
    results.loc[0, "d01_analytic_sample"] = "wrong_option_label"
    with pytest.raises(ODMKError, match="frozen manifest identity"):
        validate_full_results(results, manifest)


def test_validation_rejects_internally_inconsistent_estimate(synthetic_derived) -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    results = run_manifest(
        synthetic_derived, manifest, scope="synthetic", source_hash="synthetic-fixture"
    )
    results.loc[0, "asian_minus_white_difference"] += 0.25
    with pytest.raises(ODMKError, match="does not equal"):
        validate_full_results(results, manifest)


def test_validation_rejects_internally_inconsistent_inference(synthetic_derived) -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    results = run_manifest(
        synthetic_derived, manifest, scope="synthetic", source_hash="synthetic-fixture"
    )
    results.loc[0, "standard_error_of_difference"] *= 1.5
    with pytest.raises(ODMKError, match="ci_low_95 is inconsistent"):
        validate_full_results(results, manifest)


def test_validation_rejects_changed_focal_term(synthetic_derived) -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    results = run_manifest(
        synthetic_derived, manifest, scope="synthetic", source_hash="synthetic-fixture"
    )
    results.loc[0, "focal_term"] = "wrong focal term"
    with pytest.raises(ODMKError, match="frozen focal-term"):
        validate_full_results(results, manifest)


def test_invariance_is_not_claimed_when_no_pairs_can_be_checked(synthetic_derived) -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    results = run_manifest(
        synthetic_derived, manifest, scope="synthetic", source_hash="synthetic-fixture"
    )
    identity = {
        "paper_id",
        "registry_revision",
        "source_data_sha256",
        "specification_id",
        "point_estimate_id",
        "is_baseline",
        "d01_analytic_sample",
        "d03_outcome_construction",
        "d04_main_predictor_construction",
        "d08_variance_estimation",
        "all_option_labels",
        "focal_term",
        "status",
        "failure_category",
        "failure_reason",
    }
    results["status"] = "failed"
    results["failure_category"] = "CellEstimationError"
    results["failure_reason"] = "registered test failure"
    for column in set(results.columns) - identity:
        results[column] = np.nan

    validation = validate_full_results(results, manifest)
    assert validation["point_estimate_pairs_checked"] == 0
    assert validation["point_estimate_invariance"] is None
    assert validation["point_estimate_invariance_status"] == "not_assessed"
