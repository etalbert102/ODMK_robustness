"""Cross-language validation for the independent R baseline reconstruction."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from .constants import EXPECTED_DATA_SHA256, JK1_DF
from .exceptions import ODMKError


R_RESULT_COLUMNS = (
    "result_type",
    "label",
    "race_code",
    "unweighted_n",
    "estimate",
    "standard_error",
    "ci_low_95",
    "ci_high_95",
    "denominator_degrees_of_freedom",
)
GROUP_STATISTICS = {
    "estimate": "mean",
    "standard_error": "se",
    "ci_low_95": "ci_low",
    "ci_high_95": "ci_high",
}
CONTRAST_STATISTICS = {
    "estimate": "asian_minus_white_difference",
    "standard_error": "standard_error_of_difference",
    "ci_low_95": "ci_low_95",
    "ci_high_95": "ci_high_95",
}


def _metadata_values(metadata: pd.DataFrame) -> dict[str, str]:
    """Return a unique field-to-value mapping from the R metadata table."""

    if tuple(metadata.columns) != ("field", "value"):
        raise ODMKError("Independent R metadata has unexpected columns")
    if metadata["field"].duplicated().any():
        raise ODMKError("Independent R metadata fields must be unique")
    return {
        str(field): str(value)
        for field, value in metadata[["field", "value"]].itertuples(index=False)
    }


def compare_independent_r_baseline(
    r_results: pd.DataFrame,
    r_metadata: pd.DataFrame,
    python_validation: dict[str, Any],
    python_results: pd.DataFrame,
    *,
    tolerance: float = 1e-9,
) -> pd.DataFrame:
    """Compare the independent R baseline with Python's registered baseline.

    Args:
        r_results: Six-row R output containing five group means and the focal
            Asian-minus-White contrast.
        r_metadata: R runtime, package, source, design, and sample metadata.
        python_validation: Parsed Python ``validation.json`` record.
        python_results: Parsed one-row Python registered-baseline result file.
        tolerance: Maximum absolute difference for each cross-language numeric
            comparison.

    Returns:
        One audit row per count or statistic with R and Python values, absolute
        difference, tolerance, and passing status.

    Raises:
        ODMKError: If either artifact has the wrong schema or identity, if R did
            not reconstruct the canonical sample and design, or if any numeric
            result differs by more than ``tolerance``.
    """

    if tuple(r_results.columns) != R_RESULT_COLUMNS:
        raise ODMKError("Independent R results have unexpected columns")
    if len(r_results) != 6:
        raise ODMKError("Independent R results must contain five means and one contrast")
    if len(python_results) != 1 or python_results.iloc[0].get("status") != "success":
        raise ODMKError("Python comparison requires one successful registered baseline")

    metadata = _metadata_values(r_metadata)
    required_metadata = {
        "source_data_sha256",
        "source_rows",
        "baseline_analytic_n",
        "r_version",
        "digest_version",
        "haven_version",
        "survey_version",
        "jk1_scale",
        "design_degrees_of_freedom",
    }
    if not required_metadata.issubset(metadata):
        missing = sorted(required_metadata.difference(metadata))
        raise ODMKError(f"Independent R metadata fields are missing: {missing}")
    if metadata["source_data_sha256"] != EXPECTED_DATA_SHA256:
        raise ODMKError("Independent R output records the wrong source fingerprint")
    exact_metadata = {
        "source_rows": 3504,
        "baseline_analytic_n": 2611,
        "design_degrees_of_freedom": JK1_DF,
    }
    for field, expected in exact_metadata.items():
        if int(float(metadata[field])) != expected:
            raise ODMKError(f"Independent R {field} differs from {expected}")
    if not math.isclose(float(metadata["jk1_scale"]), 0.98, rel_tol=0, abs_tol=1e-12):
        raise ODMKError("Independent R JK1 scale differs from 0.98")

    try:
        python_groups = python_validation["full_table2"]["jk1_by_raceethn5"]
    except (KeyError, TypeError) as error:
        raise ODMKError("Python validation lacks the five-group Table 2 record") from error

    audit_rows: list[dict[str, object]] = []

    def record(component: str, statistic: str, r_value: float, python_value: float) -> None:
        """Append one passing comparison or raise on a cross-language mismatch."""

        difference = abs(r_value - python_value)
        passed = difference <= tolerance
        audit_rows.append(
            {
                "component": component,
                "statistic": statistic,
                "r_value": r_value,
                "python_value": python_value,
                "absolute_difference": difference,
                "tolerance": tolerance,
                "passed": passed,
            }
        )
        if not passed:
            raise ODMKError(
                f"Independent R mismatch for {component}/{statistic}: "
                f"{r_value} vs {python_value}"
            )

    group_rows = r_results.loc[r_results["result_type"].eq("group_mean")]
    if set(group_rows["race_code"].astype(int)) != set(range(1, 6)):
        raise ODMKError("Independent R output must contain race codes 1 through 5")
    for _, r_row in group_rows.sort_values("race_code").iterrows():
        code = str(int(r_row["race_code"]))
        if code not in python_groups:
            raise ODMKError(f"Python validation lacks race code {code}")
        python_group = python_groups[code]
        record(
            f"raceethn5_{code}",
            "unweighted_n",
            float(r_row["unweighted_n"]),
            float(python_group["unweighted_n"]),
        )
        for r_name, python_name in GROUP_STATISTICS.items():
            record(
                f"raceethn5_{code}",
                r_name,
                float(r_row[r_name]),
                float(python_group[python_name]),
            )

    contrast_rows = r_results.loc[r_results["result_type"].eq("contrast")]
    if len(contrast_rows) != 1:
        raise ODMKError("Independent R output must contain exactly one focal contrast")
    contrast = contrast_rows.iloc[0]
    python_contrast = python_results.iloc[0]
    for r_name, python_name in CONTRAST_STATISTICS.items():
        record(
            "asian_minus_white",
            r_name,
            float(contrast[r_name]),
            float(python_contrast[python_name]),
        )
    record(
        "asian_minus_white",
        "denominator_degrees_of_freedom",
        float(contrast["denominator_degrees_of_freedom"]),
        float(python_contrast["denominator_degrees_of_freedom"]),
    )
    return pd.DataFrame(audit_rows)
