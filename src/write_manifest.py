#!/usr/bin/env python3
"""Generate the preregistered 16-cell manifest without reading outcome data."""

from __future__ import annotations

import argparse
from pathlib import Path

from odmk.registry import build_manifest, load_registry
from odmk.utils import project_root


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=root / "specification_freeze.yaml")
    parser.add_argument("--output", type=Path, default=root / "manifests/specification_manifest.csv")
    args = parser.parse_args()
    manifest = build_manifest(load_registry(args.registry))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(args.output, index=False)
    print(f"Wrote {len(manifest)} registered cells to {args.output}")


if __name__ == "__main__":
    main()

