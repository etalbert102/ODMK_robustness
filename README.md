# ODMK bounded-multiverse proposal

This repository reconstructs the focal racial/ethnic difference in perceived patient-provider communication quality from the original 2018 HINTS 5 Cycle 2 public-use file and defines a proposed, 32-cell robustness design for COS. Table 3 Model 1 is the operational focal published result; Table 2 is the exact source-pipeline validation anchor. The registry is conditionally frozen pending COS confirmation that Table 3 Model 1 is the assigned focal table.

The published descriptive baseline is reproduced. The alternative multiverse has **not** been run.

## Quick result

Using all seven communication items, valid `RaceEthn5`, the final person weight, and 50 JK1 replicate weights gives `N = 2,611`. The reconstructed non-Hispanic Asian mean is 3.1161 and the non-Hispanic White mean is 3.4457. Their direct difference is −0.3296 (SE 0.1097; 95% CI −0.5502 to −0.1091), matching the paper's displayed group results within reporting precision.

The literal six-covariate adjusted reconstruction does not exactly match the operational Table 3 target: it yields `N = 2,527` and an Asian coefficient of −0.2333 (SE 0.1324), compared with the paper's −0.264 (SE 0.12). The article does not report covariate missingness handling and conflicts about whether age and gender appear in the model. This is documented, not tuned away. If COS identifies Table 2 rather than Table 3 Model 1 as the assigned statistic, the proposed registry must be versioned before any alternatives are run.

## Deliverables

- [`ODMK_COS_submission.md`](ODMK_COS_submission.md) — clean, standalone submission copy aligned to registry revision 6.
- [`ODMK_robustness_proposal.md`](ODMK_robustness_proposal.md) — submission-ready COS proposal; starts with the one-paragraph recommendation.
- [`baseline_analysis.md`](baseline_analysis.md) — published facts, source-based inferences, reconstruction, and unresolved ambiguities.
- [`data_access.md`](data_access.md) — public acquisition instructions, hashes, and required source files.
- [`dimension_audit.md`](dimension_audit.md) — full d01–d09 audit and reasons to vary or reject each choice.
- [`reviewer_red_team.md`](reviewer_red_team.md) — five strongest reviewer objections and responses.
- [`specification_freeze.yaml`](specification_freeze.yaml) — proposed five-axis registry and execution guard.
- [`src/baseline_analysis.py`](src/baseline_analysis.py) — reproducible baseline pipeline with assertions and QA.
- [`src/preflight_registry.py`](src/preflight_registry.py) — no-effect rank/separation preflight for the frozen MICE design.
- [`requirements_multiverse.txt`](requirements_multiverse.txt) — direct dependency pins for the future runner; a transitive hash lock is a pre-execution requirement.
- [`sources/source_manifest.csv`](sources/source_manifest.csv) — source URLs, provenance, and checksums.

## Directory structure

```text
ODMK_robustness/
├── data_raw/          # unmodified HINTS public-use Stata file
├── data_processed/    # code-generated baseline audit data
├── outputs/           # code-generated tables, flow, summary, and QA
├── sources/           # primary PDFs, source ledger, and searchable text copies
├── src/               # baseline and structural-preflight code; no multiverse runner
├── baseline_analysis.md
├── data_access.md
├── dimension_audit.md
├── reviewer_red_team.md
├── ODMK_robustness_proposal.md
├── requirements_multiverse.txt
└── specification_freeze.yaml
```

## Reproduce the baseline

Python 3.14.4 was used for the archived run. From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 src/baseline_analysis.py
python3 src/preflight_registry.py
```

The program verifies the canonical data SHA-256, 3,504 source rows, unique/nonmissing `HHID` and deterministic sort order, required fields, 50 replicate weights, positive weights, valid scale range, exact `RaceEthn5` frequencies, focal `N = 2,611`, and agreement with published Table 2 means. The fixed C4 module population—an observed positive route or valid follow-up content when the filter is missing—contains 2,993 respondents. Twenty-two focal-frame respondents have complete C4 data and valid race despite a missing `FreqGoProvider` filter; the strict-filter count (2,589) is retained only as QA. The program exits nonzero if a check fails.

Generated files:

- `data_processed/odmk_baseline_derived.csv.gz`;
- `outputs/table2_reproduction.csv`;
- `outputs/table3_model1_reconstruction.csv`;
- `outputs/exclusion_flow.csv`;
- `outputs/qa_checks.json`;
- `outputs/baseline_summary.json`.
- `outputs/registry_preflight.json` (from `python3 src/preflight_registry.py`).

## Proposed universe

The five binary dimensions are d02 missing covariates, d03 outcome completeness, d05 age functional form, d06 interpretive adjustment family, and d07 conditional-mean model. Their Cartesian product contains 32 specifications. Within each d02×d03 branch, the record set is fixed across d05, d06, and d07. Fixed features include the C4 module population, all seven outcome domains, `RaceEthn5`, the Asian-minus-White contrast, final person weights, JK1 replicate-weight inference, weighted standardization, and the 1–4 reporting scale; d03 varies observed scoring coverage within that population.

The baseline code contains no implementation path for alternative cells. This separation prevents accidental result inspection before the proposal is confirmed and accepted. The future multiverse runner must read `specification_freeze.yaml`, enumerate all 32 cells, enforce the common-frame and weighting invariants, and refuse hand-selected subsets or post-result repairs. Reporting is faceted into 16 demographic-core and 16 fuller socioeconomic/language-standardized cells; it must not pool the two interpretive frames into one robustness rate or distributional headline.

`requirements_multiverse.txt` pins direct dependencies but is not a transitive environment lock. Before any alternative cell is executed, the implementation must create a hash-locked `requirements_multiverse.lock` under Python 3.13.16 and archive its SHA-256 plus interpreter/platform metadata. It must also sort on unique `HHID` and pass the rank, binary-separation, finite-information, row-order, weight-rescaling, category-coding, OLS-equivalence, age-map, JK1-anchor, and Barnard–Rubin pooling tests registered in `specification_freeze.yaml`. The existing structural preflight checks no effects and confirms that the reduced log-weight-plus-stratum MICE design is full rank and nonseparated under both d03 frames.

## Source notes

The HINTS bundle is public and archived locally. The publisher article is closed, so this repository preserves PubMed metadata and the inspected author-uploaded full-text link rather than redistributing an access-controlled PDF. The 2024 public release omits documented weighting-production `_I` fields; possible release drift relative to the authors' file is unresolved. No public author code/supplement or ODMK-specific public COS template was located as of 2026-10-13. See [`sources/README.md`](sources/README.md).

## Interpretation guardrails

- This is a descriptive disparity analysis, not an estimate of a causal effect of race.
- Category-standardized predictions describe fitted racial/ethnic categories; they are not interventions on race.
- The aggregate HINTS Asian category cannot represent national-origin, migration, or language subgroup heterogeneity.
- A peer alternative is not labeled a correction to the original paper.
- Robustness is not reduced to whether `p < .05`.
- No alternatives are chosen or discarded after seeing their estimates.
- Every unresolved author choice remains labeled as unresolved.
