from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from odmk.constants import ASIAN_CHECKBOXES, PCC_ITEMS, REPLICATE_WEIGHTS
from odmk.data import derive_analysis_fields


@pytest.fixture()
def synthetic_raw() -> pd.DataFrame:
    rows = 160
    index = np.arange(rows)
    df = pd.DataFrame(
        {
            "hhid": index + 1,
            "freqgoprovider": np.where(index % 13 == 0, -9, 2),
            "raceethn5": np.select(
                [index % 8 == 0, index % 8 == 1, index % 8 < 6],
                [4, 5, 1],
                default=2,
            ),
            "hisp_cat": 10,
            "person_finwt0": 0.8 + (index % 9) / 10,
            "var_stratum": np.where(index < rows / 2, "S1", "S2"),
            "var_cluster": (index // 20) % 4 + 1,
        }
    )
    for checkbox in ASIAN_CHECKBOXES:
        df[checkbox] = 0
    df.loc[df["raceethn5"].eq(4), "chinese"] = 1
    df.loc[df["raceethn5"].eq(5) & (index % 8 == 1), "filipino"] = 1

    for item_number, item in enumerate(PCC_ITEMS):
        df[item] = ((index + item_number) % 4) + 1
    # Deterministic partial scales: five and four valid answers remain eligible
    # under the alternative, while the baseline continues to require all seven.
    df.loc[index % 11 == 0, list(PCC_ITEMS[:2])] = -9
    df.loc[index % 17 == 0, list(PCC_ITEMS[:3])] = -7

    base = df["person_finwt0"].to_numpy()
    for replicate_number, column in enumerate(REPLICATE_WEIGHTS, start=1):
        perturbation = 1 + 0.04 * np.sin((index + 1) * replicate_number / 17)
        df[column] = base * perturbation
    return df


@pytest.fixture()
def synthetic_derived(synthetic_raw: pd.DataFrame) -> pd.DataFrame:
    return derive_analysis_fields(synthetic_raw)

