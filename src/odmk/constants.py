"""Frozen constants tied to the public HINTS 5 Cycle 2 release."""

EXPECTED_DATA_SHA256 = "a727f1b7a56f293dc2212bb9cc8705cacdc4e57d6d8e5505012b713ecfd1531f"
EXPECTED_SOURCE_ROWS = 3504
REGISTRY_REVISION = 7
JK1_COEFFICIENT = 0.98
JK1_DF = 49
FOCAL_TERM = "non-Hispanic Asian minus non-Hispanic White PPPCQ mean"
FROZEN_REGISTRY_STATUS = "frozen_for_execution"

PCC_ITEMS = (
    "chanceaskquestions",
    "feelingsaddressed",
    "involveddecisions",
    "understoodnextsteps",
    "explainedclearly",
    "spentenoughtime",
    "helpuncertainty",
)
ASIAN_CHECKBOXES = (
    "asind",
    "chinese",
    "filipino",
    "japanese",
    "korean",
    "vietnamese",
    "othasian",
)
REPLICATE_WEIGHTS = tuple(f"person_finwt{i}" for i in range(1, 51))

POINT_ESTIMATE_DIMENSIONS = (
    "d01_analytic_sample",
    "d03_outcome_construction",
    "d04_main_predictor_construction",
)
VARIANCE_DIMENSION = "d08_variance_estimation"
DIMENSION_ORDER = (
    *POINT_ESTIMATE_DIMENSIONS,
    VARIANCE_DIMENSION,
)

RESULT_COLUMNS = (
    "paper_id",
    "registry_revision",
    "source_data_sha256",
    "specification_id",
    "point_estimate_id",
    "is_baseline",
    *DIMENSION_ORDER,
    "all_option_labels",
    "focal_term",
    "status",
    "failure_category",
    "failure_reason",
    "asian_mean",
    "asian_mean_se",
    "asian_mean_ci_low_95",
    "asian_mean_ci_high_95",
    "white_mean",
    "white_mean_se",
    "white_mean_ci_low_95",
    "white_mean_ci_high_95",
    "asian_minus_white_difference",
    "standard_error_of_difference",
    "ci_low_95",
    "ci_high_95",
    "test_statistic",
    "denominator_degrees_of_freedom",
    "two_sided_p_value",
    "unweighted_asian_n",
    "unweighted_white_n",
    "weighted_asian_denominator",
    "weighted_white_denominator",
)
