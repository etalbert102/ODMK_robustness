# Reviewer Red Team

## 1. “The adjusted published coefficient was not exactly reproduced, so the multiverse lacks a valid baseline.”

**Objection.** Table 3 Model 1 reports an Asian coefficient of −0.264 (SE 0.12), whereas the literal six-covariate complete-case reconstruction gives −0.2333 (SE 0.1324). The paper's covariate note and Methods also conflict.

**Response.** The proposal does not conceal this mismatch. The upstream outcome/race/design reconstruction is unusually strong: all five Table 2 weighted means and intervals and the focal `N = 2,611` reproduce from raw public data. Table 3 Model 1 is the operational focal published result, and Table 2 is the validation anchor. The adjusted mismatch is localized to undocumented covariate form/missingness, possible public-release drift, and adjustment structure, exactly the uncertainty d02, d05, and d06 address. The baseline treats negative source codes as missing and uses the six covariates named in Methods; it will not tune recodes to recover −0.264. NCI documented weighting-production hot-deck fields that the current 2024 file does not expose, so earlier-release author use remains unresolved. Because the COS sourcing sheet was unavailable locally, revision 6 is conditionally frozen pending confirmation. No alternative is authorized until then; a Table 2-only assignment requires a versioned registry.

## 2. “The sample and minimum-four scoring rules may be post hoc reconstruction choices.”

**Objection.** The instrument routes C4 through `FreqGoProvider`, yet the exact reconstruction retains missing-filter records; the minimum-four precedent also appeared after ODMK.

**Response.** NCI's editing rule says a missing filter remains missing when a follow-up was answered. The fixed module population therefore includes an observed positive route or valid C4 follow-up content and contains 2,993 respondents. Thirty complete-seven respondents have a missing filter, including 22 with valid race; a strict-filter route yields 2,589 rather than the reproduced 2,611 and is quarantined as QA. d03 changes observed scoring coverage within the fixed population. The 2001 EORTC scoring manual provides a pre-ODMK general precedent for a completed-item mean when at least half a multi-item scale is answered; it does not validate PPPCQ. Moser et al. is later same-instrument construct evidence and a precedent, not threshold validation. Only 69 source respondents have four to six valid items, so d03 is principled but empirically narrow.

## 3. “Core versus full adjustment changes the estimand rather than testing robustness.”

**Objection.** English proficiency and socioeconomic variables may be pathways through which racialized conditions shape communication; conditioning on them changes interpretation.

**Response.** The proposal labels both effects as descriptive standardized disparities and makes no causal claim. The population, outcome, exposure, reported average Asian-minus-White mean contrast, and analysis records remain fixed within each d02×d03 branch. The complete-case option requires all six candidate covariates even for the core model, so d06 does not silently become a sample-selection decision. The two adjustment families correspond to recognizable peer questions already inside the article's conceptual frame: standardization for basic demographics, and additional standardization for socioeconomic/language composition. They are therefore reported as separate 16-cell panels. All 32 cells remain enumerated, but a single pooled robustness rate, median, range, or conclusion across both frames is prohibited. The report also avoids intervention language and states that the aggregate Asian category—with 105 respondents in the complete-seven descriptive frame—cannot represent national-origin or language heterogeneity.

## 4. “MICE introduces excessive analyst discretion and may be incompatible with the survey design.”

**Objection.** Imputation-model variables, algorithms, seeds, and pooling rules can become an unbounded hidden multiverse.

**Response.** Every choice is frozen: 50 imputations; covariates only; fixed initialization, order, burn-in, spacing, random substreams, exact type-1 PMM draws and donor ties, unpenalized logistic draws, passive age groups, JK1 within-imputation variance, and Barnard–Rubin pooling. A 100-cell PSU fixed-effect design was full rank but created complete/quasi separation for English proficiency in 19 cells, threatening both MICE branches. Revision 6 therefore registers standardized log full weight plus categorical stratum and retains PSU clustering in analysis-stage JK1 inference. It explicitly concedes that JK1 does not restore within-PSU dependence omitted during imputation. Multilevel/Bayesian imputation is set aside because it would add another extensive model family, not held out as a result-dependent repair. The no-effect preflight confirms full rank and nonseparation under both d03 frames.

## 5. “The proposed fractional-logit weights do not have defined survey semantics.”

**Objection.** Generic GLM software distinguishes frequency weights from inverse-variance weights; neither label, by itself, defines HINTS probability-weight estimation. Saying only “survey-weighted fractional logit” leaves the point estimator software-dependent.

**Response.** Revision 5 defines the estimator directly. For `z = (PPPCQ − 1)/3`, it solves `Σ_i w_i x_i[z_i − expit(x_i′β)] = 0` by deterministic damped Newton iteration using the full weight, then repeats that solve with each JK1 replicate weight. Predictions are averaged with the same weight used for that fit. Generic GLM frequency/variance-weight covariance, likelihood, deviance, residual degrees of freedom, AIC, and likelihood-ratio tests are ignored; only replicate contrasts supply uncertainty. Tests require invariance to positive constant weight rescaling and verify the category-evaluation design matrices. Thus the probability-weighted point estimator and design-based variance are reproducible independently of a software weight label.

## Pre-registration stress test

- **Could each choice be made before seeing the result?** Yes; the choices are tied to scale scoring, missing-data principles, a conceptual covariate hierarchy, an official source-defined age representation, and bounded-outcome mean modeling.
- **Was any choice selected by p-value or expected direction?** No. Limited scoring-rule diagnostics were required to identify the original baseline, but their nonbaseline effects were not used. None of the 32 registered cells has been executed.
- **Does any choice change the population?** No. The fixed module population is defined by an observed positive route or valid C4 follow-up content when the filter is missing. The scale rule changes observed scoring coverage within it. A strict observed-filter rule would discard 22 complete-response, valid-race records and is quarantined as QA.
- **Does any choice change the predictor or construct?** No. `RaceEthn5`, the Asian-versus-non-Hispanic-White contrast, and all seven PPPCQ domains are fixed.
- **Are cutpoints defensible?** The four-item minimum is an analyst choice, but it is fixed ex ante as the smallest integer satisfying a general half-scale rule with a pre-ODMK scoring precedent; it is not claimed to be PPPCQ-specific validation. The age bands come directly from official `AgeGrpB`.
- **Are dimensions redundant?** d03 governs outcome-item completeness; d02 governs missing adjustment variables; d06 governs which adjustment concepts enter on a common sample; d05 governs the form of age, which enters both d06 families.
- **Are cosmetic alternatives included?** No. Pure rescaling, sum versus mean, reference-label changes, and weight normalization are excluded.
- **Is the universe bounded and feasible?** Yes: five binary decisions, 32 cells, one public dataset, two prespecified estimators, two age representations, one fixed official JK1 variance engine, and deterministic QA. Input is sorted by unique `HHID`; rank, weight-rescaling, prediction-coding, OLS-equivalence, age-map, JK1-anchor, row-order, and pooling fixtures are mandatory. AI assistance can generate and test repetitive code without participating in specification selection.

## Reviewer verdict after revision

The proposal is defensible once COS confirms Table 3 Model 1 as the operational focal result and accepts the transparent adjusted reconstruction despite the article's reporting and release-version uncertainty. The exact Table 2 reproduction substantially reduces concern that the source data, outcome, race coding, or survey design were misidentified. Revision 6 cleanly separates the fixed target population from scoring coverage, narrows the survey-MICE claim, and supplies pre-ODMK half-scale and primary fractional-logit support. Execution remains blocked until focal-table confirmation, registry acceptance/versioning, a hash-locked environment, and all pre-run tests are complete. Every attempted cell, including failures, must then be reported regardless of significance or direction.
