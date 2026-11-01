from __future__ import annotations

import pandas as pd
import pytest

from odmk.constants import EXPECTED_DATA_SHA256
from odmk.cross_language import R_RESULT_COLUMNS, compare_independent_r_baseline
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
                "label": f"group_{code}",
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
