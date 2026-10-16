# COS dimension audit: ODMK

## Audit standard

Each candidate was judged with the same question: could a competent analyst, before seeing the Asian-versus-White result, have chosen it while studying racial/ethnic differences in mean perceived patient-provider communication in the fixed 2018 HINTS C4 module population? Technical possibility alone was not enough.

The operational focal published result is Table 3 Model 1, conditional on COS confirmation because the sourcing sheet was not available locally. The proposed estimand is the survey-population-average PPPCQ mean contrast, **non-Hispanic Asian minus non-Hispanic White**, on the article's 1–4 scale. Fitted means are descriptively evaluated under Asian and White category codings over the cell's pooled observed covariate distribution using the final person weight; replicate estimates use the corresponding replicate weight for both fitting and averaging. Within each d02×d03 branch, those records are fixed across d05, d06, and d07. This is a descriptive standardized disparity, not a causal effect of race or an intervention on racial identity.

## d01 — Analytic sample construction

**Original decision.** The instrument intends C4 communication questions for respondents with `FreqGoProvider` 1–6. Exact reproduction implies a valid `RaceEthn5` value and complete responses to all seven C4 items, but it does not imply that the upstream filter must itself be observed.

**What the source permits.** The public file separates no visit (`FreqGoProvider = 0`), missing visit frequency, valid skips on C4, item nonresponse, and valid item responses. The fixed module population—an observed positive route or valid C4 content when the route is missing—contains 2,993 respondents. Thirty complete-seven respondents have a missing filter; 22 have valid race and contribute to the exact `N = 2,611` reconstruction. NCI's methodology rule preserves a missing filter when the follow-up was answered.

**Plausible alternatives.** A less restrictive item-completeness rule is plausible, but it is handled once under d03. A strict requirement that `FreqGoProvider` itself equal 1–6 would discard valid follow-up answers because of filter non-ascertainment and would not reproduce the paper. Requiring a narrower visit count, a usual source of care, internet access, English-language completion, or complete e-health exposure data would change the population or introduce an unrelated restriction.

**Same question?** Yes when the fixed module population is retained as the population of scientific interest and d03 is described as observed scoring coverage. Narrower visit, internet, or language restrictions do not preserve that population.

**Support.** The [annotated instrument](sources/HINTS5_Cycle2_Annotated_Instrument_English.pdf) and [codebook](sources/HINTS%205%20Cycle%202%20Public%20Codebook.pdf) show the intended route; the [methodology report](sources/HINTS5%20Cycle%202_Methodology%20Report.pdf) says an unanswered filter is left missing when the follow-up was answered.

**Status: Set aside.** The module population is fixed by an observed positive route or valid follow-up content. The strict-filter count is quarantined as routing QA, and partial-scale scoring is varied only under d03 to avoid counting one decision twice.

## d02 — Missing-data treatment

**Original decision.** Item nonresponse was not described. The exact Table 2 reconstruction implies deletion unless all seven PPPCQ items and race were valid. Missing-covariate handling in Table 3 is unresolved: the displayed `N = 2,611` suggests no loss beyond outcome/race, but the paper does not report imputation. NCI documented demographic hot-deck fields for weighting production; the current 2024 public file does not expose those `_I` fields, and it is unknown whether the authors used an earlier-release field.

**What the source permits.** Negative codes identify valid skips, filter-question missingness, response errors, and not-ascertained values. Among the 2,611 complete-outcome/race cases, a limited number lack at least one of the six reported covariates. The official design variables and weights can enter an imputation model.

**Plausible alternatives.** For covariates only: (A) a common complete-case frame requiring valid values for all six candidate covariates, whether the d06 core or full model is fitted; (B) 50-dataset MICE with race, d03-specific PPPCQ, all six candidate covariates, standardized log final weight, and categorical `VAR_STRATUM`. PSU fixed effects are excluded because the 100-cell representation creates separation in binary conditional models; PSU clustering enters analysis-stage uncertainty through official JK1 weights. This does not restore within-PSU dependence omitted during imputation, so the alternative is explicitly bounded rather than claimed fully design-congenial. Binary covariates use unpenalized logistic models and age uses five-donor type-1 predictive mean matching. Grouped age is passively derived. Race, PPPCQ items/scores, weights, and routing fields are never imputed. Exact draws, donor ties, rank/separation gates, substreams, and Barnard–Rubin pooling are frozen in [`specification_freeze.yaml`](specification_freeze.yaml).

**Same question?** Yes. Both target the same eligible US-adult population and the same racial contrast; they differ in whether respondents with missing adjustment variables contribute. Using all six candidate covariates to define the complete-case frame is a common-sample nested-model comparison, not an extra sample decision hidden inside d06.

**Support.** The HINTS [methodology report](sources/HINTS5%20Cycle%202_Methodology%20Report.pdf) defines missing codes and weighting-production imputations; NCI's [remediation notice](https://hints.cancer.gov/data/data-remediation.aspx) establishes later public-file changes. MICE and Rubin pooling were established before 2018; see White, Royston, and Wood (2011), <https://doi.org/10.1002/sim.4067>. Zhou et al. (2016), <https://pubmed.ncbi.nlm.nih.gov/28781418/>, motivates carrying survey-design information into imputation. It does not directly validate omission of PSU effects here. Multilevel/Bayesian imputation would introduce another extensive model family, so it is set aside rather than used as an unregistered repair.

**Status: Varied.** This is consequential because race, English proficiency, socioeconomic covariates, and outcome can jointly predict response; treating nonresponse as a reference response is explicitly prohibited.

## d03 — Outcome construction

**Original decision.** Seven equally weighted items were reverse-coded and averaged on a 1–4 scale. Exact reproduction implies all seven were required.

**What the source permits.** The same seven items can be averaged for respondents with partial valid response. There are 2,871 records with seven valid items, 58 with six, 9 with five, and 2 with four; thus only 69 source respondents have four to six valid items. The same-cycle NCI psychometric study found evidence for a unidimensional seven-item scale with alpha 0.92 and used a minimum of four valid responses.

**Plausible alternatives.** (A) mean of all seven, requiring seven valid items; (B) respondent mean of the same seven items, requiring at least four valid items. Both retain equal item weights and the article's 1–4 metric. The latter is a scoring rule, not single-value imputation.

**Same question?** Yes. Both measure the same seven-domain construct in the fixed C4 module population. The second changes observed scoring coverage, not the construct or population definition.

**Support.** The 2001 EORTC QLQ-C30 scoring manual provides a pre-ODMK general precedent for calculating a multi-item scale from the completed-item mean when at least half its items are answered: <https://www.eortc.org/app/uploads/sites/2/2018/02/SCmanual.pdf>. It is not PPPCQ validation. Moser et al. (2022), using HINTS 5 Cycle 2, supplies later same-instrument construct evidence and a minimum-four precedent: <https://doi.org/10.1371/journal.pone.0279725>. It did not validate that threshold across racial groups or missing patterns and was unavailable to ODMK's authors. Prespecified diagnostics report missingness and scoring coverage but cannot select a rule.

**Rejected alternatives.** A 0–100 transformation is pure rescaling. Sum versus mean is also rescaling when the same item-count rule is used. Dropping `HelpUncertainty`, factor weighting, or selecting a subset of items lacks a strong HINTS 5 Cycle 2 justification and changes the measured construct. Dichotomizing the score creates an arbitrary threshold and a different outcome.

**Status: Varied.** This is the strongest direct measurement decision.

## d04 — Main predictor construction

**Original decision.** Five mutually exclusive categories were derived from Hispanic ethnicity and race; non-Hispanic White is the reference, and the focal group is non-Hispanic Asian.

**What the source permits.** The official `RaceEthn5` derived variable and lower-level source components are available. A four-level derived field would absorb Asian respondents into a residual category; binary minority/nonminority codings are also mechanically possible.

**Plausible alternatives.** None that preserve the assigned Asian-versus-non-Hispanic-White contrast. Reconstructing `RaceEthn5` from its source variables is an audit check, not an analytic alternative.

**Same question?** Collapsing Asian with other groups, treating Hispanic ethnicity non-exclusively, or changing the reference group would alter or obscure the focal contrast. Changing the reference only relabels an otherwise identical fitted model and is cosmetic.

**Support.** The official [history document](sources/HINTS%205%20Cycle%202%20History%20Document.pdf) and codebook define `RaceEthn5`; its full-file frequencies exactly match the article.

**Status: No alternative available.** The focal predictor coding is fixed.

**Interpretive limit.** `RaceEthn5` aggregates Asian respondents across national origins, migration histories, and languages. The complete-seven focal frame contains 105 Asian respondents. The aggregate contrast cannot support subgroup claims, and every result will retain the group count and design-based uncertainty.

## d05 — Cutpoints/categories

**Original decision.** Race is categorical. Education, marital status, employment, and English proficiency were binary. Age's form is not reported; the literal reconstruction uses continuous years.

**What the source permits.** The file contains both exact age in years and the official five-level `AgeGrpB` derivation: 18–34, 35–49, 50–64, 65–74, and 75+. Both were defined before this robustness analysis. Education also has seven-, five-, or four-level official forms, but varying several covariate codings at once would bundle multiple decisions.

**Plausible alternatives.** (A) age entered linearly in years; (B) age entered as four indicators for the five official `AgeGrpB` categories, with 18–34 as reference. No knots or cutpoints are estimated from the focal result.

**Same question?** Yes, if these are only adjustment-variable forms. Race and outcome cutpoints are not varied.

**Support.** The HINTS codebook supplies both raw age and `AgeGrpB` as an official derived variable. Prespecified age-group adjustment was also used in the later same-cycle NCI scale validation.

**Status: Varied.** The paper leaves age form unresolved, age appears in both d06 adjustment families, and nonlinear age adjustment can change the focal standardized contrast when racial/ethnic groups have different age distributions. Unlike d08, this choice can affect the point estimate while preserving the population, predictor, outcome, and substantive question.

## d06 — Control variables

**Original decision.** The Methods name age, gender, education, employment, marital status, and English proficiency. The Table 3 note omits age and gender, although `F(10,40)` supports a ten-predictor Model 1: four race indicators plus six covariates.

**Conceptual classification.** Age and gender are basic demographic standardizers. Education, employment, and marital status are socioeconomic/social-position correlates that may both structure healthcare experiences and reflect consequences of racialized systems. English proficiency is a direct communication/language characteristic and may explain part of the disparity rather than act as a conventional pre-exposure confounder. None is labeled a causal confounder because race is not treated as a manipulable exposure and the paper's claim is descriptive.

**What the source permits.** All six are available, with the binary codings described in the article footnote. Many additional health-access, insurance, health-status, and e-health variables exist, but adding them would invite downstream adjustment or change the paper's H1 question.

**Plausible alternatives.** (A) a demographic core of age and gender; (B) the full published Methods set: age, gender, college graduation, married/living as married, current employment, and speaking English very well. Age takes the form selected under d05 in both families. Within each d02×d03 branch, both use exactly the same records and report the same weighted Asian-minus-White average standardized mean contrast.

**Same question?** Yes, with a qualification: the core set describes disparity standardized for basic demographics; the full set describes disparity additionally standardized for measured socioeconomic and language composition. Both are established interpretations of the paper's stated disparity question, but neither is causal. Because they answer distinguishable descriptive questions, results must be faceted by d06 rather than collapsed into a single robustness distribution.

**Support.** The paper itself motivates demographic, socioeconomic, and language covariates. The core/full family is theory-based and avoids one-at-a-time variable deletion.

**Rejected alternatives.** An unadjusted model is useful as the exact Table 2 validation but is not included in the 32 adjusted multiverse cells, because d02 would become irrelevant and produce duplicate/non-crossed cells. E-health variables are excluded from H1 because they are the paper's later moderators; healthcare access and health status may be downstream or redefine the adjusted question.

**Status: Varied.** This is likely the most substantively consequential model-specification decision.

## d07 — Model/functional form

**Original decision.** Survey-weighted linear regression treats the 1–4 composite as continuous.

**What the source permits.** The score is bounded, takes fractional increments when averaged, and has a substantial ceiling. Moser et al. report 33% at the upper bound under their scoring rule. Linear and fractional-response mean models can both return a population-average difference on the original scale.

**Plausible alternatives.** (A) identity-link survey-weighted linear regression; (B) probability-weighted fractional logit for `z = (PPPCQ − 1) / 3`, including boundary values, with the Asian-minus-White average marginal mean contrast standardized over the same records and multiplied by 3 to return to the 1–4 scale. In the full estimate, both fitting and prediction averaging use `PERSON_FINWT0`; in replicate `r`, both use `PERSON_FINWTr`. The fractional estimator explicitly solves `Σ_i w_i x_i(z_i − expit(x_i′β)) = 0` for the full and each replicate weight; its model-based covariance and likelihood summaries are ignored because JK1 supplies uncertainty. This avoids silently treating the HINTS weights as generic software frequency or variance weights. The fractional logit is a quasi-likelihood mean model and does not assert a beta density. See Papke and Wooldridge (1996), <https://doi.org/10.1002/(SICI)1099-1255(199611)11:6%3C619::AID-JAE418%3E3.0.CO;2-1>.

**Same question?** Yes, because both report the same population-average mean-scale contrast. Raw nonlinear coefficients or odds ratios will not be compared.

**Rejected alternatives.** An ordinal model would require treating the multi-valued composite as ordered categories and would not naturally return the same mean contrast. Dichotomization changes the outcome. Beta regression requires ad hoc treatment of exact endpoints unless a more complex boundary-inflated model is introduced; that added complexity is not warranted.

**Status: Varied.** This tests sensitivity to a bounded, ceiling-heavy conditional-mean specification without changing the reported estimand.

## d08 — Clustering/nesting/standard errors

**Original decision.** The authors used the 50 HINTS delete-one jackknife replicate weights in Stata survey procedures.

**What the source permits.** NCI provides both replicate weights and public Taylor design variables.

**Plausible alternatives.** Official JK1 and Taylor linearization are both technically supported. JK1 uses `PERSON_FINWT1`–`PERSON_FINWT50`, coefficient 0.98, and 49 denominator degrees of freedom. Taylor uses `PERSON_FINWT0`, `VAR_STRATUM`, and `VAR_CLUSTER`, with 98 denominator degrees of freedom. The alternatives leave the fitted point estimator unchanged.

**Same question?** Yes. This dimension changes sampling-variance approximation and inference, not the point estimand.

**Support.** The official [HINTS analytics recommendations](sources/HINTS%205%20Cycle%202%20Analytics%20Recommendation.pdf) describe both methods and note that Taylor estimates are often more conservative because the public design variables cannot reflect every calibration feature captured by replicate weights.

**Rejected alternatives.** IID model-based or weight-only heteroskedastic-robust errors ignore known design structure and are not peer alternatives when the official design information is present.

**Status: Set aside; JK1 fixed.** The authors used JK1, and NCI explains that the replicate weights better carry the variance effects of raking/calibration. Taylor remains a defensible software route, but varying an inference-only approximation is less substantively important than exposing the unresolved age representation. Fixing JK1 also reduces the risk that the multiverse is read as a search for significance thresholds. This is a source-authoritative guardrail, not a claim that survey uncertainty is unimportant.

## d09 — Survey weights/complex survey design

**Original decision.** Full person weights were used for point estimation; replicate weights were used for variance.

**What the source permits.** Weighted or unweighted software can be run. Weight rescaling is also possible but is immaterial to these normalized means/regressions when variance formulas are implemented consistently.

**Plausible alternatives.** None strong enough to vary. The estimand is the US noninstitutionalized adult population, and HINTS uses unequal probabilities, a high-minority sampling stratum, nonresponse adjustment, and raking. An unweighted analysis targets the respondent sample rather than the stated population. A “robust” unweighted regression does not repair that change.

**Same question?** No for unweighted analysis; it changes population representation. Weight trimming would create an analyst-selected target and is not recommended by HINTS for this release.

**Support.** The HINTS methodology report describes all stages embodied in `PERSON_FINWT0` and the replicate weights.

**Status: No alternative available.** Final person weighting is fixed, and the author/NCI-aligned JK1 implementation is fixed under d08.

## Selected five, ranked

1. **d06 control variables:** demographic core versus full published six-covariate adjustment.
2. **d03 outcome construction:** seven complete items versus at least four valid items on the same seven-item mean.
3. **d02 missing data:** complete-case covariates versus prespecified MICE for covariates only.
4. **d07 model/functional form:** linear mean model versus fractional-logit mean model, both reported as an average 1–4 mean contrast.
5. **d05 age functional form:** linear years versus the official five-category `AgeGrpB` representation.

All are binary and fully crossed, yielding `2 × 2 × 2 × 2 × 2 = 32` specifications. The C4 module population, race coding, final population weights, outcome items, non-age covariate coding, JK1 variance estimation, and focal contrast remain fixed; d03 varies observed scoring coverage. All cells will be listed, but substantive summaries will be split into 16 core-adjusted and 16 fully adjusted cells; no pooled robustness rate or distributional headline will combine the two interpretations.

## Strongest choices set aside

- **Variance estimator (d08):** Taylor linearization is officially supported, but JK1 matches the article and better carries the released calibration adjustments. Because d08 changes uncertainty rather than the point estimate, it is fixed rather than elevated over an unresolved substantive representation choice.
- **Unadjusted Table 2 analysis (d06):** retained as baseline validation, not a multiverse branch, because it makes covariate missing-data handling inapplicable and breaks the full factorial.
- **Unweighted estimation (d09):** rejected because it changes population representation in a deliberately unequal-probability survey.
- **Alternative race collapses (d04):** rejected because they erase or change the Asian-versus-White estimand.
- **Six-item or factor-weighted outcome (d03):** rejected for lack of a sufficiently strong same-cycle rationale and risk of changing the construct.
- **Dichotomized or ordinal outcome (d05/d07):** rejected because it changes the focal mean-scale quantity.
- **IID/weight-only robust errors (d08):** rejected because they omit documented design information.
