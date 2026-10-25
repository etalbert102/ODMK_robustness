"""Explicit design-weighted mean and variance estimators."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

from .constants import JK1_COEFFICIENT, JK1_DF, REPLICATE_WEIGHTS
from .exceptions import CellEstimationError


def _weighted_mean(y: np.ndarray, weights: np.ndarray, domain: np.ndarray) -> tuple[float, float]:
    denominator = float(np.sum(weights[domain]))
    if not math.isfinite(denominator) or denominator <= 0:
        raise CellEstimationError("A focal group has zero or invalid weighted denominator")
    estimate = float(np.sum(weights[domain] * y[domain]) / denominator)
    return estimate, denominator


def _inference(estimate: float, variance: float, df: int) -> dict[str, float]:
    if not math.isfinite(variance) or variance < 0:
        raise CellEstimationError(f"Variance is invalid: {variance}")
    se = math.sqrt(variance)
    critical = float(stats.t.ppf(0.975, df))
    statistic = estimate / se if se > 0 else math.nan
    p_value = float(2 * stats.t.sf(abs(statistic), df)) if se > 0 else math.nan
    return {
        "se": se,
        "ci_low": estimate - critical * se,
        "ci_high": estimate + critical * se,
        "statistic": statistic,
        "df": int(df),
        "p_value": p_value,
    }


def estimate_jk1(
    df: pd.DataFrame, y: np.ndarray, asian: np.ndarray, white: np.ndarray
) -> dict[str, float]:
    full_weights = df["person_finwt0"].to_numpy(float)
    asian_mean, asian_denominator = _weighted_mean(y, full_weights, asian)
    white_mean, white_denominator = _weighted_mean(y, full_weights, white)

    asian_replicates: list[float] = []
    white_replicates: list[float] = []
    for column in REPLICATE_WEIGHTS:
        weights = df[column].to_numpy(float)
        asian_replicates.append(_weighted_mean(y, weights, asian)[0])
        white_replicates.append(_weighted_mean(y, weights, white)[0])
    asian_reps = np.asarray(asian_replicates)
    white_reps = np.asarray(white_replicates)
    difference = asian_mean - white_mean
    difference_reps = asian_reps - white_reps

    asian_variance = JK1_COEFFICIENT * float(np.sum((asian_reps - asian_mean) ** 2))
    white_variance = JK1_COEFFICIENT * float(np.sum((white_reps - white_mean) ** 2))
    difference_variance = JK1_COEFFICIENT * float(np.sum((difference_reps - difference) ** 2))
    asian_summary = _inference(asian_mean, asian_variance, JK1_DF)
    white_summary = _inference(white_mean, white_variance, JK1_DF)
    contrast = _inference(difference, difference_variance, JK1_DF)
    return {
        "asian_mean": asian_mean,
        "asian_mean_se": asian_summary["se"],
        "asian_mean_ci_low_95": asian_summary["ci_low"],
        "asian_mean_ci_high_95": asian_summary["ci_high"],
        "white_mean": white_mean,
        "white_mean_se": white_summary["se"],
        "white_mean_ci_low_95": white_summary["ci_low"],
        "white_mean_ci_high_95": white_summary["ci_high"],
        "asian_minus_white_difference": difference,
        "standard_error_of_difference": contrast["se"],
        "ci_low_95": contrast["ci_low"],
        "ci_high_95": contrast["ci_high"],
        "test_statistic": contrast["statistic"],
        "denominator_degrees_of_freedom": contrast["df"],
        "two_sided_p_value": contrast["p_value"],
        "weighted_asian_denominator": asian_denominator,
        "weighted_white_denominator": white_denominator,
    }


def _taylor_variance(df: pd.DataFrame, influence: np.ndarray) -> tuple[float, int]:
    work = pd.DataFrame(
        {
            "stratum": df["var_stratum"].to_numpy(),
            "cluster": df["var_cluster"].to_numpy(),
            "influence": influence,
        }
    )
    psu = work.groupby(["stratum", "cluster"], sort=False, observed=True)["influence"].sum()
    variance = 0.0
    clusters_total = 0
    strata_total = 0
    for _, values in psu.groupby(level=0, sort=False, observed=True):
        totals = values.to_numpy(float)
        count = len(totals)
        if count < 2:
            raise CellEstimationError("Taylor variance requires at least two clusters per stratum")
        variance += count / (count - 1) * float(np.sum((totals - totals.mean()) ** 2))
        clusters_total += count
        strata_total += 1
    return variance, clusters_total - strata_total


def estimate_taylor(
    df: pd.DataFrame, y: np.ndarray, asian: np.ndarray, white: np.ndarray
) -> dict[str, float]:
    weights = df["person_finwt0"].to_numpy(float)
    asian_mean, asian_denominator = _weighted_mean(y, weights, asian)
    white_mean, white_denominator = _weighted_mean(y, weights, white)

    asian_influence = np.zeros(len(df), dtype=float)
    white_influence = np.zeros(len(df), dtype=float)
    asian_influence[asian] = weights[asian] * (y[asian] - asian_mean) / asian_denominator
    white_influence[white] = weights[white] * (y[white] - white_mean) / white_denominator
    asian_variance, design_df = _taylor_variance(df, asian_influence)
    white_variance, white_df = _taylor_variance(df, white_influence)
    difference_variance, difference_df = _taylor_variance(
        df, asian_influence - white_influence
    )
    if len({design_df, white_df, difference_df}) != 1:
        raise CellEstimationError("Taylor degrees of freedom were inconsistent")
    asian_summary = _inference(asian_mean, asian_variance, design_df)
    white_summary = _inference(white_mean, white_variance, design_df)
    contrast = _inference(asian_mean - white_mean, difference_variance, design_df)
    return {
        "asian_mean": asian_mean,
        "asian_mean_se": asian_summary["se"],
        "asian_mean_ci_low_95": asian_summary["ci_low"],
        "asian_mean_ci_high_95": asian_summary["ci_high"],
        "white_mean": white_mean,
        "white_mean_se": white_summary["se"],
        "white_mean_ci_low_95": white_summary["ci_low"],
        "white_mean_ci_high_95": white_summary["ci_high"],
        "asian_minus_white_difference": asian_mean - white_mean,
        "standard_error_of_difference": contrast["se"],
        "ci_low_95": contrast["ci_low"],
        "ci_high_95": contrast["ci_high"],
        "test_statistic": contrast["statistic"],
        "denominator_degrees_of_freedom": contrast["df"],
        "two_sided_p_value": contrast["p_value"],
        "weighted_asian_denominator": asian_denominator,
        "weighted_white_denominator": white_denominator,
    }
