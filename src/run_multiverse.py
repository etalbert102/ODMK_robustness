#!/usr/bin/env python3
"""Run all 16 cells only after recorded COS and researcher approval."""

from __future__ import annotations

import argparse
from pathlib import Path

from odmk.approval import assert_production_approved, load_execution_config
from odmk.data import derive_analysis_fields, read_canonical_hints, validate_canonical_structure
from odmk.engine import run_manifest
from odmk.environment import assert_frozen_environment
from odmk.exceptions import ODMKError
from odmk.provenance import build_metadata
from odmk.registry import build_manifest, load_registry
from odmk.reporting import (
    build_item_completion_distribution,
    build_scoring_coverage,
    build_specification_display,
    specification_display_markdown,
)
from odmk.utils import project_root, sha256_file, staged_output_directory, write_json
from odmk.validation import (
    validate_full_results,
    validate_published_table2_anchors,
    validate_real_baseline,
)


def parse_args(root: Path) -> argparse.Namespace:
    """Parse production paths and the explicit approval confirmation flag."""

    parser = argparse.ArgumentParser(
        description="Run all 16 registered ODMK cells after every approval gate passes."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=root / "data_raw/hints5_cycle2_public.dta",
        help="Hash-locked HINTS 5 Cycle 2 Stata file.",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=root / "specification_freeze.yaml",
        help="Frozen YAML scientific registry.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=root / "config/execution.yaml",
        help="Operational approval and provenance metadata.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "outputs/multiverse",
        help="Application-owned destination beneath the repository outputs directory.",
    )
    parser.add_argument(
        "--confirm-approved",
        action="store_true",
        help="Explicitly confirm that recorded COS and researcher approvals are current.",
    )
    return parser.parse_args()


def execute_registered_multiverse(args: argparse.Namespace, *, root: Path) -> int:
    """Execute the gated workflow and atomically publish its result artifacts."""

    # 1. Freeze the instructions and verify approval before opening source data
    # or calculating any registered effect.
    registry_hash = sha256_file(args.registry)
    registry = load_registry(args.registry)
    config = load_execution_config(args.config)
    assert_frozen_environment()
    authorization = assert_production_approved(
        config,
        root=root,
        confirmed=args.confirm_approved,
        registry_sha256=registry_hash,
    )

    # 2. Read the exact public file and construct every registered field once.
    manifest = build_manifest(registry)
    raw, data_hash = read_canonical_hints(args.data)
    derived = derive_analysis_fields(raw)
    structure = validate_canonical_structure(derived, registry)

    # 3. Reproduce the published result before calculating any alternative.
    # These are execution gates, not post-hoc diagnostics.
    baseline_results = run_manifest(
        derived, manifest, scope="baseline", source_hash=data_hash
    )
    focal_baseline = validate_real_baseline(baseline_results)
    published_table2 = validate_published_table2_anchors(derived)

    # 4. Run all frozen combinations and verify them against the manifest.
    results = run_manifest(
        derived,
        manifest,
        scope="approved",
        source_hash=data_hash,
        production_authorized=bool(authorization),
    )
    validation = validate_full_results(
        results,
        manifest,
        expected_source_hash=data_hash,
        expected_taylor_df=int(structure["design_df"]),
    )
    specification_display = build_specification_display(results)
    item_completion = build_item_completion_distribution(derived)
    scoring_coverage = build_scoring_coverage(derived)
    metadata = build_metadata(
        root=root,
        registry=registry,
        registry_hash=registry_hash,
        data_hash=data_hash,
        config=config,
        scope="approved",
    )

    # 5. Write all result and provenance files together as one complete set.
    with staged_output_directory(args.output_dir, allowed_root=root / "outputs") as staging:
        results.to_csv(staging / "results.csv", index=False)
        manifest.to_csv(staging / "cell_manifest.csv", index=False)
        (staging / "specification_table.md").write_text(
            specification_display_markdown(specification_display), encoding="utf-8"
        )
        item_completion.to_csv(staging / "item_completion_distribution.csv", index=False)
        scoring_coverage.to_csv(staging / "scoring_coverage.csv", index=False)
        write_json(
            staging / "validation.json",
            {
                **structure,
                "published_baseline_gate": {
                    "focal_result": focal_baseline,
                    "full_table2": published_table2,
                },
                **validation,
            },
        )
        write_json(staging / "run_metadata.json", metadata)
    return len(results)


def main() -> None:
    root = project_root()
    args = parse_args(root)
    completed = execute_registered_multiverse(args, root=root)
    print(f"Completed {completed} registered cells in {args.output_dir}")


if __name__ == "__main__":
    try:
        main()
    except ODMKError as error:
        raise SystemExit(f"BLOCKED: {error}") from None
