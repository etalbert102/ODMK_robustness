"""Invariants for baseline and full registered outputs."""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
from scipy import stats

from .constants import (
    DIMENSION_ORDER,
    FOCAL_TERM,
    JK1_COEFFICIENT,
    JK1_DF,
    REPLICATE_WEIGHTS,
    REGISTRY_REVISION,
    RESULT_COLUMNS,
)
from .exceptions import ODMKError


SUCCESS_NUMERIC_COLUMNS = (
    "asian_mean",
    "asian_mean_se",
    "asian_mean_ci_low_95",
    "asian_mean_ci_high_95",
    "white_mean",
    "white_mean_se",
    "white_mean_ci_low_95",
    "white_mean_ci_high_95",
    "asian_minus_white_difference",
    "standard_error_of_difference",
    "ci_low_95",
    "ci_high_95",
    "test_statistic",
    "denominator_degrees_of_freedom",
    "two_sided_p_value",
    "unweighted_asian_n",
    "unweighted_white_n",
    "weighted_asian_denominator",
    "weighted_white_denominator",
)


def validate_result_schema(results: pd.DataFrame) -> None:
    """Require exact result columns and internally consistent cell estimates.

    The checks cover row identity, success/failure representation, finite values,
    the registered 1–4 scale and contrast direction, recalculated intervals and
    tests, positive group counts, and positive weighted denominators.

    Raises:
        ODMKError: If any result-schema or within-row statistical invariant fails.
    """

    # Row identity and success/failure records.
    if tuple(results.columns) != RESULT_COLUMNS:
        raise ODMKError("Results do not match the frozen output schema")
    if results["specification_id"].duplicated().any():
        raise ODMKError("Specification IDs must be unique")
    if not results["focal_term"].eq(FOCAL_TERM).all():
        raise ODMKError("Every result row must use the frozen focal-term label")
    if not results["status"].isin(("success", "failed")).all():
        raise ODMKError("Every result status must be success or failed")
    successful = results["status"].eq("success")
    success_values = results.loc[successful, list(SUCCESS_NUMERIC_COLUMNS)]
    if not np.isfinite(success_values.to_numpy(float)).all():
        raise ODMKError("Successful cells must have finite required estimates")
    if results.loc[successful, ["failure_category", "failure_reason"]].ne("").any().any():
        raise ODMKError("Successful cells cannot include failure diagnostics")
    failed = ~successful
    if results.loc[failed, ["failure_category", "failure_reason"]].eq("").any().any():
        raise ODMKError("Failed cells must include a category and reason")
    if results.loc[failed, list(SUCCESS_NUMERIC_COLUMNS)].notna().any().any():
        raise ODMKError("Failed cells cannot retain focal estimates")

    # Point estimates must remain on the registered scale and use the frozen
    # Asian-minus-White direction.
    if not results.loc[successful, "asian_mean"].between(1, 4).all():
        raise ODMKError("Successful Asian means must remain on the registered 1-4 scale")
    if not results.loc[successful, "white_mean"].between(1, 4).all():
        raise ODMKError("Successful White means must remain on the registered 1-4 scale")
    observed_difference = results.loc[successful, "asian_minus_white_difference"]
    calculated_difference = (
        results.loc[successful, "asian_mean"] - results.loc[successful, "white_mean"]
    )
    if not np.allclose(observed_difference, calculated_difference, rtol=0, atol=1e-12):
        raise ODMKError("A focal difference does not equal Asian mean minus White mean")
    for column in ("asian_mean_se", "white_mean_se"):
        if not results.loc[successful, column].ge(0).all():
            raise ODMKError(f"{column} cannot be negative")
    if not results.loc[successful, "standard_error_of_difference"].gt(0).all():
        raise ODMKError("standard_error_of_difference must be positive")
    if not results.loc[successful, "denominator_degrees_of_freedom"].gt(0).all():
        raise ODMKError("Denominator degrees of freedom must be positive")

    # Recalculate every interval, test statistic, and p-value from the reported
    # estimate, standard error, and degrees of freedom.
    successful_rows = results.loc[successful]
    critical = stats.t.ppf(
        0.975, successful_rows["denominator_degrees_of_freedom"].to_numpy(float)
    )
    for estimate, standard_error, low, high in (
        (
            "asian_mean",
            "asian_mean_se",
            "asian_mean_ci_low_95",
            "asian_mean_ci_high_95",
        ),
        (
            "white_mean",
            "white_mean_se",
            "white_mean_ci_low_95",
            "white_mean_ci_high_95",
        ),
        (
            "asian_minus_white_difference",
            "standard_error_of_difference",
            "ci_low_95",
            "ci_high_95",
        ),
    ):
        expected_low = successful_rows[estimate].to_numpy(float) - (
            critical * successful_rows[standard_error].to_numpy(float)
        )
        expected_high = successful_rows[estimate].to_numpy(float) + (
            critical * successful_rows[standard_error].to_numpy(float)
        )
        if not np.allclose(successful_rows[low], expected_low, rtol=1e-12, atol=1e-12):
            raise ODMKError(
                f"{low} is inconsistent with its estimate, SE, and degrees of freedom"
            )
        if not np.allclose(successful_rows[high], expected_high, rtol=1e-12, atol=1e-12):
            raise ODMKError(
                f"{high} is inconsistent with its estimate, SE, and degrees of freedom"
            )

    expected_statistic = (
        successful_rows["asian_minus_white_difference"].to_numpy(float)
        / successful_rows["standard_error_of_difference"].to_numpy(float)
    )
    if not np.allclose(
        successful_rows["test_statistic"], expected_statistic, rtol=1e-12, atol=1e-12
    ):
        raise ODMKError("test_statistic is inconsistent with the focal estimate and SE")
    expected_p = 2 * stats.t.sf(
        np.abs(expected_statistic),
        successful_rows["denominator_degrees_of_freedom"].to_numpy(float),
    )
    if not np.allclose(
        successful_rows["two_sided_p_value"], expected_p, rtol=1e-12, atol=1e-12
    ):
        raise ODMKError(
            "two_sided_p_value is inconsistent with the test statistic and degrees of freedom"
        )

    # Counts and weighted denominators must describe nonempty focal groups.
    for column in ("unweighted_asian_n", "unweighted_white_n"):
        values = results.loc[successful, column]
        if not (values.gt(0) & values.eq(np.floor(values))).all():
            raise ODMKError(f"{column} must contain positive integers")
    for column in ("weighted_asian_denominator", "weighted_white_denominator"):
        if not results.loc[successful, column].gt(0).all():
            raise ODMKError(f"{column} must be positive")


def validate_full_results(
    results: pd.DataFrame,
    manifest: pd.DataFrame,
    *,
    expected_source_hash: str | None = None,
    expected_taylor_df: int | None = None,
) -> dict[str, object]:
    """Match all 16 rows to the manifest and check variance-method pairs.

    Args:
        results: Complete registered result table, including retained failures.
        manifest: Frozen 16-row identity and option table.
        expected_source_hash: Required source fingerprint when known.
        expected_taylor_df: Required Taylor denominator degrees of freedom when
            the released design has been validated.

    Returns:
        Counts of registered, successful, and failed cells plus the number and
        status of JK1/Taylor point-estimate invariance comparisons.

    Raises:
        ODMKError: If schema, manifest identity, provenance, option labels,
            degrees of freedom, pair structure, or point-estimate invariance fails.
    """

    validate_result_schema(results)
    if len(results) != 16 or set(results["specification_id"]) != set(
        manifest["specification_id"]
    ):
        raise ODMKError("Full output must contain every one of the 16 registered cells")

    # Each result must retain the exact ID and four choices assigned before the
    # analysis ran.
    identity_columns = [
        "specification_id",
        "point_estimate_id",
        "is_baseline",
        *DIMENSION_ORDER,
    ]
    observed_identity = (
        results[identity_columns].sort_values("specification_id").reset_index(drop=True)
    )
    expected_identity = (
        manifest[identity_columns].sort_values("specification_id").reset_index(drop=True)
    )
    if not observed_identity.equals(expected_identity):
        raise ODMKError("A result row does not match its frozen manifest identity and options")
    if not results["paper_id"].eq("ODMK").all():
        raise ODMKError("Every result row must identify paper ODMK")
    if not results["registry_revision"].eq(REGISTRY_REVISION).all():
        raise ODMKError(f"Every result row must identify registry revision {REGISTRY_REVISION}")

    # Preserve the source-data identity and a machine-readable copy of every
    # option label in each row.
    if expected_source_hash is not None and not results["source_data_sha256"].eq(
        expected_source_hash
    ).all():
        raise ODMKError("A result row has the wrong source-data hash")
    if results["source_data_sha256"].isna().any() or results["source_data_sha256"].eq("").any():
        raise ODMKError("Every result row must include a source-data hash")
    for _, row in results.iterrows():
        expected_options = {name: row[name] for name in DIMENSION_ORDER}
        try:
            recorded_options = json.loads(row["all_option_labels"])
        except (TypeError, json.JSONDecodeError) as error:
            raise ODMKError("all_option_labels must contain valid JSON") from error
        if recorded_options != expected_options:
            raise ODMKError("all_option_labels does not match the registered option columns")

    # Enforce the degrees of freedom registered for each standard-error method.
    successful = results["status"].eq("success")
    jk1 = successful & results["d08_variance_estimation"].eq(
        "official_jk1_replicate_weights"
    )
    if not results.loc[jk1, "denominator_degrees_of_freedom"].eq(JK1_DF).all():
        raise ODMKError(f"Successful JK1 cells must use {JK1_DF} degrees of freedom")
    if expected_taylor_df is not None:
        taylor = successful & results["d08_variance_estimation"].eq("taylor_linearization")
        if not results.loc[taylor, "denominator_degrees_of_freedom"].eq(
            expected_taylor_df
        ).all():
            raise ODMKError(
                f"Successful Taylor cells must use {expected_taylor_df} degrees of freedom"
            )
    # The two standard-error methods must give the same means and difference
    # for each of the eight sample/score/group constructions.
    successes = results.loc[successful]
    checked_pairs = 0
    for _, registered_pair in results.groupby("point_estimate_id"):
        if len(registered_pair) != 2:
            raise ODMKError("Every point-estimate construction must have two registered d08 cells")
        successful_pair = registered_pair.loc[registered_pair["status"].eq("success")]
        if len(successful_pair) != 2:
            continue
        for column in ("asian_mean", "white_mean", "asian_minus_white_difference"):
            if not np.allclose(
                successful_pair[column], successful_pair[column].iloc[0], rtol=0, atol=1e-12
            ):
                raise ODMKError("Paired d08 cells do not have identical point estimates")
        checked_pairs += 1
    if checked_pairs == 8:
        invariance: bool | None = True
        invariance_status = "verified"
    elif checked_pairs > 0:
        invariance = None
        invariance_status = "partially_verified"
    else:
        invariance = None
        invariance_status = "not_assessed"
    return {
        "registered_cells": 16,
        "successful_cells": int(len(successes)),
        "failed_cells": int((results["status"] == "failed").sum()),
        "point_estimate_invariance": invariance,
        "point_estimate_invariance_status": invariance_status,
        "point_estimate_pairs_checked": checked_pairs,
    }


def validate_published_table2_anchors(df: pd.DataFrame) -> dict[str, object]:
    """Check the reconstructed Table 2 means, JK1 SEs, and intervals.

    The baseline domain requires content-confirmed eligibility, all seven PPPCQ
    items, and a valid official five-category race value. Each reconstructed
    displayed statistic must be within 0.011 of the published two-decimal value.

    Returns:
        The analytic count, all five groups' unrounded reconstructed statistics,
        the display tolerance, and a passing status.

    Raises:
        ODMKError: If the analytic count, a weighted denominator, or any
            published-value comparison fails.
    """

    expected = {
        1: {"mean": 3.45, "se": 0.02, "ci_low": 3.39, "ci_high": 3.49},
        2: {"mean": 3.49, "se": 0.05, "ci_low": 3.38, "ci_high": 3.59},
        3: {"mean": 3.27, "se": 0.04, "ci_low": 3.17, "ci_high": 3.37},
        4: {"mean": 3.11, "se": 0.10, "ci_low": 2.90, "ci_high": 3.33},
        5: {"mean": 3.33, "se": 0.20, "ci_low": 2.91, "ci_high": 3.75},
    }
    analytic = (
        df["content_confirmed_module"]
        & df["pppcq_complete7"].notna()
        & df["raceethn5"].isin(expected)
    )
    analytic_n = int(analytic.sum())
    if analytic_n != 2611:
        raise ODMKError(f"Published Table 2 analytic N changed: {analytic_n} != 2611")

    display_tolerance = 0.011
    critical = float(stats.t.ppf(0.975, JK1_DF))
    outcome = df["pppcq_complete7"].to_numpy(float)
    observed_groups: dict[str, dict[str, float]] = {}
    for code, published in expected.items():
        domain = (analytic & df["raceethn5"].eq(code)).to_numpy(bool)
        full_weights = df["person_finwt0"].to_numpy(float)
        denominator = float(full_weights[domain].sum())
        if not math.isfinite(denominator) or denominator <= 0:
            raise ODMKError(f"Published Table 2 race code {code} has no weighted denominator")
        mean = float((full_weights[domain] * outcome[domain]).sum() / denominator)
        replicate_means = []
        for column in REPLICATE_WEIGHTS:
            replicate_weights = df[column].to_numpy(float)
            replicate_denominator = float(replicate_weights[domain].sum())
            if not math.isfinite(replicate_denominator) or replicate_denominator <= 0:
                raise ODMKError(
                    f"Published Table 2 race code {code} has an invalid replicate denominator"
                )
            replicate_means.append(
                float(
                    (replicate_weights[domain] * outcome[domain]).sum()
                    / replicate_denominator
                )
            )
        variance = JK1_COEFFICIENT * float(
            np.sum((np.asarray(replicate_means) - mean) ** 2)
        )
        standard_error = math.sqrt(variance)
        observed = {
            "unweighted_n": int(domain.sum()),
            "mean": mean,
            "se": standard_error,
            "ci_low": mean - critical * standard_error,
            "ci_high": mean + critical * standard_error,
        }
        for statistic, published_value in published.items():
            if abs(observed[statistic] - published_value) > display_tolerance:
                raise ODMKError(
                    f"Published Table 2 {statistic} failed for race code {code}: "
                    f"{observed[statistic]:.6f} vs {published_value:.2f}"
                )
        observed_groups[str(code)] = observed
    return {
        "all_checks_pass": True,
        "analytic_n_all_five_groups": analytic_n,
        "jk1_by_raceethn5": observed_groups,
        "display_tolerance": display_tolerance,
    }


def validate_real_baseline(results: pd.DataFrame) -> dict[str, object]:
    """Require the single registered cell to match frozen baseline anchors.

    Returns the exact focal means, contrast, contrast standard error, group
    counts, and degrees of freedom that were frozen after reconstruction.

    Raises:
        ODMKError: If the result schema, one-cell success requirement, or any
            numeric baseline anchor fails.
    """

    validate_result_schema(results)
    if len(results) != 1 or results.iloc[0]["status"] != "success":
        raise ODMKError("Registered baseline must produce one successful cell")
    row = results.iloc[0]
    anchors = {
        "asian_mean": 3.116125895255402,
        "white_mean": 3.4457431125742386,
        "asian_minus_white_difference": -0.32961721731883653,
        "standard_error_of_difference": 0.10974269373470233,
        "unweighted_asian_n": 105,
        "unweighted_white_n": 1703,
        "denominator_degrees_of_freedom": 49,
    }
    for name, expected in anchors.items():
        observed = float(row[name])
        tolerance = 0 if isinstance(expected, int) else 1e-10
        if not math.isclose(observed, expected, rel_tol=0, abs_tol=tolerance):
            raise ODMKError(f"Baseline anchor {name} changed: {observed} != {expected}")
    return {"all_checks_pass": True, "anchors": anchors}
