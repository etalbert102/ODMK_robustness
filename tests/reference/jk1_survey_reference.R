# Independent reference calculation for tests/test_estimators.py.
#
# Run with R and the CRAN survey package. The Python test freezes the values
# printed by survey 4.5; R is not a production dependency.

suppressPackageStartupMessages(library(survey))

fixture <- data.frame(
  id = 1:8,
  weight = c(1.2, 0.9, 1.6, 1.1, 1.4, 0.8, 1.3, 1.0),
  y = c(1, 3, 4, 2, 2, 4, 3, 1),
  group = c("A", "A", "A", "W", "W", "W", "O", "A"),
  analytic = c(TRUE, TRUE, FALSE, TRUE, TRUE, TRUE, TRUE, FALSE)
)

# These are combined replicate weights: each column contains the final
# replicate weight, rather than a multiplier applied to the full-sample weight.
replicate_weights <- sapply(1:50, function(replicate_number) {
  fixture$weight * (
    1 +
      0.08 * sin(fixture$id * replicate_number / 7) +
      0.03 * cos((fixture$id + replicate_number) / 5)
  )
})
colnames(replicate_weights) <- paste0("rep", 1:50)

design <- svrepdesign(
  data = fixture,
  weights = ~weight,
  repweights = replicate_weights,
  type = "other",
  combined.weights = TRUE,
  scale = 49 / 50,
  rscales = rep(1, 50),
  mse = TRUE
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
