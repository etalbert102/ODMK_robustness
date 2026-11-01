import numpy as np
import pytest

from odmk.constants import PCC_ITEMS, REPLICATE_WEIGHTS
from odmk.data import (
    cell_arrays,
    derive_analysis_fields,
    read_canonical_hints,
    validate_source,
)
from odmk.exceptions import DataValidationError
from odmk.registry import build_manifest, load_registry
from odmk.utils import project_root


def test_reverse_scoring_and_partial_scale_rules(synthetic_derived) -> None:
    df = synthetic_derived
    complete = df["pcc_valid_item_count"].eq(7)
    partial = df["pcc_valid_item_count"].between(4, 6)
    assert df.loc[complete, "pppcq_complete7"].notna().all()
    assert df.loc[partial, "pppcq_complete7"].isna().all()
    assert df.loc[partial, "pppcq_atleast4"].notna().all()
    first_complete = df.index[complete][0]
    source = df.loc[first_complete, PCC_ITEMS[0]]
    assert df.loc[first_complete, f"{PCC_ITEMS[0]}_reversed"] == 5 - source


def test_content_confirmation_retains_answered_followup_with_missing_filter(synthetic_derived) -> None:
    df = synthetic_derived
    repaired = ~df["recent_provider_visit"] & df["communication_followup_observed"]
    assert repaired.any()
    assert df.loc[repaired, "content_confirmed_module"].all()


def test_content_confirmation_does_not_override_recorded_zero(synthetic_raw) -> None:
    frame = synthetic_raw.copy()
    frame.loc[0, "freqgoprovider"] = 0

    derived = derive_analysis_fields(frame)

    assert derived.loc[0, "communication_followup_observed"]
    assert not derived.loc[0, "recent_provider_visit"]
    assert not derived.loc[0, "provider_visit_response_missing"]
    assert not derived.loc[0, "content_confirmed_module"]


def test_inclusive_asian_adds_multiracial_without_changing_white(synthetic_derived) -> None:
    df = synthetic_derived
    assert (df["official_asian"] <= df["inclusive_asian"]).all()
    assert (df["inclusive_asian"] & ~df["official_asian"]).any()
    assert not (df["inclusive_asian"] & df["official_white"]).any()


def test_cell_arrays_follow_manifest_options(synthetic_derived) -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    baseline = manifest.iloc[0]
    score, asian, white = cell_arrays(synthetic_derived, baseline)
    assert np.isfinite(score[asian]).all()
    assert np.isfinite(score[white]).all()
    assert not np.any(asian & white)


def test_all_point_estimate_options_have_expected_synthetic_membership(
    synthetic_derived,
) -> None:
    expected_counts = {
        (
            "content_confirmed_module",
            "require_7_of_7_valid_items",
            "official_mutually_exclusive_raceethn5",
        ): (17, 69),
        (
            "content_confirmed_module",
            "require_7_of_7_valid_items",
            "inclusive_nonhispanic_any_asian_identification",
        ): (33, 69),
        (
            "content_confirmed_module",
            "require_at_least_4_of_7_valid_items",
            "official_mutually_exclusive_raceethn5",
        ): (20, 80),
        (
            "content_confirmed_module",
            "require_at_least_4_of_7_valid_items",
            "inclusive_nonhispanic_any_asian_identification",
        ): (40, 80),
        (
            "observed_positive_filter_only",
            "require_7_of_7_valid_items",
            "official_mutually_exclusive_raceethn5",
        ): (16, 62),
        (
            "observed_positive_filter_only",
            "require_7_of_7_valid_items",
            "inclusive_nonhispanic_any_asian_identification",
        ): (31, 62),
        (
            "observed_positive_filter_only",
            "require_at_least_4_of_7_valid_items",
            "official_mutually_exclusive_raceethn5",
        ): (18, 73),
        (
            "observed_positive_filter_only",
            "require_at_least_4_of_7_valid_items",
            "inclusive_nonhispanic_any_asian_identification",
        ): (37, 73),
    }
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    jk1_cells = manifest.loc[
        manifest["d08_variance_estimation"].eq("official_jk1_replicate_weights")
    ]

    observed = {}
    for _, cell in jk1_cells.iterrows():
        score, asian, white = cell_arrays(synthetic_derived, cell)
        key = (
            cell["d01_analytic_sample"],
            cell["d03_outcome_construction"],
            cell["d04_main_predictor_construction"],
        )
        observed[key] = (int(asian.sum()), int(white.sum()))
        assert np.isfinite(score[asian | white]).all()

    assert observed == expected_counts


@pytest.mark.parametrize(
    ("corruption", "message"),
    [
        ("missing_column", "Required source columns absent"),
        ("duplicate_hhid", "HHID must be nonmissing and unique"),
        ("zero_full_weight", "PERSON_FINWT0 must be nonmissing and positive"),
        ("negative_replicate", "replicate weights must be nonmissing and nonnegative"),
        ("missing_design", "Taylor design fields must be nonmissing"),
    ],
)
def test_validate_source_rejects_invalid_inputs(synthetic_raw, corruption, message) -> None:
    frame = synthetic_raw.copy()
    if corruption == "missing_column":
        frame = frame.drop(columns=[PCC_ITEMS[0]])
    elif corruption == "duplicate_hhid":
        frame.loc[1, "hhid"] = frame.loc[0, "hhid"]
    elif corruption == "zero_full_weight":
        frame.loc[0, "person_finwt0"] = 0
    elif corruption == "negative_replicate":
        frame.loc[0, REPLICATE_WEIGHTS[0]] = -1
    elif corruption == "missing_design":
        frame.loc[0, "var_stratum"] = None
    else:  # pragma: no cover - the parameter table owns the valid cases
        raise AssertionError(f"Unknown corruption case: {corruption}")

    with pytest.raises(DataValidationError, match=message):
        validate_source(frame, require_canonical_rows=False)


def test_cell_arrays_reject_domain_that_omits_a_design_unit(synthetic_derived) -> None:
    frame = synthetic_derived.copy()
    first_unit = frame[["var_stratum", "var_cluster"]].drop_duplicates().iloc[0]
    unit = frame["var_stratum"].eq(first_unit["var_stratum"]) & frame[
        "var_cluster"
    ].eq(first_unit["var_cluster"])
    frame.loc[unit, ["pppcq_complete7", "pppcq_atleast4"]] = np.nan
    manifest = build_manifest(load_registry(project_root() / "specification_freeze.yaml"))

    with pytest.raises(DataValidationError, match="omits 1 released"):
        cell_arrays(frame, manifest.iloc[0])


def test_canonical_reader_rejects_wrong_file_hash(tmp_path) -> None:
    wrong_file = tmp_path / "not-canonical.dta"
    wrong_file.write_bytes(b"not the registered public-use file")

    with pytest.raises(DataValidationError, match="Source SHA-256"):
        read_canonical_hints(wrong_file)
