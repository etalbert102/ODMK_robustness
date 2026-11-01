# Code review guide

This guide shows where each frozen analysis choice is implemented and tested.
It describes the active files at the repository root, not the dated submission
snapshots.

## What the program does

The program reconstructs the published Table 2 comparison, then—only after
Center for Open Science (COS) and researcher approval—runs the 16 combinations
defined in `specification_freeze.yaml`. The outcome is always the 1–4 perceived
patient-provider communication quality (PPPCQ) score, and the reported
difference is always the weighted Asian mean minus the weighted non-Hispanic
White mean.

Before approval, real Health Information National Trends Survey (HINTS) data
may be used only to reproduce the published baseline and check that the required
variables and survey structure are present. Made-up test data exercise all 16
code paths without producing robustness results from HINTS.

## Suggested review order

1. `specification_freeze.yaml` — scientific choices and fixed features.
2. `src/odmk/registry.py` — checks the registry and creates the same 16 rows
   every time.
3. `src/odmk/data.py` — source checks and construction of scores and groups.
4. `src/odmk/estimators.py` — weighted means, JK1, and Taylor formulas.
5. `src/odmk/engine.py` — runs one analysis and controls which analyses are
   allowed before and after approval.
6. `src/odmk/validation.py` — checks the reproduced baseline and result files.
7. `src/odmk/reporting.py` — creates the registered 4 by 4 display and coverage
   diagnostics.
8. `src/run_multiverse.py` — approval gates and end-to-end production order.
9. `verification/independent_r_baseline.R` — separate, baseline-only
   reconstruction used to cross-check the Python result.

## Frozen choices and their implementations

| COS choice | Options in the registry | Implemented in | Main tests |
|---|---|---|---|
| d01 eligible sample | answered communication content can confirm eligibility; recorded provider visit required | `derive_analysis_fields()` and `cell_arrays()` in `src/odmk/data.py` | `tests/test_data.py` |
| d03 PPPCQ scoring | all 7 items required; at least 4 of 7 required | `derive_analysis_fields()` and `cell_arrays()` in `src/odmk/data.py` | `tests/test_data.py` |
| d04 Asian-group definition | official `RaceEthn5=4`; non-Hispanic any-Asian identification | `derive_analysis_fields()` and `cell_arrays()` in `src/odmk/data.py` | `tests/test_data.py` |
| d08 standard errors | official 50-weight JK1; Taylor linearization | `estimate_jk1()` and `estimate_taylor()` in `src/odmk/estimators.py` | `tests/test_estimators.py` and `tests/reference/` |

The first three choices determine who contributes to each weighted mean. They
produce eight versions of the same Asian-versus-White comparison. The d08 choice
changes only the standard error and confidence interval, so the code verifies
that each JK1/Taylor pair has identical means and differences.

## End-to-end execution order

`src/run_multiverse.py` performs these steps in order:

1. fingerprint and check the frozen registry;
2. verify the exact Python environment;
3. require recorded COS and researcher approval, explicit command-line
   confirmation, the approved registry fingerprint, and no uncommitted changes;
4. read and validate the exact public HINTS file;
5. reproduce the registered baseline and all five published Table 2 means;
6. run all 16 registered combinations;
7. check every result against the prespecified 16-row analysis list; and
8. create the registered display and completion/coverage reports; and
9. write the complete result set and run record together.

The approval checks occur before the source data are opened. The baseline checks
occur before any alternative comparison is calculated.

## Failure behavior

An expected calculation failure remains in `results.csv` with its registered ID
and a reason. The program does not replace it with another sample, score, group
definition, or standard-error method. A problem with the registry, approval,
source identity, or result checks stops the run because it no longer matches the
prespecified analysis.

## Verification commands

- `make verify-code` checks the software versions, regenerates the 16-row
  analysis list, and runs all tests without respondent data.
- `make verify-preapproval` additionally reproduces the single registered
  baseline from the locally acquired public HINTS file.
- `make verify-r-baseline` independently reconstructs that published baseline
  from the Stata file with R `survey` and compares 30 counts and statistics with
  Python. It cannot run a robustness alternative.
- `make multiverse` remains blocked until the approval record is complete and
  the approved registry hash is recorded.

The ordinary test suite uses synthetic data. The real-data test and baseline
command calculate only the already-published baseline.
