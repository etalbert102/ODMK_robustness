from argparse import Namespace
import json
from pathlib import Path
import subprocess

import pandas as pd
import pytest
import yaml

import run_multiverse
from odmk.exceptions import ApprovalError, ODMKError
from odmk.utils import OUTPUT_OWNERSHIP_MARKER, project_root, sha256_file


def _arguments(tmp_path: Path) -> Namespace:
    root = project_root()
    return Namespace(
        data=tmp_path / "unused-synthetic-input.dta",
        registry=root / "specification_freeze.yaml",
        config=root / "config/execution.yaml",
        output_dir=tmp_path / "outputs/multiverse",
        confirm_approved=True,
    )


def _approved_arguments(tmp_path: Path) -> Namespace:
    arguments = _arguments(tmp_path)
    registry_hash = sha256_file(arguments.registry)
    config = {
        "approval": {
            "cos_status": "approved",
            "cos_approved_at": "2026-11-01",
            "cos_approval_record": "record/synthetic-integration-test",
            "approved_registry_sha256": registry_hash,
            "researcher_status": "approved",
            "researcher_name": "Integration test",
            "researcher_approved_at": "2026-11-01",
        },
        "provenance": {"fixture": True},
        "execution_policy": {"require_clean_git_for_multiverse": True},
    }
    arguments.config = tmp_path / "execution.yaml"
    arguments.config.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "tests@example.invalid"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "ODMK tests"], cwd=tmp_path, check=True
    )
    subprocess.run(["git", "add", "execution.yaml"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=tmp_path, check=True)
    return arguments


def _patch_synthetic_canonical_boundaries(monkeypatch, synthetic_raw) -> None:
    monkeypatch.setattr(
        run_multiverse,
        "read_canonical_hints",
        lambda path: (synthetic_raw.copy(), "synthetic-runner-fixture"),
    )
    monkeypatch.setattr(
        run_multiverse,
        "validate_canonical_structure",
        lambda frame, registry: {
            "structural_anchors": {"fixture": True},
            "clusters_per_stratum": {"S1": 4, "S2": 4},
            "design_df": 6,
        },
    )
    monkeypatch.setattr(
        run_multiverse,
        "validate_real_baseline",
        lambda results: {"all_checks_pass": True},
    )
    monkeypatch.setattr(
        run_multiverse,
        "validate_published_table2_anchors",
        lambda frame: {"all_checks_pass": True},
    )


def test_pending_approval_blocks_before_source_data_are_opened(
    tmp_path: Path, monkeypatch
) -> None:
    opened = False

    def fail_if_opened(path: Path):
        nonlocal opened
        opened = True
        raise AssertionError("source data must not be opened")

    monkeypatch.setattr(run_multiverse, "assert_frozen_environment", lambda: {})
    monkeypatch.setattr(run_multiverse, "read_canonical_hints", fail_if_opened)
    arguments = _arguments(tmp_path)
    pending_config = {
        "approval": {
            "cos_status": "pending",
            "researcher_status": "approved",
        },
        "execution_policy": {"require_clean_git_for_multiverse": False},
    }
    arguments.config = tmp_path / "pending-execution.yaml"
    arguments.config.write_text(
        yaml.safe_dump(pending_config, sort_keys=False), encoding="utf-8"
    )

    with pytest.raises(ApprovalError, match="cos_status"):
        run_multiverse.execute_registered_multiverse(
            arguments, root=project_root()
        )

    assert opened is False


def test_failed_baseline_gate_prevents_approved_cells(
    tmp_path: Path, monkeypatch, synthetic_raw
) -> None:
    arguments = _approved_arguments(tmp_path)
    _patch_synthetic_canonical_boundaries(monkeypatch, synthetic_raw)
    scopes = []
    real_run_manifest = run_multiverse.run_manifest

    def record_scope(*args, **kwargs):
        scopes.append(kwargs["scope"])
        return real_run_manifest(*args, **kwargs)

    monkeypatch.setattr(run_multiverse, "run_manifest", record_scope)

    def fail_baseline(results):
        raise ODMKError("baseline gate failed")

    monkeypatch.setattr(
        run_multiverse,
        "validate_real_baseline",
        fail_baseline,
    )
    with pytest.raises(ODMKError, match="baseline gate failed"):
        run_multiverse.execute_registered_multiverse(arguments, root=tmp_path)

    assert scopes == ["baseline"]
    assert not arguments.output_dir.exists()


def test_approved_synthetic_orchestration_publishes_complete_artifact_set(
    tmp_path: Path, monkeypatch, synthetic_raw
) -> None:
    arguments = _approved_arguments(tmp_path)
    _patch_synthetic_canonical_boundaries(monkeypatch, synthetic_raw)
    scopes = []
    real_run_manifest = run_multiverse.run_manifest

    def record_scope(*args, **kwargs):
        scopes.append(kwargs["scope"])
        return real_run_manifest(*args, **kwargs)

    monkeypatch.setattr(run_multiverse, "run_manifest", record_scope)
    completed = run_multiverse.execute_registered_multiverse(arguments, root=tmp_path)

    assert completed == 16
    assert scopes == ["baseline", "approved"]
    assert {path.name for path in arguments.output_dir.iterdir()} == {
        OUTPUT_OWNERSHIP_MARKER,
        "results.csv",
        "cell_manifest.csv",
        "specification_table.md",
        "item_completion_distribution.csv",
        "scoring_coverage.csv",
        "validation.json",
        "run_metadata.json",
    }
    results = pd.read_csv(arguments.output_dir / "results.csv")
    manifest = pd.read_csv(arguments.output_dir / "cell_manifest.csv")
    item_completion = pd.read_csv(
        arguments.output_dir / "item_completion_distribution.csv"
    )
    scoring_coverage = pd.read_csv(arguments.output_dir / "scoring_coverage.csv")
    specification_table = (arguments.output_dir / "specification_table.md").read_text()
    metadata = json.loads((arguments.output_dir / "run_metadata.json").read_text())
    assert len(results) == len(manifest) == 16
    assert results["status"].eq("success").all()
    assert len(item_completion) == 64
    assert len(scoring_coverage) == 16
    assert all(
        specification_id in specification_table
        for specification_id in results["specification_id"]
    )
    assert metadata["scope"] == "approved"
    assert metadata["registry_sha256"] == sha256_file(arguments.registry)
    assert metadata["approval"]["cos_status"] == "approved"
    assert metadata["git"]["dirty"] is False
