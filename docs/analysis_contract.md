# Analysis contract

The production code implements `specification_freeze.yaml` revision 7. The
registry, not handwritten control flow, owns the scientific options. Every run
expands the registry into a deterministic 16-row manifest.

## Fixed facts

- The focal quantity is the survey-weighted Asian mean minus the
  non-Hispanic White mean on the 1–4 PPPCQ scale.
- `PERSON_FINWT0` is used for every point estimate.
- Non-Hispanic White is always `RaceEthn5=1`.
- The seven registered communication items, reverse-scoring rule, and no-
  imputation rule are fixed.
- The survey design is built on all 3,504 records before any analytic domain
  is selected.

## Choices that vary

The registry varies who is eligible (d01), how many answered items are required
for PPPCQ (d03), who belongs to the Asian group (d04), and how standard errors
are calculated (d08). The first three choices create eight versions of the
Asian-versus-White comparison. JK1 and Taylor standard errors are calculated for
each version, producing 16 result rows.

## Where each rule lives

- `specification_freeze.yaml` owns option names, baselines, algorithms, and
  required outputs.
- `src/odmk/data.py` owns source validation and derived membership variables.
- `src/odmk/registry.py` owns deterministic cell enumeration and stable IDs.
- `src/odmk/estimators.py` owns the JK1 and Taylor survey formulas.
- `src/odmk/engine.py` owns scope control, estimation, and failed-cell records.
- `src/odmk/validation.py` owns output invariants and baseline anchors.
- `config/execution.yaml` owns operational approval metadata only. It cannot
  change a scientific option.

Other modules read these rules from their authoritative location rather than
guessing them from labels, row order, or prose.

In code, `POINT_ESTIMATE_DIMENSIONS` names d01, d03, and d04 explicitly. The
d08 variance choice is stored separately because it must not change either
weighted group mean or their difference. Point-estimate IDs are therefore
constructed from named dimensions rather than their positions in a row.

## Pre-approval guard

Before COS approval, real HINTS execution is limited to the published baseline
and structural checks. `src/run_multiverse.py` requires all of the
following before it reads the source data:

1. the explicit `--confirm-approved` flag;
2. COS and researcher approval statuses in `config/execution.yaml`;
3. approval dates and a record locator;
4. a recorded SHA-256 matching the unchanged frozen registry; and
5. a clean Git worktree.

Synthetic tests may exercise all 16 cells, but the engine rejects synthetic
scope when it receives the canonical HINTS file hash.

After approval and before any alternative is calculated, the production
runner must pass the frozen published-baseline gates: the focal result, the
2,611-person analytic sample, and all five Table 2 race/ethnicity means. After
execution, each result row must match the corresponding frozen manifest row,
including its specification ID, point-estimate ID, baseline flag, and four
option labels. Inferential fields must be internally consistent with the
recorded estimates, standard errors, and degrees of freedom. Point-estimate
invariance is reported as verified only when both variance cells succeed for
all eight point-estimate constructions.

Both standard-error methods retain all 3,504 source records while calculating
replicate or linearized estimates. True/false membership indicators identify
the records in each analysis. Records outside a focal group contribute zeros
instead of being discarded before the survey calculation.

## Failure policy

Every registered cell is attempted after approval. A failed cell remains in
the result file with a stable ID, category, and diagnostic. Failed cells carry
no focal estimate. The code never substitutes a new population, race rule,
score, or variance method after seeing a failure.

## Output publication

Each run writes its complete file set to a staging directory. The staging
directory replaces the prior destination only after every file is written;
an exception before publication leaves the prior complete output set intact.
The destination must be below the repository's `outputs/` directory. The
runner refuses to replace an existing directory unless its ownership marker
shows that the directory was created by an earlier ODMK run.
