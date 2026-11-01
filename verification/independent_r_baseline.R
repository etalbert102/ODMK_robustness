#!/usr/bin/env Rscript

# Independent baseline-only reconstruction using R's survey package.
# This script deliberately defines only the published Table 2 specification;
# it has no arguments or branches for any registered robustness alternative.

arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) != 2) {
  stop(
    "Usage: independent_r_baseline.R DATA_PATH OUTPUT_DIRECTORY",
    call. = FALSE
  )
}

required_packages <- c("digest", "haven", "survey")
missing_packages <- required_packages[
  !vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)
]
if (length(missing_packages) > 0) {
  stop(
    paste(
      "Missing R packages:",
      paste(missing_packages, collapse = ", "),
      "Install them before running the independent baseline check."
    ),
    call. = FALSE
  )
}

data_path <- normalizePath(arguments[[1]], mustWork = TRUE)
output_directory <- arguments[[2]]
dir.create(output_directory, recursive = TRUE, showWarnings = FALSE)

expected_sha256 <- "a727f1b7a56f293dc2212bb9cc8705cacdc4e57d6d8e5505012b713ecfd1531f"
observed_sha256 <- digest::digest(file = data_path, algo = "sha256")
if (!identical(observed_sha256, expected_sha256)) {
  stop(
    sprintf("Source SHA-256 is %s, expected %s", observed_sha256, expected_sha256),
    call. = FALSE
  )
}

data <- as.data.frame(haven::read_dta(data_path))
names(data) <- tolower(names(data))

pppcq_items <- c(
  "chanceaskquestions",
  "feelingsaddressed",
  "involveddecisions",
  "understoodnextsteps",
  "explainedclearly",
  "spentenoughtime",
  "helpuncertainty"
)
replicate_weights <- paste0("person_finwt", seq_len(50))
required_columns <- c(
  "hhid",
  "freqgoprovider",
  "raceethn5",
  "person_finwt0",
  pppcq_items,
  replicate_weights
)
missing_columns <- setdiff(required_columns, names(data))
if (length(missing_columns) > 0) {
  stop(
    paste("Required source columns absent:", paste(missing_columns, collapse = ", ")),
    call. = FALSE
  )
}
if (nrow(data) != 3504) {
  stop(sprintf("Expected 3504 source rows; found %d", nrow(data)), call. = FALSE)
}
if (anyNA(data$hhid) || anyDuplicated(data$hhid)) {
  stop("HHID must be nonmissing and unique", call. = FALSE)
}

# Reconstruct the published seven-item PPPCQ score independently from source
# responses. Source codes outside 1--4 are missing; no item is imputed.
reversed_items <- vapply(
  pppcq_items,
  function(item) {
    values <- as.numeric(data[[item]])
    ifelse(values %in% 1:4, 5 - values, NA_real_)
  },
  numeric(nrow(data))
)
valid_item_count <- rowSums(!is.na(reversed_items))
complete_score <- rowMeans(reversed_items, na.rm = FALSE)
complete_score[valid_item_count != 7] <- NA_real_

# The baseline eligibility rule accepts a recorded visit or an answered
# communication follow-up when the routing response is explicitly -9.
provider_frequency <- as.numeric(data$freqgoprovider)
recent_provider_visit <- provider_frequency %in% 1:6
content_confirmed <- recent_provider_visit |
  (provider_frequency == -9 & valid_item_count > 0)
official_race <- as.numeric(data$raceethn5)
baseline_domain <- content_confirmed &
  !is.na(complete_score) &
  official_race %in% 1:5

race_labels <- c(
  "non_hispanic_white",
  "non_hispanic_black",
  "hispanic",
  "non_hispanic_asian",
  "non_hispanic_other"
)
data$pppcq_complete7 <- complete_score
data$baseline_domain <- baseline_domain
data$race_group <- factor(official_race, levels = 1:5, labels = race_labels)

# HINTS supplies combined replicate weights. The official JK1 coefficient is
# 0.98, and mse=TRUE centers replicate estimates on the full-sample estimate.
design <- survey::svrepdesign(
  data = data,
  weights = ~person_finwt0,
  repweights = as.matrix(data[replicate_weights]),
  type = "other",
  combined.weights = TRUE,
  scale = 0.98,
  rscales = rep(1, 50),
  mse = TRUE
)
baseline_design <- subset(design, baseline_domain)
model <- survey::svyglm(
  pppcq_complete7 ~ 0 + race_group,
  design = baseline_design
)

coefficient_names <- paste0("race_group", race_labels)
coefficients <- stats::coef(model)[coefficient_names]
covariance <- stats::vcov(model)[coefficient_names, coefficient_names, drop = FALSE]
standard_errors <- sqrt(diag(covariance))
design_df <- survey::degf(baseline_design)
if (design_df != 49) {
  stop(sprintf("Expected 49 replicate-design degrees of freedom; found %d", design_df))
}
critical <- stats::qt(0.975, df = design_df)
group_counts <- vapply(
  1:5,
  function(code) sum(baseline_domain & official_race == code),
  integer(1)
)

contrast_vector <- c(-1, 0, 0, 1, 0)
contrast_estimate <- as.numeric(crossprod(contrast_vector, coefficients))
contrast_variance <- as.numeric(
  t(contrast_vector) %*% covariance %*% contrast_vector
)
contrast_se <- sqrt(contrast_variance)

results <- data.frame(
  result_type = c(rep("group_mean", 5), "contrast"),
  label = c(race_labels, "non_hispanic_asian_minus_non_hispanic_white"),
  race_code = c(1:5, NA_integer_),
  unweighted_n = c(group_counts, NA_integer_),
  estimate = c(as.numeric(coefficients), contrast_estimate),
  standard_error = c(as.numeric(standard_errors), contrast_se),
  ci_low_95 = c(
    as.numeric(coefficients - critical * standard_errors),
    contrast_estimate - critical * contrast_se
  ),
  ci_high_95 = c(
    as.numeric(coefficients + critical * standard_errors),
    contrast_estimate + critical * contrast_se
  ),
  denominator_degrees_of_freedom = design_df,
  stringsAsFactors = FALSE
)
utils::write.csv(
  results,
  file.path(output_directory, "results.csv"),
  row.names = FALSE,
  na = ""
)

metadata <- data.frame(
  field = c(
    "source_data_sha256",
    "source_rows",
    "baseline_analytic_n",
    "r_version",
    "digest_version",
    "haven_version",
    "survey_version",
    "jk1_scale",
    "design_degrees_of_freedom"
  ),
  value = c(
    observed_sha256,
    nrow(data),
    sum(baseline_domain),
    as.character(getRversion()),
    as.character(utils::packageVersion("digest")),
    as.character(utils::packageVersion("haven")),
    as.character(utils::packageVersion("survey")),
    0.98,
    design_df
  ),
  stringsAsFactors = FALSE
)
utils::write.csv(
  metadata,
  file.path(output_directory, "metadata.csv"),
  row.names = FALSE
)

cat(sprintf(
  paste0(
    "Independent R baseline passed: N=%d; ",
    "Asian-minus-White=%.10f (SE %.10f)\n"
  ),
  sum(baseline_domain),
  contrast_estimate,
  contrast_se
))
