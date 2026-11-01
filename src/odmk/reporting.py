"""Deterministic reviewer-facing tables for an approved multiverse run."""

from __future__ import annotations

import math

import pandas as pd

from .constants import FROZEN_DIMENSION_OPTIONS
from .exceptions import ODMKError


ROW_LABELS = {
    ("content_confirmed_module", "require_7_of_7_valid_items"): (
        "Content-confirmed module; 7 of 7 items"
    ),
    ("content_confirmed_module", "require_at_least_4_of_7_valid_items"): (
        "Content-confirmed module; at least 4 of 7 items"
    ),
    ("observed_positive_filter_only", "require_7_of_7_valid_items"): (
        "Recorded positive filter; 7 of 7 items"
    ),
    ("observed_positive_filter_only", "require_at_least_4_of_7_valid_items"): (
        "Recorded positive filter; at least 4 of 7 items"
    ),
}

COLUMN_LABELS = {
    ("official_mutually_exclusive_raceethn5", "official_jk1_replicate_weights"): (
        "Official Asian; JK1"
    ),
    ("official_mutually_exclusive_raceethn5", "taylor_linearization"): (
        "Official Asian; Taylor"
    ),
    (
        "inclusive_nonhispanic_any_asian_identification",
        "official_jk1_replicate_weights",
    ): "Any Asian identification; JK1",
    (
        "inclusive_nonhispanic_any_asian_identification",
        "taylor_linearization",
    ): "Any Asian identification; Taylor",
}


def _ordered_pairs(first: str, second: str) -> list[tuple[str, str]]:
    """Return the registry-ordered Cartesian product of two dimensions."""

    return [
        (left, right)
        for left in FROZEN_DIMENSION_OPTIONS[first]
        for right in FROZEN_DIMENSION_OPTIONS[second]
    ]


def build_specification_display(results: pd.DataFrame) -> pd.DataFrame:
    """Arrange all 16 registered results as the promised 4 by 4 display.

    Rows cross sample and PPPCQ scoring; columns cross Asian-group construction
    and variance method. Successful cells display the contrast and 95% interval,
    while failed cells display their registered ID and failure reason.

    Raises:
        ODMKError: If a display position has other than one registered result.
    """

    row_pairs = _ordered_pairs("d01_analytic_sample", "d03_outcome_construction")
    column_pairs = _ordered_pairs(
        "d04_main_predictor_construction", "d08_variance_estimation"
    )
    rows: list[list[str]] = []
    for sample, scoring in row_pairs:
        display_row: list[str] = []
        for race, variance in column_pairs:
            selected = results.loc[
                results["d01_analytic_sample"].eq(sample)
                & results["d03_outcome_construction"].eq(scoring)
                & results["d04_main_predictor_construction"].eq(race)
                & results["d08_variance_estimation"].eq(variance)
            ]
            if len(selected) != 1:
                raise ODMKError("Each 4 by 4 display position must contain one result")
            result = selected.iloc[0]
            specification_id = str(result["specification_id"])
            if result["status"] == "success":
                display_row.append(
                    f"{specification_id}: "
                    f"{float(result['asian_minus_white_difference']):.4f} "
                    f"[{float(result['ci_low_95']):.4f}, "
                    f"{float(result['ci_high_95']):.4f}]"
                )
            else:
                display_row.append(
                    f"{specification_id}: failed — {result['failure_category']}: "
                    f"{result['failure_reason']}"
                )
        rows.append(display_row)

    table = pd.DataFrame(
        rows,
        index=[ROW_LABELS[pair] for pair in row_pairs],
        columns=[COLUMN_LABELS[pair] for pair in column_pairs],
    )
    table.index.name = "Eligible sample and PPPCQ scoring"
    return table


def specification_display_markdown(table: pd.DataFrame) -> str:
    """Render the 4 by 4 result table without an optional Markdown dependency."""

    def escape(value: object) -> str:
        """Escape table delimiters and line breaks in one Markdown cell."""

        return str(value).replace("|", "\\|").replace("\n", " ")

    header = [escape(table.index.name or "Specification"), *map(escape, table.columns)]
    lines = [
        "# Registered 4 × 4 specification table",
        "",
        "Each cell reports `specification ID: Asian minus White difference "
        "[95% confidence interval]`. Failed analyses remain visible with their reason.",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for index, row in table.iterrows():
        cells = [escape(index), *[escape(value) for value in row]]
        lines.append(
            "| " + " | ".join(cells) + " |"
        )
    return "\n".join(lines) + "\n"


def _coverage_domains(df: pd.DataFrame) -> dict[str, pd.Series]:
    """Return the four full-frame group domains used in coverage reports."""

    return {
        "all_eligible_respondents": pd.Series(True, index=df.index),
        "official_nonhispanic_asian": df["official_asian"],
        "inclusive_nonhispanic_any_asian": df["inclusive_asian"],
        "nonhispanic_white": df["official_white"],
    }


def _sample_domains(df: pd.DataFrame) -> dict[str, pd.Series]:
    """Return the two full-frame eligibility domains used in reports."""

    return {
        "content_confirmed_module": df["content_confirmed_module"],
        "observed_positive_filter_only": df["recent_provider_visit"],
    }


def build_item_completion_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Report the weighted distribution of zero through seven valid PPPCQ items.

    Returns one row per eligibility rule, reporting group, and valid-item count,
    with unweighted counts, weighted totals, and within-domain percentages.

    Raises:
        ODMKError: If an eligibility/group domain has no positive finite weight.
    """

    weights = df["person_finwt0"]
    rows: list[dict[str, object]] = []
    for sample_name, sample in _sample_domains(df).items():
        for group_name, group in _coverage_domains(df).items():
            domain = sample & group
            denominator = float(weights.loc[domain].sum())
            if not math.isfinite(denominator) or denominator <= 0:
                raise ODMKError(
                    f"Completion coverage has no weight for {sample_name}/{group_name}"
                )
            for valid_count in range(8):
                count_domain = domain & df["pcc_valid_item_count"].eq(valid_count)
                weighted_total = float(weights.loc[count_domain].sum())
                rows.append(
                    {
                        "d01_analytic_sample": sample_name,
                        "group_definition": group_name,
                        "pcc_valid_item_count": valid_count,
                        "unweighted_n": int(count_domain.sum()),
                        "weighted_total": weighted_total,
                        "weighted_percent": 100.0 * weighted_total / denominator,
                    }
                )
    return pd.DataFrame(rows)


def build_scoring_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """Report how much of each eligible group is retained by each scoring rule.

    Returns unweighted and weighted denominators and coverage percentages for
    every eligibility, reporting-group, and PPPCQ completion-rule combination.

    Raises:
        ODMKError: If an eligibility/group domain has no records or no positive
            finite weight.
    """

    weights = df["person_finwt0"]
    score_available = {
        "require_7_of_7_valid_items": df["pppcq_complete7"].notna(),
        "require_at_least_4_of_7_valid_items": df["pppcq_atleast4"].notna(),
    }
    rows: list[dict[str, object]] = []
    for sample_name, sample in _sample_domains(df).items():
        for group_name, group in _coverage_domains(df).items():
            eligible = sample & group
            eligible_n = int(eligible.sum())
            eligible_weight = float(weights.loc[eligible].sum())
            invalid_weight = not math.isfinite(eligible_weight) or eligible_weight <= 0
            if eligible_n <= 0 or invalid_weight:
                raise ODMKError(
                    f"Scoring coverage has no eligible records for {sample_name}/{group_name}"
                )
            for scoring_name, available in score_available.items():
                scored = eligible & available
                scored_n = int(scored.sum())
                scored_weight = float(weights.loc[scored].sum())
                rows.append(
                    {
                        "d01_analytic_sample": sample_name,
                        "group_definition": group_name,
                        "d03_outcome_construction": scoring_name,
                        "eligible_unweighted_n": eligible_n,
                        "scored_unweighted_n": scored_n,
                        "unweighted_coverage_percent": 100.0 * scored_n / eligible_n,
                        "eligible_weighted_denominator": eligible_weight,
                        "scored_weighted_denominator": scored_weight,
                        "weighted_coverage_percent": 100.0 * scored_weight / eligible_weight,
                    }
                )
    return pd.DataFrame(rows)
