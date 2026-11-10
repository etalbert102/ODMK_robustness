from pathlib import Path

import pandas as pd
import pytest

from odmk.cos_reporting import (
    COS_RESULTS_COLUMNS,
    build_cos_results,
    validate_cos_results,
    write_cos_results,
)
from odmk.exceptions import ODMKError
from odmk.registry import build_manifest, load_registry


def test_cos_columns_match_supplied_results_header() -> None:
    root = Path(__file__).resolve().parents[1]
    supplied_header = pd.read_csv(
        root / "sources/COS_results_file_header.csv", nrows=0
    ).columns

    assert tuple(supplied_header) == COS_RESULTS_COLUMNS


def native_results() -> pd.DataFrame:
    root = Path(__file__).resolve().parents[1]
    manifest = build_manifest(load_registry(root / "specification_freeze.yaml"))
    results = manifest.copy()
    results["paper_id"] = "ODMK"
    results["status"] = "success"
    results["failure_category"] = ""
    results["failure_reason"] = ""
    results["asian_minus_white_difference"] = -0.3
    results["standard_error_of_difference"] = 0.1
    results["test_statistic"] = -3.0
    results["denominator_degrees_of_freedom"] = results[
        "d08_variance_estimation"
    ].map({"official_jk1_replicate_weights": 49, "taylor_linearization": 98})
    results["two_sided_p_value"] = 0.004
    results["unweighted_asian_n"] = 105
    results["unweighted_white_n"] = 1703
    return results


def test_cos_export_has_exact_schema_and_registered_option_names(tmp_path: Path) -> None:
    exported = build_cos_results(native_results(), analyst="Eli Talbert")

    assert tuple(exported.columns) == COS_RESULTS_COLUMNS
    assert exported["spec_id"].tolist() == list(range(1, 17))
    assert exported["is_baseline"].sum() == 1
    assert exported.loc[0, ["d01", "d03", "d04", "d08"]].tolist() == [
        "orig_content",
        "orig_7of7",
        "orig_official",
        "orig_jk1",
    ]
    assert exported.loc[15, ["d01", "d03", "d04", "d08"]].tolist() == [
        "alt_filter",
        "alt_4of7",
        "alt_any_asian",
        "alt_taylor",
    ]
    assert exported["n_analytic"].eq(1808).all()
    assert exported[["d02", "d05", "d06", "d07", "d09"]].eq("").all().all()
    assert exported[["se_procedure", "se_unit"]].eq("").all().all()
    assert exported["se_n_units"].isna().all()

    output = tmp_path / "results_ODMK.csv"
    write_cos_results(exported, output)
    header = output.read_text(encoding="utf-8").splitlines()[0].split(",")
    assert tuple(header) == COS_RESULTS_COLUMNS


def test_failed_cell_is_retained_with_blank_estimates() -> None:
    native = native_results()
    native.loc[10, "status"] = "failed"
    native.loc[10, "failure_category"] = "insufficient_n"
    native.loc[10, "failure_reason"] = "Registered focal group is empty"

    exported = build_cos_results(native, analyst="Eli Talbert")
    failed = exported.iloc[10]

    assert failed["status"] == "insufficient_n"
    assert failed["error_message"] == "Registered focal group is empty"
    assert pd.isna(failed["n_analytic"])
    assert pd.isna(failed["estimate"])
    assert pd.isna(failed["p_value"])


def test_cos_export_rejects_unknown_option() -> None:
    native = native_results()
    native.loc[0, "d01_analytic_sample"] = "post_hoc_sample"

    with pytest.raises(ODMKError, match="Unregistered d01_analytic_sample option"):
        build_cos_results(native, analyst="Eli Talbert")


def test_cos_validation_rejects_missing_specification() -> None:
    exported = build_cos_results(native_results(), analyst="Eli Talbert").iloc[:-1]

    with pytest.raises(ODMKError, match="spec_id"):
        validate_cos_results(exported)
