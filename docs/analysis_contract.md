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

## Varied facts

The registry varies d01 eligibility, d03 item-completion scoring, d04 Asian
category construction, and d08 variance estimation. The first three choices
create eight point-estimate constructions. JK1 and Taylor inference are paired
with each, producing 16 cells.

## Fact ownership

- `specification_freeze.yaml` owns option names, baselines, algorithms, and
  required outputs.
- `src/odmk/data.py` owns source validation and derived membership variables.
- `src/odmk/registry.py` owns deterministic cell enumeration and stable IDs.
- `src/odmk/estimators.py` owns the JK1 and Taylor survey formulas.
- `src/odmk/engine.py` owns scope control, estimation, and failed-cell records.
- `src/odmk/validation.py` owns output invariants and baseline anchors.
- `config/execution.yaml` owns operational approval metadata only. It cannot
  change a scientific option.

Downstream code consumes these owners and does not re-derive their facts from
labels, row order, or prose.

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

Both variance paths calculate influence or replicate estimates from the full
3,504-row frame. Analytic membership is represented by Boolean domains, so
records and design units outside a focal group contribute zeros rather than
being discarded before the design calculation.

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
