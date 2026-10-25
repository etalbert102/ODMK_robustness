# ODMK robustness-analysis proposal

## Recommended proposal in one paragraph

We propose 16 prespecified analyses of the Table 2 finding that Asian respondents reported lower perceived patient-provider communication quality (PPPCQ) than non-Hispanic White respondents. We will reconstruct the result from the original HINTS 5 Cycle 2 data and vary four reasonable choices. These concern eligibility for the communication questions (d01), the number of answered items needed to calculate PPPCQ (d03), the treatment of multiracial Asian identities (d04), and how uncertainty is calculated (d08). The first three choices define eight group comparisons; two uncertainty methods for each produce 16 analyses. The communication domains, 1–4 scale, White comparison group, population weight, and target population remain fixed. We will report both means and their difference, focusing on its size and uncertainty rather than statistical significance. We propose four rather than five dimensions because the remaining candidates would change the assigned question or duplicate an included choice.

## Paper and focal result

**Paper ID:** ODMK

**Citation:** Kim, H.-S., Kim, H. J., and Juon, H.-S. (2021). “Racial/Ethnic Disparities in Patient-Provider Communication and the Role of E-Health Use.” *Journal of Health Communication*, 26(3), 194–203. <https://doi.org/10.1080/10810730.2021.1919248>.

The COS sourcing sheet assigns the Table 2 comparison: Asian mean 3.11 (SE 0.10; 95% CI 2.90–3.33) versus non-Hispanic White mean 3.45 (SE 0.02; 95% CI 3.39–3.49). The authors interpret the confidence intervals as showing lower PPPCQ among Asian respondents. The article does not report the difference between the two means or its standard error.

For consistent reporting, each analysis will show both weighted means and the Asian mean minus the non-Hispanic White mean on the 1–4 PPPCQ scale. A negative difference means that the Asian mean is lower. This keeps the focus on Table 2 rather than replacing it with the adjusted coefficient from Table 3.

The reconstructed baseline gives an Asian mean of 3.1161 and a White mean of 3.4457. Their difference is −0.3296 (JK1 SE 0.1097; 95% CI −0.5502 to −0.1091). The difference is calculated from the reconstructed means; it was not reported in the article.

## Data source and feasibility

HINTS 5 Cycle 2 is publicly available from the US National Cancer Institute and requires no restricted-data application. The analysis uses the 3,504-record Stata file from the 2024-05-07 public bundle. Required materials are:

- the public-use respondent file;
- the public codebook and data dictionary;
- the annotated English and Spanish survey instruments;
- the methodology and sampling report;
- the analytics recommendations for final weights, replicate weights, JK1, Taylor linearization, and degrees of freedom;
- the history document and NCI remediation notice;
- the COS available-papers sheet and robustness guidance; and
- the COS-linked copy of the ODMK article.

The raw respondent file is preserved unchanged and verified by SHA-256. Source URLs, provenance, and checksums are recorded in `sources/source_manifest.csv`. No public author analysis code or supplementary analysis file was located.

## Baseline reconstruction

The patient-provider communication questions comprise seven C4 items: opportunity to ask questions, attention to feelings, involvement in decisions, understanding next steps, clear explanations, sufficient time, and help with uncertainty. Source responses 1–4 are reverse-scored as `5 − response` and equally averaged, so higher values indicate better communication on a 1–4 scale.

The baseline reconstruction:

1. includes respondents with `FreqGoProvider` in 1–6 or at least one valid C4 response when the routing filter is missing, following NCI's editing rule for answered follow-ups;
2. requires all seven C4 items to be valid;
3. uses official `RaceEthn5=4` for non-Hispanic Asian and `RaceEthn5=1` for non-Hispanic White;
4. uses `PERSON_FINWT0` for the two weighted means; and
5. uses `PERSON_FINWT1`–`PERSON_FINWT50` for JK1 variance, with coefficient 0.98 and 49 denominator degrees of freedom.

The survey design will be created before limiting the analysis to eligible respondents or the two focal groups. The code will mark who belongs in each analysis rather than first deleting everyone else. This preserves the full survey structure needed to calculate uncertainty correctly.

Under the baseline eligibility rule, 2,993 respondents belong to the communication-question population. Requiring all seven items and valid `RaceEthn5` produces the article's Table 2 analytic `N = 2,611` across all five race/ethnicity categories and reproduces every published group mean and interval within display precision. The two focal groups contain 105 Asian and 1,703 non-Hispanic White respondents.

The article does not state how many completed items were required or how it handled respondents who answered C4 despite a missing routing response. Requiring all seven items and retaining answered follow-ups reproduces the displayed Table 2 values and sample size. We therefore use that rule as the baseline while clearly labeling it as an inference.

## Proposed robustness dimensions

The dimensions are listed in order of methodological importance.

### 1. d04 — Race/ethnicity construction

**Baseline:** Use the official mutually exclusive `RaceEthn5` categories. Asian is `RaceEthn5=4`; non-Hispanic White is `RaceEthn5=1`. Non-Hispanic multiracial respondents remain in “Other.”

**Reasonable alternative:** Define non-Hispanic Asian as `Hisp_Cat=10` plus selection of at least one Asian checkbox—`AsInd`, `Chinese`, `Filipino`, `Japanese`, `Korean`, `Vietnamese`, or `OthAsian`—including respondents who also selected another race. Keep the comparison group fixed at `RaceEthn5=1`.

**Why reasonable:** The survey allows respondents to select more than one race. Researchers can therefore use either the official mutually exclusive category or an inclusive “any Asian identification” category while still asking the same Asian-versus-non-Hispanic-White question. The inclusive rule adds 21 non-Hispanic multiracial Asian respondents in the full source file; it does not combine Asian respondents with a broad minority category.

**Why it may matter:** The definition determines whose experiences contribute to the Asian mean. Because the Asian group is small, adding multiracial Asian respondents could affect the estimate. We do not predict a direction.

**Risk and safeguard:** This option uses a broader definition of the Asian group. Both definitions will be labeled clearly, the White group will remain fixed, and no claims will be made about specific national-origin groups.

### 2. d01 — Eligible sample

**Baseline:** Include respondents with `FreqGoProvider` in 1–6 or at least one valid C4 response when the filter is missing. This answered-follow-up rule gives 2,993 respondents.

**Reasonable alternative:** Require an observed positive routing response, `FreqGoProvider` in 1–6, without using answered C4 items to resolve a missing filter. This gives 2,961 module respondents before outcome and race requirements.

**Why reasonable:** Both rules aim to identify respondents reporting on communication with providers during the previous 12 months. The baseline follows NCI's rule for retaining answered follow-up questions; the alternative follows the recorded routing response literally. An analyst reconstructing eligibility could reasonably choose either rule before examining racial differences.

**Why it may matter:** Thirty respondents with all seven items have a missing routing response, including three respondents in the official Asian group. Including or excluding them changes who contributes to the group means.

**Risk and safeguard:** The strict rule may discard useful answers, while the baseline infers eligibility from answered follow-up questions. Neither rule will be described as correcting the other.

### 3. d03 — PPPCQ scoring

**Baseline:** Equally average the seven reverse-scored items only when all seven are valid.

**Reasonable alternative:** Equally average the available items when at least four of the same seven are valid. Do not fill in missing items.

**Why reasonable:** The all-seven rule reproduces the displayed Table 2 values and sample size. A common approach for multi-item scales is to calculate a score when at least half of the items were answered. A later HINTS 5 Cycle 2 study used a minimum of four responses for this same seven-item measure. That study shows that the rule is workable for this measure; it does not show that the original authors used it. A 2001 scoring manual provides an earlier general precedent for the half-scale rule.

**Why it may matter:** Item completion may be related to communication experiences or respondent characteristics. The alternative gives scores to some respondents who answered four to six items, using only their answered items. It keeps the same seven communication domains and the same 1–4 scale. Sixty-nine respondents have four to six valid items, so this is a limited but meaningful choice.

**Risk and safeguard:** Calculating a score from answered items assumes those items still represent the same communication construct. We will report item completion and weighted coverage overall and for both focal groups, but those checks cannot be used to change the four-item rule.

### 4. d08 — Standard errors and confidence intervals

**Baseline:** Use all 50 official replicate weights with JK1 coefficient 0.98 and 49 denominator degrees of freedom.

**Reasonable alternative:** Use Taylor linearization with `PERSON_FINWT0`, `VAR_STRATUM`, `VAR_CLUSTER`, and 98 denominator degrees of freedom, as documented for HINTS 5 Cycle 2.

**Why reasonable:** NCI documents both methods for this survey. JK1 matches the paper's description and uses the released replicate weights. Taylor linearization is an official alternative that uses the public stratum and cluster fields.

**Why it may matter:** Because the Asian group is small, the two methods may produce different standard errors and confidence intervals. They must produce identical group means because both use `PERSON_FINWT0` for those estimates.

**Risk and safeguard:** This dimension changes only how uncertainty is calculated, not the mean difference itself. Automated checks will require identical point estimates under both methods. If a Taylor analysis fails, it will be reported as failed rather than repaired with an unregistered method.

## Why four dimensions rather than five

COS guidance treats five dimensions as a target rather than a quota and permits fewer when the study supports fewer genuine choices. We did not add a fifth dimension because the remaining candidates would answer a different question, duplicate an included choice, or add weakly supported assumptions:

- **d02 missing data:** d03 already addresses partial outcome data with an established scale-specific rule. Item-level multiple imputation would overlap that choice and require a new response model with no PPPCQ-specific support. Race is not imputed.
- **d05 cutpoints/categories:** the focal mean remains continuous, and no continuous predictor or control is categorized.
- **d06 controls:** Table 2 is an unadjusted mean comparison. Adding controls would change it to an adjusted comparison.
- **d07 model/form:** weighted regression with only group indicators would produce the same means. Ordinal, median, or robust-location models would answer different questions.
- **d09 weights:** unweighted means describe the respondents in the file rather than the same national population. Weight trimming or recalibration would require unsupported new rules.

We also rejected changes that would only alter the units or answer a different question, including sum instead of mean scoring under the same completion rule, changing the reference label, splitting the outcome into categories, dropping communication domains, and changing the significance threshold.

## Number of analyses and reporting

The four two-option dimensions yield `2 × 2 × 2 × 2 = 16` analyses: eight ways of defining the sample, outcome, and Asian group, each paired with two methods for calculating uncertainty. Every analysis will be attempted and listed, including any failures. For each one, we will report the weighted Asian and White means, their difference, its standard error and 95% confidence interval, the test statistic, degrees of freedom, two-sided p-value, unweighted group sizes, weighted denominators, and the options used.

We will compare the size and uncertainty of the Asian-minus-White difference across all 16 analyses. Statistical significance will not determine which analyses are included, emphasized, or preferred. The article's group-specific confidence intervals will be shown for context, but the same direct difference will be used throughout.

## Software and reproducibility

The raw source file will remain unchanged. The existing Python reconstruction checks the source-data fingerprint, required fields, 3,504-row count, unique `HHID`, valid outcome ranges, race frequencies, weights, 50 replicate weights, sample sizes, and the published Table 2 values. This explicit JK1 calculation will remain an independent check of the baseline.

The 16 analyses will be estimated in Python with explicit, tested survey formulas. The Python and package versions will be fixed before any alternative result is calculated. JK1 will use the final weight and all 50 supplied replicate weights, coefficient 0.98, and 49 degrees of freedom. Taylor linearization will use `PERSON_FINWT0`, `VAR_STRATUM`, and `VAR_CLUSTER`, with 98 degrees of freedom. Both methods will retain the full survey design and then identify the respondents belonging in each analysis.

The analysis program must read `specification_freeze.yaml` revision 7 and generate all 16 combinations automatically. For each analysis, it will record the options used, the source-data fingerprint, eligible and focal-group counts, weighted denominators, variance method, degrees of freedom, completion status, and any reason for failure.

Before producing robustness results, the program must confirm that:

- the source file and required fields match the archived version;
- the baseline sample size is 2,611 and each displayed baseline mean is within 0.011 of the article;
- all 50 replicate weights are present;
- the Taylor design matches the HINTS documentation; and
- the program generates exactly 16 analyses.

Other automated checks cover data order, race coding, scoring rules, group overlap, and positive weights. They also verify preservation of the full survey design, baseline reproduction, Taylor degrees of freedom, identical point estimates across the two uncertainty methods, and visible reporting of failed analyses. A failed analysis may not be repaired by changing its population, race groups, outcome rule, or method after seeing the result.

AI may assist with code generation, testing, repetitive enumeration, and documentation. The analysis record will identify the AI system and date of use, the code and environment versions, the checks run, and any manual edits. The researcher will approve all scientific choices, verify the generated code and outputs, and remain responsible for the final analysis. AI output may not add or remove analyses based on estimates, intervals, or p-values.

## Pre-analysis declaration

Only the published Table 2 baseline and the structural checks needed to reconstruct it have been run. Before the COS sourcing sheet was available, we examined the adjusted Table 3 model; revision 7 removes that design, and Table 3 is not an alternative in this proposal. We used membership and missingness counts only to confirm that the proposed choices can be implemented. We have not calculated any alternative group mean, Asian-minus-White difference, standard error, confidence interval, or p-value. Any change requested by COS will be recorded before the affected analyses are run.

## Methodological references

- Center for Open Science. *Analytical Robustness Study: Guidance for Analysts and Reviewers*. Supplied project guidance, accessed 2026-10-15.
- Fayers, P. M., Aaronson, N. K., Bjordal, K., Groenvold, M., Curran, D., and Bottomley, A. (2001). *The EORTC QLQ-C30 Scoring Manual*, 3rd ed. <https://www.eortc.org/app/uploads/sites/2/2018/02/SCmanual.pdf>.
- Moser, R. P., Trivedi, N., Murray, A., Jensen, R. E., Willis, G., and Blake, K. D. (2022). Patient-Centered Communication (PCC) scale: Psychometric analysis and validation of a health survey measure. *PLOS ONE*, 17(12), e0279725. <https://doi.org/10.1371/journal.pone.0279725>.
- National Cancer Institute. *HINTS 5 Cycle 2 Analytics Recommendations*. Public survey-analysis guidance.
- Lumley, T. (2010). *Complex Surveys: A Guide to Analysis Using R*. Wiley.
- Westat. (2018). *Health Information National Trends Survey 5 (HINTS 5), Cycle 2 Methodology Report*.

## Companion submission files

- `specification_freeze.yaml` (revision 7)
- `baseline_analysis.md`
- `dimension_audit.md`
- `reviewer_red_team.md`
- `DAAF_review.md`
- `data_access.md`
- `sources/source_manifest.csv`
- `src/baseline_analysis.py`
- `src/preflight_registry.py`
- `outputs/table2_reproduction.csv`
- `outputs/exclusion_flow.csv`
- `outputs/qa_checks.json`
- `outputs/registry_preflight.json`
