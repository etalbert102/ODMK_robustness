# Code review guide

This guide traces the frozen analysis choices from the registry to the code and
tests. It describes the active files at the repository root, not the dated
submission snapshots.

## What the program does

The program reconstructs the published Table 2 comparison, then—only after COS
and researcher approval—runs the 16 combinations defined in
`specification_freeze.yaml`. The outcome is always the 1–4 PPPCQ score, and the
reported difference is always the weighted Asian mean minus the weighted
non-Hispanic White mean.

Before approval, real HINTS data may be used only for the published baseline and
structural checks. Synthetic data exercise all 16 code paths without producing
robustness results from HINTS.

## Suggested review order

1. `specification_freeze.yaml` — scientific choices and fixed features.
2. `src/odmk/registry.py` — validation and deterministic expansion to 16 rows.
3. `src/odmk/data.py` — source checks and construction of scores and groups.
4. `src/odmk/estimators.py` — weighted means, JK1, and Taylor formulas.
5. `src/odmk/engine.py` — one-cell estimation and permitted execution scopes.
6. `src/odmk/validation.py` — baseline anchors and result consistency checks.
7. `src/run_multiverse.py` — approval gates and end-to-end production order.

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

1. hash and validate the frozen registry;
2. verify the exact Python environment;
3. require recorded COS and researcher approval, explicit command-line
   confirmation, the approved registry hash, and a clean Git worktree;
4. read and validate the exact public HINTS file;
5. reproduce the registered baseline and all five published Table 2 means;
6. run all 16 registered combinations;
7. validate every result against the frozen manifest; and
8. write the complete result set and run record together.

The approval checks occur before the source data are opened. The baseline checks
occur before any alternative comparison is calculated.

## Failure behavior

An expected estimation failure remains in `results.csv` with its registered ID
and a reason. The program does not replace it with another sample, score, group
definition, or standard-error method. A registry, approval, provenance, or
validation failure stops the run because the requested analysis contract is no
longer satisfied.

## Verification commands

- `make verify-code` checks the environment, regenerates the manifest, and runs
  all tests without respondent data.
- `make verify-preapproval` additionally reproduces the single registered
  baseline from the locally acquired public HINTS file.
- `make multiverse` remains blocked until the approval record is complete and
  the approved registry hash is recorded.

The ordinary test suite uses synthetic data. The real-data test and baseline
command calculate only the already-published baseline.
