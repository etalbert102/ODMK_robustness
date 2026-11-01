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


def read_canonical_hints(path: Path) -> tuple[pd.DataFrame, str]:
    """Read, normalize, validate, and deterministically order the HINTS file.

    Returns the complete 3,504-row frame and its SHA-256. The hash is also
    attached to ``DataFrame.attrs`` so later execution cannot silently pair a
    frame with different provenance. This production reader accepts only the
    frozen public-use file; synthetic tests construct data frames directly.

    Raises:
        DataValidationError: If the file fingerprint, row count, identifiers,
            required columns, weights, or design fields fail validation.
    """

    data_hash = sha256_file(path)
    if data_hash != EXPECTED_DATA_SHA256:
        raise DataValidationError(
            f"Source SHA-256 is {data_hash}, expected {EXPECTED_DATA_SHA256}"
        )
    raw = pd.read_stata(path, convert_categoricals=False)
    raw.columns = [column.lower() for column in raw.columns]
    validate_source(raw, require_canonical_rows=True)
    ordered = raw.sort_values("hhid", kind="mergesort").reset_index(drop=True)
    ordered.attrs["source_sha256"] = data_hash
    return ordered, data_hash


def validate_source(df: pd.DataFrame, *, require_canonical_rows: bool = True) -> None:
    """Validate fields and design weights required by every registered cell.

    Args:
        df: Source frame whose column names have already been normalized to
            lowercase.
        require_canonical_rows: Whether to require exactly 3,504 records. Tests
            may disable only this row-count check for synthetic frames.

    Raises:
        DataValidationError: If required columns, identifiers, row count,
            final weights, replicate weights, or Taylor design fields are
            invalid.
    """

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
    """Construct the two scores, two eligibility rules, and focal race groups.

    The returned frame retains every source record. It adds seven reverse-coded
    items, valid-item counts, both PPPCQ scores, both eligibility indicators,
    the routing diagnostics, and the official/inclusive Asian and official
    White indicators. Eligibility and race are Boolean survey-domain indicators;
    no row is filtered and no missing item is imputed at this stage.
    """

    df = raw.copy()

    # Outcome construction: reverse all seven source items so that larger
    # values consistently mean better communication, then create both frozen
    # completion rules without imputing an item.
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

    # Sample construction: one rule uses the recorded visit response only; the
    # other also recognizes an answered follow-up when the routing response is
    # explicitly missing. A recorded zero is never overridden by follow-up
    # content.
    df["recent_provider_visit"] = df["freqgoprovider"].isin((1, 2, 3, 4, 5, 6))
    df["provider_visit_response_missing"] = df["freqgoprovider"].eq(-9)
    df["communication_followup_observed"] = df["pcc_valid_item_count"].gt(0)
    df["content_confirmed_module"] = (
        df["recent_provider_visit"]
        | (
            df["provider_visit_response_missing"]
            & df["communication_followup_observed"]
        )
    )

    # Group construction: White remains the official mutually exclusive group
    # under both options. Only the Asian-group definition varies.
    df["official_asian"] = df["raceethn5"].eq(4)
    df["inclusive_asian"] = (
        df["hisp_cat"].eq(10) & df[list(ASIAN_CHECKBOXES)].eq(1).any(axis=1)
    )
    df["official_white"] = df["raceethn5"].eq(1)
    return df


def validate_canonical_structure(df: pd.DataFrame, registry: dict) -> dict[str, object]:
    """Match the complete derived frame to frozen membership and design anchors.

    Returns a validation record containing ``structural_anchors``,
    ``clusters_per_stratum``, and ``design_df`` for inclusion in the run output.

    Raises:
        DataValidationError: If the released design, group relationships, or
            any registry-defined structural count differs from its frozen value.
    """

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
    """Return one cell's outcome and full-frame Asian and White domains.

    The outcome array has one value per source record. The two Boolean arrays
    combine the selected eligibility, score-availability, and race rules while
    preserving the full survey frame for variance estimation.

    Raises:
        DataValidationError: If an option label is not registered, the analytic
            domain omits a released design unit, or the focal groups overlap.
    """

    # Translate the frozen registry labels into the derived columns above. The
    # explicit branches make every permitted option visible to a code reviewer.
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
