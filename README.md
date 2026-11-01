# ODMK bounded-multiverse analysis

This repository rebuilds the Center for Open Science (COS)-assigned Table 2
comparison from the original 2018 Health Information National Trends Survey
(HINTS 5 Cycle 2) public-use data. The comparison asks whether the weighted mean
rating of patient-provider communication quality (PPPCQ) differs between Asian
and non-Hispanic White respondents. The repository also implements 16
prespecified versions of that comparison. This is a bounded multiverse: a fixed
set of reasonable choices is analyzed in every combination.

The published baseline is reproduced. The full engine has been tested with
synthetic data, but no alternative specification has been run on HINTS data.

## Choose your path

- **Review the concise COS proposal:** open
  [`ODMK_COS_robustness_proposal.docx`](ODMK_COS_robustness_proposal.docx) or
  its editable source, [`ODMK_COS_brief_proposal.md`](ODMK_COS_brief_proposal.md).
- **Review the scientific design:** read [`baseline_analysis.md`](baseline_analysis.md),
  [`dimension_audit.md`](dimension_audit.md), and
  [`reviewer_red_team.md`](reviewer_red_team.md).
- **Review the code:** start with
  [`docs/code_review_guide.md`](docs/code_review_guide.md), then follow its
  design-to-code-and-test map.
- **Reproduce the published baseline:** follow
  [Set up and verify](#set-up-and-verify-the-pre-approval-repository) and
  [`data_access.md`](data_access.md).
- **Run the approved multiverse:** follow
  [Approval-gated production run](#approval-gated-production-run) only after COS
  and researcher approval are recorded.

## Contents

- [Code reviewer quick start](#code-reviewer-quick-start)
- [Quick result](#quick-result)
- [Proposed analysis set](#proposed-analysis-set)
- [Repository artifacts](#repository-artifacts)
- [Authoritative code and directory structure](#which-code-is-authoritative)
- [Set up and verify](#set-up-and-verify-the-pre-approval-repository)
- [Approval-gated production run](#approval-gated-production-run)
- [Troubleshooting](#troubleshooting)
- [Environment files](#environment-files)
- [Source notes](#source-notes)
- [Interpretation guardrails](#interpretation-guardrails)

## Code reviewer quick start

The active implementation is at the repository root; dated directories under
`submission/` are archived snapshots. A short review can follow this order:

1. [`specification_freeze.yaml`](specification_freeze.yaml) defines the four
   frozen choices and their 16 combinations.
2. [`src/odmk/data.py`](src/odmk/data.py) constructs eligibility, PPPCQ scores,
   and the two Asian-group definitions from the source variables.
3. [`src/odmk/estimators.py`](src/odmk/estimators.py) implements the two survey
   standard-error methods.
4. [`src/odmk/engine.py`](src/odmk/engine.py) runs one or all registered
   combinations without changing a failed combination after seeing its result.
5. [`src/run_multiverse.py`](src/run_multiverse.py) enforces approval and
   baseline checks before any alternative can run.

[`docs/code_review_guide.md`](docs/code_review_guide.md) maps every frozen
choice to its implementation and tests. The single command `make verify-code`
checks the environment, regenerates the 16-row manifest, and runs the test suite
without using respondent data.

Four terms recur in the code and documentation:

- **registry:** the frozen YAML file that records the approved choices;
- **manifest:** the generated 16-row table listing one choice combination per
  row;
- **analysis or cell:** one row of that manifest and its result; and
- **baseline:** the choice combination that most closely reproduces Table 2.

## Quick result

Using all seven communication items, official `RaceEthn5`, the final-person
weight, and 50 delete-one jackknife (JK1) replicate weights gives `N = 2,611`
across the five published race/ethnicity groups. The reconstructed
non-Hispanic Asian mean is 3.1161 and the non-Hispanic White mean is 3.4457,
closely reproducing the article's displayed 3.11 and 3.45. Their derived direct
difference is −0.3296 (SE 0.1097; 95% CI −0.5502 to −0.1091).

The COS sourcing sheet assigns the Table 2 means and confidence intervals.
Table 3 Model 1 is not the assigned result and is not part of registry revision
7.

## Proposed analysis set

Four choices with two options each yield 16 analyses. The labels d01, d03, d04,
and d08 come from the COS robustness framework. The first three choices produce
eight versions of the Asian-versus-White comparison; the final choice calculates
the uncertainty around each comparison in two accepted ways:

- **d01 eligible sample:** include people whose answers show that they reached
  the communication questions, or require a recorded provider visit;
- **d03 PPPCQ scoring:** require all seven communication items, or require at
  least four;
- **d04 Asian-group definition:** use the official mutually exclusive category,
  or include any non-Hispanic respondent who selected an Asian identity; and
- **d08 standard errors:** use the official JK1 replicate weights, or Taylor
  linearization based on the released strata and clusters.

Every analysis keeps the same seven communication topics, 1–4 score, White
comparison group, final population weight (`PERSON_FINWT0`), national target
population, and Asian-minus-White direction.

COS asks analysts to consider about five dimensions, but does not require five.
A fifth is not added here because the remaining candidates would change the
question or target population, repeat an included choice, or add assumptions
that are not well supported for this measure.

## Repository artifacts

### COS submission and preregistration

- [`ODMK_COS_robustness_proposal.docx`](ODMK_COS_robustness_proposal.docx) — primary concise COS submission file.
- [`ODMK_COS_brief_proposal.md`](ODMK_COS_brief_proposal.md) — editable Markdown source for the concise submission.
- [`ODMK_COS_submission.md`](ODMK_COS_submission.md) — main Markdown source for the longer methodological record.
- [`ODMK_robustness_proposal.md`](ODMK_robustness_proposal.md) — byte-identical compatibility copy retained under the originally requested filename.
- [`ODMK_robustness_proposal.docx`](ODMK_robustness_proposal.docx) — formatted copy of the longer methodological record.
- [`ODMK_preregistration.docx`](ODMK_preregistration.docx) — completed COS preregistration draft for the post-proposal review workflow.
- [`preregistration_template.docx`](preregistration_template.docx) — unfilled source template retained to document its origin.

### Scientific record

- [`baseline_analysis.md`](baseline_analysis.md) — assigned result, reconstruction, source inferences, and unresolved ambiguities.
- [`data_access.md`](data_access.md) — public acquisition instructions and checksums.
- [`dimension_audit.md`](dimension_audit.md) — d01–d09 audit.
- [`reviewer_red_team.md`](reviewer_red_team.md) — skeptical review of the revised design.
- [`DAAF_review.md`](DAAF_review.md) — improvements adopted after review against DAAF 3.0.2.

### Implementation and provenance

- [`specification_freeze.yaml`](specification_freeze.yaml) — revision 7 machine-readable registry.
- [`src/odmk/`](src/odmk/) — reusable Python package implementing data construction, both survey estimators, execution gates, and validation.
- [`src/run_registered_baseline.py`](src/run_registered_baseline.py) — baseline-only entry point through the registered package.
- [`src/run_multiverse.py`](src/run_multiverse.py) — approval-gated entry point for all 16 registered cells.
- [`manifests/specification_manifest.csv`](manifests/specification_manifest.csv) — repeatable 16-row analysis list.
- [`docs/analysis_contract.md`](docs/analysis_contract.md) — ownership rules and execution boundary.
- [`docs/survey_estimators.md`](docs/survey_estimators.md) — exact JK1 and Taylor formulas.
- [`docs/output_schema.md`](docs/output_schema.md) — exact result, metadata, and reviewer-report fields.
- [`sources/source_manifest.csv`](sources/source_manifest.csv) — source URLs, history, and checksums.

## Which code is authoritative?

The registered production path is:

```text
specification_freeze.yaml
        ↓
src/odmk/registry.py ──→ repeatable 16-row analysis list
        ↓
src/odmk/data.py ──→ scores, eligibility, and comparison groups
        ↓
src/odmk/engine.py ──→ src/odmk/estimators.py
        ↓
src/odmk/validation.py ──→ results and validation records
```

`src/run_registered_baseline.py` runs only the registered baseline through that
path. `src/run_multiverse.py` is the approval-gated entry point for all 16
cells. There is no second executable implementation: the frozen registry and
`src/odmk/` own all active analysis behavior.

## Directory structure

```text
ODMK_robustness/
├── data_raw/          # ignored by Git; unmodified public-use respondent file
├── docs/              # implementation contract and estimator documentation
├── manifests/         # generated 16-row analysis list
├── outputs/           # documented legacy QA plus generated baseline/results directories
├── sources/           # primary documents, source ledger, and search-aid text
├── src/odmk/          # reusable analysis package
├── tests/             # synthetic unit tests and optional real-baseline test
├── submission/        # finalized submission package and checksum
├── config/execution.yaml
├── pyproject.toml
├── Makefile
├── ODMK_COS_submission.md
├── baseline_analysis.md
├── data_access.md
├── dimension_audit.md
├── reviewer_red_team.md
└── specification_freeze.yaml
```

## Set up and verify the pre-approval repository

### Prerequisites

Use a POSIX-style shell with Git, Make, and Python 3.14.4. The registered checks
reject a different Python version. `curl`, `unzip`, and either `shasum` or
`sha256sum` are needed only to reacquire and verify the public data. From this
directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
make setup
make verify-code
```

`make verify-code` needs no respondent data. It checks the exact software
versions, regenerates the same 16-row analysis list, and runs the synthetic and
repository tests. A successful run reports that every test passed and total
branch-aware coverage is at least 80%. To run the baseline and structural
checks, first follow the acquisition steps in
[`data_access.md`](data_access.md) so that the unmodified file is at
`data_raw/hints5_cycle2_public.dta`, then run:

```bash
make verify-preapproval
```

The full command repeats the code checks and runs the registered baseline. It
checks the source-file structure, expected sample counts, survey design, assigned
comparison, and all five published Table 2 means before writing the baseline
output files. The optional real-data test is skipped when the
public-use file is absent, but the `baseline` Make target requires it;
therefore `make verify-preapproval` is intentionally a data-required command.

Continuous integration runs two sets of checks. The first uses synthetic data
and enforces the coverage threshold. It also checks active Markdown links,
basic Markdown hygiene, output-schema completeness, and the documented baseline
values. The second downloads the public NCI data, verifies both file checksums,
runs the same baseline command a researcher would run, checks its three output
files, and requires the real-data baseline test to complete. Third-party GitHub
actions are pinned to full commit hashes.

The baseline checks verify the exact data-file fingerprint, 3,504 source rows,
unique and present `HHID` values, stable sorting, required fields, 50 replicate
weights, valid weights, PPPCQ range, exact `RaceEthn5` counts, the 2,611-person
analysis sample, all five published Table 2 means, and the JK1 standard error.

The registered baseline verifies registry revision 7, all 16 combinations of
the four choices, the expected sample and scoring counts, both Asian-group
definitions, nonoverlapping Asian and White groups, and the survey design. It
does not calculate an alternative group mean or difference. Eligibility and
racial-group membership are applied while retaining the complete source file,
as required for correct survey standard errors.

## Approval-gated production run

Python implements both registered standard-error methods directly. Exact versions
are pinned in `pyproject.toml` and `requirements_multiverse.txt`. Before a
production run:

1. record COS and researcher approval in `config/execution.yaml`;
2. calculate the unchanged registry fingerprint with the following command and
   record its output as `approved_registry_sha256` in that file:

   ```bash
   python3 -c 'from pathlib import Path; import hashlib; print(hashlib.sha256(Path("specification_freeze.yaml").read_bytes()).hexdigest())'
   ```

3. commit the approval configuration so the worktree is clean; and
4. run `make multiverse`.

The command refuses to open the source data unless the approval record, approved
registry fingerprint, explicit confirmation flag, and clean-Git check all pass.
The scientific registry remains unchanged after
approval. Before the command calculates any alternative, it must reproduce the
frozen baseline,
`N = 2,611`, and all five published Table 2 group means. It then writes all 16
registered analyses, including a row and explanation for any failure, under
`outputs/multiverse/`. The same output set includes the registered 4 by 4
specification display and the item-completion and scoring-coverage diagnostics.
Final validation also requires every result row to
match its prespecified ID and options exactly. All output files are
built in a temporary directory and moved into place together, so an interrupted
write cannot mix files from different runs. Output destinations must be inside
this repository's `outputs/` directory. The runner replaces an existing
directory only when a marker confirms that an earlier ODMK run created it.

The complete engine is tested on synthetic data using the real environment,
approval, clean-Git, registry-checksum, run-record, and output-writing code.
Only the real-data reader and real-data baseline checks are replaced. Synthetic
mode refuses the canonical HINTS file hash, so it cannot bypass the approval
gate for real data. Independent examples generated with R `survey` 4.5 verify
both standard-error implementations.

## Troubleshooting

- **The environment check rejects Python or a package.** Confirm that
  `python3 --version` reports 3.14.4, reactivate `.venv`, and rerun `make setup`.
- **The baseline cannot find the data.** Confirm that the unmodified file is
  `data_raw/hints5_cycle2_public.dta`; then follow the checksum instructions in
  [`data_access.md`](data_access.md).
- **The source-data fingerprint fails.** Remove the incorrect local download,
  reacquire the canonical bundle, and verify both checksums. Do not bypass the
  fingerprint check.
- **The multiverse remains blocked.** Confirm that both approval statuses,
  dates, the COS approval record, and `approved_registry_sha256` are filled in
  under `approval` in `config/execution.yaml`. Then commit that file and confirm
  that `git status --short` prints nothing.
- **The approved registry fingerprint fails.** Recalculate the fingerprint from
  the unchanged `specification_freeze.yaml`. If the registry changed after
  approval, stop and obtain approval for the changed registry rather than
  replacing the recorded fingerprint.
- **A registered analysis fails after execution begins.** Do not change its
  choices. The runner preserves the registered ID and failure reason in
  `results.csv`; see [`docs/analysis_contract.md`](docs/analysis_contract.md).

## Environment files

- `requirements-lock.txt` is the complete reproducible installation lock used
  by `make setup` and continuous integration.
- `pyproject.toml` declares the installable package and its direct runtime
  dependencies.
- `requirements.txt` is the minimal direct runtime dependency list for tools
  that expect that conventional filename.
- `requirements_multiverse.txt` is the human-readable direct analysis and test
  environment retained with the preregistration materials.
- `src/odmk/environment.py` enforces the frozen Python and direct-package
  versions before an approved production run.

The repeated direct versions are deliberate reviewable assertions. When an
environment changes, update all five records together and rerun the tests; do
not edit only one file.

## Source notes

The public HINTS bundle, COS sheet and guidance, and COS-linked article are archived or recorded in `sources/`. The current HINTS release is dated 2024-05-07. No public author analysis code or supplementary analysis file was located. See [`sources/README.md`](sources/README.md).

The directories under `submission/` are immutable submission snapshots and
contain duplicated copies by design. Review the active implementation at the
repository root and in `src/odmk/`, not the copies inside those archives.

## Interpretation guardrails

- This is a descriptive population disparity, not a causal effect of race.
- The two Asian definitions are category-construction choices, not interventions on identity.
- The aggregate Asian category cannot support national-origin, migration, or language subgroup claims.
- Peer alternatives are not corrections to the paper.
- Robustness is not reduced to whether `p < .05`.
- No alternative can be added, removed, or revised after seeing its estimate.
- Every unresolved author choice remains labeled as unresolved.
