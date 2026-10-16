# Baseline analysis: ODMK

## Identification

- **Paper ID:** ODMK
- **Article:** Kim, H.-S., Kim, H. J., & Juon, H.-S. (2021), “Racial/Ethnic Disparities in Patient-Provider Communication and the Role of E-Health Use,” *Journal of Health Communication, 26*(3), 194–203. <https://doi.org/10.1080/10810730.2021.1919248>.
- **Source data:** 2018 Health Information National Trends Survey, HINTS 5 Cycle 2.
- **Assigned finding:** Asian respondents reported lower perceived patient-provider communication quality (PPPCQ) than non-Hispanic White respondents.

The article was inspected through the [author-uploaded full-text page](https://www.researchgate.net/publication/351109589_RacialEthnic_Disparities_in_Patient-Provider_Communication_and_the_Role_of_E-Health_Use); bibliographic metadata are preserved in [`sources/ODMK_PubMed_record.txt`](sources/ODMK_PubMed_record.txt).

## Where the focal result appears

The paper tests Hypothesis 1 most directly in **Table 2**, which reports survey-weighted PPPCQ means by the five race/ethnicity categories. The Asian group has the lowest reported mean, 3.11 (SE 0.10; 95% CI 2.90–3.33), compared with 3.45 (SE 0.02; 95% CI 3.39–3.49) for non-Hispanic White respondents. The paper interprets the confidence intervals as evidence that Asian and Hispanic respondents reported lower communication quality than non-Hispanic White respondents. A single Asian-minus-White mean difference is not printed.

The same contrast also appears in **Table 3, Model 1**, the first hierarchical regression: the published Asian indicator coefficient is −0.264 (SE 0.12, `p < .05`) with non-Hispanic White as reference. Because Table 2 is the direct H1 test and is exactly reconstructible, it is the clean published anchor. Table 3 is the operational adjusted-model target, conditional on COS confirmation, and an ambiguity diagnostic.

## Published Table 2 and reconstruction

| Group | Article group `n` | Published mean (SE) | Published 95% CI | Reconstructed analytic `n` | Reconstructed mean (SE) | Reconstructed 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| Non-Hispanic White | 1,983 | 3.45 (0.02) | 3.39–3.49 | 1,703 | 3.4457 (0.0242) | 3.3971–3.4944 |
| Non-Hispanic Black | 444 | 3.49 (0.05) | 3.38–3.59 | 360 | 3.4908 (0.0531) | 3.3841–3.5976 |
| Hispanic | 461 | 3.27 (0.04) | 3.17–3.37 | 337 | 3.2753 (0.0488) | 3.1772–3.3735 |
| Non-Hispanic Asian | 138 | 3.11 (0.10) | 2.90–3.33 | 105 | 3.1161 (0.1068) | 2.9015–3.3307 |
| Non-Hispanic Other | 125 | 3.33 (0.20) | 2.91–3.75 | 106 | 3.3367 (0.2090) | 2.9166–3.7567 |

The article's `n` column reproduces the full-file frequencies of `RaceEthn5`, not the nonmissing outcome counts used for the group means. The reconstructed analytic counts sum to 2,611, the focal analysis `N`. The paper appears to truncate some displayed values at two decimals; the underlying estimates agree within 0.01 and the intervals agree to the displayed precision.

The directly reconstructed **Asian-minus-White contrast** is −0.3296 PPPCQ points (JK1 SE 0.1097; 95% CI −0.5502 to −0.1091; `t(49) = −3.004`, two-sided `p = .0042`). This contrast is computed from the published-baseline group means and their replicate estimates; it is not a statistic printed in the article.

Machine-readable results are in [`outputs/table2_reproduction.csv`](outputs/table2_reproduction.csv) and [`outputs/baseline_summary.json`](outputs/baseline_summary.json).

## Variable construction

### Eligibility and outcome

**Explicitly stated by the authors**

- PPPCQ comprises seven HINTS items.
- Each source item is coded 1 “Always,” 2 “Usually,” 3 “Sometimes,” and 4 “Never.”
- The authors reverse-coded the items so higher values indicate better communication and averaged them into a 1–4 composite.
- The reported internal consistency was Cronbach's alpha 0.91.

**Verified from the NCI instrument/codebook**

The instrument routes C4a–C4g from `FreqGoProvider` values 1–6, indicating one or more non-emergency visits to a doctor, nurse, or other health professional during the prior 12 months. The methodology report also instructs that when a filter is missing but a follow-up is answered, the missing filter remains. The fixed C4 module population is therefore defined by an observed positive route or at least one valid C4 response when the filter is missing. It contains 2,993 respondents. Outcome-scoring rules determine observed analytic coverage within that target population; they do not redefine substantive eligibility. The seven variables are:

| Item | HINTS variable |
|---|---|
| Chance to ask all health-related questions | `ChanceAskQuestions` |
| Attention to feelings and emotions | `FeelingsAddressed` |
| Involvement in decisions as much as wanted | `InvolvedDecisions` |
| Made sure next self-care steps were understood | `UnderstoodNextSteps` |
| Explained things understandably | `ExplainedClearly` |
| Spent enough time | `SpentEnoughTime` |
| Helped with uncertainty about health or care | `HelpUncertainty` |

The code sets every value outside 1–4 to missing, reverses each valid response as `5 − source_value`, and takes the unweighted item mean.

**Inferred from exact reproduction**

The article does not state how many valid items were required. Requiring all seven items produces `N = 2,611` after valid race/ethnicity and reproduces every Table 2 mean and interval. This is therefore the strongest reconstruction of the published rule. It remains an inference because no author code is available.

The nested raw-data flow is:

| Stage | `n` |
|---|---:|
| Public-use file | 3,504 |
| Fixed C4 module population | 2,993 |
| At least one valid C4 communication response | 2,951 |
| All seven communication items valid | 2,871 |
| All seven items and `RaceEthn5` valid | 2,611 |
| Six-covariate complete-case diagnostic | 2,527 |

The source has 2,871 respondents with seven valid items, 58 with six, 9 with five, 2 with four, 5 with three, 6 with one, and 553 with zero. Thirty complete-seven records have `FreqGoProvider = -9`; 22 also have valid `RaceEthn5` and are part of the exact `N = 2,611` reconstruction. A strict observed-filter rule would retain only 2,589 and is used solely as a routing QA diagnostic, not as an alternative sample. The exact count and range checks are in [`outputs/qa_checks.json`](outputs/qa_checks.json). The reconstructed unweighted complete-seven alpha is 0.925; the later same-cycle NCI validation reports 0.92, while the ODMK article reports 0.91.

### Race/ethnicity

**Explicitly stated by the authors**

The paper derives five mutually exclusive groups from race and Hispanic ethnicity: non-Hispanic White, non-Hispanic Black, Hispanic, non-Hispanic Asian, and non-Hispanic Other. The Other category combines American Indian/Alaska Native, Native Hawaiian/Pacific Islander, and multiracial respondents. Non-Hispanic White is the regression reference category.

**Verified from data/documentation**

The official derived variable `RaceEthn5` exactly reproduces the five published full-file group counts: 1,983, 444, 461, 138, and 125; 353 records have code −9. The reconstruction uses valid codes 1–5 and never assigns missing race to a category.

### Covariates

**Explicitly stated in the Methods**

The text names age, gender, education, employment, marital status, and English proficiency. A footnote defines education as college graduate versus not, marital status as married/living as married versus not, employment as employed versus not, and English proficiency as “very well” versus otherwise.

**Literal source reconstruction**

- `Age`: continuous years, 18–97 in observed valid data;
- `GenderC`: female versus male;
- `Education`: codes 6–7 (college graduate/postgraduate) versus 1–5;
- `MaritalStatus`: codes 1–2 (married/living as married) versus 3–6;
- `Employed`: 1 versus 2;
- `SpeakEnglish`: 1 (“Very well”) versus 2–4.

All negative HINTS codes are treated as missing. This prevents “not ascertained” or response-error codes from silently entering a reference category.

### Survey weighting and variance

**Explicitly stated by the authors**

The paper says that full-sample weights and replicate weights were used, with delete-one jackknife variance estimation in Stata 15's survey procedures.

**Verified from NCI documentation**

The public file contains `PERSON_FINWT0` and `PERSON_FINWT1`–`PERSON_FINWT50`. The official [analytics recommendations](sources/HINTS%205%20Cycle%202%20Analytics%20Recommendation.pdf) specify JK1, `jkcoefs = 0.98`, and 49 denominator degrees of freedom for a single cycle. The [methodology report](sources/HINTS5%20Cycle%202_Methodology%20Report.pdf) documents two-stage address sampling, high-minority-stratum oversampling, within-household “next birthday” selection, nonresponse adjustment, raking, and replicate-weight construction.

## Statistical model

Table 2 uses survey-weighted means and 95% confidence intervals. Table 3 is a survey-weighted linear regression of the 1–4 PPPCQ composite, followed in later models by e-health variables and race-by-e-health interactions. The focal adjusted coefficient is the Asian indicator relative to non-Hispanic White in Model 1.

The transparent six-covariate complete-case reconstruction produces `N = 2,527` and an Asian coefficient of −0.2333 (JK1 SE 0.1324; 95% CI −0.4993 to 0.0327), rather than the published −0.264 (SE 0.12). No reasonable recoding was altered to force agreement. Full coefficients are in [`outputs/table3_model1_reconstruction.csv`](outputs/table3_model1_reconstruction.csv).

## Unresolved ambiguities

1. **External assignment scope.** No sourcing-sheet file was supplied or found locally. The proposal therefore operationally registers Table 3 Model 1 as the focal published result and uses Table 2 as the exact upstream validation anchor. The registry is conditionally frozen and no alternative is authorized until COS confirms that focal-table interpretation. If COS identifies Table 2 only, the registry must be versioned before any alternative is executed. This is an explicit preregistration choice, not a claim that the unavailable sheet was recovered.
2. **Table 3 covariate inconsistency.** The Methods name six covariates, but the Table 3 note lists only education, marital status, employment, and English proficiency. The reported `F(10,40)` is consistent with four race indicators plus six covariates, which supports the Methods description, but does not reveal coding.
3. **Missing-covariate treatment and public-release drift.** The article does not say how missing covariates were handled. The Table 3 displayed `N = 2,611` suggests no loss from the complete-outcome/race sample, while the six-covariate complete-case implementation yields 2,527. The [methodology report](sources/HINTS5%20Cycle%202_Methodology%20Report.pdf) documents hot-deck variables such as `Age_I`, `GenderC_I`, `Education_I`, and `MaritalStatus_I` for weighting production, but the current 2024 public-use Stata file does not expose those `_I` fields; NCI documents release changes on its [remediation page](https://hints.cancer.gov/data/data-remediation.aspx). They are not treated here as author analytic imputations, and it is unknown whether the authors used any fields available in an earlier release. This version difference may contribute to the Table 3 mismatch.
4. **Age and gender coding.** The article does not say whether age was centered or categorized, or which raw/derived field version was used.
5. **Routing-filter inconsistency.** The instrument's intended route is `FreqGoProvider = 1,...,6`, but the public data contain answered C4 items when that filter is missing. Following the methodology rule, the fixed module population includes either route evidence; d03 governs score availability within it. A stricter filter is quarantined as a QA count and is not a registered alternative.
6. **Published table precision.** Some displayed means/CIs look truncated rather than conventionally rounded.
7. **No author code.** No public analysis code or supplement was located, so these choices cannot be settled by inspection.

These ambiguities are not filled with guesses. The preregistration defines transparent, source-code-based rules, and the baseline report keeps the exact Table 2 reproduction separate from the imperfect adjusted reconstruction.
