# ODMK robustness-analysis proposal

## Proposed design

We propose 16 prespecified analyses of the Table 2 finding that Asian respondents reported lower perceived patient-provider communication quality (PPPCQ) than non-Hispanic White respondents. Using the public HINTS 5 Cycle 2 source data, we will vary four reasonable analytical choices: eligibility for the communication questions (d01), the number of answered items required to calculate PPPCQ (d03), the treatment of multiracial Asian identities (d04), and the method used to calculate uncertainty (d08). The communication domains, 1–4 outcome scale, non-Hispanic White comparison group, population weight, and target population remain fixed. The first three choices define eight group comparisons; applying two variance methods to each produces 16 analyses. We propose four rather than five dimensions because the remaining candidates would change the assigned question, duplicate an included choice, or require weakly supported assumptions.

## Paper and focal result

**Paper ID:** ODMK

**Citation:** Kim, H.-S., Kim, H. J., and Juon, H.-S. (2021). “Racial/Ethnic Disparities in Patient-Provider Communication and the Role of E-Health Use.” *Journal of Health Communication*, 26(3), 194–203. <https://doi.org/10.1080/10810730.2021.1919248>.

The COS sourcing sheet assigns the Table 2 comparison: Asian mean 3.11 (SE 0.10; 95% CI 2.90–3.33) versus non-Hispanic White mean 3.45 (SE 0.02; 95% CI 3.39–3.49). The article does not report the difference between these means. Each analysis will therefore retain the two weighted means and also report the Asian-minus-White difference on the 1–4 PPPCQ scale. A negative difference indicates a lower Asian mean.

Our reconstructed baseline gives an Asian mean of 3.1161 and a White mean of 3.4457. The derived difference is −0.3296 (JK1 SE 0.1097; 95% CI −0.5502 to −0.1091). This direct contrast is calculated from the reconstructed means and was not printed in the article.

## Data and baseline reconstruction

HINTS 5 Cycle 2 is publicly available from the US National Cancer Institute and requires no restricted-data application. We reconstructed the analysis from the 3,504-record public-use respondent file rather than from an author-created analytical dataset. We used the public codebook, survey instruments, methodology report, and NCI analytics guidance. No public author analysis code was located.

PPPCQ is the equal-weight mean of seven communication items: opportunity to ask questions, attention to feelings, involvement in decisions, understanding next steps, clear explanations, sufficient time, and help with uncertainty. Responses are reverse-scored as `5 − response`, so higher values indicate better communication.

The baseline:

1. includes respondents with `FreqGoProvider` in 1–6, plus respondents who answered at least one communication item when the routing response is missing;
2. requires valid answers to all seven communication items;
3. defines non-Hispanic Asian as `RaceEthn5=4` and non-Hispanic White as `RaceEthn5=1`;
4. uses `PERSON_FINWT0` for the weighted means; and
5. uses the 50 replicate weights for JK1 variance, with coefficient 0.98 and 49 denominator degrees of freedom.

This reconstruction gives the article’s Table 2 analytic `N = 2,611` across the five published race/ethnicity groups and reproduces their displayed means and intervals within rounding precision. The focal groups contain 105 Asian and 1,703 non-Hispanic White respondents. The article does not state the required number of completed items or its treatment of answered follow-ups with a missing routing response; the baseline rules above are therefore inferences supported by the successful reproduction.

## Proposed robustness dimensions

The alternatives below are peer analytical choices, not corrections to the original analysis. They were selected without examining their effects on the focal comparison.

### d01 — Eligible sample

**Baseline:** Include respondents with `FreqGoProvider` in 1–6 or at least one valid communication response when the routing field is missing. This follows NCI’s editing rule for answered follow-up questions.

**Alternative:** Require an observed positive routing response (`FreqGoProvider` in 1–6) and do not use answered follow-ups to resolve a missing routing field.

**Why reasonable:** Both rules identify respondents reporting on provider communication during the previous 12 months. One follows NCI’s answered-follow-up rule; the other follows the recorded routing response literally. Thirty respondents with all seven items have a missing routing response, including three in the official Asian group, so this choice determines who contributes to the means.

### d03 — PPPCQ scoring

**Baseline:** Calculate PPPCQ only when all seven items are valid.

**Alternative:** Calculate the equal-weight mean of the available items when at least four of the same seven are valid; do not impute missing items.

**Why reasonable:** Requiring all seven items reproduces Table 2. A later validation study using these HINTS 5 Cycle 2 items calculated the seven-item score for respondents with at least four valid responses (Moser et al., 2022). The alternative preserves the same communication domains and 1–4 scale while including respondents who answered four to six items. Sixty-nine respondents meet that condition. We will report completion patterns for both focal groups but will not revise the threshold after seeing results.

### d04 — Race/ethnicity construction

**Baseline:** Use the official mutually exclusive categories: Asian is `RaceEthn5=4`, White is `RaceEthn5=1`, and non-Hispanic multiracial respondents remain in “Other.”

**Alternative:** Define non-Hispanic Asian as `Hisp_Cat=10` plus at least one Asian checkbox (`AsInd`, `Chinese`, `Filipino`, `Japanese`, `Korean`, `Vietnamese`, or `OthAsian`), including respondents who selected another race. Keep the White group fixed at `RaceEthn5=1`.

**Why reasonable:** HINTS permits multiple race selections. A researcher could therefore use either the official mutually exclusive category or an inclusive “any Asian identification” category while preserving the Asian-versus-non-Hispanic-White comparison. The broader definition adds 21 non-Hispanic multiracial Asian respondents in the source file. Both definitions will be labeled clearly, and no national-origin subgroup claims will be made.

### d08 — Standard errors and confidence intervals

**Baseline:** Use all 50 official replicate weights with the JK1 coefficient of 0.98 and 49 denominator degrees of freedom.

**Alternative:** Use Taylor linearization with `PERSON_FINWT0`, `VAR_STRATUM`, and `VAR_CLUSTER`, with 98 denominator degrees of freedom.

**Why reasonable:** NCI documents both methods for HINTS 5 Cycle 2. They use the same population weight and must therefore produce identical point estimates; only the standard errors and confidence intervals may differ. The analysis will verify that invariance and report any failed specification without substituting an unregistered method.

## Dimensions not varied

- **d02 missing data — Set aside:** d03 already governs partial outcome-item data. Multiple imputation would duplicate that decision and add more assumption-heavy response modeling without PPPCQ-specific guidance; race will not be imputed.
- **d05 cutpoints/categories — Not applicable:** the focal outcome remains continuous, and no continuous predictor or control is categorized.
- **d06 controls — No alternative available:** adding controls to Table 2’s unadjusted weighted means would change the assigned result to an adjusted comparison.
- **d07 model/form — No alternative available:** group-indicator regression reproduces the direct weighted means; ordinal or median models estimate different quantities.
- **d09 weights — No alternative available:** the released population weight remains fixed (`PERSON_FINWT0`); unweighted estimates would describe the respondent sample rather than the same national population.

## Analysis and reproducibility

The four binary dimensions yield `2 × 2 × 2 × 2 = 16` analyses. For each, we will report the weighted Asian and White means, the Asian-minus-White difference, its standard error and 95% confidence interval, the two-sided p-value, group sizes, and the selected options. Interpretation will emphasize the size and uncertainty of the difference rather than whether individual specifications cross a significance threshold.

The analyses will be generated programmatically in Python using explicit, tested survey formulas and the released HINTS final and design weights. Each estimator will retain the full public-use file before applying the relevant analytical domain. Code, package versions, and specification labels will be retained so that all 16 analyses can be reproduced. Only the published baseline and structural feasibility checks have been run; no proposed alternative result has been calculated.

## Key methodological sources

- Kim, H.-S., Kim, H. J., and Juon, H.-S. (2021). “Racial/Ethnic Disparities in Patient-Provider Communication and the Role of E-Health Use.” *Journal of Health Communication*, 26(3), 194–203. <https://doi.org/10.1080/10810730.2021.1919248>.
- Moser, R. P., Trivedi, N., Murray, A., Jensen, R. E., Willis, G., and Blake, K. D. (2022). Patient-Centered Communication (PCC) scale: Psychometric analysis and validation of a health survey measure. *PLOS ONE*, 17(12), e0279725. <https://doi.org/10.1371/journal.pone.0279725>.
- National Cancer Institute. *HINTS 5 Cycle 2 Analytics Recommendations*.
- Westat. (2018). *Health Information National Trends Survey 5, Cycle 2 Methodology Report*.
