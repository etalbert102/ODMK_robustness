# COS dimension audit: ODMK Table 2

## Audit standard

Each candidate was judged by one question: could a competent researcher using 2018 HINTS 5 Cycle 2 have made this choice before seeing the result while estimating the same population mean PPPCQ difference between Asian and non-Hispanic White respondents?

The COS sourcing sheet assigns the Table 2 descriptive means, not the adjusted Table 3 coefficient. The focal quantity is therefore the survey-weighted Asian mean minus the survey-weighted non-Hispanic White mean on the 1–4 seven-domain PPPCQ scale. The analysis is descriptive, not causal.

## Summary

| COS dimension | Status | Decision |
|---|---|---|
| d01 Analytic sample | **Varied** | Content-confirmed C4 eligibility vs literal positive routing filter |
| d02 Missing data | **Set aside** | No imputation; partial-scale handling is varied under d03 |
| d03 Outcome construction | **Varied** | Require 7/7 vs at least 4/7 valid PPPCQ items |
| d04 Main predictor | **Varied** | Official mutually exclusive Asian vs inclusive non-Hispanic any-Asian identification |
| d05 Cutpoints/categories | **Not applicable** | No continuous analysis variable is categorized |
| d06 Control variables | **No alternative available** | Adding controls changes the assigned marginal contrast |
| d07 Model/form | **No alternative available** | Equivalent models are cosmetic; non-equivalent models change the quantity |
| d08 Clustering/SE | **Varied** | Official JK1 vs official Taylor linearization |
| d09 Survey weights | **No alternative available** | Final-person weights are fixed to preserve the national target |

Four dimensions are varied. COS guidance treats five as a target and explicitly permits fewer when the study supports fewer genuine decisions. A fifth dimension is rejected rather than manufactured.

## d01 — Analytic sample construction

**Original decision.** The article says the seven communication questions refer to providers seen during the previous 12 months but does not give a row-level eligibility rule. Exact Table 2 reproduction retains respondents with complete C4 answers even when the routing filter is missing.

**What the source permits.** `FreqGoProvider` records the routing response. NCI's edit documentation says that a missing filter remains missing when a follow-up was answered. The source therefore permits both content-confirmed and literal-filter reconstructions of the intended module population.

**Plausible alternatives.** (A) Baseline content-confirmed population: `FreqGoProvider` in 1–6 or at least one valid C4 response. (B) Literal routing population: require `FreqGoProvider` in 1–6.

**Same question?** Yes. Both operationalize respondents with relevant provider experience during the same 12-month period; neither introduces a new visit window or healthcare-access restriction.

**Support.** The survey instrument defines the route; the methodology/history documentation supplies the answered-follow-up edit rule. The content-confirmed population is 2,993 and the literal positive-filter population is 2,961.

**Status: Varied.** Thirty complete-seven respondents have a missing filter, including three official Asian respondents. The decision can affect group membership while preserving the intended scientific population.

**Rejected sample alternatives.** Requiring a usual source of care, English fluency, e-health use, a particular provider type, or a narrower visit period would change the target population or question.

## d02 — Missing-data treatment

**Original decision.** The paper does not describe missing-item treatment. Exact reproduction implies that the published PPPCQ means required all seven valid items. Missing race values were excluded.

**What the source permits.** The seven C4 items contain both complete and partial response patterns. Sixty-nine source respondents have four to six valid items; 42 content-confirmed module respondents have no valid item. Race and demographic variables also contain missing values.

**Plausible alternatives.** Item-level multiple imputation is technically possible. Race imputation is also technically possible but is not appropriate for defining a focal self-identified racial category.

**Same question?** Outcome-item imputation could target the same eligible population, but its result would depend on an extensive conditional response model. Race imputation would make group membership model-derived rather than self-reported and is rejected.

**Support.** General multiple-imputation guidance exists, but no PPPCQ-specific imputation model was identified. A later same-cycle validation instead uses a transparent four-valid-item scoring rule.

**Status: Set aside.** The consequential, scale-specific missingness choice is registered under d03. Adding item-level imputation would overlap that choice, expand the universe with weakly anchored modeling decisions, and be selected mainly to fill a fifth slot.

## d03 — Outcome construction

**Original decision.** Seven reverse-scored 1–4 items were equally combined. The valid-item threshold is unstated; all seven valid items reproduce Table 2 exactly.

**What the source permits.** Every component item and its negative missing codes are available. The score can be calculated from complete responses or prorated across answered items while retaining the same seven intended domains and 1–4 range.

**Plausible alternatives.** (A) Require 7/7 valid items. (B) Require at least 4/7 and average the available reverse-scored items. Neither option imputes an item.

**Same question?** Yes. Both estimate mean PPPCQ using the same seven-item instrument. The alternative changes observed scoring coverage, not the target population or substantive construct.

**Support.** The EORTC QLQ-C30 scoring manual supplies a pre-ODMK general precedent for calculating a multi-item mean when at least half the items are answered. Moser et al. (2022) later used a four-valid-item threshold for this exact seven-item HINTS 5 Cycle 2 scale. The later study is same-instrument feasibility evidence, not proof of the original authors' rule or contemporaneous threshold validation.

**Status: Varied.** Sixty-nine respondents have four to six valid items, so this is a real inclusion/scoring decision rather than a rescaling.

**Rejected outcome alternatives.** Sum versus mean with identical completeness is pure rescaling. Transformation to 0–100 is also rescaling. Dichotomization changes the focal mean. Dropping domains, using a five-item cross-cycle subset, or estimating a latent factor changes the measured outcome more substantially and has weaker support for this assigned comparison.

## d04 — Main predictor construction

**Original decision.** The article reports five mutually exclusive categories. `RaceEthn5=4` identifies non-Hispanic Asian respondents and `RaceEthn5=1` identifies non-Hispanic White respondents. Multiracial non-Hispanic respondents are assigned to Other.

**What the source permits.** The questionnaire instructs respondents to select one or more races and provides separate indicators for Asian Indian, Chinese, Filipino, Japanese, Korean, Vietnamese, and Other Asian identification. Hispanic origin is separately available through `Hisp_Cat`.

**Plausible alternatives.** (A) Official mutually exclusive non-Hispanic Asian. (B) Inclusive non-Hispanic any-Asian identification: `Hisp_Cat=10` and any Asian checkbox selected, including multiracial selections. The non-Hispanic White reference remains `RaceEthn5=1` in both.

**Same question?** Yes, with an explicit boundary qualification. Both compare respondents identified as Asian with the same mutually exclusive non-Hispanic White reference. The alternative does not collapse Asian respondents into a broad minority group or change the reference.

**Support.** The source instrument itself authorizes multiple selections; the official history document shows how the mutually exclusive derived variable moves multiracial respondents to Other. The inclusive rule adds 21 non-Hispanic multiracial Asian respondents in the full source file.

**Status: Varied.** How multiracial Asian identification is represented is a substantive category-construction decision and especially relevant when the official Asian group is small.

**Risks and rejected alternatives.** The inclusive rule broadens the category and must be labeled. Hispanic any-Asian respondents remain outside the non-Hispanic focal group. Binary White/non-White coding, combining Asian with Other, changing the reference only, or national-origin subgroup analyses would change or obscure the assigned contrast.

## d05 — Cutpoints and categories

**Original decision.** PPPCQ is analyzed as a continuous mean. Race/ethnicity is inherently categorical and its construction is handled under d04. No continuous control enters Table 2.

**What the source permits.** PPPCQ could be dichotomized or divided into quantiles, but doing so would replace the assigned mean comparison.

**Plausible alternatives.** None that preserve the focal quantity.

**Same question?** No. A top-box proportion, median split, or other threshold estimates a different outcome.

**Status: Not applicable.** No continuous predictor or control is categorized in this pipeline. The minimum number of valid scale items is an outcome-scoring rule under d03, not a cutpoint on PPPCQ values.

## d06 — Control variables

**Original decision.** Table 2 reports unadjusted survey-weighted means. The covariates described later in the Methods belong to Table 3 moderation models.

**What the source permits.** Age, gender, education, marital status, employment, English proficiency, and other characteristics are available.

**Plausible alternatives.** Adjusted standardized means could be estimated mechanically, but they would no longer be the assigned marginal Table 2 means.

**Same question?** Not sufficiently. Adjustment would move from the population disparity as observed to a disparity standardized over selected characteristics. That may be valuable for another analysis, but it is a different estimand.

**Status: No alternative available.** No controls are used in any registered cell. The former Table 3 adjustment branches are retired rather than repurposed.

## d07 — Model and functional form

**Original decision.** Table 2 uses direct design-weighted group means.

**What the source permits.** The same means can be written as a saturated weighted linear model with race indicators. Ordinal, fractional, robust-location, and quantile models are also technically possible.

**Plausible alternatives.** The saturated weighted linear representation is algebraically identical and therefore not a genuine alternative. The other models do not estimate the same arithmetic mean difference.

**Same question?** Only the equivalent linear representation does, and it cannot provide robustness variation.

**Status: No alternative available.** Direct weighted means are fixed. Fractional logit from revision 6 is retired because with group indicators alone it is either saturated and reproduces the means or requires restrictions that alter the assigned quantity.

## d08 — Clustering, nesting, and standard errors

**Original decision.** The article describes delete-one jackknife replicate weights. Exact reconstruction uses all 50 official replicate weights, coefficient 0.98, and 49 degrees of freedom.

**What the source permits.** HINTS supplies both the replicate weights and the public `VAR_STRATUM`/`VAR_CLUSTER` fields. NCI documents JK1 and Taylor linearization for this cycle.

**Plausible alternatives.** (A) Official JK1 replicate-weight variance. (B) Taylor linearization with the final weight, public strata and clusters, and 98 degrees of freedom.

**Same question?** Yes. Both use the same final-person weight for point estimates and differ only in the design-based variance approximation.

**Implementation safeguard.** Construct the survey design from the full public-use file before applying eligibility, score-availability, or focal-race restrictions. Treat those restrictions as survey domains so non-domain records and released design units remain available to variance estimation. Do not create a Taylor design from an Asian-and-White-only file.

**Support.** The HINTS 5 Cycle 2 Analytics Recommendations document both implementations.

**Status: Varied.** The focal Asian group is small, so uncertainty estimation is consequential. A mandatory invariant requires identical point estimates across d08.

**Rejected inference alternatives.** Weight-only heteroskedasticity-robust errors ignore the released design. Normal critical values ignore the documented finite survey degrees of freedom. Alternative significance thresholds and multiple-comparison adjustments are outside the assigned question.

## d09 — Survey weights and complex design

**Original decision.** The paper uses sampling weights to make population inferences. `PERSON_FINWT0` exactly reconstructs Table 2.

**What the source permits.** Analysts can mechanically calculate unweighted sample means, but the public file supplies one final-person weighting system for the 2018 population target.

**Plausible alternatives.** None that preserve the same national population mean. Weight trimming or recalibration would require new thresholds or external margins not justified by the paper.

**Same question?** Unweighted means describe the realized respondent sample, not the same HINTS population target.

**Status: No alternative available.** Final-person weighting is fixed; d08 varies how its sampling uncertainty is calculated.

## Selected dimensions ranked by importance

1. **d04 race construction:** directly changes who counts as Asian while preserving the focal reference.
2. **d01 sample construction:** resolves a documented routing-versus-content conflict that affects focal-group membership.
3. **d03 outcome construction:** changes score availability under an established scale-prorating rule.
4. **d08 variance estimation:** uses two official HINTS design-based methods and may matter for a small focal group.

The four binary decisions yield 16 fully crossed specifications. The strongest rejected candidates—adjustment, unweighted means, multiple imputation, and alternative outcome models—were set aside because they change the assigned quantity or population, duplicate a selected choice, or require substantially weaker assumptions.
