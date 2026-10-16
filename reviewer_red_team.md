# Reviewer Red Team: ODMK Table 2 proposal

## 1. COS robustness reviewer: “Four dimensions may be too narrow.”

**Objection.** COS normally targets about five consequential decisions, while
revision 7 proposes four.

**Response.** COS guidance permits fewer when a study does not support five
genuine dimensions. Adding covariate adjustment, a different outcome model, or
unweighted analysis would change the assigned Table 2 quantity or population;
a saturated weighted regression would be algebraically identical. Item-level
multiple imputation would overlap the partial-scale decision and introduce an
unvalidated response model. Four real decisions are preferable to a fifth
chosen to meet a quota.

## 2. Race-measurement reviewer: “Inclusive Asian coding changes the group.”

**Objection.** Moving multiracial respondents into the Asian group may redefine
the assigned contrast rather than test its robustness.

**Response.** The questionnaire permits more than one race selection, while
`RaceEthn5` forces non-Hispanic multiracial respondents into Other. The
alternative still requires non-Hispanic status and an explicit Asian selection,
and it keeps the reference fixed at `RaceEthn5=1`. It adds 21 multiracial Asian
respondents in the full source file and never collapses Asian respondents into
a generic minority category. Outputs will label the category rule prominently.

**Residual risk.** The inclusive group is broader, and neither aggregate Asian
definition supports national-origin, migration-history, or language-subgroup
claims.

## 3. Measurement reviewer: “The routing and four-item rules are not stated by the authors.”

**Objection.** A strict routing filter may discard answered communication data,
while the four-item rule relies partly on a later validation paper.

**Response.** The proposal presents neither option as the authors' hidden rule.
For d01, the source supports both the NCI content edit and a literal observed
filter; both target the same 12-month provider-contact population. For d03, the
four-item minimum is the smallest integer satisfying a prespecified half-scale
rule with a pre-ODMK general precedent. Moser et al. provides later
same-instrument feasibility evidence, not contemporaneous proof. The same seven
domains and 1–4 metric remain fixed, and no item is imputed.

**Safeguard.** Counts and missingness patterns may confirm implementation but
cannot be used to revise either rule after effects are seen.

## 4. Survey-methods reviewer: “Taylor changes only inference, and subgroup filtering can corrupt its variance.”

**Objection.** d08 does not alter point estimates, and a Taylor design created
after filtering to Asian and White records would lose design information.

**Response.** The assigned claim relies on confidence intervals, and NCI
officially documents both JK1 and Taylor methods, so uncertainty is part of the
result. The proposal now requires the survey design to be constructed from the
full public-use file before restrictions; eligibility and focal groups are
survey domains. d08 is labeled as an inference-only decision, and its paired
cells must have identical point estimates. The universe is therefore described
as eight distinct point-estimate constructions crossed with two variance
methods, not 16 distinct effect definitions.

## 5. Reproducibility reviewer: “The direct contrast is derived, and the proposal may already have inspected alternatives.”

**Objection.** Table 2 prints two marginal means rather than a direct contrast,
and structural counts for alternative rules were examined during planning.

**Response.** Every cell retains both assigned component means. Their
Asian-minus-White difference is a deterministic reporting contrast and is
labeled as derived rather than published. Only membership and missingness
counts were calculated for alternative rules; no nonbaseline mean, contrast,
standard error, interval, or p-value was computed. The source hash, registry,
execution environment, AI use, cell manifest, and failure record will be
preserved so this boundary can be audited.

## Specification-fishing audit

- **Were options chosen from focal estimates?** No. Only the published baseline
  was reproduced; alternatives came from survey structure, documentation,
  category construction, and measurement guidance.
- **Does any option change the substantive question?** The four options retain
  the Asian-versus-non-Hispanic-White PPPCQ population mean comparison. Their
  operational boundaries and residual risks are explicit.
- **Are there arbitrary thresholds?** The four-item minimum is the smallest
  integer satisfying the prespecified half-scale rule; it was not chosen from
  an effect estimate.
- **Are dimensions redundant or cosmetic?** No. d01 changes module membership,
  d03 changes score availability, d04 changes focal category membership, and
  d08 changes design-based uncertainty. Cosmetic rescalings and equivalent
  regression coding were rejected.
- **Will failures remain visible?** Yes. No post-result merging, substitution,
  or threshold revision is permitted.

## Reviewer recommendation

**Accept subject to ordinary COS review.** Revision 7 targets the exact sourcing
sheet result and defines four well-bounded peer decisions. Its 16 cells are
methodologically legible, its survey-domain implementation preserves the
released design, and its stop conditions prevent silent repair after results
are known.
