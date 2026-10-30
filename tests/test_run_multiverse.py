from argparse import Namespace
from pathlib import Path

import pandas as pd
import pytest

import run_multiverse
from odmk.exceptions import ApprovalError, ODMKError
from odmk.utils import OUTPUT_OWNERSHIP_MARKER, project_root


def _arguments(tmp_path: Path) -> Namespace:
    root = project_root()
    return Namespace(
        data=tmp_path / "unused-synthetic-input.dta",
        registry=root / "specification_freeze.yaml",
        config=root / "config/execution.yaml",
        output_dir=tmp_path / "outputs/multiverse",
        confirm_approved=True,
    )


def _patch_approved_synthetic_run(monkeypatch, synthetic_raw) -> None:
    monkeypatch.setattr(run_multiverse, "assert_frozen_environment", lambda: {})
    monkeypatch.setattr(
        run_multiverse,
        "assert_production_approved",
        lambda *args, **kwargs: {"authorized": True},
    )
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
    monkeypatch.setattr(
        run_multiverse,
        "build_metadata",
        lambda **kwargs: {"scope": "approved", "fixture": True},
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

    with pytest.raises(ApprovalError, match="cos_status"):
        run_multiverse.execute_registered_multiverse(
            _arguments(tmp_path), root=project_root()
        )

    assert opened is False


def test_failed_baseline_gate_prevents_approved_cells(
    tmp_path: Path, monkeypatch, synthetic_raw
) -> None:
    _patch_approved_synthetic_run(monkeypatch, synthetic_raw)
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
    arguments = _arguments(tmp_path)

    with pytest.raises(ODMKError, match="baseline gate failed"):
        run_multiverse.execute_registered_multiverse(arguments, root=tmp_path)

    assert scopes == ["baseline"]
    assert not arguments.output_dir.exists()


def test_approved_synthetic_orchestration_publishes_complete_artifact_set(
    tmp_path: Path, monkeypatch, synthetic_raw
) -> None:
    _patch_approved_synthetic_run(monkeypatch, synthetic_raw)
    scopes = []
    real_run_manifest = run_multiverse.run_manifest

    def record_scope(*args, **kwargs):
        scopes.append(kwargs["scope"])
        return real_run_manifest(*args, **kwargs)

    monkeypatch.setattr(run_multiverse, "run_manifest", record_scope)
    arguments = _arguments(tmp_path)

    completed = run_multiverse.execute_registered_multiverse(arguments, root=tmp_path)

    assert completed == 16
    assert scopes == ["baseline", "approved"]
    assert {path.name for path in arguments.output_dir.iterdir()} == {
        OUTPUT_OWNERSHIP_MARKER,
        "results.csv",
        "cell_manifest.csv",
        "validation.json",
        "run_metadata.json",
    }
    results = pd.read_csv(arguments.output_dir / "results.csv")
    manifest = pd.read_csv(arguments.output_dir / "cell_manifest.csv")
    assert len(results) == len(manifest) == 16
    assert results["status"].eq("success").all()
