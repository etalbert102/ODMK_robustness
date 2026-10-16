# Recommended proposal in one paragraph

For ODMK, I propose a 32-specification, fully crossed robustness analysis of the adjusted population-average non-Hispanic Asian-minus-non-Hispanic White difference in the seven-item, 1–4 patient-provider communication quality mean for the fixed 2018 HINTS 5 Cycle 2 C4 module population. The operational focal published result is Table 3 Model 1; the exactly reconstructed Table 2 means are the upstream validation anchor, and execution is blocked until COS confirms that focal-table interpretation. The five binary peer-analysis decisions are: (1) require all seven items versus at least four valid items to score the same seven-item mean (d03); (2) complete-case treatment of missing covariates versus 50-dataset prespecified MICE for covariates only (d02); (3) use a demographic core versus the full published adjustment set (d06); (4) enter age linearly versus as the official five-level HINTS `AgeGrpB` variable (d05); and (5) use survey-weighted linear regression versus fractional logit, reporting the same weighted average marginal mean difference back on the 1–4 scale (d07). The target population, five-category race variable and White reference, all seven outcome domains, final-person weights, JK1 inference, and focal contrast remain fixed; d03 varies observed scoring coverage within that population. The 32 cells will be interpreted in separate 16-cell panels for the two adjustment frames, not pooled into one robustness rate. No registered alternative specification has been run.

# Proposal to the Center for Open Science

## Paper and assigned result

**Paper ID:** ODMK

**Citation:** Kim, H.-S., Kim, H. J., & Juon, H.-S. (2021). Racial/Ethnic Disparities in Patient-Provider Communication and the Role of E-Health Use. *Journal of Health Communication, 26*(3), 194–203. <https://doi.org/10.1080/10810730.2021.1919248>.

**Assigned result:** The paper reports lower perceived patient-provider communication quality (PPPCQ) among non-Hispanic Asian respondents than among non-Hispanic White respondents. For this proposal, the operational focal statistic is the adjusted Asian indicator in **Table 3 Model 1**: −0.264 (SE 0.12, `p < .05`), with non-Hispanic White as reference.

The paper also presents the direct Hypothesis 1 comparison in Table 2: Asian mean 3.11 (SE 0.10; 95% CI 2.90–3.33) versus White mean 3.45 (SE 0.02; 95% CI 3.39–3.49). Those means are exactly reconstructible and validate the source data, outcome, race coding, eligibility, and survey design. They are not an additional multiverse branch. No COS sourcing-sheet file was available locally, so the Table 3 choice is stated rather than silently assumed. The registry is **conditionally frozen pending COS confirmation of the focal table**; if COS identifies Table 2 only, it must be versioned before any alternative is executed. The proposal treats the registered focal quantity as a weighted, covariate-standardized Asian-minus-White difference on the original 1–4 mean scale, not as a binary “significant/non-significant” conclusion.

## Data source and feasibility

HINTS 5 Cycle 2 is publicly obtainable from the US National Cancer Institute. The current Stata bundle and all supporting documents have been archived with SHA-256 checksums in [`sources/`](sources/). Required files are:

- the 3,504-record public-use Stata file;
- public codebook/data dictionary;
- annotated English survey instrument (plus the archived Spanish instrument);
- methodology and sampling report;
- analytics recommendations documenting final weights, replicate weights, Taylor variables, jackknife coefficient, and degrees of freedom;
- history/remediation documentation.

The data require no restricted-data application. Exact URLs and reacquisition commands are in [`data_access.md`](data_access.md). The article was inspected through an author-uploaded full-text page; no public author code or supplement was located. No paper-specific COS template was found in the workspace or on the public benchmark page, so the supplied d01–d09 protocol governs this proposal.

## Baseline reconstruction

The raw HINTS file is never edited. The reproducible code:

1. defines the fixed C4 module population by an observed positive `FreqGoProvider` value or at least one valid C4 response, retaining answered follow-ups when the filter is missing as directed by the methodology report;
2. reverse-scores `ChanceAskQuestions`, `FeelingsAddressed`, `InvolvedDecisions`, `UnderstoodNextSteps`, `ExplainedClearly`, `SpentEnoughTime`, and `HelpUncertainty` as `5 − response`;
3. averages all seven items, requiring seven valid responses;
4. uses official `RaceEthn5` codes 1–5, with non-Hispanic White as reference and non-Hispanic Asian as the focal group;
5. uses `PERSON_FINWT0` for point estimation and `PERSON_FINWT1`–`PERSON_FINWT50` for JK1 variance, coefficient 0.98, 49 degrees of freedom;
6. converts every negative survey code to missing rather than a substantive reference value.

The fixed module population contains 2,993 respondents. Requiring seven valid items and valid race produces `N = 2,611` and reproduces all five Table 2 group means and confidence intervals within display precision. Thirty complete-seven respondents have a missing routing filter; 22 have valid race and remain in the reconstruction. Requiring an observed positive filter would conflict with NCI's editing rule and reduce the focal frame to 2,589. The directly reconstructed Asian-minus-White difference is −0.3296 (JK1 SE 0.1097; 95% CI −0.5502 to −0.1091).

For the adjusted baseline cell, the code uses the six covariates named in the Methods—continuous age, gender, college graduation, married/living as married, current employment, and speaking English very well—and complete cases. This yields `N = 2,527` and an Asian coefficient of −0.2333 (SE 0.1324), not the published −0.264 (SE 0.12). The discrepancy is not tuned away. The article does not report missing-covariate handling, its Table 3 note conflicts with the Methods, and the current 2024 public file may differ from the authors' release. [`baseline_analysis.md`](baseline_analysis.md) separates facts, inferences, and unresolved points.

## Proposed robustness dimensions

### 1. d06 — Control variables

**Baseline/full option:** age, gender, college graduation, married/living as married, current employment, and speaking English very well, matching the Methods. Age takes the form selected under d05.

**Peer alternative:** a demographic core of age and gender, with age again governed by d05.

**Scientific justification:** The full set asks whether disparity remains after standardizing for observed socioeconomic, household, employment, and language composition. The core set standardizes only basic demographics and avoids automatically conditioning on characteristics—especially English proficiency—that may be part of how racialized social position relates to communication. These are coherent model families, not one-variable-at-a-time fishing.

**Expected mechanism:** The groups differ in age, socioeconomic composition, and English proficiency, and these characteristics can predict reported communication. Adjustment can therefore change the standardized contrast through composition and conditional association, without implying a direction.

**Implementation:** Fit the selected survey mean model with four race indicators and either two or six covariates. Within each d02×d03 branch, the analytic records are fixed across both d06 options: the complete-case branch requires valid values for all six candidate covariates even when the core model uses only age and gender; the MICE branch imputes all six candidate covariates before either model is fitted. This prevents the covariate-set choice from also becoming a sample-selection choice. For every model, evaluate the fitted mean twice over the same observed covariate distribution—once with the race-indicator block coded as Asian and once as White—and report their weighted average difference. This is descriptive regression standardization, not an intervention on race.

**Risk:** Adjustment changes the conditional interpretation. The report will call both quantities descriptive standardized disparities, not causal effects, and will display results by adjustment family.

### 2. d03 — Outcome construction

**Baseline option:** reverse-score and average the seven listed items only when all seven are valid.

**Peer alternative:** average the same reverse-scored seven items when at least four are valid.

**Scientific justification:** Requiring all seven is inferred from exact article reproduction. A minimum-half rule preserves respondents with limited item nonresponse while retaining the same domains and equal weights. A pre-ODMK general precedent is the 2001 EORTC QLQ-C30 scoring manual, which scores a multi-item scale from the completed-item mean when at least half its items are answered: Fayers et al. (2001), <https://www.eortc.org/app/uploads/sites/2/2018/02/SCmanual.pdf>. This does not validate the threshold for PPPCQ; it establishes that a competent analyst could have selected the rule ex ante. A later same-cycle study found a unidimensional seven-item construct (alpha 0.92) and used four valid items: Moser et al. (2022), <https://doi.org/10.1371/journal.pone.0279725>. That later study is construct evidence and a same-instrument precedent, not threshold validation or evidence available to ODMK's authors.

**Expected mechanism:** Item completion may relate to respondent characteristics and communication experience. The rule changes observed scoring coverage within the fixed C4 module population and how partial records contribute, without changing that population or the scale's content.

**Implementation:** Valid responses are 1–4; negative codes are missing. Compute the row mean after reversal only when the selected count threshold is met. Retain the 1–4 metric. Before analysis, report item-missingness patterns, item-specific missingness, and scoring eligibility/weighted coverage overall and by `RaceEthn5` under both rules. These diagnostics cannot change the registry. Only 69 source respondents have four to six valid items, so this is a conceptually meaningful but empirically narrow branch.

**Risk:** This changes analytic coverage and therefore relies on different observed-outcome assumptions. It does not redefine the target population or impute item responses. Pure rescaling, item deletion, factor weighting, and dichotomization are excluded.

### 3. d02 — Missing-data treatment

**Baseline option:** a common complete-case frame requiring valid values for all six candidate covariates after negative codes are made missing, regardless of which d06 adjustment family is fitted.

**Peer alternative:** 50-dataset MICE for covariates only.

**Scientific justification:** Complete-case analysis is transparent and consistent with default regression behavior when missing is correctly coded. Requiring the same six-covariate complete-case frame for both nested adjustment families prevents sample composition from masquerading as an adjustment-set effect. MICE is a standard alternative when covariate response may depend on observed race, outcomes, design, and other covariates. NCI documented demographic hot-deck fields for weighting production, but the current 2024 public-use file does not expose those `_I` fields; they are not treated as author analytic imputations, and use of an earlier-release field remains unresolved.

**Expected mechanism:** Covariate response and complete-case inclusion may be associated with race/ethnicity, language, socioeconomic position, or PPPCQ. The methods therefore use different information and assumptions about observed nonresponse, without targeting a direction.

**Implementation:** Sort by unique, nonmissing `HHID`; use `PCG64` with `SeedSequence(20261013).spawn(2)` for the two d03 branches. Do not impute routing fields, race, PPPCQ items/scores, weights, or design variables. Conditional models include four race indicators, d03-specific PPPCQ, the other candidate covariates, standardized log `PERSON_FINWT0`, and categorical `VAR_STRATUM`. The 100 stratum×PSU fixed effects are excluded because structural preflight found separation in binary models; PSU clustering is instead retained in analysis-stage uncertainty through the official JK1 weights. This bounded representation incorporates unequal selection and stratification but is not claimed to model every design feature inside MICE. Zhou et al. (2016), <https://pubmed.ncbi.nlm.nih.gov/28781418/>, motivates inclusion of survey-design information.

Initialize age at its observed median and binary variables at observed modes; run 20 burn-in cycles in the fixed order age, gender, education, marital status, employment, and English proficiency; then save 50 datasets five cycles apart. Age uses five-donor type-1 predictive mean matching with a residual-variance and coefficient draw; binary variables use unpenalized logistic coefficient and Bernoulli draws. Donor tie-breaking, exact distributions, separation/rank gates, and failure rules are frozen in [`specification_freeze.yaml`](specification_freeze.yaml). Grouped age is passively derived from completed age using official boundaries. The no-effect structural preflight in [`outputs/registry_preflight.json`](outputs/registry_preflight.json) confirms full rank and no complete or quasi-complete separation under both d03 frames.

Within each completed dataset, calculate the full and 50-replicate standardized contrast and JK1 variance, then pool with the exact Rubin/Barnard–Rubin formula registered in YAML, using 49 complete-data degrees of freedom; see Barnard and Rubin (1999), <https://doi.org/10.1093/biomet/86.4.948>. Diagnostics assess convergence, valid ranges/categories, observed-versus-imputed distributions, and Monte Carlo error—not focal significance.

**Risk:** MICE entails modeling assumptions. The log-weight-plus-stratum model is a pragmatic bounded alternative, not fully design-congenial: analysis-stage JK1 inference does not restore within-PSU dependence omitted during imputation. PSU random-effects or Bayesian imputation would add a separate modeling framework and are set aside rather than introduced as hidden repairs. Free choices are frozen; race/outcome imputation and result-driven diagnostic changes are prohibited.

### 4. d07 — Model/functional form

**Baseline option:** survey-weighted linear regression of the 1–4 score.

**Peer alternative:** survey-weighted fractional logit for `z = (PPPCQ − 1) / 3`, retaining observations at zero and one.

**Scientific justification:** Linear regression directly matches the paper and gives an easily interpreted mean difference. Fractional logit is a conventional conditional-mean model for bounded responses, including endpoints; see Papke and Wooldridge (1996), <https://doi.org/10.1002/(SICI)1099-1255(199611)11:6%3C619::AID-JAE418%3E3.0.CO;2-1>. It is relevant because the later same-cycle study reports a substantial ceiling, and it avoids both a beta-density assumption and ad hoc endpoint corrections.

**Expected mechanism:** Identity and logit mean functions extrapolate and weight covariate patterns differently near the scale bounds. This could matter when race groups have different covariate distributions or ceiling prevalence, without prespecifying a direction.

**Implementation:** For both models, construct Asian- and White-coded evaluation rows for every record in the cell's fixed analysis frame while leaving covariates unchanged. Fit with `PERSON_FINWT0`, evaluate both category codings, and calculate `sum[w_i(pred_Asian,i − pred_White,i)] / sum(w_i)`. For each JK1 replicate `r`, refit with `PERSON_FINWTr` and use `PERSON_FINWTr` to average that replicate's prediction differences. For fractional logit, set `μ_i = expit(x_i′β)` and solve the explicit probability-weighted Bernoulli quasi-score `Σ_i w_i x_i(z_i − μ_i) = 0`, with information matrix `Σ_i w_i μ_i(1 − μ_i)x_ix_i′`, for the full and every replicate weight. Do not treat the HINTS weights as generic GLM frequency or variance weights, and ignore model-based covariance, likelihood, deviance, and AIC; statsmodels defines those weight types differently in its [GLM documentation](https://www.statsmodels.org/stable/_modules/statsmodels/genmod/generalized_linear_model.html). Multiply the fractional-logit contrast by 3 to return to the 1–4 scale. The identical category-evaluation algorithm is used for OLS even though, without interactions, it algebraically equals the Asian coefficient.

**Risk:** Raw fractional-logit coefficients are not comparable to OLS coefficients. Only average marginal mean contrasts and design-based intervals will enter the multiverse summary.

### 5. d05 — Age functional form

**Baseline option:** age entered linearly in years.

**Peer alternative:** age entered categorically using official HINTS `AgeGrpB`: 18–34, 35–49, 50–64, 65–74, and 75+, with 18–34 as reference.

**Scientific justification:** The article names age but does not report its functional form. Both exact age and `AgeGrpB` are source-defined HINTS variables available before analysis. Linear age is parsimonious; the official categories allow nonlinearity without choosing cutpoints from the focal result.

**Expected mechanism:** Racial/ethnic groups can differ in age composition, and the association between age and PPPCQ need not be linear. Different adjustment representations can therefore change standardized race contrasts without predetermining a direction.

**Implementation:** Age is present in both d06 adjustment families, so d05 crosses every adjusted cell. Under complete-case analysis, use valid `Age` or the equivalent official `AgeGrpB`. Under MICE, impute age in years and passively derive the categories using the fixed boundaries. No data-derived knots, merging, or reference changes are permitted.

**Risk:** Categories lose within-band information and may reduce precision. They are retained as a peer representation choice because the bands are official and prespecified, not because categorical age is presumed superior.

## Dimensions considered but not varied

- **d01 analytic sample:** the fixed module population includes an observed positive routing response or valid C4 follow-up content when the filter is missing. d03 changes observed scoring coverage within that population. A strict observed-filter rule would discard valid follow-up data and is retained only as QA; e-health or language restrictions would change the population.
- **d04 main predictor:** `RaceEthn5` and the Asian-versus-White contrast are fixed. Collapsing Asian respondents changes the assigned question; reference recoding is cosmetic.
- **d08 variance estimation:** JK1 is fixed because it matches the authors and better reflects the released raking/calibration adjustments. Taylor linearization is technically supported but affects inference rather than the point estimate and is not elevated above the unresolved age representation.
- **d09 weights:** `PERSON_FINWT0` is fixed. An unweighted analysis does not represent the same national target under HINTS's unequal-probability, oversampled, calibrated design.
- **Additional rejected options:** six-item/factor-weighted outcomes, scale rescaling, outcome dichotomization, ordinal models, weight-only robust errors, and one-covariate-at-a-time adjustment are either cosmetic, poorly supported, redundant, or change the focal quantity.

The full nine-dimension rationale is in [`dimension_audit.md`](dimension_audit.md). The public-use `RaceEthn5` category aggregates heterogeneous Asian national-origin, migration, and language groups. The study can address only the registered aggregate contrast; it will not generalize subgroup-specific experiences from the 105 Asian respondents in the complete-seven Table 2 frame.

## Specification count and reporting

Five binary dimensions give **32 unique, fully crossed specifications**. All 32 will be attempted and listed after registration, including any cell that fails under the preregistered failure policy. Because d06 represents two scientifically different standardization frames, primary summaries will use a 16-cell demographic-core panel and a 16-cell fuller socioeconomic/language-standardized panel. Each panel will show the Asian-minus-White estimate, design-based SE and 95% interval, unweighted group counts, and all option labels; failed cells remain visible. No single pooled robustness rate, median, range, or preferred conclusion will be calculated across both d06 frames, and conventional significance will not determine inclusion or emphasis.

The exact Table 2 descriptive reconstruction remains a validation output and is not an extra universe branch. This prevents duplicate cells in which missing-covariate handling would be irrelevant.

## Software and reproducibility

The baseline pipeline is implemented in Python 3 with pinned NumPy, pandas, and SciPy versions in [`requirements.txt`](requirements.txt). [`requirements_multiverse.txt`](requirements_multiverse.txt) pins the proposed Python 3.13.16 direct dependencies but is not represented as a full environment lock. Before execution, the implementation will resolve every transitive distribution, create `requirements_multiverse.lock` with hashes, and archive that file's SHA-256 with interpreter and platform metadata. The official software links are preserved in [`sources/source_manifest.csv`](sources/source_manifest.csv). [`src/baseline_analysis.py`](src/baseline_analysis.py) checks the source SHA-256, required variables, row count, scale range, missingness, race counts, weight positivity, replicate count, analytic `N`, and published Table 2 anchors. It writes a fully derived audit file and machine-readable output tables.

Before multiverse code is executed, COS must confirm the focal table and the conditionally frozen decision registry in [`specification_freeze.yaml`](specification_freeze.yaml) must be accepted or versioned and deposited. Required tests cover deterministic row order, full rank, binary-model nonseparation, finite positive-definite information, OLS standardization equivalence, weight-rescaling invariance, race-category coding, passive age bands, baseline JK1 anchors, and Barnard–Rubin pooling.

The failure policy is fixed in advance. Nonlinear fits start at zero and use deterministic Newton steps with backtracking; convergence requires the registered scaled score tolerance within 1,000 iterations. There is no IRLS/Newton relabeling or estimator substitution. If a fit fails, no variable is dropped, category merged, penalty added, or repair selected after inspecting an estimate. An imputation failure invalidates the corresponding d03 MICE branch; a later analysis failure labels only that registered cell. Exact numerical gates are in the registry.

AI will assist with code generation, tests, repetitive model enumeration, and documentation. Human-locked scientific decisions are the registry in this proposal; AI output will not add/drop specifications based on estimates or p-values.

## Pre-analysis declaration

Only the published-baseline reconstruction and structural diagnostics needed to identify a feasible pipeline have been run. Candidate item-count rules were checked to identify the published rule. A strict `FreqGoProvider` route was also inspected to diagnose a documentation/code contradiction: it retains 2,589 rather than 2,611 complete-seven valid-race records. Any nonbaseline effect encountered in either diagnostic is quarantined, unreported, and did not select a dimension or expected direction. Rank/separation preflight estimated no focal effects. No imputed, core-adjusted, grouped-age, fractional-logit, or crossed registered cell has been executed. Any COS-requested specification change will be versioned before affected alternatives run.
