from pathlib import Path

import pytest

from odmk.data import derive_analysis_fields, read_canonical_hints, validate_canonical_structure
from odmk.engine import run_manifest
from odmk.registry import build_manifest, load_registry
from odmk.utils import project_root
from odmk.exceptions import ODMKError
from odmk.validation import validate_published_table2_anchors, validate_real_baseline


def test_canonical_registered_baseline_when_data_are_available() -> None:
    root = project_root()
    data_path = root / "data_raw/hints5_cycle2_public.dta"
    if not data_path.exists():
        pytest.skip("Canonical public-use file is not installed")
    registry = load_registry(root / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    raw, data_hash = read_canonical_hints(data_path)
    derived = derive_analysis_fields(raw)
    validate_canonical_structure(derived, registry)
    results = run_manifest(derived, manifest, scope="baseline", source_hash=data_hash)
    validation = validate_real_baseline(results)
    assert validation["all_checks_pass"]
    published = validate_published_table2_anchors(derived)
    assert published["analytic_n_all_five_groups"] == 2611

    changed = derived.copy()
    changed.loc[changed["raceethn5"].eq(1), "pppcq_complete7"] += 0.1
    with pytest.raises(ODMKError, match="mean failed"):
        validate_published_table2_anchors(changed)
