#!/usr/bin/env python3
"""Run only the single registered baseline cell on canonical HINTS data."""

from __future__ import annotations

import argparse
from pathlib import Path

from odmk.approval import load_execution_config
from odmk.data import derive_analysis_fields, read_canonical_hints, validate_canonical_structure
from odmk.engine import run_manifest
from odmk.provenance import build_metadata
from odmk.registry import build_manifest, load_registry
from odmk.utils import project_root, sha256_file, staged_output_directory, write_json
from odmk.validation import validate_published_table2_anchors, validate_real_baseline


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser(
        description="Run only the frozen baseline through the registered production engine."
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
        help="Operational approval and provenance metadata recorded with the baseline.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "outputs/registered_baseline",
        help="Application-owned destination beneath the repository outputs directory.",
    )
    args = parser.parse_args()

    registry_hash = sha256_file(args.registry)
    registry = load_registry(args.registry)
    manifest = build_manifest(registry)
    raw, data_hash = read_canonical_hints(args.data)
    derived = derive_analysis_fields(raw)
    structure = validate_canonical_structure(derived, registry)
    results = run_manifest(derived, manifest, scope="baseline", source_hash=data_hash)
    validation = validate_real_baseline(results)
    published_table2 = validate_published_table2_anchors(derived)
    config = load_execution_config(args.config)
    metadata = build_metadata(
        root=root,
        registry=registry,
        registry_hash=registry_hash,
        data_hash=data_hash,
        config=config,
        scope="baseline",
    )

    with staged_output_directory(args.output_dir, allowed_root=root / "outputs") as staging:
        results.to_csv(staging / "results.csv", index=False)
        write_json(
            staging / "validation.json",
            {
                **structure,
                "focal_result": validation,
                "full_table2": published_table2,
            },
        )
        write_json(staging / "run_metadata.json", metadata)
    print(results.to_string(index=False))
    print("Registered baseline validation passed.")


if __name__ == "__main__":
    main()
