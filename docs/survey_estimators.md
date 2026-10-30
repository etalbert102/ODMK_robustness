# Survey estimator implementation

The production implementation uses explicit Python formulas tied to
`specification_freeze.yaml`. This keeps both registered variance choices
auditable and avoids relying on undocumented software defaults.

## Shared point estimator

For focal group `g`, every cell estimates the ratio mean

`mean_g = sum(w_i * I_ig * y_i) / sum(w_i * I_ig)`,

where `w_i` is `PERSON_FINWT0` and `I_ig` is the registered analytic-domain
indicator. The focal estimate is `mean_Asian - mean_White`. The code evaluates
the domain indicators on the full public-use frame; it does not construct a
survey design from a prefiltered focal-group file.

## Official JK1 replicate weights

The code recalculates both group means and their difference with each of
`PERSON_FINWT1` through `PERSON_FINWT50`. For any estimate `theta`, it uses

`variance(theta) = 0.98 * sum((theta_r - theta_0)^2)`.

Confidence intervals and two-sided tests use 49 denominator degrees of
freedom. This is the algorithm specified in the HINTS 5 Cycle 2 methodology
documentation and the frozen registry.

## Taylor linearization

For a group mean, record `i` has the linearized value

`z_ig = w_i * I_ig * (y_i - mean_g) / sum(w_i * I_ig)`.

For the focal difference, its linearized value is `z_iAsian - z_iWhite`.
These values are summed within each released `VAR_STRATUM` and `VAR_CLUSTER`
pair. Within each stratum containing `m_h` clusters, the contribution is

`m_h / (m_h - 1) * sum((Z_hj - mean(Z_h))^2)`.

The stratum contributions are summed. The released design has two strata and
100 stratum-specific clusters, so inference uses `100 - 2 = 98` denominator
degrees of freedom. No finite-population correction is applied because none is
provided in the registered public-use design.

Both implementations are independently checked against frozen output from R
`survey` 4.5. `tests/reference/jk1_survey_reference.R` checks weighted group
means and their direct contrast with 50 combined replicate weights.
`tests/reference/taylor_survey_reference.R` checks the same quantities in a
weighted, stratified survey example. R is used only to create these reference
values and is not required to run the analysis.

## Enforced checks

- JK1 and Taylor paired cells must have identical group means and contrasts.
- Invariance is marked verified only when all eight pairs can be compared.
- Every replicate denominator must be positive.
- Every Taylor stratum must contain at least two released clusters.
- The canonical file must contain two strata and 50 clusters per stratum.
- Failed registered cells remain in the output with their identity and reason.
