#!/usr/bin/env python3
"""Structural preflight for the frozen ODMK MICE design.

This program checks design-matrix rank and binary-model separation without
performing an imputation, fitting a focal analysis, or estimating any racial
contrast.  It is safe to run before the multiverse is authorized.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linprog

from baseline_analysis import EXPECTED_DATA_SHA256, PCC_ITEMS, make_derived, sha256


TARGETS = [
    "age_years",
    "female",
    "college_graduate",
    "married_or_partnered",
    "currently_employed",
    "english_very_well",
]
BINARY_TARGETS = set(TARGETS[1:])


def numerical_rank(x: np.ndarray) -> tuple[int, float, float]:
    singular_values = np.linalg.svd(x, compute_uv=False)
    largest = float(singular_values[0]) if singular_values.size else 0.0
    tolerance = max(x.shape) * np.finfo(np.float64).eps * largest
    return int(np.sum(singular_values > tolerance)), tolerance, float(singular_values[-1])


def separation_lp(x: np.ndarray, y: np.ndarray) -> dict[str, float | bool]:
    """Detect complete or quasi-complete separation by bounded LPs.

    With signed rows S_i=(2y_i-1)X_i, complete separation exists if a bounded
    coefficient vector yields a positive common margin.  Quasi-complete
    separation exists if all margins are nonnegative and at least one is
    positive.  Bounds merely normalize the otherwise scale-free certificate.
    """

    signed = (2.0 * y - 1.0)[:, None] * x
    p = x.shape[1]
    complete_objective = np.r_[np.zeros(p), -1.0]
    complete_constraints = np.column_stack([-signed, np.ones(len(y))])
    complete = linprog(
        complete_objective,
        A_ub=complete_constraints,
        b_ub=np.zeros(len(y)),
        bounds=[(-1.0, 1.0)] * p + [(0.0, None)],
        method="highs",
    )
    complete_margin = float(complete.x[-1]) if complete.success else float("nan")

    quasi = linprog(
        -signed.sum(axis=0),
        A_ub=-signed,
        b_ub=np.zeros(len(y)),
        bounds=[(-1.0, 1.0)] * p,
        method="highs",
    )
    quasi_margin_sum = float(signed.sum(axis=0) @ quasi.x) if quasi.success else float("nan")
    tolerance = 1e-9
    return {
        "complete_separation": bool(complete.success and complete_margin > tolerance),
        "quasi_complete_separation": bool(
            quasi.success and quasi_margin_sum > tolerance and complete_margin <= tolerance
        ),
        "complete_margin": complete_margin,
        "quasi_margin_sum": quasi_margin_sum,
    }


def initialized_frame(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for target in TARGETS:
        observed = out[target].dropna()
        if target == "age_years":
            fill = float(observed.median())
        else:
            fill = float(observed.mode().sort_values().iloc[0])
        out[target] = out[target].fillna(fill)
    return out


def target_matrix(frame: pd.DataFrame, target: str, score: str) -> tuple[np.ndarray, np.ndarray]:
    observed = frame[target].notna()
    work = initialized_frame(frame)
    predictors = [name for name in TARGETS if name != target]
    race = np.column_stack([(work["race5"] == code).astype(float) for code in [2, 3, 4, 5]])
    strata = pd.get_dummies(work["var_stratum"].astype(str), drop_first=True, dtype=float).to_numpy()
    log_weight = np.log(work["person_finwt0"].to_numpy(float))
    log_weight = (log_weight - log_weight.mean()) / log_weight.std(ddof=0)
    x = np.column_stack(
        [
            np.ones(len(work)),
            race,
            work[score].to_numpy(float),
            *[work[name].to_numpy(float) for name in predictors],
            log_weight,
            strata,
        ]
    )
    return x[observed], frame.loc[observed, target].to_numpy(float)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=project_root / "data_raw/hints5_cycle2_public.dta")
    parser.add_argument("--project-root", type=Path, default=project_root)
    args = parser.parse_args()

    data_path = args.data.resolve()
    if sha256(data_path) != EXPECTED_DATA_SHA256:
        raise RuntimeError("Preflight requires the hash-locked canonical public-use file")
    raw = pd.read_stata(data_path, convert_categoricals=False)
    raw.columns = [name.lower() for name in raw.columns]
    raw = raw.sort_values("hhid", kind="mergesort").reset_index(drop=True)
    df = make_derived(raw)
    reversed_items = [f"{item}_reversed" for item in PCC_ITEMS]
    df["pppcq_min4"] = df[reversed_items].mean(axis=1).where(df["pcc_valid_item_count"] >= 4)

    results: dict[str, object] = {
        "scope": "Structural registry preflight only; no imputation or focal analysis executed.",
        "design_representation": "four race indicators + PPPCQ + other covariates + standardized log weight + reference-coded VAR_STRATUM",
        "rank_tolerance": "max(n,p) * float64_eps * largest_singular_value",
        "superseded_psu_fixed_effect_diagnostic": (
            "Counts all-one English-proficiency PSU cells only; no imputation or effect estimate."
        ),
        "branches": {},
    }
    all_pass = True
    for branch, score in [("require_7_of_7", "pppcq_complete7"), ("require_at_least_4_of_7", "pppcq_min4")]:
        frame = df.loc[df[score].notna() & df["race5"].isin([1, 2, 3, 4, 5])].copy()
        psu_id = frame["var_stratum"].astype(str) + "|" + frame["var_cluster"].astype(str)
        english_by_psu = (
            frame.assign(psu_id=psu_id)
            .dropna(subset=["english_very_well"])
            .groupby("psu_id")["english_very_well"]
            .agg(["nunique", "first"])
        )
        branch_result: dict[str, object] = {
            "frame_n": len(frame),
            "superseded_psu_cell_count": len(english_by_psu),
            "superseded_psu_cells_all_english_very_well": int(
                ((english_by_psu["nunique"] == 1) & (english_by_psu["first"] == 1)).sum()
            ),
            "targets": {},
        }
        for target in TARGETS:
            x, y = target_matrix(frame, target, score)
            rank, tolerance, smallest = numerical_rank(x)
            target_result: dict[str, object] = {
                "observed_target_n": len(y),
                "columns": x.shape[1],
                "rank": rank,
                "rank_tolerance": tolerance,
                "smallest_singular_value": smallest,
                "full_rank": rank == x.shape[1],
            }
            if target in BINARY_TARGETS:
                target_result.update(separation_lp(x, y))
            target_pass = bool(target_result["full_rank"]) and not bool(
                target_result.get("complete_separation", False)
                or target_result.get("quasi_complete_separation", False)
            )
            target_result["pass"] = target_pass
            all_pass = all_pass and target_pass
            branch_result["targets"][target] = target_result
        results["branches"][branch] = branch_result
    results["all_checks_pass"] = all_pass

    output = args.project_root.resolve() / "outputs/registry_preflight.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
