# Baseline analysis: ODMK

## Assigned result

- **Paper ID:** ODMK
- **Paper:** Kim, H.-S., Kim, H. J., and Juon, H.-S. (2021), “Racial/Ethnic Disparities in Patient-Provider Communication and the Role of E-Health Use.”
- **Source data:** 2018 HINTS 5 Cycle 2 public-use respondent file.
- **COS-assigned finding:** Table 2 reports lower mean perceived patient-provider communication quality (PPPCQ) among Asian respondents than among non-Hispanic White respondents.
- **Published values:** Asian mean 3.11 (SE 0.10; 95% CI 2.90–3.33) and non-Hispanic White mean 3.45 (SE 0.02; 95% CI 3.39–3.49).

The COS available-papers sheet quotes these Table 2 values directly. Table 3 Model 1 is therefore not the focal result. Its adjusted Asian coefficient was examined earlier only while the assignment was unresolved and is excluded from registry revision 7.

## Focal quantity

The article prints the two group means and marginal confidence intervals, then states that Asian respondents reported significantly lower PPPCQ than non-Hispanic White respondents. It does not print the Asian-minus-White mean difference or a standard error for that direct contrast.

For reproducible reporting, the focal quantity is:

`survey-weighted Asian PPPCQ mean − survey-weighted non-Hispanic White PPPCQ mean`

Both component means remain required outputs. The direction is fixed so a negative value indicates lower PPPCQ among Asian respondents.

## Published Table 2 and reconstruction

| Race/ethnicity | Full-file n shown in paper | Published mean (SE) | Published 95% CI | Reconstructed analytic n | Reconstructed mean (SE) | Reconstructed 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| Non-Hispanic White | 1,983 | 3.45 (0.02) | 3.39–3.49 | 1,703 | 3.4457 (0.0243) | 3.3968–3.4945 |
| Black | 444 | 3.49 (0.05) | 3.38–3.59 | 360 | 3.4908 (0.0531) | 3.3841–3.5976 |
| Hispanic | 461 | 3.27 (0.04) | 3.17–3.37 | 337 | 3.2753 (0.0488) | 3.1772–3.3735 |
| Non-Hispanic Asian | 138 | 3.11 (0.10) | 2.90–3.33 | 105 | 3.1161 (0.1068) | 2.9015–3.3307 |
| Non-Hispanic Other | 125 | 3.33 (0.20) | 2.91–3.75 | 106 | 3.3367 (0.2090) | 2.9166–3.7567 |

The reconstructed analytic counts total `N = 2,611`, matching the sample size shown in the Table 2 notes for the e-health comparisons. Every PPPCQ group mean and interval matches within display precision.

The directly reconstructed Asian-minus-White difference is −0.3296 PPPCQ points (JK1 SE 0.1097; 95% CI −0.5502 to −0.1091; `t(49) = −3.004`, two-sided `p = .0042`). This is a derived reporting quantity, not a statistic printed by the authors.

## Outcome construction

### Facts stated by the authors

- PPPCQ is a composite of seven four-point items.
- Responses are reverse-coded so `1 = Never` and `4 = Always` after scoring.
- The seven items cover asking questions, attention to feelings, involvement in decisions, understanding next steps, clear explanations, sufficient time, and help with uncertainty.
- The reported internal consistency is `α = .91`.

### Source variables

1. `ChanceAskQuestions`
2. `FeelingsAddressed`
3. `InvolvedDecisions`
4. `UnderstoodNextSteps`
5. `ExplainedClearly`
6. `SpentEnoughTime`
7. `HelpUncertainty`

Valid source responses are 1–4. The reconstruction applies `5 − response` and averages the seven reverse-scored values.

### Inferred baseline rule

The article does not state how many valid items were required. Requiring all seven items gives `N = 2,611` after valid official race/ethnicity and exactly reproduces every Table 2 PPPCQ estimate. Registry revision 7 therefore treats all seven valid items as the baseline rule while labeling it as an inference.

## Analytic population and routing

`FreqGoProvider` is the routing item for the C4 communication module. The NCI editing rule states that a missing filter remains missing when a respondent answered a follow-up item. The baseline therefore defines the content-confirmed module population as:

- `FreqGoProvider` in 1–6; or
- at least one valid C4 response when `FreqGoProvider` is missing.

This population contains 2,993 respondents. A literal positive-filter rule contains 2,961. Thirty respondents with all seven C4 items have a missing filter; 22 have valid official race/ethnicity, including three official Asian respondents. This unresolved operational choice is varied as d01 rather than hidden.

## Race/ethnicity construction

### Facts stated by the authors

The article reports five mutually exclusive groups: non-Hispanic White, Black, Hispanic, Asian, and Other. The public `RaceEthn5` variable reproduces all five Table 2 estimates and is the baseline source variable.

### Source-data alternative

The questionnaire allows one or more race selections and provides separate indicators for Asian Indian, Chinese, Filipino, Japanese, Korean, Vietnamese, and Other Asian identification. The official `RaceEthn5` variable assigns non-Hispanic multiracial respondents to “Other.”

An inclusive non-Hispanic any-Asian rule—`Hisp_Cat=10` and at least one Asian checkbox selected—contains every official Asian respondent plus 21 multiracial respondents in the full file. It is registered as d04 while the non-Hispanic White definition remains `RaceEthn5=1`.

## Survey design

### Facts stated by the authors

- Analyses were weighted in Stata using `svy`.
- Full-sample weights adjust for unequal selection, household nonresponse, person selection, and population calibration.
- Replicate weights were constructed with delete-one jackknife.

### Source documentation

- `PERSON_FINWT0` is the final person weight.
- `PERSON_FINWT1`–`PERSON_FINWT50` are the 50 JK1 replicate weights.
- NCI specifies JK1 coefficient 0.98 and 49 denominator degrees of freedom.
- NCI also documents Taylor linearization using `PERSON_FINWT0`, `VAR_STRATUM`, and `VAR_CLUSTER`, with 98 denominator degrees of freedom for this cycle.

The exact Table 2 reconstruction uses the final weight for point estimates and JK1 for uncertainty. Taylor linearization is the registered d08 alternative; it must reproduce the same point estimates.

For production inference, the survey design will be created from the full public-use file before analytic or focal-group restrictions are applied. Eligibility, score availability, and race groups will be represented as survey domains. This preserves the released strata and clusters for variance estimation and prevents an Asian-and-White-only data filter from redefining the design.

## Missingness and exclusion flow

| Stage | N |
|---|---:|
| Public-use file | 3,504 |
| Content-confirmed C4 module population | 2,993 |
| At least one valid C4 item | 2,951 |
| All seven C4 items valid | 2,871 |
| All seven valid plus official `RaceEthn5` | 2,611 |

Within the full source file, 69 respondents have four to six valid items. The d03 alternative scores these partial responders from their available items when at least four are present. No outcome item, race value, routing field, weight, or design field is imputed.

## Automated baseline checks

`src/run_registered_baseline.py`, through the shared `src/odmk/` package,
verifies:

- the canonical data SHA-256;
- 3,504 rows and unique, nonmissing `HHID`;
- required C4, race, routing, weight, and design fields;
- 50 replicate weights and valid weight ranges;
- the 2,993 content-confirmed module count;
- the seven-item PPPCQ range;
- official `RaceEthn5` frequencies;
- focal analytic `N = 2,611`; and
- agreement with all five published Table 2 means, JK1 standard errors, and
  confidence intervals, plus the focal direct-contrast uncertainty;
- revision 7 registry structure and the 16-cell Cartesian product;
- routing and scoring-coverage anchors;
- official and inclusive Asian membership and focal-group disjointness; and
- the complete Taylor design structure.

The runner selects only the registered baseline cell. These checks therefore
calculate no nonbaseline group mean or effect.

## Remaining ambiguities

1. **Outcome completeness:** the all-seven rule is inferred from exact reproduction because the article does not state it.
2. **Routing:** the article does not say whether answered C4 items were used when `FreqGoProvider` was missing.
3. **Race-category boundary:** the article describes five categories but does not discuss respondents selecting Asian with another race.
4. **Published group comparison:** the article relies on the displayed marginal confidence intervals rather than printing a direct Asian-minus-White contrast.
5. **Exact survey command details:** the article names `svy` and jackknife weights but does not print the full Stata declaration. The NCI documentation and exact Table 2 reproduction resolve the baseline implementation as closely as the public record permits.

These ambiguities are exposed as registered choices or reporting qualifications. No reasonable coding decision is altered merely to force numerical agreement.
