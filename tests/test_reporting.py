import math

from odmk.engine import run_manifest
from odmk.registry import build_manifest, load_registry
from odmk.reporting import (
    build_item_completion_distribution,
    build_scoring_coverage,
    build_specification_display,
    specification_display_markdown,
)
from odmk.utils import project_root


def _synthetic_results(synthetic_derived):
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    return run_manifest(
        synthetic_derived,
        manifest,
        scope="synthetic",
        source_hash="synthetic-reporting-fixture",
    )


def test_specification_display_contains_each_registered_cell_once(
    synthetic_derived,
) -> None:
    results = _synthetic_results(synthetic_derived)

    table = build_specification_display(results)
    markdown = specification_display_markdown(table)

    assert table.shape == (4, 4)
    for specification_id in results["specification_id"]:
        assert markdown.count(specification_id) == 1
    assert "Asian minus White difference" in markdown


def test_item_completion_distribution_covers_each_sample_and_group(
    synthetic_derived,
) -> None:
    distribution = build_item_completion_distribution(synthetic_derived)

    assert len(distribution) == 64
    assert set(distribution["pcc_valid_item_count"]) == set(range(8))
    grouped_percent = distribution.groupby(
        ["d01_analytic_sample", "group_definition"]
    )["weighted_percent"].sum()
    assert all(math.isclose(value, 100.0, abs_tol=1e-10) for value in grouped_percent)


def test_four_item_scoring_rule_never_has_less_coverage_than_complete_case(
    synthetic_derived,
) -> None:
    coverage = build_scoring_coverage(synthetic_derived)

    assert len(coverage) == 16
    for _, pair in coverage.groupby(["d01_analytic_sample", "group_definition"]):
        by_rule = pair.set_index("d03_outcome_construction")
        complete = by_rule.loc["require_7_of_7_valid_items"]
        partial = by_rule.loc["require_at_least_4_of_7_valid_items"]
        assert partial["scored_unweighted_n"] >= complete["scored_unweighted_n"]
        assert partial["scored_weighted_denominator"] >= complete[
            "scored_weighted_denominator"
        ]
        assert 0 <= complete["weighted_coverage_percent"] <= 100
        assert 0 <= partial["weighted_coverage_percent"] <= 100
