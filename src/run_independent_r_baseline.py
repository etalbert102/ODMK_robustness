#!/usr/bin/env python3
"""Run and validate the independent baseline-only R reconstruction."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import pandas as pd

from odmk.constants import EXPECTED_DATA_SHA256
from odmk.cross_language import compare_independent_r_baseline
from odmk.exceptions import ODMKError
from odmk.utils import project_root, sha256_file, staged_output_directory, write_json


def parse_args(root: Path) -> argparse.Namespace:
    """Parse paths for the baseline-only R verification workflow."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=root / "data_raw/hints5_cycle2_public.dta")
    parser.add_argument(
        "--python-results",
        type=Path,
        default=root / "outputs/registered_baseline/results.csv",
    )
    parser.add_argument(
        "--python-validation",
        type=Path,
        default=root / "outputs/registered_baseline/validation.json",
    )
    parser.add_argument(
        "--r-script",
        type=Path,
        default=root / "verification/independent_r_baseline.R",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "outputs/independent_r_baseline",
    )
    parser.add_argument("--rscript", default="Rscript", help="Rscript executable name or path")
    return parser.parse_args()


def main() -> None:
    """Run R on canonical data and atomically publish cross-language checks."""

    root = project_root()
    args = parse_args(root)
    rscript = shutil.which(args.rscript)
    if rscript is None:
        raise ODMKError(f"Rscript executable not found: {args.rscript}")
    if sha256_file(args.data) != EXPECTED_DATA_SHA256:
        raise ODMKError("Independent R check requires the canonical HINTS source file")
    if not args.r_script.is_file():
        raise ODMKError(f"Independent R script is missing: {args.r_script}")
    if not args.python_results.is_file() or not args.python_validation.is_file():
        raise ODMKError("Run the registered Python baseline before the R comparison")

    python_results = pd.read_csv(args.python_results)
    python_validation = json.loads(args.python_validation.read_text(encoding="utf-8"))
    with staged_output_directory(args.output_dir, allowed_root=root / "outputs") as staging:
        subprocess.run(
            [rscript, str(args.r_script), str(args.data), str(staging)],
            cwd=root,
            check=True,
        )
        r_results_path = staging / "results.csv"
        r_metadata_path = staging / "metadata.csv"
        if not r_results_path.is_file() or not r_metadata_path.is_file():
            raise ODMKError("Independent R script did not create both required files")
        r_results = pd.read_csv(r_results_path)
        r_metadata = pd.read_csv(r_metadata_path, dtype=str, keep_default_na=False)
        audit = compare_independent_r_baseline(
            r_results,
            r_metadata,
            python_validation,
            python_results,
        )
        audit.to_csv(staging / "comparison.csv", index=False)
        write_json(
            staging / "validation.json",
            {
                "all_checks_pass": True,
                "comparisons": len(audit),
                "maximum_absolute_difference": float(audit["absolute_difference"].max()),
                "tolerance": float(audit["tolerance"].max()),
                "guardrail": "Published baseline only; no robustness alternative is implemented.",
            },
        )
    print(f"Independent R comparison passed with {len(audit)} checks.")


if __name__ == "__main__":
    main()
