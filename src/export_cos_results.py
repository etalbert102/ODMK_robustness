#!/usr/bin/env python3
"""Export approved ODMK results using the COS results-file schema."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from odmk.cos_reporting import build_cos_results, write_cos_results
from odmk.exceptions import ODMKError
from odmk.utils import project_root


def parse_args(root: Path) -> argparse.Namespace:
    """Parse native-input, output, and analyst arguments."""

    parser = argparse.ArgumentParser(
        description="Convert validated 16-row ODMK results to the COS CSV format."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=root / "outputs/multiverse/results.csv",
        help="Native validated ODMK result table.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "submission/results_ODMK.csv",
        help="COS-formatted UTF-8 CSV destination.",
    )
    parser.add_argument("--analyst", default="Eli Talbert")
    return parser.parse_args()


def main() -> None:
    """Read native results, validate the mapping, and write the COS file."""

    root = project_root()
    args = parse_args(root)
    if not args.input.is_file():
        raise ODMKError(f"Native multiverse results do not exist: {args.input}")
    native = pd.read_csv(args.input)
    exported = build_cos_results(native, analyst=args.analyst)
    write_cos_results(exported, args.output)
    print(f"Wrote {len(exported)} COS result rows to {args.output}")


if __name__ == "__main__":
    try:
        main()
    except ODMKError as error:
        raise SystemExit(f"BLOCKED: {error}") from None
