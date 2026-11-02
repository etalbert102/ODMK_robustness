#!/usr/bin/env Rscript

# Independent baseline-only reconstruction using R's survey package.
# This file deliberately defines only the published Table 2 specification; it
# has no arguments or branches for any registered robustness alternative.

EXPECTED_SHA256 <- "a727f1b7a56f293dc2212bb9cc8705cacdc4e57d6d8e5505012b713ecfd1531f"
EXPECTED_SOURCE_ROWS <- 3504L
EXPECTED_BASELINE_N <- 2611L
JK1_SCALE <- 0.98
JK1_DF <- 49L
PPPCQ_ITEMS <- c(
  "chanceaskquestions",
  "feelingsaddressed",
  "involveddecisions",
  "understoodnextsteps",
  "explainedclearly",
  "spentenoughtime",
  "helpuncertainty"
)
REPLICATE_WEIGHTS <- paste0("person_finwt", seq_len(50))
RACE_LABELS <- c(
  "non_hispanic_white",
  "non_hispanic_black",
  "hispanic",
  "non_hispanic_asian",
  "non_hispanic_other"
)
REQUIRED_PACKAGES <- c("digest", "haven", "survey")


parse_arguments <- function(arguments) {
  # Resolve the two paths accepted by this baseline-only command.
  if (length(arguments) != 2) {
    stop(
      "Usage: independent_r_baseline.R DATA_PATH OUTPUT_DIRECTORY",
      call. = FALSE
    )
  }
  output_directory <- arguments[[2]]
  dir.create(output_directory, recursive = TRUE, showWarnings = FALSE)
  list(
    data_path = normalizePath(arguments[[1]], mustWork = TRUE),
    output_directory = normalizePath(output_directory, mustWork = TRUE)
  )
}


check_package_environment <- function() {
  # Keep this audit separate from the pinned Python production environment.
  missing_packages <- REQUIRED_PACKAGES[
    !vapply(REQUIRED_PACKAGES, requireNamespace, logical(1), quietly = TRUE)
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
}


read_and_validate_source <- function(data_path) {
  # Verify source identity before reading or deriving any analysis field.
  observed_sha256 <- digest::digest(file = data_path, algo = "sha256")
  if (!identical(observed_sha256, EXPECTED_SHA256)) {
    stop(
      sprintf(
        "Source SHA-256 is %s, expected %s",
        observed_sha256,
        EXPECTED_SHA256
      ),
      call. = FALSE
    )
  }

  data <- as.data.frame(haven::read_dta(data_path))
  names(data) <- tolower(names(data))
  required_columns <- c(
    "hhid",
    "freqgoprovider",
    "raceethn5",
    "person_finwt0",
    PPPCQ_ITEMS,
    REPLICATE_WEIGHTS
  )
  missing_columns <- setdiff(required_columns, names(data))
  if (length(missing_columns) > 0) {
    stop(
      paste("Required source columns absent:", paste(missing_columns, collapse = ", ")),
      call. = FALSE
    )
  }
  if (nrow(data) != EXPECTED_SOURCE_ROWS) {
    stop(
      sprintf("Expected %d source rows; found %d", EXPECTED_SOURCE_ROWS, nrow(data)),
      call. = FALSE
    )
  }
  if (anyNA(data$hhid) || anyDuplicated(data$hhid)) {
    stop("HHID must be nonmissing and unique", call. = FALSE)
  }
  list(data = data, sha256 = observed_sha256)
}


derive_baseline_fields <- function(data) {
  # Reverse the seven items and require all seven; no response is imputed.
  reversed_items <- vapply(
    PPPCQ_ITEMS,
    function(item) {
      values <- as.numeric(data[[item]])
      ifelse(values %in% 1:4, 5 - values, NA_real_)
    },
    numeric(nrow(data))
  )
  valid_item_count <- rowSums(!is.na(reversed_items))
  complete_score <- rowMeans(reversed_items, na.rm = FALSE)
  complete_score[valid_item_count != 7] <- NA_real_

  # A recorded visit or an answered follow-up with explicit -9 routing confirms
  # membership in the published communication module population.
  provider_frequency <- as.numeric(data$freqgoprovider)
  recent_provider_visit <- provider_frequency %in% 1:6
  content_confirmed <- recent_provider_visit |
    (provider_frequency == -9 & valid_item_count > 0)
  official_race <- as.numeric(data$raceethn5)
  baseline_domain <- content_confirmed &
    !is.na(complete_score) &
    official_race %in% 1:5
  if (sum(baseline_domain) != EXPECTED_BASELINE_N) {
    stop(
      sprintf(
        "Expected baseline N=%d; reconstructed N=%d",
        EXPECTED_BASELINE_N,
        sum(baseline_domain)
      ),
      call. = FALSE
    )
  }

  data$pppcq_complete7 <- complete_score
  data$baseline_domain <- baseline_domain
  data$race_group <- factor(official_race, levels = 1:5, labels = RACE_LABELS)
  data
}


estimate_baseline <- function(data) {
  # Use the 50 combined replicate weights and the official HINTS JK1 factor.
  design <- survey::svrepdesign(
    data = data,
    weights = ~person_finwt0,
    repweights = as.matrix(data[REPLICATE_WEIGHTS]),
    type = "other",
    combined.weights = TRUE,
    scale = JK1_SCALE,
    rscales = rep(1, 50),
    mse = TRUE
  )
  baseline_design <- subset(design, baseline_domain)
  model <- survey::svyglm(
    pppcq_complete7 ~ 0 + race_group,
    design = baseline_design
  )

  coefficient_names <- paste0("race_group", RACE_LABELS)
  coefficients <- stats::coef(model)[coefficient_names]
  covariance <- stats::vcov(model)[
    coefficient_names,
    coefficient_names,
    drop = FALSE
  ]
  standard_errors <- sqrt(diag(covariance))
  design_df <- survey::degf(baseline_design)
  if (design_df != JK1_DF) {
    stop(
      sprintf("Expected %d replicate-design degrees of freedom; found %d", JK1_DF, design_df),
      call. = FALSE
    )
  }

  contrast_vector <- c(-1, 0, 0, 1, 0)
  contrast_estimate <- as.numeric(crossprod(contrast_vector, coefficients))
  contrast_variance <- as.numeric(
    t(contrast_vector) %*% covariance %*% contrast_vector
  )
  contrast_se <- sqrt(contrast_variance)
  critical <- stats::qt(0.975, df = design_df)
  group_counts <- vapply(
    1:5,
    function(code) sum(data$baseline_domain & as.numeric(data$raceethn5) == code),
    integer(1)
  )

  results <- data.frame(
    result_type = c(rep("group_mean", 5), "contrast"),
    label = c(RACE_LABELS, "non_hispanic_asian_minus_non_hispanic_white"),
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
  list(
    results = results,
    contrast_estimate = contrast_estimate,
    contrast_se = contrast_se,
    design_df = design_df
  )
}


write_audit_files <- function(output_directory, source, data, estimates) {
  # Write only baseline results and provenance; no multiverse schema is present.
  utils::write.csv(
    estimates$results,
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
      source$sha256,
      nrow(data),
      sum(data$baseline_domain),
      as.character(getRversion()),
      as.character(utils::packageVersion("digest")),
      as.character(utils::packageVersion("haven")),
      as.character(utils::packageVersion("survey")),
      JK1_SCALE,
      estimates$design_df
    ),
    stringsAsFactors = FALSE
  )
  utils::write.csv(
    metadata,
    file.path(output_directory, "metadata.csv"),
    row.names = FALSE
  )
}


main <- function() {
  paths <- parse_arguments(commandArgs(trailingOnly = TRUE))
  check_package_environment()
  source <- read_and_validate_source(paths$data_path)
  data <- derive_baseline_fields(source$data)
  estimates <- estimate_baseline(data)
  write_audit_files(paths$output_directory, source, data, estimates)
  cat(sprintf(
    paste0(
      "Independent R baseline passed: N=%d; ",
      "Asian-minus-White=%.10f (SE %.10f)\n"
    ),
    sum(data$baseline_domain),
    estimates$contrast_estimate,
    estimates$contrast_se
  ))
}


main()
