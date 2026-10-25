# Output schema

`outputs/multiverse/results.csv` contains one row per registered cell after an
approved production run. `manifests/specification_manifest.csv` contains the
same 16 stable cell identities without results and is safe to generate before
approval.

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

## Status and diagnostics

- `status`: `success` or `failed`
- `failure_category`
- `failure_reason`

Failed cells retain their identity and options but have no focal estimates.
Run validation records how many JK1/Taylor pairs were compared and labels
point-estimate invariance as `verified`, `partially_verified`, or
`not_assessed`. The Boolean field is `true` only for complete verification and
is otherwise null.

## Estimates

- Asian and White weighted means, standard errors, and 95% intervals
- Asian-minus-White difference, standard error, 95% interval, test statistic,
  registered denominator degrees of freedom, and two-sided p-value
- unweighted Asian and White counts
- weighted Asian and White denominators

## Provenance

- source-data SHA-256
- frozen-registry SHA-256
- registry revision
- Git commit

Run-level metadata additionally records Python and package versions, AI use,
approval metadata, dirty-worktree state, and the UTC execution time.

The results file is written only by an approved production run. Pre-approval
baseline output uses the same schema but contains only `ODMK-01`. Each complete
file set is staged and published as a directory so partial output is never
presented as a completed run.
