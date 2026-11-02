from __future__ import annotations

import pandas as pd
import pytest

from odmk.constants import EXPECTED_DATA_SHA256
from odmk.cross_language import (
    EXPECTED_GROUP_LABELS,
    R_RESULT_COLUMNS,
    compare_independent_r_baseline,
)
from odmk.exceptions import ODMKError


def comparison_artifacts() -> tuple[pd.DataFrame, pd.DataFrame, dict, pd.DataFrame]:
    """Return internally matching R and Python baseline artifacts."""

    group_rows = []
    python_groups = {}
    for code in range(1, 6):
        estimate = 3.0 + code / 20
        standard_error = code / 100
        low = estimate - 0.1
        high = estimate + 0.1
        count = 100 + code
        group_rows.append(
            {
                "result_type": "group_mean",
                "label": EXPECTED_GROUP_LABELS[code],
                "race_code": code,
                "unweighted_n": count,
                "estimate": estimate,
                "standard_error": standard_error,
                "ci_low_95": low,
                "ci_high_95": high,
                "denominator_degrees_of_freedom": 49,
            }
        )
        python_groups[str(code)] = {
            "unweighted_n": count,
            "mean": estimate,
            "se": standard_error,
            "ci_low": low,
            "ci_high": high,
        }
    group_rows.append(
        {
            "result_type": "contrast",
            "label": "non_hispanic_asian_minus_non_hispanic_white",
            "race_code": None,
            "unweighted_n": None,
            "estimate": -0.3,
            "standard_error": 0.1,
            "ci_low_95": -0.5,
            "ci_high_95": -0.1,
            "denominator_degrees_of_freedom": 49,
        }
    )
    r_results = pd.DataFrame(group_rows, columns=R_RESULT_COLUMNS)
    metadata_values = {
        "source_data_sha256": EXPECTED_DATA_SHA256,
        "source_rows": "3504",
        "baseline_analytic_n": "2611",
        "r_version": "4.6.1",
        "digest_version": "0.6.39",
        "haven_version": "2.5.5",
        "survey_version": "4.5",
        "jk1_scale": "0.98",
        "design_degrees_of_freedom": "49",
    }
    r_metadata = pd.DataFrame(
        {"field": metadata_values.keys(), "value": metadata_values.values()}
    )
    python_validation = {"full_table2": {"jk1_by_raceethn5": python_groups}}
    python_results = pd.DataFrame(
        [
            {
                "status": "success",
                "asian_minus_white_difference": -0.3,
                "standard_error_of_difference": 0.1,
                "ci_low_95": -0.5,
                "ci_high_95": -0.1,
                "denominator_degrees_of_freedom": 49,
            }
        ]
    )
    return r_results, r_metadata, python_validation, python_results


def test_matching_independent_r_baseline_passes() -> None:
    r_results, r_metadata, python_validation, python_results = comparison_artifacts()

    audit = compare_independent_r_baseline(
        r_results, r_metadata, python_validation, python_results
    )

    assert len(audit) == 30
    assert audit["passed"].all()
    assert audit["absolute_difference"].eq(0).all()


def test_cross_language_numeric_mismatch_is_rejected() -> None:
    r_results, r_metadata, python_validation, python_results = comparison_artifacts()
    r_results.loc[r_results["race_code"].eq(4), "estimate"] += 0.001

    with pytest.raises(ODMKError, match="raceethn5_4/estimate"):
        compare_independent_r_baseline(
            r_results, r_metadata, python_validation, python_results
        )


def test_cross_language_source_mismatch_is_rejected() -> None:
    r_results, r_metadata, python_validation, python_results = comparison_artifacts()
    r_metadata.loc[r_metadata["field"].eq("source_data_sha256"), "value"] = "wrong"

    with pytest.raises(ODMKError, match="wrong source fingerprint"):
        compare_independent_r_baseline(
            r_results, r_metadata, python_validation, python_results
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("baseline_analytic_n", "2610", "baseline_analytic_n differs"),
        ("jk1_scale", "1", "jk1_scale differs"),
        ("source_rows", "not-a-number", "source_rows is not numeric"),
        ("survey_version", "", "survey_version is blank"),
    ],
)
def test_invalid_r_metadata_is_rejected(field: str, value: str, message: str) -> None:
    """Reject wrong or unusable R provenance fields with a direct explanation."""

    r_results, r_metadata, python_validation, python_results = comparison_artifacts()
    r_metadata.loc[r_metadata["field"].eq(field), "value"] = value

    with pytest.raises(ODMKError, match=message):
        compare_independent_r_baseline(
            r_results, r_metadata, python_validation, python_results
        )


def test_duplicate_r_metadata_field_is_rejected() -> None:
    """Require one unambiguous value for each R provenance field."""

    r_results, r_metadata, python_validation, python_results = comparison_artifacts()
    r_metadata.loc[1, "field"] = "source_data_sha256"

    with pytest.raises(ODMKError, match="must be unique"):
        compare_independent_r_baseline(
            r_results, r_metadata, python_validation, python_results
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("drop_column", "unexpected columns"),
        ("wrong_label", "label is wrong for race code 4"),
        ("wrong_df", "must use 49 degrees of freedom"),
        ("contrast_count", "cannot have a race code or count"),
        ("negative_se", "standard errors cannot be negative"),
    ],
)
def test_invalid_r_result_structure_is_rejected(mutation: str, message: str) -> None:
    """Reject malformed R rows before comparing their numeric values."""

    r_results, r_metadata, python_validation, python_results = comparison_artifacts()
    if mutation == "drop_column":
        r_results = r_results.drop(columns="label")
    elif mutation == "wrong_label":
        r_results.loc[r_results["race_code"].eq(4), "label"] = "wrong"
    elif mutation == "wrong_df":
        r_results.loc[0, "denominator_degrees_of_freedom"] = 48
    elif mutation == "contrast_count":
        r_results.loc[r_results["result_type"].eq("contrast"), "unweighted_n"] = 1
    elif mutation == "negative_se":
        r_results.loc[0, "standard_error"] = -0.01

    with pytest.raises(ODMKError, match=message):
        compare_independent_r_baseline(
            r_results, r_metadata, python_validation, python_results
        )


def test_incomplete_python_group_record_is_rejected() -> None:
    """Require all five Python Table 2 records and their comparison fields."""

    r_results, r_metadata, python_validation, python_results = comparison_artifacts()
    del python_validation["full_table2"]["jk1_by_raceethn5"]["5"]

    with pytest.raises(ODMKError, match="race codes 1 through 5"):
        compare_independent_r_baseline(
            r_results, r_metadata, python_validation, python_results
        )


def test_unsuccessful_python_baseline_is_rejected() -> None:
    """Do not compare R output with a failed Python baseline row."""

    r_results, r_metadata, python_validation, python_results = comparison_artifacts()
    python_results.loc[0, "status"] = "failed"

    with pytest.raises(ODMKError, match="one successful registered baseline"):
        compare_independent_r_baseline(
            r_results, r_metadata, python_validation, python_results
        )


def test_invalid_comparison_tolerance_is_rejected() -> None:
    """Reject a tolerance that could make the audit meaningless."""

    artifacts = comparison_artifacts()

    with pytest.raises(ODMKError, match="finite and nonnegative"):
        compare_independent_r_baseline(*artifacts, tolerance=float("inf"))
