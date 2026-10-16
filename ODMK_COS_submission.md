# ODMK robustness-analysis proposal

## Recommended proposal in one paragraph

For ODMK, I propose 32 robustness analyses covering every combination of five reasonable decisions. This bounded multiverse asks how sensitive the estimated Asian–White disparity is to a small set of defensible analytical choices that researchers could have made before seeing the results, while holding the population, racial comparison, communication construct, and survey design fixed. The purpose is not to find a specification that makes the published result disappear. Each analysis estimates the average adjusted difference in patient-provider communication quality between non-Hispanic Asian and non-Hispanic White respondents in the fixed 2018 HINTS 5 Cycle 2 patient-provider communication population. Subject to COS confirmation, the focal published result is Table 3 Model 1; the exactly reconstructed Table 2 means check the data and measures. No alternative analysis will run before that confirmation. The five decisions are: require all seven communication items or at least four valid items to calculate the same seven-item mean (d03); exclude records with missing covariates or use 50-dataset multiple imputation by chained equations (MICE) for covariates only (d02); adjust for age and gender or for the full published covariate set (d06); model age in years or with the official five HINTS age groups (d05); and use survey-weighted linear regression or fractional logit, a model suited to outcomes bounded between 0 and 1 (d07). Both models report the same weighted average adjusted difference on the original 1–4 scale. The target population, race coding, outcome content, population weights, jackknife repeated replication (JK1) inference, and Asian-minus-White comparison remain fixed. The results will show how the estimated magnitude and uncertainty vary across these peer choices. They will be presented in separate 16-analysis panels for the two adjustment approaches, not reduced to a single robustness rate or significance-based verdict.

## Paper and focal result

**Paper ID:** ODMK

**Citation:** Kim, H.-S., Kim, H. J., and Juon, H.-S. (2021). “Racial/Ethnic Disparities in Patient-Provider Communication and the Role of E-Health Use.” *Journal of Health Communication*, 26(3), 194–203. <https://doi.org/10.1080/10810730.2021.1919248>.

The assigned substantive finding is that non-Hispanic Asian respondents reported lower perceived patient-provider communication quality (PPPCQ) than non-Hispanic White respondents. I treat the adjusted Asian indicator in Table 3 Model 1 as the focal published statistic: −0.264 (SE 0.12, displayed as `p < .05`), with non-Hispanic White as the reference group.

Table 2 presents the direct descriptive comparison: Asian mean 3.11 (SE 0.10; 95% CI 2.90–3.33) versus White mean 3.45 (SE 0.02; 95% CI 3.39–3.49). Exact reproduction checks the source data, outcome, race coding, and survey-design implementation; these means are not another robustness analysis.

The COS sourcing sheet was not among the supplied or local materials. The companion registry is provisionally locked until COS confirms that Table 3 Model 1 is the intended focal result. If COS identifies Table 2 alone, I will revise and reapprove the registry before running any alternative analysis.

## Data source and feasibility

HINTS 5 Cycle 2 is publicly obtainable from the US National Cancer Institute and requires no restricted-data application. The reconstruction uses the 3,504-record public-use Stata file from the 2024-05-07 bundle. Required materials are:

- the public-use respondent file;
- the public codebook/data dictionary;
- the annotated English survey instrument and archived Spanish instrument;
- the methodology and sampling report;
- the analytics recommendations for final weights, replicate weights, JK1 coefficient, and degrees of freedom; and
- the history document and NCI remediation notice.

The raw file is preserved unchanged and verified by SHA-256. Source URLs, provenance, and checksums are recorded in `sources/source_manifest.csv`. No public author analysis code or supplementary analysis file was located.

## Baseline reconstruction

The fixed patient-provider communication module population includes respondents with `FreqGoProvider` in 1–6, plus respondents who answered at least one C4 item even though the routing filter is missing. This follows NCI's editing rule that a missing filter remains missing when a respondent answered a follow-up question. The fixed population contains 2,993 respondents. The outcome-scoring decision changes which of these respondents receive a score; it does not redefine the target population.

The baseline pipeline:

1. treats C4 responses 1–4 as valid and all negative codes as missing;
2. reverse-scores `ChanceAskQuestions`, `FeelingsAddressed`, `InvolvedDecisions`, `UnderstoodNextSteps`, `ExplainedClearly`, `SpentEnoughTime`, and `HelpUncertainty` as `5 − response`;
3. averages the seven items on the 1–4 scale, requiring all seven for the reconstructed baseline;
4. uses official `RaceEthn5` codes 1–5, with non-Hispanic White as reference and non-Hispanic Asian as the focal group; and
5. uses `PERSON_FINWT0` for point estimates and `PERSON_FINWT1`–`PERSON_FINWT50` for JK1 variance, with coefficient 0.98 and 49 degrees of freedom.

Requiring seven valid items and valid race gives `N = 2,611` and reproduces all five Table 2 group means and intervals within display precision. The reconstructed Asian-minus-White difference is −0.3296 (JK1 SE 0.1097; 95% CI −0.5502 to −0.1091). Thirty respondents with all seven items have a missing routing filter; 22 also have valid race. Requiring an observed routing filter would reduce the sample to 2,589. That result is recorded only as a diagnostic and is not a robustness option.

The direct adjusted reconstruction uses the six covariates named in the Methods—age in years, gender, college graduation, married/living as married, current employment, and speaking English very well—and excludes records missing any of them. It yields `N = 2,527` and an Asian coefficient of −0.2333 (JK1 SE 0.1324), rather than the published −0.264 (SE 0.12). I do not change reasonable coding decisions merely to force a match. The discrepancy may reflect undocumented treatment of missing covariates, a conflict between the Methods and the Table 3 note, or differences between the data release used by the authors and the current public file.

## Proposed robustness dimensions

### 1. d06 — Control variables

**Baseline/full option:** age, gender, college graduation, married/living as married, current employment, and speaking English very well, matching the Methods.

**Peer alternative:** a demographic core of age and gender.

**Justification and mechanism:** The core model estimates the group difference after adjusting for basic demographics. The full model also adjusts for socioeconomic, household, employment, and language characteristics. English proficiency and related characteristics may be part of the processes through which racialized social position is associated with communication, so neither adjustment approach is treated as uniquely correct. Differences in group composition and in how these characteristics relate to communication scores can affect the adjusted comparison; no direction is predicted.

**Implementation and risk:** Age takes the form selected under d05. Within each d02×d03 combination, both d06 models use the same records: complete-case analysis requires all six covariates even for the core model, and MICE imputes all six before either model is fitted. Both estimates are adjusted descriptive differences, not causal effects, and appear in separate 16-analysis panels.

### 2. d03 — Outcome construction

**Baseline option:** average the seven reverse-scored items only when all seven are valid.

**Peer alternative:** average the same seven items when at least four are valid.

**Justification and mechanism:** The all-seven rule is inferred from the exact reproduction. Requiring at least half of the items allows limited item nonresponse without changing the outcome's content, weighting, or scale. The 2001 EORTC QLQ-C30 scoring manual provides a pre-ODMK general precedent for calculating a multi-item scale when at least half of its items are answered; it does not validate this rule specifically for PPPCQ. A later HINTS 5 Cycle 2 study found that these items measure a common concept and used four valid items, but it postdates ODMK and is not treated as validation of the threshold. Item completion may relate to respondent characteristics or communication experience, affecting who receives a score without changing the target population.

**Implementation and risk:** Valid responses are 1–4. The respondent mean is calculated only when the selected threshold is met and remains on the 1–4 scale. Missingness patterns and weighted coverage will be reported overall and by race, but cannot change the rule. Only 69 source respondents have four to six valid items, so this option is scientifically meaningful but likely to affect few respondents. No PPPCQ item or score is imputed.

### 3. d02 — Missing-covariate treatment

**Baseline option:** a common complete-case frame requiring valid values for all six candidate covariates for both d06 models.

**Peer alternative:** multiple imputation by chained equations (MICE), using 50 completed datasets, for the six covariates only.

**Justification and mechanism:** Complete-case analysis is transparent but excludes anyone missing a covariate. MICE is reasonable when reporting may depend on race, PPPCQ, the survey design, and other observed characteristics. The options can differ if covariate reporting—and thus complete-case inclusion—is associated with race, language, socioeconomic position, or reported communication.

**Implementation:** Records are sorted by unique `HHID`, and fixed random seeds are assigned to the two d03 options. Each imputation model includes race, the PPPCQ score from the selected d03 option, the other candidate covariates, the standardized log final weight, and survey stratum. Age uses predictive mean matching with five possible donors; binary variables use standard logistic-regression imputation. The procedure uses 20 initial cycles and saves 50 completed datasets at five-cycle intervals. Age groups are recalculated from each imputed age. Race, routing fields, PPPCQ items and scores, weights, and survey-design variables are never imputed. The exact algorithms, tie-breaking rules, technical checks, random-number streams, and Barnard–Rubin rules for combining multiple-imputation results are fixed in `specification_freeze.yaml` revision 6.

**Risk:** This practical, bounded imputation model does not reproduce every survey-design feature during imputation. Adding fixed effects for all 100 stratum-by-primary-sampling-unit (PSU) cells caused separation in the binary imputation models. Analysis-stage JK1 retains the released variance design but cannot restore similarity among respondents in the same sampling cluster that the imputation model omits. PSU random-effects or Bayesian imputation would add another large family of decisions, so they are set aside rather than used as unregistered repairs.

### 4. d07 — Model and functional form

**Baseline option:** probability-weighted linear regression of the 1–4 score.

**Peer alternative:** probability-weighted fractional logit, a model for outcomes bounded between 0 and 1, applied to `z = (PPPCQ − 1)/3` and retaining boundary values.

**Justification and mechanism:** Linear regression matches the paper and directly reports a mean difference. Fractional logit is an established model for bounded responses, including scores at either endpoint (Papke and Wooldridge, 1996), and is relevant because many PPPCQ scores are near the upper limit. The two models may fit scores near that limit and across respondent characteristics differently.

**Implementation and risk:** Both models report the same weighted average adjusted Asian-minus-White difference on the 1–4 scale. For the full and replicate weights, Asian and White predictions are calculated over the same covariate distribution and averaged with the weight used for that fit. Fractional logit uses JK1 replicate differences for uncertainty; its model-based covariance, likelihood summaries, and raw coefficients are not used for comparison. Exact estimation details are fixed in the registry.

### 5. d05 — Age functional form

**Baseline option:** age entered linearly in years.

**Peer alternative:** official `AgeGrpB` categories: 18–34, 35–49, 50–64, 65–74, and 75+, with 18–34 as reference.

**Justification and mechanism:** The article names age but does not report its form. Both representations were available in the source data before analysis. Racial/ethnic groups may differ in age composition, and the relationship between age and PPPCQ may be nonlinear.

**Implementation and risk:** Age appears in both d06 adjustment approaches. Under MICE, age is imputed in years and the categories are recalculated using the official boundaries. No cut points chosen after examining the data and no category merging are permitted. Categories lose information about differences within each band and may reduce precision, but they are an official representation specified in advance.

## Dimensions considered but not varied

- **d01 analytic sample:** The C4 module population is fixed. d03 alone governs observed score availability. E-health, language, usual-care-source, or narrower visit restrictions would change the population or question.
- **d04 main predictor:** `RaceEthn5`, the five mutually exclusive categories, the Asian focal group, and White reference are fixed. Collapsing Asian respondents changes the assigned question; changing the reference only relabels the same model.
- **d08 clustering and variance:** JK1 is fixed because it matches the authors and carries the released replicate-weight calibration. Taylor linearization is supported but changes an inference approximation rather than the point estimate.
- **d09 survey weights:** Final-person weighting is fixed. An unweighted analysis does not represent the same national target under the unequal-probability HINTS design.
- **Other rejected options:** pure rescaling, sum versus mean under an identical completeness rule, outcome dichotomization, six-item or factor-weighted outcomes, ordinal models, weight-only robust errors, and one-covariate-at-a-time adjustment are cosmetic, insufficiently supported, redundant, or change the focal quantity.

## Specification count and reporting

The five binary dimensions yield `2 × 2 × 2 × 2 × 2 = 32` analyses. Every analysis will be attempted and listed, including failures under the registered policy. Results will appear in one 16-analysis demographic-core panel and one 16-analysis panel using the fuller socioeconomic and language adjustment. Each result will include the Asian-minus-White estimate, design-based SE and 95% interval, unweighted focal-group counts, and option labels. No pooled robustness rate, median, range, or preferred conclusion will combine the two d06 interpretations. Statistical significance will not determine inclusion or emphasis.

## Software and reproducibility

The raw source file remains unchanged. The Python baseline pipeline verifies the file checksum, required variables, 3,504-row count, fixed `HHID` ordering, valid outcome range, race frequencies, positive weights, 50 replicate weights, analytic sample sizes, and published Table 2 values. The future analysis program must read `specification_freeze.yaml` revision 6 and run every combination rather than allowing models to be selected by hand.

Before execution, exact Python package versions and dependencies will be locked and verified with hashes. Tests cover row-order and weight-rescaling invariance; model rank, separation, and information matrices; linear-regression standardization; construction of race comparison records and age groups; JK1 baseline reproduction; and the Barnard–Rubin rules for combining estimates across imputed datasets. Numerical failures may not be repaired by dropping variables, merging categories, adding a penalty, substituting an estimator, or inspecting the focal estimate. Failed analyses remain visible.

AI may assist with code generation, testing, repetitive model enumeration, and documentation. The scientific decisions are fixed by the human-approved registry; AI output may not add or remove specifications based on estimates, intervals, or p-values.

## Pre-analysis declaration

Only the published-baseline reconstruction and technical checks needed to identify and verify the pipeline have been run. Candidate item-count rules were checked to identify the published baseline. A strict routing-filter restriction was inspected only to diagnose a contradiction between the documentation and code; any nonbaseline effect encountered in that check is kept separate, not reported, and not used. The model-rank and separation checks estimated no focal effects. No imputed, core-adjusted, grouped-age, fractional-logit, or other analysis from the registered 32-analysis set has been run. Any change requested by COS will be recorded in a new registry version before the affected alternatives are run.

## Methodological references

- Barnard, J., and Rubin, D. B. (1999). Small-sample degrees of freedom with multiple imputation. *Biometrika*, 86(4), 948–955. <https://doi.org/10.1093/biomet/86.4.948>.
- Fayers, P. M., Aaronson, N. K., Bjordal, K., Groenvold, M., Curran, D., and Bottomley, A. (2001). *The EORTC QLQ-C30 Scoring Manual*, 3rd ed. <https://www.eortc.org/app/uploads/sites/2/2018/02/SCmanual.pdf>.
- Moser, R. P., Trivedi, N., Murray, A., Jensen, R. E., Willis, G., and Blake, K. D. (2022). Patient-Centered Communication (PCC) scale: Psychometric analysis and validation of a health survey measure. *PLOS ONE*, 17(12), e0279725. <https://doi.org/10.1371/journal.pone.0279725>.
- Papke, L. E., and Wooldridge, J. M. (1996). Econometric methods for fractional response variables with an application to 401(k) plan participation rates. *Journal of Applied Econometrics*, 11(6), 619–632. <https://doi.org/10.1002/(SICI)1099-1255(199611)11:6%3C619::AID-JAE418%3E3.0.CO;2-1>.
- White, I. R., Royston, P., and Wood, A. M. (2011). Multiple imputation using chained equations: Issues and guidance for practice. *Statistics in Medicine*, 30(4), 377–399. <https://doi.org/10.1002/sim.4067>.
- Zhou, H., Elliott, M. R., and Raghunathan, T. E. (2016). Multiple imputation in two-stage cluster samples using the weighted finite population Bayesian bootstrap. <https://pubmed.ncbi.nlm.nih.gov/28781418/>.

## Companion submission files

- `specification_freeze.yaml` (revision 6)
- `baseline_analysis.md`
- `dimension_audit.md`
- `reviewer_red_team.md`
- `data_access.md`
- `sources/source_manifest.csv`
- `src/baseline_analysis.py`
- `src/preflight_registry.py`
- `outputs/table2_reproduction.csv`
- `outputs/table3_model1_reconstruction.csv`
- `outputs/exclusion_flow.csv`
- `outputs/qa_checks.json`
- `outputs/registry_preflight.json`
