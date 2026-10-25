# Independent reference calculation for tests/test_estimators.py.
#
# Run with R and the CRAN survey package. The Python test freezes the values
# printed by survey 4.5; R is not a production dependency.

suppressPackageStartupMessages(library(survey))
options(survey.lonely.psu = "fail")

rows <- list()
position <- 1
for (h in 1:3) {
  for (j in 1:3) {
    rows[[position]] <- data.frame(
      stratum = paste0("S", h), cluster = j, group = "A",
      analytic = !(h == 2 && j == 3),
      weight = 0.8 + 0.23 * h + 0.11 * j,
      y = 1 + ((2 * h + j) %% 4)
    )
    position <- position + 1
    rows[[position]] <- data.frame(
      stratum = paste0("S", h), cluster = j, group = "W",
      analytic = !(h == 1 && j == 2),
      weight = 0.9 + 0.17 * h + 0.13 * j,
      y = 1 + ((h + 2 * j) %% 4)
    )
    position <- position + 1
    rows[[position]] <- data.frame(
      stratum = paste0("S", h), cluster = j, group = "O",
      analytic = TRUE,
      weight = 1.0 + 0.07 * h + 0.19 * j,
      y = 1 + ((3 * h + j) %% 4)
    )
    position <- position + 1
    rows[[position]] <- data.frame(
      stratum = paste0("S", h), cluster = j, group = "A",
      analytic = FALSE,
      weight = 2.0 + 0.1 * h,
      y = 4
    )
    position <- position + 1
  }
}

fixture <- do.call(rbind, rows)
design <- svydesign(
  ids = ~cluster,
  strata = ~stratum,
  weights = ~weight,
  data = fixture,
  nest = TRUE
)
domain <- subset(design, analytic & group %in% c("A", "W"))
means <- svyby(~y, ~group, domain, svymean, covmat = TRUE, keep.var = TRUE)
contrast <- svycontrast(means, quote(A - W))

cat(sprintf("asian_mean=%.15f\n", coef(means)[["A"]]))
cat(sprintf("asian_se=%.15f\n", SE(means)[[1]]))
cat(sprintf("white_mean=%.15f\n", coef(means)[["W"]]))
cat(sprintf("white_se=%.15f\n", SE(means)[[2]]))
cat(sprintf("difference=%.15f\n", coef(contrast)[[1]]))
cat(sprintf("difference_se=%.15f\n", SE(contrast)[[1]]))
cat(sprintf("design_df=%d\n", degf(design)))
