"""Source-data validation and preregistered variable construction."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .constants import (
    ASIAN_CHECKBOXES,
    EXPECTED_DATA_SHA256,
    EXPECTED_SOURCE_ROWS,
    PCC_ITEMS,
    REPLICATE_WEIGHTS,
)
from .exceptions import DataValidationError
from .utils import sha256_file

REQUIRED_COLUMNS = {
    "hhid",
    "freqgoprovider",
    "raceethn5",
    "hisp_cat",
    "person_finwt0",
    "var_stratum",
    "var_cluster",
    *PCC_ITEMS,
    *ASIAN_CHECKBOXES,
    *REPLICATE_WEIGHTS,
}


def read_canonical_hints(path: Path, *, allow_hash_mismatch: bool = False) -> tuple[pd.DataFrame, str]:
    data_hash = sha256_file(path)
    if data_hash != EXPECTED_DATA_SHA256 and not allow_hash_mismatch:
        raise DataValidationError(
            f"Source SHA-256 is {data_hash}, expected {EXPECTED_DATA_SHA256}"
        )
    raw = pd.read_stata(path, convert_categoricals=False)
    raw.columns = [column.lower() for column in raw.columns]
    validate_source(raw, require_canonical_rows=not allow_hash_mismatch)
    ordered = raw.sort_values("hhid", kind="mergesort").reset_index(drop=True)
    ordered.attrs["source_sha256"] = data_hash
    return ordered, data_hash


def validate_source(df: pd.DataFrame, *, require_canonical_rows: bool = True) -> None:
    missing = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing:
        raise DataValidationError(f"Required source columns absent: {missing}")
    if require_canonical_rows and len(df) != EXPECTED_SOURCE_ROWS:
        raise DataValidationError(f"Expected {EXPECTED_SOURCE_ROWS} records; found {len(df)}")
    if df["hhid"].isna().any() or not df["hhid"].is_unique:
        raise DataValidationError("HHID must be nonmissing and unique")
    if df["person_finwt0"].isna().any() or not df["person_finwt0"].gt(0).all():
        raise DataValidationError("PERSON_FINWT0 must be nonmissing and positive")
    replicate = df[list(REPLICATE_WEIGHTS)]
    if replicate.isna().any().any() or not replicate.ge(0).all().all():
        raise DataValidationError("All 50 replicate weights must be nonmissing and nonnegative")
    if df["var_stratum"].isna().any() or df["var_cluster"].isna().any():
        raise DataValidationError("Taylor design fields must be nonmissing")


def derive_analysis_fields(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    reversed_items: list[str] = []
    for item in PCC_ITEMS:
        name = f"{item}_reversed"
        valid = df[item].where(df[item].isin((1, 2, 3, 4))).astype(float)
        df[name] = 5.0 - valid
        reversed_items.append(name)

    df["pcc_valid_item_count"] = df[reversed_items].notna().sum(axis=1)
    mean_available = df[reversed_items].mean(axis=1)
    df["pppcq_complete7"] = mean_available.where(df["pcc_valid_item_count"].eq(7))
    df["pppcq_atleast4"] = mean_available.where(df["pcc_valid_item_count"].ge(4))

    df["recent_provider_visit"] = df["freqgoprovider"].isin((1, 2, 3, 4, 5, 6))
    df["communication_followup_observed"] = df["pcc_valid_item_count"].gt(0)
    df["content_confirmed_module"] = (
        df["recent_provider_visit"] | df["communication_followup_observed"]
    )

    df["official_asian"] = df["raceethn5"].eq(4)
    df["inclusive_asian"] = (
        df["hisp_cat"].eq(10) & df[list(ASIAN_CHECKBOXES)].eq(1).any(axis=1)
    )
    df["official_white"] = df["raceethn5"].eq(1)
    return df


def validate_canonical_structure(df: pd.DataFrame, registry: dict) -> dict[str, object]:
    pairs = df[["var_stratum", "var_cluster"]].drop_duplicates()
    clusters = df.groupby("var_stratum", observed=True)["var_cluster"].nunique().to_dict()
    if len(clusters) != 2 or sorted(clusters.values()) != [50, 50]:
        raise DataValidationError(f"Expected two strata with 50 clusters each; found {clusters}")
    if len(pairs) - len(clusters) != 98:
        raise DataValidationError("Taylor design degrees of freedom must equal 98")
    if not ((~df["official_asian"]) | df["inclusive_asian"]).all():
        raise DataValidationError("Official Asian records must be contained in inclusive Asian")
    if (df["inclusive_asian"] & df["official_white"]).any():
        raise DataValidationError("Registered Asian and White groups must be disjoint")

    observed = {
        "source_rows": len(df),
        "content_confirmed_module_n": int(df["content_confirmed_module"].sum()),
        "observed_positive_filter_n": int(df["recent_provider_visit"].sum()),
        "complete_7_n_content_confirmed": int(
            (df["content_confirmed_module"] & df["pcc_valid_item_count"].eq(7)).sum()
        ),
        "complete_7_official_asian_n_content_confirmed": int(
            (df["content_confirmed_module"] & df["pcc_valid_item_count"].eq(7) & df["official_asian"]).sum()
        ),
        "complete_7_inclusive_asian_n_content_confirmed": int(
            (df["content_confirmed_module"] & df["pcc_valid_item_count"].eq(7) & df["inclusive_asian"]).sum()
        ),
        "complete_7_white_n_content_confirmed": int(
            (df["content_confirmed_module"] & df["pcc_valid_item_count"].eq(7) & df["official_white"]).sum()
        ),
        "inclusive_asian_additional_multiracial_n_full_source": int(
            (df["inclusive_asian"] & ~df["official_asian"]).sum()
        ),
    }
    expected = {k: v for k, v in registry["structural_anchors"].items() if k != "note"}
    if observed != expected:
        raise DataValidationError(f"Structural anchors changed: {observed} != {expected}")
    return {"structural_anchors": observed, "clusters_per_stratum": clusters, "design_df": 98}


def cell_arrays(df: pd.DataFrame, cell: pd.Series) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sample_name = cell["d01_analytic_sample"]
    if sample_name == "content_confirmed_module":
        sample = df["content_confirmed_module"]
    elif sample_name == "observed_positive_filter_only":
        sample = df["recent_provider_visit"]
    else:
        raise DataValidationError(f"Unknown d01 option: {sample_name}")

    outcome_name = cell["d03_outcome_construction"]
    if outcome_name == "require_7_of_7_valid_items":
        score = df["pppcq_complete7"]
    elif outcome_name == "require_at_least_4_of_7_valid_items":
        score = df["pppcq_atleast4"]
    else:
        raise DataValidationError(f"Unknown d03 option: {outcome_name}")

    race_name = cell["d04_main_predictor_construction"]
    if race_name == "official_mutually_exclusive_raceethn5":
        asian = df["official_asian"]
    elif race_name == "inclusive_nonhispanic_any_asian_identification":
        asian = df["inclusive_asian"]
    else:
        raise DataValidationError(f"Unknown d04 option: {race_name}")

    score_available = score.notna()
    analytic_domain = sample & score_available
    full_design_units = set(
        map(tuple, df[["var_stratum", "var_cluster"]].drop_duplicates().to_numpy())
    )
    domain_design_units = set(
        map(
            tuple,
            df.loc[analytic_domain, ["var_stratum", "var_cluster"]]
            .drop_duplicates()
            .to_numpy(),
        )
    )
    if domain_design_units != full_design_units:
        missing_units = len(full_design_units - domain_design_units)
        raise DataValidationError(
            f"The analytic domain omits {missing_units} released stratum-cluster units"
        )
    asian_domain = (analytic_domain & asian).to_numpy(bool)
    white_domain = (analytic_domain & df["official_white"]).to_numpy(bool)
    if np.any(asian_domain & white_domain):
        raise DataValidationError("Asian and White cell domains overlap")
    return score.to_numpy(float), asian_domain, white_domain
