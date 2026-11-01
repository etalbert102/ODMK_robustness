# Output file schema

After an approved run, `outputs/multiverse/results.csv` contains one row for
each of the 16 prespecified analyses for Center for Open Science (COS) paper
ODMK. A pre-approval baseline run writes the same columns to
`outputs/registered_baseline/results.csv`, but includes only `ODMK-01`.
`manifests/specification_manifest.csv` lists the 16 IDs and choices without
results, so it is safe to generate before approval.

Blank estimate fields in `results.csv` mean that the registered analysis failed;
`failure_category` and `failure_reason` then explain why. They do not mean zero.

## `results.csv`

### Identity and registered choices

| Column | Type | Meaning |
|---|---|---|
| `paper_id` | string | COS paper ID; always `ODMK`. |
| `registry_revision` | integer | Frozen registry revision; currently `7`. |
| `source_data_sha256` | string | SHA-256 of the source respondent file. |
| `specification_id` | string | Complete analysis ID, `ODMK-01` through `ODMK-16`. |
| `point_estimate_id` | string | Groups the delete-one jackknife (JK1) and Taylor rows that share a sample, score, and race definition. |
| `is_baseline` | Boolean | `true` only for the published-baseline combination. |
| `d01_analytic_sample` | string | Registered eligible-sample option. |
| `d03_outcome_construction` | string | Registered perceived patient-provider communication quality (PPPCQ) completion option. |
| `d04_main_predictor_construction` | string | Registered Asian-group option. |
| `d08_variance_estimation` | string | Registered standard-error option. |
| `all_option_labels` | JSON string | All four option names in one machine-readable object. |
| `focal_term` | string | Fixed Asian-minus-White PPPCQ contrast label. |

`specification_id` identifies one complete analysis, including its
standard-error method. `point_estimate_id` identifies one of the eight distinct
point estimates; each ID normally appears once with JK1 and once with Taylor
linearization.

### Status

| Column | Type | Meaning |
|---|---|---|
| `status` | string | `success` or `failed`. |
| `failure_category` | string or blank | Failure class for a failed row. |
| `failure_reason` | string or blank | Human-readable explanation for a failed row. |

### Estimates and diagnostics

| Column | Type | Meaning |
|---|---|---|
| `asian_mean` | number | Survey-weighted Asian PPPCQ mean. |
| `asian_mean_se` | number | Standard error of the Asian mean. |
| `asian_mean_ci_low_95` | number | Lower endpoint of the Asian mean's 95% interval. |
| `asian_mean_ci_high_95` | number | Upper endpoint of the Asian mean's 95% interval. |
| `white_mean` | number | Survey-weighted non-Hispanic White PPPCQ mean. |
| `white_mean_se` | number | Standard error of the White mean. |
| `white_mean_ci_low_95` | number | Lower endpoint of the White mean's 95% interval. |
| `white_mean_ci_high_95` | number | Upper endpoint of the White mean's 95% interval. |
| `asian_minus_white_difference` | number | Main Asian mean minus White mean contrast. |
| `standard_error_of_difference` | number | Standard error of the main contrast. |
| `ci_low_95` | number | Lower endpoint of the contrast's 95% interval. |
| `ci_high_95` | number | Upper endpoint of the contrast's 95% interval. |
| `test_statistic` | number | Contrast divided by its standard error. |
| `denominator_degrees_of_freedom` | integer | Registered survey degrees of freedom. |
| `two_sided_p_value` | number | Two-sided p-value for a zero contrast. |
| `unweighted_asian_n` | integer | Number of Asian records contributing to the mean. |
| `unweighted_white_n` | integer | Number of White records contributing to the mean. |
| `weighted_asian_denominator` | number | Sum of final-person weights in the Asian domain. |
| `weighted_white_denominator` | number | Sum of final-person weights in the White domain. |

All estimate fields are blank when `status` is `failed`. Failed rows keep their
registered IDs and choices.

## `run_metadata.json`

The run-level provenance record contains these top-level fields:

| Field | Type | Meaning |
|---|---|---|
| `paper_id` | string | COS paper ID. |
| `registry_revision` | integer | Frozen registry revision. |
| `registry_status` | string | Registry execution status. |
| `registry_sha256` | string | Frozen-registry fingerprint. |
| `scope` | string | `baseline` or `approved`. |
| `executed_at_utc` | timestamp | ISO 8601 execution time in UTC. |
| `source_data_sha256` | string | Source-data fingerprint. |
| `python_version` | string | Python version used for the run. |
| `package_versions` | object | Versions of the direct analysis packages. |
| `git` | object | Commit and clean-worktree status. |
| `ai` | object | Recorded AI system, date, and role. |
| `approval` | object | Approval statuses, dates, record locator, and approved registry hash. |

## `validation.json`

A baseline validation record contains source-structure checks and the fixed
published-result anchors. An approved-run record also contains the number and
status of completed analyses and the number of JK1/Taylor pairs compared.
Point-estimate equality is `verified` only when all eight pairs have identical
group means and contrasts; it is `partially_verified` when some pairs are
available and `not_assessed` when none are available.

## Reviewer-facing reports

An approved run also writes:

- `cell_manifest.csv`, the exact 16-row manifest used for the run;
- `specification_table.md`, the registered 4 by 4 display of all 16
  Asian-minus-White differences and confidence intervals;
- `item_completion_distribution.csv`, with columns
  `d01_analytic_sample`, `group_definition`, `pcc_valid_item_count`,
  `unweighted_n`, `weighted_total`, and `weighted_percent`; and
- `scoring_coverage.csv`, with columns `d01_analytic_sample`,
  `group_definition`, `d03_outcome_construction`, `eligible_unweighted_n`,
  `scored_unweighted_n`, `unweighted_coverage_percent`,
  `eligible_weighted_denominator`, `scored_weighted_denominator`, and
  `weighted_coverage_percent`.

Failed analyses remain visible in the 4 by 4 display with their registered ID
and failure reason. Each complete output set is built in a temporary directory
and moved into place together, so partial output is never presented as a
completed run.
