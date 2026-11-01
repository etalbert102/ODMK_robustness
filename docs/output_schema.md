# Output file fields

After an approved run, `outputs/multiverse/results.csv` contains one row for each
of the 16 prespecified analyses. `manifests/specification_manifest.csv` lists
the same 16 IDs and choices without any results, so it is safe to generate
before approval.

## Identity and options

- `paper_id`
- `specification_id` (`ODMK-01` through `ODMK-16`)
- `is_baseline`
- `registry_revision`
- `source_data_sha256`
- `point_estimate_id`
- one column for each of d01, d03, d04, and d08
- `all_option_labels`, a machine-readable JSON object
- `focal_term`

`specification_id` identifies one complete analysis, including its
standard-error method. `point_estimate_id` groups the two rows that use the same
sample, PPPCQ score, and Asian-group definition but different standard-error
methods.

## Status and diagnostics

- `status`: `success` or `failed`
- `failure_category`
- `failure_reason`

Failed analyses retain their ID and choices but have no main estimates. The
validation file records how many JK1/Taylor pairs could be compared. It reports
that point estimates are unchanged only when every comparable pair has the same
means and Asian-minus-White difference. The status field is `verified` when all
eight pairs are checked, `partially_verified` when some are checked, and
`not_assessed` when none can be checked. Its companion Boolean field is `true`
only for complete verification and is otherwise null.

## Estimates

- Asian and White weighted means, standard errors, and 95% intervals
- Asian-minus-White difference, standard error, 95% interval, test statistic,
  registered denominator degrees of freedom, and two-sided p-value
- unweighted Asian and White counts
- sums of the analysis weights for the Asian and White groups

## Run record

- source-data SHA-256
- frozen-registry SHA-256
- registry revision
- Git commit

The run-level record also includes Python and package versions, AI use, approval
information, whether Git had uncommitted changes, and the UTC execution time.

The results file is written only by an approved production run. Pre-approval
baseline output uses the same fields but contains only `ODMK-01`. Each complete
file set is written in a temporary directory and moved into place together, so
partial output is never presented as a completed run.
