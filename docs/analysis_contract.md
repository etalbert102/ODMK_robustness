# Analysis contract

The production code implements `specification_freeze.yaml` revision 7. This
frozen registry is the authoritative list of scientific choices. The program
turns it into the same 16-row analysis list every time; each row contains one
combination of choices.

## Fixed facts

- The main result is the survey-weighted Asian mean minus the
  non-Hispanic White mean on the 1–4 PPPCQ scale.
- `PERSON_FINWT0` is used to calculate every weighted mean.
- Non-Hispanic White is always `RaceEthn5=1`.
- The seven registered communication items, reverse-scoring rule, and no-
  imputation rule are fixed.
- All 3,504 records are retained while the program identifies which records
  belong to each analysis. This preserves the full survey design.

## Choices that vary

The registry varies who is eligible (d01), how many answered items are required
for PPPCQ (d03), who belongs to the Asian group (d04), and how standard errors
are calculated (d08). The first three choices create eight versions of the
Asian-versus-White comparison. JK1 and Taylor standard errors are calculated for
each version, producing 16 result rows.

## Where each rule lives

- `specification_freeze.yaml` defines option names, baselines, algorithms, and
  required outputs.
- `src/odmk/data.py` checks the source and creates scores and group membership.
- `src/odmk/registry.py` creates the 16 analysis rows and stable IDs.
- `src/odmk/estimators.py` implements the JK1 and Taylor survey formulas.
- `src/odmk/engine.py` controls which analyses may run and records failures.
- `src/odmk/validation.py` checks outputs and the reproduced baseline values.
- `config/execution.yaml` records operational approval information only. It cannot
  change a scientific option.

Other modules read these rules from their authoritative location rather than
guessing them from labels, row order, or prose.

Before respondent data are opened, the registry loader also requires the exact
revision-7 option names, each dimension's published-baseline choice, and the
complete four-part baseline cell. A changed alternative cannot be relabeled as
the baseline-only analysis.

In code, `POINT_ESTIMATE_DIMENSIONS` names d01, d03, and d04 explicitly. The
d08 standard-error choice is stored separately because it must not change
either weighted group mean or their difference. The ID for each comparison is
built from the three named choices rather than their positions in a row.

## Pre-approval guard

Before COS approval, real HINTS execution is limited to the published baseline
and structural checks. `src/run_multiverse.py` requires all of the
following before it reads the source data:

1. the explicit `--confirm-approved` flag;
2. COS and researcher approval statuses in `config/execution.yaml`;
3. approval dates and a record locator;
4. a recorded SHA-256 matching the unchanged frozen registry; and
5. a clean Git worktree.

Synthetic tests may exercise all 16 analyses, but the engine rejects synthetic
mode when it receives the real HINTS file fingerprint.

After approval and before any alternative is calculated, the production
runner must reproduce the main result, the 2,611-person sample, and all five
Table 2 race/ethnicity means. After execution, each result row must match its
prespecified ID and four option labels. Confidence intervals, test statistics,
and p-values must agree with the reported estimates, standard errors, and
degrees of freedom. The program reports that point estimates are unchanged by
the standard-error method only when both methods succeed for all eight
comparisons.

Both standard-error methods retain all 3,504 source records while calculating
replicate or linearized estimates. True/false membership indicators identify
the records in each analysis. Records outside a comparison group contribute zeros
instead of being discarded before the survey calculation.

## Failure policy

Every registered analysis is attempted after approval. A failed analysis
remains in the result file with its stable ID and an explanation. It carries no
main estimate. The code never substitutes a new population, race rule, score,
or standard-error method after seeing a failure.

## Output publication

Each run first writes its complete file set to a temporary directory. It
replaces the prior output only after every file is written. If writing fails,
the earlier complete output remains intact.
An approved run includes the 16-row results, the 4 by 4 specification display,
and the item-completion and scoring-coverage diagnostics promised in the
proposal.
The destination must be below the repository's `outputs/` directory. The
runner refuses to replace an existing directory unless its ownership marker
shows that the directory was created by an earlier ODMK run.
