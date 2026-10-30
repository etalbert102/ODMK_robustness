from pathlib import Path
import subprocess

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


def test_dirty_git_worktree_blocks_approved_production(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "tests@example.invalid"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "ODMK tests"], cwd=tmp_path, check=True
    )
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("clean\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=tmp_path, check=True)
    tracked.write_text("dirty\n", encoding="utf-8")

    config = {
        "approval": {
            "cos_status": "approved",
            "cos_approved_at": "2026-11-01",
            "cos_approval_record": "record/example",
            "approved_registry_sha256": "a" * 64,
            "researcher_status": "approved",
            "researcher_approved_at": "2026-11-01",
        },
        "execution_policy": {"require_clean_git_for_multiverse": True},
    }

    with pytest.raises(ApprovalError, match="clean Git worktree"):
        assert_production_approved(
            config,
            root=tmp_path,
            confirmed=True,
            registry_sha256="a" * 64,
        )


def test_clean_git_worktree_allows_approved_production(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "tests@example.invalid"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "ODMK tests"], cwd=tmp_path, check=True
    )
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("clean\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=tmp_path, check=True)
    config = {
        "approval": {
            "cos_status": "approved",
            "cos_approved_at": "2026-11-01",
            "cos_approval_record": "record/example",
            "approved_registry_sha256": "a" * 64,
            "researcher_status": "approved",
            "researcher_approved_at": "2026-11-01",
        },
        "execution_policy": {"require_clean_git_for_multiverse": True},
    }

    authorization = assert_production_approved(
        config,
        root=tmp_path,
        confirmed=True,
        registry_sha256="a" * 64,
    )

    assert authorization["git"]["dirty"] is False
    assert authorization["git"]["commit"]


@pytest.mark.parametrize(
    "missing_field",
    ["cos_approved_at", "cos_approval_record", "researcher_approved_at"],
)
def test_missing_approval_record_fields_are_rejected(
    tmp_path: Path, missing_field: str
) -> None:
    approval = {
        "cos_status": "approved",
        "cos_approved_at": "2026-11-01",
        "cos_approval_record": "record/example",
        "approved_registry_sha256": "a" * 64,
        "researcher_status": "approved",
        "researcher_approved_at": "2026-11-01",
    }
    approval[missing_field] = None
    config = {
        "approval": approval,
        "execution_policy": {"require_clean_git_for_multiverse": False},
    }

    with pytest.raises(ApprovalError, match=missing_field):
        assert_production_approved(
            config,
            root=tmp_path,
            confirmed=True,
            registry_sha256="a" * 64,
        )


def test_malformed_approved_registry_hash_is_rejected(tmp_path: Path) -> None:
    config = {
        "approval": {
            "cos_status": "approved",
            "cos_approved_at": "2026-11-01",
            "cos_approval_record": "record/example",
            "approved_registry_sha256": "A" * 64,
            "researcher_status": "approved",
            "researcher_approved_at": "2026-11-01",
        },
        "execution_policy": {"require_clean_git_for_multiverse": False},
    }

    with pytest.raises(ApprovalError, match="lowercase SHA-256"):
        assert_production_approved(
            config,
            root=tmp_path,
            confirmed=True,
            registry_sha256="a" * 64,
        )


def test_unverifiable_git_state_blocks_production(tmp_path: Path) -> None:
    config = {
        "approval": {
            "cos_status": "approved",
            "cos_approved_at": "2026-11-01",
            "cos_approval_record": "record/example",
            "approved_registry_sha256": "a" * 64,
            "researcher_status": "approved",
            "researcher_approved_at": "2026-11-01",
        },
        "execution_policy": {"require_clean_git_for_multiverse": True},
    }

    with pytest.raises(ApprovalError, match="Cannot verify Git state"):
        assert_production_approved(
            config,
            root=tmp_path,
            confirmed=True,
            registry_sha256="a" * 64,
        )
