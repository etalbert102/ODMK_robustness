import numpy as np

from odmk.constants import PCC_ITEMS
from odmk.data import cell_arrays
from odmk.registry import build_manifest, load_registry
from odmk.utils import project_root


def test_reverse_scoring_and_partial_scale_rules(synthetic_derived) -> None:
    df = synthetic_derived
    complete = df["pcc_valid_item_count"].eq(7)
    partial = df["pcc_valid_item_count"].between(4, 6)
    assert df.loc[complete, "pppcq_complete7"].notna().all()
    assert df.loc[partial, "pppcq_complete7"].isna().all()
    assert df.loc[partial, "pppcq_atleast4"].notna().all()
    first_complete = df.index[complete][0]
    source = df.loc[first_complete, PCC_ITEMS[0]]
    assert df.loc[first_complete, f"{PCC_ITEMS[0]}_reversed"] == 5 - source


def test_content_confirmation_retains_answered_followup_with_missing_filter(synthetic_derived) -> None:
    df = synthetic_derived
    repaired = ~df["recent_provider_visit"] & df["communication_followup_observed"]
    assert repaired.any()
    assert df.loc[repaired, "content_confirmed_module"].all()


def test_inclusive_asian_adds_multiracial_without_changing_white(synthetic_derived) -> None:
    df = synthetic_derived
    assert (df["official_asian"] <= df["inclusive_asian"]).all()
    assert (df["inclusive_asian"] & ~df["official_asian"]).any()
    assert not (df["inclusive_asian"] & df["official_white"]).any()


def test_cell_arrays_follow_manifest_options(synthetic_derived) -> None:
    registry = load_registry(project_root() / "specification_freeze.yaml")
    manifest = build_manifest(registry)
    baseline = manifest.iloc[0]
    score, asian, white = cell_arrays(synthetic_derived, baseline)
    assert np.isfinite(score[asian]).all()
    assert np.isfinite(score[white]).all()
    assert not np.any(asian & white)

