# ODMK bounded-multiverse analysis

This repository reconstructs the COS-assigned Table 2 racial/ethnic difference in perceived patient-provider communication quality (PPPCQ) from the original 2018 HINTS 5 Cycle 2 public-use file. It also implements the proposed 16-specification robustness design for the Asian-versus-non-Hispanic-White weighted mean comparison.

The published baseline is reproduced. The full engine has been tested with
synthetic data, but no alternative specification has been run on HINTS data.

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

## Quick result

Using all seven communication items, official `RaceEthn5`, the final-person weight, and 50 JK1 replicate weights gives `N = 2,611` across the five published race/ethnicity groups. The reconstructed non-Hispanic Asian mean is 3.1161 and the non-Hispanic White mean is 3.4457, reproducing the article's displayed 3.11 and 3.45. Their derived direct difference is −0.3296 (SE 0.1097; 95% CI −0.5502 to −0.1091).

The COS sourcing sheet assigns the Table 2 means and confidence intervals. Table 3 Model 1 is not the focal result and is not part of registry revision 7.

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
  linearization.

Fixed features include the seven communication domains, the 1–4 outcome scale, the non-Hispanic White reference, `PERSON_FINWT0` point weighting, the national population target, and the Asian-minus-White direction.

COS treats five dimensions as a target, not a quota. A fifth is not added because covariate adjustment, alternative outcome models, and unweighted analysis would change the Table 2 estimand or population; equivalent weighted regression would be cosmetic; and item-level imputation would overlap d03 while adding weakly anchored assumptions.

## Deliverables

- [`ODMK_COS_robustness_proposal.docx`](ODMK_COS_robustness_proposal.docx) — primary concise COS submission file.
- [`ODMK_COS_brief_proposal.md`](ODMK_COS_brief_proposal.md) — editable Markdown source for the concise submission.
- [`ODMK_COS_submission.md`](ODMK_COS_submission.md) — longer methodological record.
- [`ODMK_robustness_proposal.md`](ODMK_robustness_proposal.md) — identical longer record retained under the originally requested filename.
- [`baseline_analysis.md`](baseline_analysis.md) — focal result, reconstruction, source inferences, and unresolved ambiguities.
- [`data_access.md`](data_access.md) — public acquisition instructions and checksums.
- [`dimension_audit.md`](dimension_audit.md) — d01–d09 audit.
- [`reviewer_red_team.md`](reviewer_red_team.md) — skeptical review of the revised design.
- [`DAAF_review.md`](DAAF_review.md) — improvements adopted after review against DAAF 3.0.2.
- [`specification_freeze.yaml`](specification_freeze.yaml) — revision 7 machine-readable registry.
- [`src/odmk/`](src/odmk/) — reusable Python package implementing data construction, both survey estimators, execution gates, and validation.
- [`src/run_registered_baseline.py`](src/run_registered_baseline.py) — baseline-only entry point through the registered package.
- [`src/run_multiverse.py`](src/run_multiverse.py) — approval-gated entry point for all 16 registered cells.
- [`manifests/specification_manifest.csv`](manifests/specification_manifest.csv) — deterministic 16-cell manifest.
- [`docs/analysis_contract.md`](docs/analysis_contract.md) — ownership rules and execution boundary.
- [`docs/survey_estimators.md`](docs/survey_estimators.md) — exact JK1 and Taylor formulas.
- [`sources/source_manifest.csv`](sources/source_manifest.csv) — source URLs, provenance, and checksums.

## Which code is authoritative?

The registered production path is:

```text
specification_freeze.yaml
        ↓
src/odmk/registry.py ──→ deterministic 16-cell manifest
        ↓
src/odmk/data.py ──→ registered variables and analytic domains
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
├── manifests/         # generated, deterministic specification manifest
├── outputs/           # baseline QA and, after approval, multiverse results
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

Python 3.14.4 was used for the archived baseline run. From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
make setup
make verify-code
```

`make verify-code` needs no respondent data: it checks the pinned environment,
generates the deterministic manifest, and runs the synthetic and repository
tests. The test target enforces at least 80% branch-aware coverage across the
active analysis package and production runner. To run the baseline and
structural checks, first follow the acquisition steps in
[`data_access.md`](data_access.md) so that the unmodified file is at
`data_raw/hints5_cycle2_public.dta`, then run:

```bash
make verify-preapproval
```

The full command repeats the code checks and runs the registered baseline. That
run validates the source structure, frozen membership anchors, complete survey
design, focal result, and all five published Table 2 means before publishing a
baseline artifact set. The optional real-data pytest is skipped when the
public-use file is absent, but the `baseline` Make target requires it;
therefore `make verify-preapproval` is intentionally a data-required command.

Continuous integration runs two sets of checks. The first uses synthetic data
and enforces the coverage threshold. The second downloads the public NCI data,
verifies both file checksums, runs the same baseline command a researcher would
run, checks its three output files, and requires the real-data baseline test to
complete. Third-party GitHub actions are pinned to full commit hashes.

The baseline checks verify the canonical data SHA-256, 3,504 source rows,
unique/nonmissing `HHID`, deterministic sorting, required fields, 50 replicate
weights, weight validity, PPPCQ range, exact `RaceEthn5` frequencies, focal
`N = 2,611`, all five published Table 2 means, and the focal JK1 uncertainty.

The registered baseline verifies registry revision 7, all 16 combinations of
the four choices, the expected sample and scoring counts, both Asian-group
definitions, nonoverlapping Asian and White groups, and the survey design. It
does not calculate an alternative group mean or difference. Eligibility and
racial-group membership are applied while retaining the complete source file,
as required for correct survey standard errors.

## Approval-gated production run

Python implements both registered variance choices directly. Exact versions
are pinned in `pyproject.toml` and `requirements_multiverse.txt`. Before a
production run:

1. record COS and researcher approval in `config/execution.yaml`;
2. record the unchanged `specification_freeze.yaml` SHA-256 as
   `approved_registry_sha256` in that file;
3. commit the approval configuration so the worktree is clean; and
4. run `make multiverse`.

The command refuses to open the source data unless approval metadata, the
approved registry checksum, the explicit confirmation flag, and the
clean-worktree check all pass. The scientific registry remains unchanged after
approval. Before the command calculates any alternative, it must reproduce the
frozen focal baseline,
`N = 2,611`, and all five published Table 2 group means. It then writes all 16
registered cells, including explicit records for any failed cell, under
`outputs/multiverse/`. Final validation also requires every result row to
match its frozen manifest identity and options exactly. All output files are
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
