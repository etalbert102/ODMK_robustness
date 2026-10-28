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
from odmk.utils import project_root, sha256_file, staged_output_directory, write_json
from odmk.validation import (
    validate_full_results,
    validate_published_table2_anchors,
    validate_real_baseline,
)


def main() -> None:
    root = project_root()
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
    args = parser.parse_args()

    # The approval and clean-worktree checks deliberately occur before source
    # data are opened or any registered effect can be calculated.
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

    manifest = build_manifest(registry)
    raw, data_hash = read_canonical_hints(args.data)
    derived = derive_analysis_fields(raw)
    structure = validate_canonical_structure(derived, registry)

    # These are execution gates, not post-hoc diagnostics. Confirm the complete
    # published Table 2 reconstruction before calculating any alternative cell.
    baseline_results = run_manifest(
        derived, manifest, scope="baseline", source_hash=data_hash
    )
    focal_baseline = validate_real_baseline(baseline_results)
    published_table2 = validate_published_table2_anchors(derived)

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
    metadata = build_metadata(
        root=root,
        registry=registry,
        registry_hash=registry_hash,
        data_hash=data_hash,
        config=config,
        scope="approved",
    )

    with staged_output_directory(args.output_dir, allowed_root=root / "outputs") as staging:
        results.to_csv(staging / "results.csv", index=False)
        manifest.to_csv(staging / "cell_manifest.csv", index=False)
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
    print(f"Completed {len(results)} registered cells in {args.output_dir}")


if __name__ == "__main__":
    try:
        main()
    except ODMKError as error:
        raise SystemExit(f"BLOCKED: {error}") from None
