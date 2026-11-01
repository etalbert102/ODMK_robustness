"""Run-level provenance records."""

from __future__ import annotations

import importlib.metadata
import platform
from pathlib import Path
from typing import Any

from .utils import git_state, utc_now


def build_metadata(
    *,
    root: Path,
    registry: dict[str, Any],
    registry_hash: str,
    data_hash: str,
    config: dict[str, Any],
    scope: str,
) -> dict[str, Any]:
    """Build the run-level record of data, registry, code, software, and approval.

    The returned JSON-ready dictionary records source and registry fingerprints,
    scope, UTC execution time, Python and package versions, Git state, AI use,
    and the operational approval block. It contains no respondent-level data.
    """

    packages = {}
    for distribution in ("numpy", "pandas", "PyYAML", "scipy"):
        packages[distribution] = importlib.metadata.version(distribution)
    return {
        "paper_id": registry["paper_id"],
        "registry_revision": registry["revision"],
        "registry_status": registry["status"],
        "registry_sha256": registry_hash,
        "scope": scope,
        "executed_at_utc": utc_now(),
        "source_data_sha256": data_hash,
        "python_version": platform.python_version(),
        "package_versions": packages,
        "git": git_state(root),
        "ai": config.get("provenance", {}),
        "approval": config.get("approval", {}),
    }
