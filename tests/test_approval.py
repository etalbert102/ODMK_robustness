from pathlib import Path

import pytest

from odmk.approval import assert_production_approved, load_execution_config
from odmk.exceptions import ApprovalError
from odmk.utils import project_root


def test_repository_config_blocks_unapproved_production() -> None:
    config = load_execution_config(project_root() / "config/execution.yaml")
    with pytest.raises(ApprovalError, match="cos_status"):
        assert_production_approved(
            config,
            root=project_root(),
            confirmed=True,
            registry_sha256="a" * 64,
        )


def test_explicit_confirmation_is_always_required(tmp_path: Path) -> None:
    config = {
        "approval": {
            "cos_status": "approved",
            "cos_approved_at": "2026-11-01",
            "cos_approval_record": "record/example",
            "researcher_status": "approved",
            "researcher_approved_at": "2026-11-01",
        },
        "execution_policy": {"require_clean_git_for_multiverse": False},
    }
    with pytest.raises(ApprovalError, match="--confirm-approved"):
        assert_production_approved(
            config,
            root=tmp_path,
            confirmed=False,
            registry_sha256="a" * 64,
        )


def test_unapproved_registry_hash_blocks_otherwise_approved_production(
    tmp_path: Path,
) -> None:
    config = {
        "approval": {
            "cos_status": "approved",
            "cos_approved_at": "2026-11-01",
            "cos_approval_record": "record/example",
            "approved_registry_sha256": "a" * 64,
            "researcher_status": "approved",
            "researcher_approved_at": "2026-11-01",
        },
        "execution_policy": {"require_clean_git_for_multiverse": False},
    }
    with pytest.raises(ApprovalError, match="differs from the approved registry"):
        assert_production_approved(
            config,
            root=tmp_path,
            confirmed=True,
            registry_sha256="b" * 64,
        )


def test_approved_registry_hash_allows_approved_production(tmp_path: Path) -> None:
    config = {
        "approval": {
            "cos_status": "approved",
            "cos_approved_at": "2026-11-01",
            "cos_approval_record": "record/example",
            "approved_registry_sha256": "a" * 64,
            "researcher_status": "approved",
            "researcher_approved_at": "2026-11-01",
        },
        "execution_policy": {"require_clean_git_for_multiverse": False},
    }
    authorization = assert_production_approved(
        config,
        root=tmp_path,
        confirmed=True,
        registry_sha256="a" * 64,
    )
    assert authorization["registry_sha256"] == "a" * 64
