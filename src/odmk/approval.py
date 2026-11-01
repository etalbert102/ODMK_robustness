"""Operational gate separating approved production from pre-approval work."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .exceptions import ApprovalError
from .utils import git_state


def load_execution_config(path: Path) -> dict[str, Any]:
    """Load operational approval metadata from YAML.

    The execution file records authorization and provenance only; it cannot add
    or alter a scientific option in the frozen registry.
    """

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def assert_production_approved(
    config: dict[str, Any], *, root: Path, confirmed: bool, registry_sha256: str
) -> dict[str, Any]:
    """Validate every production gate and return an authorization record.

    Args:
        config: Parsed execution configuration containing approval metadata and
            the clean-worktree policy.
        root: Git repository whose commit and worktree state will be recorded.
        confirmed: Whether the operator supplied the explicit production
            confirmation flag.
        registry_sha256: Fingerprint calculated from the registry about to run.

    Returns:
        The recorded approval block, validated registry fingerprint, and current
        Git state. A truthy returned record is required by approved execution.

    Raises:
        ApprovalError: If explicit confirmation, either approval, approval
            metadata, registry identity, or the required clean Git state is
            absent or invalid.
    """

    if not confirmed:
        raise ApprovalError("Production requires the explicit --confirm-approved flag")
    approval = config.get("approval", {})
    required = {
        "cos_status": "approved",
        "researcher_status": "approved",
    }
    for field, expected in required.items():
        if approval.get(field) != expected:
            raise ApprovalError(f"approval.{field} must equal {expected!r}")
    for field in ("cos_approved_at", "cos_approval_record", "researcher_approved_at"):
        if not approval.get(field):
            raise ApprovalError(f"approval.{field} must be recorded")
    approved_registry_sha256 = approval.get("approved_registry_sha256")
    if not isinstance(approved_registry_sha256, str) or (
        len(approved_registry_sha256) != 64
        or any(character not in "0123456789abcdef" for character in approved_registry_sha256)
    ):
        raise ApprovalError("approval.approved_registry_sha256 must be a lowercase SHA-256")
    if approved_registry_sha256 != registry_sha256:
        raise ApprovalError("The registry SHA-256 differs from the approved registry")
    state = git_state(root)
    if config.get("execution_policy", {}).get("require_clean_git_for_multiverse", True):
        if state["dirty"] is None:
            raise ApprovalError("Cannot verify Git state for production execution")
        if state["dirty"]:
            raise ApprovalError("Production execution requires a clean Git worktree")
    return {"approval": approval, "registry_sha256": registry_sha256, "git": state}
