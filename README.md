# ODMK bounded-multiverse proposal

This repository reconstructs the COS-assigned Table 2 racial/ethnic difference in perceived patient-provider communication quality (PPPCQ) from the original 2018 HINTS 5 Cycle 2 public-use file. It defines a proposed 16-specification robustness design for the Asian-versus-non-Hispanic-White weighted mean comparison.

The published baseline is reproduced. No alternative specification has been run.

## Quick result

Using all seven communication items, official `RaceEthn5`, the final-person weight, and 50 JK1 replicate weights gives `N = 2,611` across the five published race/ethnicity groups. The reconstructed non-Hispanic Asian mean is 3.1161 and the non-Hispanic White mean is 3.4457, reproducing the article's displayed 3.11 and 3.45. Their derived direct difference is −0.3296 (SE 0.1097; 95% CI −0.5502 to −0.1091).

The COS sourcing sheet assigns the Table 2 means and confidence intervals. Table 3 Model 1 is not the focal result and is not part of registry revision 7.

## Proposed universe

Four binary decisions yield 16 fully crossed specifications. d01, d03, and d04
produce eight distinct point-estimate constructions; d08 evaluates each with
two variance estimators:

- **d01 analytic sample:** content-confirmed C4 eligibility versus a literal positive routing filter;
- **d03 outcome construction:** require all seven items versus at least four valid items;
- **d04 race construction:** official mutually exclusive non-Hispanic Asian versus inclusive non-Hispanic any-Asian identification; and
- **d08 variance estimation:** official JK1 replicate weights versus Taylor linearization.

Fixed features include the seven communication domains, the 1–4 outcome scale, the non-Hispanic White reference, `PERSON_FINWT0` point weighting, the national population target, and the Asian-minus-White direction.

COS treats five dimensions as a target, not a quota. A fifth is not added because covariate adjustment, alternative outcome models, and unweighted analysis would change the Table 2 estimand or population; equivalent weighted regression would be cosmetic; and item-level imputation would overlap d03 while adding weakly anchored assumptions.

## Deliverables

- [`ODMK_COS_submission.md`](ODMK_COS_submission.md) — concise standalone submission copy.
- [`ODMK_robustness_proposal.md`](ODMK_robustness_proposal.md) — proposal copy retained under the originally requested filename.
- [`baseline_analysis.md`](baseline_analysis.md) — focal result, reconstruction, source inferences, and unresolved ambiguities.
- [`data_access.md`](data_access.md) — public acquisition instructions and checksums.
- [`dimension_audit.md`](dimension_audit.md) — d01–d09 audit.
- [`reviewer_red_team.md`](reviewer_red_team.md) — skeptical review of the revised design.
- [`DAAF_review.md`](DAAF_review.md) — improvements adopted after review against DAAF 3.0.2.
- [`specification_freeze.yaml`](specification_freeze.yaml) — revision 7 machine-readable registry.
- [`src/baseline_analysis.py`](src/baseline_analysis.py) — reproducible published-baseline pipeline.
- [`src/preflight_registry.py`](src/preflight_registry.py) — structural checks only; it estimates no alternative effects.
- [`sources/source_manifest.csv`](sources/source_manifest.csv) — source URLs, provenance, and checksums.

## Directory structure

```text
ODMK_robustness/
├── data_raw/          # ignored by Git; unmodified public-use respondent file
├── data_processed/    # ignored by Git; generated row-level audit data
├── outputs/           # generated baseline and structural QA records
├── sources/           # primary documents, source ledger, and search-aid text
├── src/               # baseline and structural-preflight code
├── submission/        # finalized submission package and checksum
├── ODMK_COS_submission.md
├── baseline_analysis.md
├── data_access.md
├── dimension_audit.md
├── reviewer_red_team.md
└── specification_freeze.yaml
```

## Reproduce the permitted baseline checks

Python 3.14.4 was used for the archived baseline run. From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 src/baseline_analysis.py
python3 src/preflight_registry.py
```

The baseline program verifies the canonical data SHA-256, 3,504 source rows, unique/nonmissing `HHID`, deterministic sorting, required fields, 50 replicate weights, weight validity, PPPCQ range, exact `RaceEthn5` frequencies, focal `N = 2,611`, and agreement with all five published Table 2 means and intervals.

The structural preflight verifies registry revision 7, the four binary dimensions, the 16-cell Cartesian product, eight point-estimate constructions, routing counts, score-coverage counts, official and inclusive Asian membership, focal-group disjointness, and survey-design structure. It computes no alternative group mean or contrast. The production analysis will create the survey design before applying eligibility or racial-group domains so subgroup estimation does not discard design units.

Production robustness estimation is planned in R's `survey` package after COS approval, with the exact R and package versions frozen before any nonbaseline effect is calculated. The explicit Python JK1 reconstruction remains an independent baseline check.

## Source notes

The public HINTS bundle, COS sheet and guidance, and COS-linked article are archived or recorded in `sources/`. The current HINTS release is dated 2024-05-07. No public author analysis code or supplementary analysis file was located. See [`sources/README.md`](sources/README.md).

## Interpretation guardrails

- This is a descriptive population disparity, not a causal effect of race.
- The two Asian definitions are category-construction choices, not interventions on identity.
- The aggregate Asian category cannot support national-origin, migration, or language subgroup claims.
- Peer alternatives are not corrections to the paper.
- Robustness is not reduced to whether `p < .05`.
- No alternative can be added, removed, or revised after seeing its estimate.
- Every unresolved author choice remains labeled as unresolved.
