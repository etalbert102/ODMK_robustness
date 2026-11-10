"""Convert validated ODMK results to the COS results-file specification."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .exceptions import ODMKError


COS_RESULTS_COLUMNS = (
    "paper_id",
    "analyst",
    "spec_id",
    "is_baseline",
    "d01",
    "d02",
    "d03",
    "d04",
    "d05",
    "d06",
    "d07",
    "d08",
    "d09",
    "n_analytic",
    "estimate",
    "estimate_std",
    "se",
    "test_stat",
    "test_stat_type",
    "df1",
    "df2",
    "effect_size",
    "effect_size_measure",
    "p_value",
    "status",
    "error_message",
    "se_procedure",
    "se_unit",
    "se_n_units",
)

OPTION_NAMES = {
    "d01_analytic_sample": {
        "content_confirmed_module": "orig_content",
        "observed_positive_filter_only": "alt_filter",
    },
    "d03_outcome_construction": {
        "require_7_of_7_valid_items": "orig_7of7",
        "require_at_least_4_of_7_valid_items": "alt_4of7",
    },
    "d04_main_predictor_construction": {
        "official_mutually_exclusive_raceethn5": "orig_official",
        "inclusive_nonhispanic_any_asian_identification": "alt_any_asian",
    },
    "d08_variance_estimation": {
        "official_jk1_replicate_weights": "orig_jk1",
        "taylor_linearization": "alt_taylor",
    },
}

FAILURE_STATUS = {
    "nonconvergence": "nonconvergence",
    "singular": "singular",
    "insufficient_n": "insufficient_n",
    "degenerate": "degenerate",
    "not_estimable": "not_estimable",
}

REQUIRED_NATIVE_COLUMNS = {
    "paper_id",
    "specification_id",
    "is_baseline",
    *OPTION_NAMES,
    "status",
    "failure_category",
    "failure_reason",
    "asian_minus_white_difference",
    "standard_error_of_difference",
    "test_statistic",
    "denominator_degrees_of_freedom",
    "two_sided_p_value",
    "unweighted_asian_n",
    "unweighted_white_n",
}


def _option_name(dimension: str, native_name: object) -> str:
    """Return the exact option label used in the approved preregistration."""

    try:
        return OPTION_NAMES[dimension][str(native_name)]
    except KeyError as error:
        raise ODMKError(f"Unregistered {dimension} option in native results: {native_name}") from error


def _spec_number(specification_id: object) -> int:
    """Convert a stable ``ODMK-01`` identifier to the COS integer ID."""

    match = re.fullmatch(r"ODMK-(\d{2})", str(specification_id))
    if match is None:
        raise ODMKError(f"Invalid ODMK specification ID: {specification_id}")
    return int(match.group(1))


def build_cos_results(native: pd.DataFrame, *, analyst: str) -> pd.DataFrame:
    """Map the complete native result table to COS's fixed 29-column schema.

    ``n_analytic`` is the number of disjoint Asian and non-Hispanic White
    respondents contributing to the focal contrast. Records outside those two
    survey domains remain in the full design object for variance estimation but
    do not contribute an outcome to the focal Asian-minus-White estimate.

    The survey standard errors are computed as part of each direct estimator,
    not as a post-fit correction, so the three optional ``se_`` fields remain
    blank under the COS instructions.
    """

    missing = sorted(REQUIRED_NATIVE_COLUMNS.difference(native.columns))
    if missing:
        raise ODMKError(f"Native results lack columns required for COS export: {missing}")
    if len(native) != 16:
        raise ODMKError(f"COS export requires 16 registered rows; found {len(native)}")

    rows: list[dict[str, object]] = []
    for _, result in native.iterrows():
        spec_id = _spec_number(result["specification_id"])
        success = result["status"] == "success"
        if success:
            analytic_n = int(result["unweighted_asian_n"]) + int(
                result["unweighted_white_n"]
            )
            status = "ok"
            error_message: object = ""
        else:
            analytic_n = pd.NA
            category = str(result["failure_category"] or "other")
            status = FAILURE_STATUS.get(category, "other")
            error_message = str(result["failure_reason"] or category)

        rows.append(
            {
                "paper_id": str(result["paper_id"]),
                "analyst": analyst,
                "spec_id": spec_id,
                "is_baseline": int(bool(result["is_baseline"])),
                "d01": _option_name("d01_analytic_sample", result["d01_analytic_sample"]),
                "d02": "",
                "d03": _option_name(
                    "d03_outcome_construction", result["d03_outcome_construction"]
                ),
                "d04": _option_name(
                    "d04_main_predictor_construction",
                    result["d04_main_predictor_construction"],
                ),
                "d05": "",
                "d06": "",
                "d07": "",
                "d08": _option_name(
                    "d08_variance_estimation", result["d08_variance_estimation"]
                ),
                "d09": "",
                "n_analytic": analytic_n,
                "estimate": result["asian_minus_white_difference"] if success else pd.NA,
                "estimate_std": 0 if success else pd.NA,
                "se": result["standard_error_of_difference"] if success else pd.NA,
                "test_stat": result["test_statistic"] if success else pd.NA,
                "test_stat_type": "t" if success else "",
                "df1": result["denominator_degrees_of_freedom"] if success else pd.NA,
                "df2": pd.NA,
                "effect_size": pd.NA,
                "effect_size_measure": "",
                "p_value": result["two_sided_p_value"] if success else pd.NA,
                "status": status,
                "error_message": error_message,
                "se_procedure": "",
                "se_unit": "",
                "se_n_units": pd.NA,
            }
        )

    exported = pd.DataFrame(rows, columns=COS_RESULTS_COLUMNS).sort_values("spec_id")
    validate_cos_results(exported)
    return exported.reset_index(drop=True)


def validate_cos_results(results: pd.DataFrame) -> None:
    """Enforce the COS schema and ODMK-specific registration invariants."""

    if tuple(results.columns) != COS_RESULTS_COLUMNS:
        raise ODMKError("COS results columns or order differ from the supplied specification")
    if results["spec_id"].tolist() != list(range(1, 17)):
        raise ODMKError("COS spec_id must run from 1 through 16 without gaps")
    if not results["paper_id"].eq("ODMK").all():
        raise ODMKError("Every COS result row must identify paper ODMK")
    if int(results["is_baseline"].sum()) != 1 or not bool(results.iloc[0]["is_baseline"]):
        raise ODMKError("Exactly specification 1 must be the COS baseline")
    if not results["status"].isin({"ok", *FAILURE_STATUS.values(), "other"}).all():
        raise ODMKError("COS results contain an unsupported status")

    successful = results["status"].eq("ok")
    required_when_ok = (
        "n_analytic",
        "estimate",
        "estimate_std",
        "se",
        "test_stat",
        "test_stat_type",
        "df1",
        "p_value",
    )
    if results.loc[successful, list(required_when_ok)].isna().any().any():
        raise ODMKError("A successful COS row has a missing required estimate field")
    if not results.loc[successful, "test_stat_type"].eq("t").all():
        raise ODMKError("Every successful ODMK row must report a t statistic")
    if not results.loc[successful, "estimate_std"].eq(0).all():
        raise ODMKError("The PPPCQ mean difference is not standardized")
    if not results.loc[successful, "n_analytic"].gt(0).all():
        raise ODMKError("Every successful ODMK row must have a positive analytic N")

    failed = ~successful
    failed_numeric = (
        "n_analytic",
        "estimate",
        "estimate_std",
        "se",
        "test_stat",
        "df1",
        "df2",
        "effect_size",
        "p_value",
    )
    failed_text = ("test_stat_type", "effect_size_measure")
    if results.loc[failed, list(failed_numeric)].notna().any().any() or not results.loc[
        failed, list(failed_text)
    ].eq("").all().all():
        raise ODMKError("A failed COS row must leave n_analytic through p_value blank")
    if results.loc[failed, "error_message"].eq("").any():
        raise ODMKError("A failed COS row must explain the failure")


def write_cos_results(results: pd.DataFrame, path: Path) -> None:
    """Write a validated UTF-8, comma-delimited COS results file."""

    validate_cos_results(results)
    path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(path, index=False, encoding="utf-8", na_rep="")
