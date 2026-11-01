# Survey estimator implementation

The Python code states each survey formula directly instead of relying on hidden
software defaults. This lets a reviewer compare the implementation with the
frozen instructions in `specification_freeze.yaml`. The two registered methods
are delete-one jackknife (JK1) replicate-weight inference and Taylor
linearization.

## Shared point estimator

For either comparison group, every analysis calculates the weighted mean

`mean_g = sum(w_i * I_ig * y_i) / sum(w_i * I_ig)`,

Here, `w_i` is the final population weight (`PERSON_FINWT0`), `y_i` is the PPPCQ
score, and `I_ig` equals 1 when record `i` belongs to group `g` and 0 otherwise.
The main result is `mean_Asian - mean_White`. The code retains the full
public-use file during this calculation instead of first deleting records
outside the two comparison groups.

## Official JK1 replicate weights

The code recalculates both group means and their difference with each of
`PERSON_FINWT1` through `PERSON_FINWT50`. For any estimate, written as `theta`,
it uses

`variance(theta) = 0.98 * sum((theta_r - theta_0)^2)`.

Confidence intervals and two-sided tests use 49 denominator degrees of
freedom. This is the algorithm specified in the HINTS 5 Cycle 2 methodology
documentation and the frozen registry.

## Taylor linearization

For a group mean, record `i` has the linearized value

`z_ig = w_i * I_ig * (y_i - mean_g) / sum(w_i * I_ig)`.

For the main difference, its linearized value is `z_iAsian - z_iWhite`.
These values are summed within each released `VAR_STRATUM` and `VAR_CLUSTER`
pair. Within each stratum containing `m_h` clusters, the contribution is

`m_h / (m_h - 1) * sum((Z_hj - mean(Z_h))^2)`.

The code adds the contributions from all strata. The released design has two
strata and 100 clusters within those strata, so tests and confidence intervals
use `100 - 2 = 98` denominator degrees of freedom. No finite-population
correction is applied because the public-use design does not provide one.

Both implementations are independently checked against frozen output from R
`survey` 4.5. `tests/reference/jk1_survey_reference.R` checks weighted group
means and their direct contrast with 50 combined replicate weights.
`tests/reference/taylor_survey_reference.R` checks the same quantities in a
weighted, stratified survey example. R is used only to create these reference
values and is not required to run the analysis.

## Enforced checks

- JK1 and Taylor rows using the same sample, score, and groups must have
  identical means and Asian-minus-White differences.
- The program reports this equality as verified only when all eight pairs can
  be compared.
- Every replicate denominator must be positive.
- Every Taylor stratum must contain at least two released clusters.
- The registered HINTS file must contain two strata and 50 clusters per stratum.
- Failed analyses remain in the output with their ID and reason.
