"""Frozen production runtime checks."""

from __future__ import annotations

import importlib.metadata
import platform

from .exceptions import ODMKError

EXPECTED_PYTHON = "3.14.4"
EXPECTED_PACKAGES = {
    "numpy": "2.4.4",
    "pandas": "3.0.2",
    "PyYAML": "6.0.3",
    "scipy": "1.17.1",
    "pytest": "9.0.3",
}


def assert_frozen_environment() -> dict[str, object]:
    observed_python = platform.python_version()
    mismatches = []
    if observed_python != EXPECTED_PYTHON:
        mismatches.append(f"Python: {observed_python} != {EXPECTED_PYTHON}")
    observed_packages = {}
    for distribution, expected in EXPECTED_PACKAGES.items():
        observed = importlib.metadata.version(distribution)
        observed_packages[distribution] = observed
        if observed != expected:
            mismatches.append(f"{distribution}: {observed} != {expected}")
    if mismatches:
        raise ODMKError("Frozen environment mismatch: " + "; ".join(mismatches))
    return {"python": observed_python, "packages": observed_packages}

