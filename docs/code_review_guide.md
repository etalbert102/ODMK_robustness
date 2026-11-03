# Code review guide and analysis contract

This guide maps the frozen scientific choices to their implementation, tests,
and execution safeguards. The active code is at the repository root; local
submission archives are excluded from version control.

## Fixed contract

`specification_freeze.yaml` revision 7 is the authoritative list of scientific
choices. Every analysis estimates the survey-weighted Asian mean minus the
non-Hispanic White mean on the 1–4 perceived patient-provider communication
quality (PPPCQ) scale. These features never vary:

- seven registered communication items, reverse scoring, and no imputation;
- `PERSON_FINWT0` for every weighted mean;
- non-Hispanic White defined as `RaceEthn5=1`; and
- all 3,504 source records retained while domain indicators identify who
  contributes to each estimate.

The registry varies d01 eligibility, d03 PPPCQ completion, d04 Asian-group
membership, and d08 variance estimation. The first three choices produce eight
point estimates; JK1 and Taylor uncertainty for each produce 16 result rows.
`config/execution.yaml` records approval only and cannot change these choices.

## Suggested review order

1. `specification_freeze.yaml` — fixed features, choices, and required outputs.
2. `src/odmk/registry.py` — validates revision 7 and creates stable IDs.
3. `src/odmk/data.py` — verifies the source and constructs scores and groups.
4. `src/odmk/estimators.py` — implements weighted means, JK1, and Taylor.
5. `src/odmk/engine.py` — runs registered analyses and records failures.
6. `src/odmk/validation.py` — checks baseline and result invariants.
7. `src/odmk/reporting.py` — creates the 4 by 4 display and diagnostics.
8. `src/run_multiverse.py` — enforces approval and production order.
9. `verification/independent_r_baseline.R` — independently checks only the
   published baseline.

## Choice-to-code map

| COS choice | Registered options | Implementation | Main tests |
|---|---|---|---|
| d01 eligible sample | answered content confirms eligibility; recorded visit required | `derive_analysis_fields()` and `cell_arrays()` in `src/odmk/data.py` | `tests/test_data.py` |
| d03 PPPCQ scoring | all 7 valid; at least 4 of 7 valid | `derive_analysis_fields()` and `cell_arrays()` in `src/odmk/data.py` | `tests/test_data.py` |
| d04 Asian group | official `RaceEthn5=4`; non-Hispanic any-Asian identification | `derive_analysis_fields()` and `cell_arrays()` in `src/odmk/data.py` | `tests/test_data.py` |
| d08 standard errors | official 50-weight JK1; Taylor linearization | `estimate_jk1()` and `estimate_taylor()` in `src/odmk/estimators.py` | `tests/test_estimators.py` and `tests/reference/` |

d08 must not change either group mean or their difference. Validation therefore
requires identical point estimates for each successful JK1/Taylor pair.

## Execution safeguards

Before opening real HINTS data, `src/run_multiverse.py` requires:

1. explicit command-line confirmation;
2. COS and researcher approvals, dates, and an approval record;
3. the approved SHA-256 of the unchanged registry; and
4. a clean Git worktree.

Synthetic tests may exercise all 16 paths, but synthetic mode rejects the
canonical HINTS fingerprint. After approval, the production runner validates
the source, reproduces the 2,611-person baseline and all five Table 2 means,
runs the 16 registered rows, and checks every row against its ID and four option
labels. Intervals, tests, and p-values are recalculated from the reported
estimates, standard errors, and degrees of freedom.

## Failure and output policy

A failed registered analysis remains in `results.csv` with its stable ID and
reason and no focal estimate. The program never substitutes a new population,
race rule, score, or variance method after observing a failure. A registry,
approval, source-identity, or validation failure stops the run.

Each complete output set is written to a temporary directory and then moved
into place. The destination must be under `outputs/`, and an existing directory
is replaced only if its marker identifies an earlier ODMK run. Approved output
includes all 16 results, the registered display, and completion and coverage
diagnostics.

## Verification commands

- `make verify-code` checks pinned software, regenerates the manifest, and runs
  all tests without respondent data.
- `make verify-preapproval` also reproduces the registered HINTS baseline.
- `make verify-r-baseline` independently compares 30 R and Python baseline
  counts and statistics; it cannot run an alternative.
- `make multiverse` remains blocked until the approval record is complete and
  its registry fingerprint matches.
