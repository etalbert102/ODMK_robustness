#!/usr/bin/env python3
"""Reconstruct the published ODMK HINTS 5 Cycle 2 baseline.

This program intentionally runs only the published/baseline reconstruction.  It
does not execute any robustness alternatives.  The bounded multiverse is to be
implemented only after the proposal's specification set is frozen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


EXPECTED_DATA_SHA256 = "a727f1b7a56f293dc2212bb9cc8705cacdc4e57d6d8e5505012b713ecfd1531f"
JK_COEFFICIENT = 0.98
JK_DF = 49

PCC_ITEMS = [
    "chanceaskquestions",
    "feelingsaddressed",
    "involveddecisions",
    "understoodnextsteps",
    "explainedclearly",
    "spentenoughtime",
    "helpuncertainty",
]
RACE_LABELS = {
    1: "Non-Hispanic White",
    2: "Non-Hispanic Black",
    3: "Hispanic",
    4: "Non-Hispanic Asian",
    5: "Non-Hispanic Other",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    return float(np.sum(values * weights) / np.sum(weights))


def jackknife_summary(full: float, replicates: np.ndarray, df: int = JK_DF) -> dict[str, float]:
    variance = float(JK_COEFFICIENT * np.sum((replicates - full) ** 2))
    se = math.sqrt(variance)
    critical = float(stats.t.ppf(0.975, df))
    t_value = full / se if se > 0 else math.nan
    p_value = float(2 * stats.t.sf(abs(t_value), df)) if se > 0 else math.nan
    return {
        "estimate": full,
        "se": se,
        "ci_low": full - critical * se,
        "ci_high": full + critical * se,
        "t": t_value,
        "df": df,
        "p_value": p_value,
    }


def recode_positive(series: pd.Series) -> pd.Series:
    return series.where(series > 0).astype(float)


def make_derived(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # HINTS source coding is 1=Always, ..., 4=Never.  Reverse to 1=Never,
    # ..., 4=Always, as stated by the article.
    reversed_items = []
    for item in PCC_ITEMS:
        valid = out[item].where(out[item].isin([1, 2, 3, 4])).astype(float)
        new_name = f"{item}_reversed"
        out[new_name] = 5.0 - valid
        reversed_items.append(new_name)

    out["pcc_valid_item_count"] = out[reversed_items].notna().sum(axis=1)
    out["pppcq_complete7"] = out[reversed_items].mean(axis=1).where(
        out["pcc_valid_item_count"] == 7
    )
    out["race5"] = recode_positive(out["raceethn5"])
    # A valid C4 response is direct evidence that the communication follow-up
    # was administered.  Do not discard it merely because the upstream routing
    # item was not ascertained; the methodology report explicitly permits a
    # missing filter alongside an answered follow-up.
    out["communication_followup_observed"] = out["pcc_valid_item_count"] > 0
    out["recent_provider_visit"] = out["freqgoprovider"].isin([1, 2, 3, 4, 5, 6])
    # The fixed substantive module population includes respondents with an
    # observed positive routing response and respondents whose valid follow-up
    # answers establish that the module was administered despite a missing
    # filter. Outcome-scoring rules govern observed analytic coverage within
    # this population; they do not redefine the target population.
    out["c4_module_eligible"] = (
        out["recent_provider_visit"] | out["communication_followup_observed"]
    )

    return out


def table2_reproduction(df: pd.DataFrame, replicate_cols: list[str]) -> tuple[pd.DataFrame, dict]:
    analytic = df.loc[df["pppcq_complete7"].notna() & df["race5"].isin(RACE_LABELS)].copy()
    rows: list[dict] = []
    group_estimates: dict[int, tuple[float, np.ndarray]] = {}

    for code, label in RACE_LABELS.items():
        group = analytic.loc[analytic["race5"] == code]
        y = group["pppcq_complete7"].to_numpy(float)
        full = weighted_mean(y, group["person_finwt0"].to_numpy(float))
        reps = np.array(
            [weighted_mean(y, group[col].to_numpy(float)) for col in replicate_cols]
        )
        summary = jackknife_summary(full, reps)
        group_estimates[code] = (full, reps)
        rows.append(
            {
                "race_code": code,
                "race_group": label,
                "source_race_group_n": int((df["race5"] == code).sum()),
                "analytic_n_complete7": len(group),
                **summary,
            }
        )

    asian_full, asian_reps = group_estimates[4]
    white_full, white_reps = group_estimates[1]
    contrast = jackknife_summary(asian_full - white_full, asian_reps - white_reps)
    contrast["contrast"] = "Non-Hispanic Asian minus non-Hispanic White"
    contrast["analytic_n"] = len(analytic)
    return pd.DataFrame(rows), contrast


def cronbach_alpha_complete(df: pd.DataFrame) -> float:
    columns = [f"{item}_reversed" for item in PCC_ITEMS]
    complete = df.loc[df[columns].notna().all(axis=1), columns].to_numpy(float)
    item_variances = complete.var(axis=0, ddof=1)
    total_variance = complete.sum(axis=1).var(ddof=1)
    k = complete.shape[1]
    return float(k / (k - 1) * (1 - item_variances.sum() / total_variance))


def build_qa(df: pd.DataFrame, replicate_cols: list[str], data_hash: str) -> dict:
    item_valid_counts = {item: int(df[item].isin([1, 2, 3, 4]).sum()) for item in PCC_ITEMS}
    pcc_count_distribution = {
        str(int(key)): int(value)
        for key, value in df["pcc_valid_item_count"].value_counts().sort_index().items()
    }
    race_counts = {
        str(int(key)): int(value)
        for key, value in df.loc[df["race5"].notna(), "race5"].value_counts().sort_index().items()
    }
    return {
        "data_sha256": data_hash,
        "expected_data_sha256": EXPECTED_DATA_SHA256,
        "row_count": len(df),
        "hhid_nonmissing": bool(df["hhid"].notna().all()),
        "hhid_unique": bool(df["hhid"].is_unique),
        "hhid_sort_monotonic": bool(df["hhid"].is_monotonic_increasing),
        "column_count_after_derivation": len(df.columns),
        "replicate_weight_count": len(replicate_cols),
        "all_full_weights_positive": bool((df["person_finwt0"] > 0).all()),
        "all_replicate_weights_nonnegative": bool((df[replicate_cols] >= 0).all().all()),
        "full_weight_sum": float(df["person_finwt0"].sum()),
        "race5_counts": race_counts,
        "recent_provider_visit_n": int(df["recent_provider_visit"].sum()),
        "c4_module_eligible_n": int(df["c4_module_eligible"].sum()),
        "any_valid_communication_item_n": int(df["communication_followup_observed"].sum()),
        "item_valid_counts": item_valid_counts,
        "pcc_valid_item_count_distribution": pcc_count_distribution,
        "complete7_n": int(df["pppcq_complete7"].notna().sum()),
        "complete7_with_valid_race_n": int(
            (df["pppcq_complete7"].notna() & df["race5"].isin(RACE_LABELS)).sum()
        ),
        "complete7_with_freqgoprovider_missing_n": int(
            (df["pppcq_complete7"].notna() & (df["freqgoprovider"] == -9)).sum()
        ),
        "complete7_with_valid_race_and_freqgoprovider_missing_n": int(
            (
                df["pppcq_complete7"].notna()
                & df["race5"].isin(RACE_LABELS)
                & (df["freqgoprovider"] == -9)
            ).sum()
        ),
        "complete7_with_valid_race_and_observed_positive_freqgoprovider_n": int(
            (
                df["pppcq_complete7"].notna()
                & df["race5"].isin(RACE_LABELS)
                & df["recent_provider_visit"]
            ).sum()
        ),
        "complete7_score_min": float(df["pppcq_complete7"].min()),
        "complete7_score_max": float(df["pppcq_complete7"].max()),
        "cronbach_alpha_unweighted_complete7": cronbach_alpha_complete(df),
        "jk_coefficient": JK_COEFFICIENT,
        "jk_degrees_of_freedom": JK_DF,
    }


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=Path,
        default=project_root / "data_raw" / "hints5_cycle2_public.dta",
    )
    parser.add_argument("--project-root", type=Path, default=project_root)
    parser.add_argument(
        "--allow-hash-mismatch",
        action="store_true",
        help="Permit a differently hashed official data release after manual provenance review.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_path = args.data.resolve()
    project_root = args.project_root.resolve()
    outputs = project_root / "outputs"
    processed = project_root / "data_processed"
    outputs.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)

    data_hash = sha256(data_path)
    if data_hash != EXPECTED_DATA_SHA256 and not args.allow_hash_mismatch:
        raise RuntimeError(
            f"Source-data SHA-256 mismatch: got {data_hash}; expected {EXPECTED_DATA_SHA256}. "
            "Review provenance, then use --allow-hash-mismatch only if appropriate."
        )

    raw = pd.read_stata(data_path, convert_categoricals=False)
    raw.columns = [name.lower() for name in raw.columns]
    replicate_cols = [f"person_finwt{i}" for i in range(1, 51)]
    required = {
        "hhid",
        "freqgoprovider",
        "raceethn5",
        "person_finwt0",
        "var_stratum",
        "var_cluster",
        *PCC_ITEMS,
        *replicate_cols,
    }
    missing_columns = sorted(required.difference(raw.columns))
    if missing_columns:
        raise KeyError(f"Required source columns absent: {missing_columns}")
    if len(raw) != 3504:
        raise AssertionError(f"Expected 3,504 public-use records; found {len(raw)}")
    if raw["hhid"].isna().any() or not raw["hhid"].is_unique:
        raise AssertionError("HHID must be nonmissing and unique before deterministic sorting")
    raw = raw.sort_values("hhid", kind="mergesort").reset_index(drop=True)

    df = make_derived(raw)
    table2, contrast = table2_reproduction(df, replicate_cols)
    qa = build_qa(df, replicate_cols, data_hash)

    # Published anchors are used only to validate the baseline reconstruction.
    published_means = {1: 3.45, 2: 3.49, 3: 3.27, 4: 3.11, 5: 3.33}
    for code, target in published_means.items():
        observed = float(table2.loc[table2["race_code"] == code, "estimate"].iloc[0])
        # The paper's displayed values appear truncated for some groups rather
        # than rounded conventionally, so agreement within 0.01 is the relevant
        # two-decimal reproduction check.
        if abs(observed - target) > 0.011:
            raise AssertionError(
                f"Table 2 mean failed reproduction for race code {code}: {observed:.6f} vs {target:.2f}"
            )
    if qa["complete7_with_valid_race_n"] != 2611:
        raise AssertionError("Expected the published focal-analysis N=2,611")
    routing_anchors = {
        "c4_module_eligible_n": 2993,
        "any_valid_communication_item_n": 2951,
        "complete7_with_freqgoprovider_missing_n": 30,
        "complete7_with_valid_race_and_freqgoprovider_missing_n": 22,
        "complete7_with_valid_race_and_observed_positive_freqgoprovider_n": 2589,
    }
    for name, expected in routing_anchors.items():
        if qa[name] != expected:
            raise AssertionError(f"Routing QA anchor {name} changed: {qa[name]} != {expected}")

    exclusion_flow = pd.DataFrame(
        [
            {"stage": "Public-use file", "n": len(df)},
            {"stage": "Fixed C4 module population", "n": qa["c4_module_eligible_n"]},
            {"stage": "At least one valid C4 communication response", "n": qa["any_valid_communication_item_n"]},
            {"stage": "All seven PCC items valid", "n": int(df["pppcq_complete7"].notna().sum())},
            {"stage": "All seven PCC items valid and RaceEthn5 valid", "n": qa["complete7_with_valid_race_n"]},
        ]
    )

    table2.to_csv(outputs / "table2_reproduction.csv", index=False)
    exclusion_flow.to_csv(outputs / "exclusion_flow.csv", index=False)
    (outputs / "qa_checks.json").write_text(json.dumps(qa, indent=2) + "\n")
    summary = {
        "table2_asian_minus_white": contrast,
        "guardrail": "No robustness alternatives were executed by this program.",
    }
    (outputs / "baseline_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    source_and_derived = [
        "hhid",
        "freqgoprovider",
        *PCC_ITEMS,
        *[f"{item}_reversed" for item in PCC_ITEMS],
        "pcc_valid_item_count",
        "pppcq_complete7",
        "raceethn5",
        "race5",
        "communication_followup_observed",
        "recent_provider_visit",
        "c4_module_eligible",
        "person_finwt0",
        "var_stratum",
        "var_cluster",
        *replicate_cols,
    ]
    df[source_and_derived].to_csv(
        processed / "odmk_baseline_derived.csv.gz", index=False, compression="gzip"
    )

    print(json.dumps({"qa": qa, "asian_minus_white": contrast}, indent=2))


if __name__ == "__main__":
    main()
