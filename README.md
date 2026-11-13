# ODMK bounded-multiverse analysis

This repository reconstructs the Center for Open Science (COS)-assigned Table 2
comparison from the 2018 Health Information National Trends Survey (HINTS 5
Cycle 2). It compares survey-weighted patient-provider communication quality
(PPPCQ) means for Asian and non-Hispanic White respondents across 16
prespecified analyses.

The published baseline and all 16 approved specifications were run on
2026-11-13. Every specification estimated lower PPPCQ among Asian respondents;
the Asian-minus-White difference ranged from −0.3511 to −0.2797.

## Choose your path

- **COS proposal:**
  [`ODMK_COS_robustness_proposal.docx`](ODMK_COS_robustness_proposal.docx) and
  its editable [`Markdown source`](ODMK_COS_brief_proposal.md); the
  [`extended record`](ODMK_robustness_proposal.md) preserves additional detail.
- **Preregistration:** [`ODMK_preregistration.docx`](ODMK_preregistration.docx).
- **Final results:** [`COS-format results`](submission/results_ODMK.csv),
  [`outcome report`](submission/ODMK_robustness_analysis_report.docx), and
  [`native run outputs`](outputs/multiverse/).
- **Scientific design:** [`baseline_analysis.md`](baseline_analysis.md),
  [`dimension_audit.md`](dimension_audit.md), and
  [`reviewer_red_team.md`](reviewer_red_team.md).
- **Code review:** [`docs/code_review_guide.md`](docs/code_review_guide.md).
- **Data acquisition:** [`data_access.md`](data_access.md).
- **Independent R check:** [R baseline verification](#independent-r-baseline-verification).

## Study at a glance

The baseline requires all seven communication items, uses official
`RaceEthn5`, `PERSON_FINWT0`, and 50 delete-one jackknife (JK1) replicate
weights. It gives `N = 2,611`, an Asian mean of 3.1161, a non-Hispanic White
mean of 3.4457, and a derived Asian-minus-White difference of −0.3296 (SE
0.1097; 95% CI −0.5502 to −0.1091). The `N` includes all five published
racial/ethnic groups. The article displays the group means; the direct
difference is a reconstructed reporting quantity.

Four binary choices produce 16 analyses:

| COS dimension | Baseline | Alternative |
|---|---|---|
| d01 eligible sample | answered communication content can confirm eligibility | recorded provider visit required |
| d03 PPPCQ scoring | all 7 items required | at least 4 of 7 required |
| d04 Asian-group definition | official mutually exclusive category | non-Hispanic any-Asian identification |
| d08 standard errors | official JK1 replicate weights | Taylor linearization |

The communication domains, 1–4 scale, non-Hispanic White group, final
population weight, target population, and contrast direction remain fixed. A
fifth dimension is not added because the remaining candidates would change the
question or population, duplicate an included choice, or require weakly
supported assumptions.

## Authoritative files

`specification_freeze.yaml` revision 7 owns the scientific choices. The active
production path is:

```text
specification_freeze.yaml
        ↓
src/odmk/registry.py ──→ 16-row manifest
        ↓
src/odmk/data.py ──→ scores, eligibility, and groups
        ↓
src/odmk/engine.py ──→ src/odmk/estimators.py
        ↓
src/odmk/validation.py ──→ checked results and records
        ↓
src/odmk/cos_reporting.py ──→ COS 29-column submission CSV
```

Key supporting files are:

- `manifests/specification_manifest.csv` — generated IDs and choices;
- `docs/survey_estimators.md` — JK1 and Taylor formulas;
- `docs/output_schema.md` — result and metadata fields;
- `verification/independent_r_baseline.R` — baseline-only cross-language check;
- `sources/source_manifest.csv` — source URLs and checksums; and
- `config/execution.yaml` — operational approvals only; it cannot change an
  analysis choice.

The frozen registry and `src/odmk/` are the only multiverse implementation. The
R script reconstructs only the published baseline. The final report and
aggregate result files are committed for review. Raw HINTS records, expanded
submission archives, and local render files remain outside the repository.

## Set up and verify

Use a POSIX-style shell, Git, Make, and Python 3.14.4. `curl`, `unzip`, and
`shasum` or `sha256sum` are needed only to reacquire the public data.

```bash
python3 -m venv .venv
source .venv/bin/activate
make setup
make verify-code
```

`make verify-code` checks the pinned environment, regenerates the manifest, and
runs all synthetic and repository tests without respondent data.

To reproduce the published baseline, acquire the canonical file as described
in [`data_access.md`](data_access.md), place it at
`data_raw/hints5_cycle2_public.dta`, and run:

```bash
make verify-preapproval
```

This command repeats the code checks, verifies the source identity and survey
structure, and reproduces the assigned sample and all five Table 2 group means.
It calculates no robustness alternative.

## Independent R baseline verification

A separate baseline-only implementation reads the Stata file directly and
rebuilds the baseline with R `survey`. It neither imports Python-derived fields
nor implements an alternative specification.

```bash
make verify-r-baseline
```

The audit compares 30 counts and statistics. Requirements and output files are
documented in [`verification/README.md`](verification/README.md). Continuous
integration separately runs the synthetic suite, canonical Python baseline,
real-data test, and R comparison.

## Approval-gated production run

Before a real multiverse run:

1. record COS and researcher approval statuses and dates, plus the COS approval
   record, in `config/execution.yaml`;
2. calculate the registry fingerprint and save it as
   `approved_registry_sha256`:

   ```bash
   python3 -c 'from pathlib import Path; import hashlib; print(hashlib.sha256(Path("specification_freeze.yaml").read_bytes()).hexdigest())'
   ```

3. commit the approval record so the worktree is clean; and
4. run `make multiverse`.

The runner refuses to open HINTS data unless approval, fingerprint, explicit
confirmation, and clean-worktree checks pass. It then reproduces the frozen
baseline before calculating an alternative. Every registered analysis remains
in the output, including failures with their IDs and reasons; the program never
substitutes a new choice after seeing a result.

Complete outputs are written together under `outputs/multiverse/`, including
the 16-row results, 4 by 4 specification display, and coverage diagnostics. A
temporary directory and ownership marker prevent partial or unrelated output
from being presented as a completed ODMK run. See the
[`code review guide`](docs/code_review_guide.md) for the enforced contract and
[`output schema`](docs/output_schema.md) for file details.

After the approved run, `make cos-results` converts the validated native table
to `submission/results_ODMK.csv`, using the exact 29-column COS schema and the
option names in the approved preregistration. This is a reporting-only
transformation; it does not reopen the respondent data or recompute an estimate.

## Troubleshooting

- **Environment rejected:** confirm Python 3.14.4, reactivate `.venv`, and run
  `make setup`.
- **Data missing or fingerprint rejected:** reacquire the canonical bundle and
  verify both checksums in [`data_access.md`](data_access.md); never bypass the
  fingerprint check.
- **Multiverse blocked:** complete and commit every approval field, including
  the unchanged registry fingerprint.
- **Registered analysis fails:** retain its ID and failure reason; do not change
  its sample, score, group, or estimator.

## Environment and sources

`requirements-lock.txt` is the installation lock used by `make setup` and
continuous integration. `pyproject.toml`, `requirements.txt`, and
`requirements_multiverse.txt` expose the direct dependencies for packaging and
review, while `src/odmk/environment.py` enforces their exact production
versions.

Redistributable HINTS materials and COS guidance are under `sources/`; the
source ledger records URLs, checksums, and local-only research materials. The
canonical HINTS release is dated 2024-05-07. No public author analysis code or
supplementary analysis file was located. See
[`sources/README.md`](sources/README.md).

## Interpretation guardrails

- This is a descriptive population disparity, not a causal effect of race.
- Asian definitions are category-construction choices, not interventions on
  identity.
- The aggregate Asian category cannot support national-origin, migration, or
  language subgroup claims.
- Peer alternatives are not corrections to the paper.
- Robustness is not reduced to whether `p < .05`.
- No alternative may be added, removed, or revised after seeing its estimate.

## Licensing

Original code, tests, workflows, and configuration are licensed under the
[`MIT License`](LICENSE). Project-authored proposals and documentation are
licensed under [`CC BY 4.0`](LICENSE-DOCUMENTATION.md). These licenses do not
cover third-party publications, data, instruments, or guidance; see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
