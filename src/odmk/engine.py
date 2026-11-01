"""Cell execution with scope guards and explicit failed-cell records."""

from __future__ import annotations

import json
import math
from typing import Literal

import numpy as np
import pandas as pd

from .constants import (
    DIMENSION_ORDER,
    EXPECTED_DATA_SHA256,
    FOCAL_TERM,
    REGISTRY_REVISION,
    RESULT_COLUMNS,
)
from .data import cell_arrays
from .estimators import estimate_jk1, estimate_taylor
from .exceptions import CellEstimationError, DataValidationError, ODMKError

Scope = Literal["baseline", "synthetic", "approved"]


def _identity(cell: pd.Series) -> dict[str, object]:
    """Return immutable registry identity fields for one manifest row."""

    options = {name: cell[name] for name in DIMENSION_ORDER}
    return {
        "paper_id": "ODMK",
        "registry_revision": REGISTRY_REVISION,
        "specification_id": cell["specification_id"],
        "point_estimate_id": cell["point_estimate_id"],
        "is_baseline": bool(cell["is_baseline"]),
        **options,
        "all_option_labels": json.dumps(options, sort_keys=True, separators=(",", ":")),
        "focal_term": FOCAL_TERM,
    }


def _failed(cell: pd.Series, error: Exception) -> dict[str, object]:
    """Represent an expected cell failure without changing its registered choices."""

    row: dict[str, object] = {
        **_identity(cell),
        "status": "failed",
        "failure_category": type(error).__name__,
        "failure_reason": str(error),
    }
    for name in RESULT_COLUMNS:
        row.setdefault(name, math.nan)
    return row


def estimate_cell(df: pd.DataFrame, cell: pd.Series) -> dict[str, object]:
    """Estimate one manifest row and return the frozen result-schema fields.

    The function constructs the selected outcome and domains, dispatches only
    to the registered variance estimator, and appends unweighted group counts.

    Raises:
        DataValidationError: If the selected sample, score, or group rule
            violates the frozen data contract.
        CellEstimationError: If a focal group is empty, the variance option is
            unknown, or estimation cannot produce a valid registered result.
    """

    y, asian, white = cell_arrays(df, cell)
    if asian.sum() == 0 or white.sum() == 0:
        raise CellEstimationError("Both focal groups must contain at least one observation")
    variance_option = cell["d08_variance_estimation"]
    if variance_option == "official_jk1_replicate_weights":
        estimates = estimate_jk1(df, y, asian, white)
    elif variance_option == "taylor_linearization":
        estimates = estimate_taylor(df, y, asian, white)
    else:
        raise CellEstimationError(f"Unknown d08 option: {variance_option}")
    return {
        **_identity(cell),
        "status": "success",
        "failure_category": "",
        "failure_reason": "",
        **estimates,
        "unweighted_asian_n": int(asian.sum()),
        "unweighted_white_n": int(white.sum()),
    }


def run_manifest(
    df: pd.DataFrame,
    manifest: pd.DataFrame,
    *,
    scope: Scope,
    source_hash: str,
    production_authorized: bool = False,
) -> pd.DataFrame:
    """Run the cells permitted by ``scope`` while enforcing provenance guards.

    ``baseline`` selects only the frozen baseline, ``synthetic`` permits all
    cells only on noncanonical data, and ``approved`` requires authorization
    returned by the production gate. Expected cell-level failures are retained
    as explicit rows; contract or authorization failures stop the run.

    Args:
        df: Complete derived source frame. Canonical frames carry their source
            fingerprint in ``DataFrame.attrs``.
        manifest: Frozen manifest with one row per registered specification.
        scope: Execution boundary: ``baseline``, ``synthetic``, or ``approved``.
        source_hash: Claimed fingerprint for the supplied frame.
        production_authorized: Truthy only after the production approval gate
            succeeds; ignored outside approved scope.

    Returns:
        Result rows in the exact order and columns defined by ``RESULT_COLUMNS``.
        Expected cell failures remain present with blank estimates and reasons.

    Raises:
        ODMKError: If provenance, scope, baseline uniqueness, or approved-run
            authorization violates the analysis contract.
    """

    attached_hash = df.attrs.get("source_sha256")
    if attached_hash is not None and attached_hash != source_hash:
        raise ODMKError("The supplied source hash does not match the data-frame provenance")
    effective_hash = attached_hash or source_hash
    if scope == "synthetic" and effective_hash == EXPECTED_DATA_SHA256:
        raise ODMKError("Synthetic scope cannot be used with the canonical HINTS source hash")
    if scope == "baseline":
        selected = manifest.loc[manifest["is_baseline"]]
        if len(selected) != 1:
            raise ODMKError("Baseline scope requires exactly one baseline cell")
    elif scope == "approved":
        if not production_authorized:
            raise ODMKError("Approved scope requires an authorization returned by the production gate")
        selected = manifest
    elif scope == "synthetic":
        selected = manifest
    else:
        raise ODMKError(f"Unknown execution scope: {scope}")

    rows: list[dict[str, object]] = []
    for _, cell in selected.iterrows():
        try:
            rows.append(estimate_cell(df, cell))
        except (CellEstimationError, DataValidationError, FloatingPointError, ZeroDivisionError) as error:
            rows.append(_failed(cell, error))
    results = pd.DataFrame(rows, columns=RESULT_COLUMNS)
    results["source_data_sha256"] = effective_hash
    return results.loc[:, RESULT_COLUMNS]
