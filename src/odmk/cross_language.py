"""Validate the independent R reconstruction against the Python baseline."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from .constants import (
    EXPECTED_BASELINE_N,
    EXPECTED_DATA_SHA256,
    EXPECTED_SOURCE_ROWS,
    JK1_COEFFICIENT,
    JK1_DF,
)
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
EXPECTED_GROUP_LABELS = {
    1: "non_hispanic_white",
    2: "non_hispanic_black",
    3: "hispanic",
    4: "non_hispanic_asian",
    5: "non_hispanic_other",
}
CONTRAST_LABEL = "non_hispanic_asian_minus_non_hispanic_white"
REQUIRED_METADATA = {
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


def _validate_r_metadata(r_metadata: pd.DataFrame) -> None:
    """Require the canonical source, sample, and JK1 design in R metadata."""

    metadata = _metadata_values(r_metadata)
    missing = sorted(REQUIRED_METADATA.difference(metadata))
    if missing:
        raise ODMKError(f"Independent R metadata fields are missing: {missing}")
    if metadata["source_data_sha256"] != EXPECTED_DATA_SHA256:
        raise ODMKError("Independent R output records the wrong source fingerprint")

    expected_numeric = {
        "source_rows": float(EXPECTED_SOURCE_ROWS),
        "baseline_analytic_n": float(EXPECTED_BASELINE_N),
        "jk1_scale": JK1_COEFFICIENT,
        "design_degrees_of_freedom": float(JK1_DF),
    }
    for field, expected in expected_numeric.items():
        try:
            observed = float(metadata[field])
        except ValueError as error:
            raise ODMKError(f"Independent R {field} is not numeric") from error
        if not math.isclose(observed, expected, rel_tol=0, abs_tol=1e-12):
            raise ODMKError(f"Independent R {field} differs from {expected:g}")
    for field in ("r_version", "digest_version", "haven_version", "survey_version"):
        if not metadata[field].strip():
            raise ODMKError(f"Independent R {field} is blank")


def _validate_r_results(r_results: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Check the six-row R result schema and return its means and contrast."""

    if tuple(r_results.columns) != R_RESULT_COLUMNS:
        raise ODMKError("Independent R results have unexpected columns")
    if len(r_results) != 6:
        raise ODMKError("Independent R results must contain five means and one contrast")

    results = r_results.copy()
    numeric_columns = (
        "race_code",
        "unweighted_n",
        "estimate",
        "standard_error",
        "ci_low_95",
        "ci_high_95",
        "denominator_degrees_of_freedom",
    )
    for column in numeric_columns:
        results[column] = pd.to_numeric(results[column], errors="coerce")
    always_numeric = (
        "estimate",
        "standard_error",
        "ci_low_95",
        "ci_high_95",
        "denominator_degrees_of_freedom",
    )
    if not np.isfinite(results[list(always_numeric)].to_numpy(float)).all():
        raise ODMKError("Independent R estimates must be finite numbers")
    if not results["denominator_degrees_of_freedom"].eq(JK1_DF).all():
        raise ODMKError(f"Independent R results must use {JK1_DF} degrees of freedom")
    if not results["standard_error"].ge(0).all():
        raise ODMKError("Independent R standard errors cannot be negative")

    group_rows = results.loc[results["result_type"].eq("group_mean")].copy()
    if len(group_rows) != 5 or group_rows["race_code"].isna().any():
        raise ODMKError("Independent R output must contain five coded group means")
    codes = group_rows["race_code"].to_numpy(float)
    if not np.equal(codes, np.floor(codes)).all() or set(codes.astype(int)) != set(
        EXPECTED_GROUP_LABELS
    ):
        raise ODMKError("Independent R output must contain race codes 1 through 5")
    if group_rows["unweighted_n"].isna().any() or not (
        group_rows["unweighted_n"].gt(0)
        & group_rows["unweighted_n"].eq(np.floor(group_rows["unweighted_n"]))
    ).all():
        raise ODMKError("Independent R group counts must be positive integers")
    for _, row in group_rows.iterrows():
        code = int(row["race_code"])
        if row["label"] != EXPECTED_GROUP_LABELS[code]:
            raise ODMKError(f"Independent R label is wrong for race code {code}")

    contrast_rows = results.loc[results["result_type"].eq("contrast")]
    if len(contrast_rows) != 1:
        raise ODMKError("Independent R output must contain exactly one focal contrast")
    contrast = contrast_rows.iloc[0]
    if contrast["label"] != CONTRAST_LABEL:
        raise ODMKError("Independent R focal contrast has the wrong label")
    if pd.notna(contrast["race_code"]) or pd.notna(contrast["unweighted_n"]):
        raise ODMKError("Independent R focal contrast cannot have a race code or count")
    return group_rows.sort_values("race_code"), contrast


def _validate_python_baseline(
    python_validation: dict[str, Any], python_results: pd.DataFrame
) -> tuple[dict[str, Any], pd.Series]:
    """Return the five Python groups and one successful focal baseline row."""

    if len(python_results) != 1 or python_results.iloc[0].get("status") != "success":
        raise ODMKError("Python comparison requires one successful registered baseline")
    python_contrast = python_results.iloc[0]
    required_contrast_fields = set(CONTRAST_STATISTICS.values()) | {
        "denominator_degrees_of_freedom"
    }
    missing_contrast = sorted(required_contrast_fields.difference(python_results.columns))
    if missing_contrast:
        raise ODMKError(f"Python baseline fields are missing: {missing_contrast}")

    try:
        python_groups = python_validation["full_table2"]["jk1_by_raceethn5"]
    except (KeyError, TypeError) as error:
        raise ODMKError("Python validation lacks the five-group Table 2 record") from error
    if not isinstance(python_groups, dict) or set(python_groups) != {
        str(code) for code in EXPECTED_GROUP_LABELS
    }:
        raise ODMKError("Python validation must contain Table 2 race codes 1 through 5")
    required_group_fields = {"unweighted_n", *GROUP_STATISTICS.values()}
    for code, group in python_groups.items():
        if not isinstance(group, dict):
            raise ODMKError(f"Python Table 2 race code {code} is not a record")
        missing_group = sorted(required_group_fields.difference(group))
        if missing_group:
            raise ODMKError(
                f"Python Table 2 race code {code} fields are missing: {missing_group}"
            )
    return python_groups, python_contrast


def compare_independent_r_baseline(
    r_results: pd.DataFrame,
    r_metadata: pd.DataFrame,
    python_validation: dict[str, Any],
    python_results: pd.DataFrame,
    *,
    tolerance: float = 1e-9,
) -> pd.DataFrame:
    """Compare all five R group results and the focal contrast with Python.

    Args:
        r_results: Six-row R output containing five group means and the focal
            Asian-minus-White contrast.
        r_metadata: R runtime, package, source, design, and sample metadata.
        python_validation: Parsed Python ``validation.json`` record.
        python_results: Parsed one-row Python registered-baseline result file.
        tolerance: Maximum absolute difference for each numeric comparison.

    Returns:
        One audit row per count or statistic with both values, their absolute
        difference, the tolerance, and passing status.

    Raises:
        ODMKError: If an artifact has the wrong schema or identity, if either
            implementation did not use the canonical baseline, or if any value
            differs by more than ``tolerance``.
    """

    if not math.isfinite(tolerance) or tolerance < 0:
        raise ODMKError("Cross-language tolerance must be finite and nonnegative")
    _validate_r_metadata(r_metadata)
    group_rows, contrast = _validate_r_results(r_results)
    python_groups, python_contrast = _validate_python_baseline(
        python_validation, python_results
    )
    audit_rows: list[dict[str, object]] = []

    def record(component: str, statistic: str, r_value: float, python_value: float) -> None:
        """Append one passing comparison or raise on a mismatch."""

        difference = abs(r_value - python_value)
        passed = math.isfinite(difference) and difference <= tolerance
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

    for _, r_row in group_rows.iterrows():
        code = str(int(r_row["race_code"]))
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
