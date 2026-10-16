#!/usr/bin/env python3
"""Structural preflight for the frozen ODMK Table 2 multiverse.

This program verifies registry structure, sample membership, race construction,
and released survey-design fields. It never calculates a group outcome mean,
racial contrast, standard error, confidence interval, or p-value.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml

from baseline_analysis import EXPECTED_DATA_SHA256, PCC_ITEMS, make_derived, sha256


ASIAN_CHECKBOXES = [
    "asind",
    "chinese",
    "filipino",
    "japanese",
    "korean",
    "vietnamese",
    "othasian",
]


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=project_root / "data_raw/hints5_cycle2_public.dta")
    parser.add_argument("--registry", type=Path, default=project_root / "specification_freeze.yaml")
    parser.add_argument("--project-root", type=Path, default=project_root)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    data_path = args.data.resolve()
    registry_path = args.registry.resolve()

    if sha256(data_path) != EXPECTED_DATA_SHA256:
        raise RuntimeError("Preflight requires the hash-locked canonical public-use file")

    registry = yaml.safe_load(registry_path.read_text())
    if registry.get("paper_id") != "ODMK" or registry.get("revision") != 7:
        raise AssertionError("Preflight requires ODMK specification_freeze.yaml revision 7")
    if registry["cell_construction"]["expected_specifications"] != 16:
        raise AssertionError("Revision 7 must register exactly 16 fully crossed specifications")
    if registry["cell_construction"]["distinct_point_estimate_constructions"] != 8:
        raise AssertionError("Revision 7 must register exactly eight point-estimate constructions")
    if len(registry["dimensions"]) != 4:
        raise AssertionError("Revision 7 must contain exactly four varied dimensions")

    raw = pd.read_stata(data_path, convert_categoricals=False)
    raw.columns = [name.lower() for name in raw.columns]
    required = {
        "hhid",
        "hisp_cat",
        "raceethn5",
        "freqgoprovider",
        "person_finwt0",
        "var_stratum",
        "var_cluster",
        *PCC_ITEMS,
        *ASIAN_CHECKBOXES,
    }
    missing = sorted(required.difference(raw.columns))
    if missing:
        raise KeyError(f"Required source columns absent: {missing}")
    raw = raw.sort_values("hhid", kind="mergesort").reset_index(drop=True)
    df = make_derived(raw)

    df["official_asian"] = df["raceethn5"].eq(4)
    df["inclusive_asian"] = df["hisp_cat"].eq(10) & df[ASIAN_CHECKBOXES].eq(1).any(axis=1)
    df["official_white"] = df["raceethn5"].eq(1)

    routes = {
        "content_confirmed_module": df["c4_module_eligible"],
        "observed_positive_filter_only": df["recent_provider_visit"],
    }
    outcome_rules = {
        "require_7_of_7_valid_items": df["pcc_valid_item_count"].eq(7),
        "require_at_least_4_of_7_valid_items": df["pcc_valid_item_count"].ge(4),
    }
    race_rules = {
        "official_mutually_exclusive_raceethn5": df["official_asian"],
        "inclusive_nonhispanic_any_asian_identification": df["inclusive_asian"],
    }

    membership_cells: list[dict[str, int | str]] = []
    for route_name, route in routes.items():
        for outcome_name, outcome in outcome_rules.items():
            for race_name, asian in race_rules.items():
                eligible = route & outcome
                membership_cells.append(
                    {
                        "d01": route_name,
                        "d03": outcome_name,
                        "d04": race_name,
                        "eligible_n_all_races": int(eligible.sum()),
                        "asian_n": int((eligible & asian).sum()),
                        "white_n": int((eligible & df["official_white"]).sum()),
                    }
                )

    if len(membership_cells) != 8:
        raise AssertionError("d01 x d03 x d04 must generate eight membership cells")

    design_pairs = df[["var_stratum", "var_cluster"]].drop_duplicates()
    clusters_per_stratum = {
        str(key): int(value)
        for key, value in design_pairs.groupby("var_stratum")["var_cluster"].nunique().items()
    }
    official_subset_inclusive = bool((~df["official_asian"] | df["inclusive_asian"]).all())
    focal_groups_disjoint = bool((~df["inclusive_asian"] | ~df["official_white"]).all())
    additional_multiracial = int((df["inclusive_asian"] & ~df["official_asian"]).sum())

    structural = {
        "source_rows": len(df),
        "content_confirmed_module_n": int(routes["content_confirmed_module"].sum()),
        "observed_positive_filter_n": int(routes["observed_positive_filter_only"].sum()),
        "complete_7_n_content_confirmed": int(
            (routes["content_confirmed_module"] & outcome_rules["require_7_of_7_valid_items"]).sum()
        ),
        "complete_7_official_asian_n_content_confirmed": int(
            (
                routes["content_confirmed_module"]
                & outcome_rules["require_7_of_7_valid_items"]
                & df["official_asian"]
            ).sum()
        ),
        "complete_7_inclusive_asian_n_content_confirmed": int(
            (
                routes["content_confirmed_module"]
                & outcome_rules["require_7_of_7_valid_items"]
                & df["inclusive_asian"]
            ).sum()
        ),
        "complete_7_white_n_content_confirmed": int(
            (
                routes["content_confirmed_module"]
                & outcome_rules["require_7_of_7_valid_items"]
                & df["official_white"]
            ).sum()
        ),
        "inclusive_asian_additional_multiracial_n_full_source": additional_multiracial,
    }
    expected_structural = registry["structural_anchors"].copy()
    expected_structural.pop("note", None)
    if structural != expected_structural:
        raise AssertionError(
            f"Structural anchors changed: observed={structural}, registered={expected_structural}"
        )
    if not official_subset_inclusive:
        raise AssertionError("Official Asian records must be a subset of the inclusive Asian rule")
    if not focal_groups_disjoint:
        raise AssertionError("The registered Asian and White groups must be disjoint")
    if clusters_per_stratum != {"5_2_HM": 50, "5_2_LM": 50}:
        raise AssertionError(f"Unexpected Taylor design structure: {clusters_per_stratum}")
    if df["person_finwt0"].isna().any() or not df["person_finwt0"].gt(0).all():
        raise AssertionError("PERSON_FINWT0 must be nonmissing and positive")

    results = {
        "scope": (
            "Structural registry preflight only. No nonbaseline outcome mean, racial contrast, "
            "standard error, confidence interval, or p-value was calculated."
        ),
        "paper_id": registry["paper_id"],
        "registry_revision": registry["revision"],
        "registered_dimensions": list(registry["dimensions"]),
        "registered_specifications": registry["cell_construction"]["expected_specifications"],
        "distinct_point_estimate_constructions": registry["cell_construction"][
            "distinct_point_estimate_constructions"
        ],
        "structural_anchors": structural,
        "race_checks": {
            "official_asian_subset_of_inclusive_asian": official_subset_inclusive,
            "inclusive_asian_disjoint_from_official_white": focal_groups_disjoint,
            "official_asian_n_full_source": int(df["official_asian"].sum()),
            "inclusive_asian_n_full_source": int(df["inclusive_asian"].sum()),
            "additional_multiracial_asian_n_full_source": additional_multiracial,
        },
        "taylor_design_checks": {
            "strata_n": int(df["var_stratum"].nunique()),
            "clusters_per_stratum": clusters_per_stratum,
            "design_degrees_of_freedom": int(len(design_pairs) - df["var_stratum"].nunique()),
        },
        "membership_cells_excluding_d08_duplicate": membership_cells,
        "all_checks_pass": True,
    }

    output = project_root / "outputs/registry_preflight.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
