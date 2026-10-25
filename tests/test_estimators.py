import math

import numpy as np
import pandas as pd

from odmk.estimators import estimate_taylor


def test_taylor_linearization_matches_hand_calculation() -> None:
    rows = []
    asian_values = [1.0, 3.0, 2.0, 4.0]
    white_values = [2.0, 2.0, 4.0, 4.0]
    for position, (asian_y, white_y) in enumerate(zip(asian_values, white_values, strict=True)):
        stratum = "S1" if position < 2 else "S2"
        cluster = position % 2 + 1
        rows.extend(
            [
                {"var_stratum": stratum, "var_cluster": cluster, "person_finwt0": 1.0, "y": asian_y, "group": "A"},
                {"var_stratum": stratum, "var_cluster": cluster, "person_finwt0": 1.0, "y": white_y, "group": "W"},
            ]
        )
    frame = pd.DataFrame(rows)
    y = frame["y"].to_numpy()
    asian = frame["group"].eq("A").to_numpy()
    white = frame["group"].eq("W").to_numpy()
    result = estimate_taylor(frame, y, asian, white)

    assert result["asian_mean"] == 2.5
    assert result["white_mean"] == 3.0
    assert result["asian_minus_white_difference"] == -0.5
    assert math.isclose(result["standard_error_of_difference"], math.sqrt(0.5))
    assert result["denominator_degrees_of_freedom"] == 2


def test_taylor_linearization_matches_r_survey_weighted_domain_reference() -> None:
    """Match the frozen output of tests/reference/taylor_survey_reference.R."""

    rows = []
    for h in range(1, 4):
        for j in range(1, 4):
            rows.extend(
                [
                    {
                        "var_stratum": f"S{h}",
                        "var_cluster": j,
                        "person_finwt0": 0.8 + 0.23 * h + 0.11 * j,
                        "y": 1 + ((2 * h + j) % 4),
                        "group": "A",
                        "analytic": not (h == 2 and j == 3),
                    },
                    {
                        "var_stratum": f"S{h}",
                        "var_cluster": j,
                        "person_finwt0": 0.9 + 0.17 * h + 0.13 * j,
                        "y": 1 + ((h + 2 * j) % 4),
                        "group": "W",
                        "analytic": not (h == 1 and j == 2),
                    },
                    {
                        "var_stratum": f"S{h}",
                        "var_cluster": j,
                        "person_finwt0": 1.0 + 0.07 * h + 0.19 * j,
                        "y": 1 + ((3 * h + j) % 4),
                        "group": "O",
                        "analytic": True,
                    },
                    {
                        "var_stratum": f"S{h}",
                        "var_cluster": j,
                        "person_finwt0": 2.0 + 0.1 * h,
                        "y": 4,
                        "group": "A",
                        "analytic": False,
                    },
                ]
            )
    frame = pd.DataFrame(rows)
    y = frame["y"].to_numpy(float)
    analytic = frame["analytic"].to_numpy(bool)
    asian = analytic & frame["group"].eq("A").to_numpy()
    white = analytic & frame["group"].eq("W").to_numpy()
    result = estimate_taylor(frame, y, asian, white)

    expected = {
        "asian_mean": 2.341005967604433,
        "asian_mean_se": 0.470795518352500,
        "white_mean": 2.588331963845522,
        "white_mean_se": 0.401934283884296,
        "asian_minus_white_difference": -0.247325996241089,
        "standard_error_of_difference": 0.655938295699806,
    }
    for field, value in expected.items():
        assert math.isclose(result[field], value, rel_tol=0, abs_tol=1e-12)
    assert result["denominator_degrees_of_freedom"] == 6
