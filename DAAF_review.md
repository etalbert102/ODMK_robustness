# DAAF-informed review of the ODMK proposal

## Review basis

The proposal was reviewed on 2026-10-15 against DAAF 3.0.2, commit
`4c5fc85138451a30a174b714fea18457b0d3f7a0` (released 2026-08-18). The review
used DAAF's goal-backward plan checks, validation checkpoints, survey-domain
guidance, audit-trail standard, and AI-disclosure guidance. COS's project
instructions remain controlling; DAAF was used as an internal quality lens.

## Improvements adopted

1. **Survey-domain estimation is now explicit.** The design must be created
   from the full public-use file before eligibility or focal-group restrictions.
   Restrictions are implemented as survey domains so strata and PSUs are not
   lost by filtering the raw data to Asian and White respondents.
2. **The universe is described more precisely.** d01, d03, and d04 create eight
   distinct point-estimate constructions; d08 crosses each with two variance
   estimators, yielding 16 inferential specifications.
3. **Execution gates are measurable.** Hash, schema, baseline sample size,
   published-mean tolerance, replicate-weight count, Taylor design structure,
   Cartesian-product size, and point-estimate equality across d08 are explicit
   stop conditions.
4. **Artifact wiring is specified.** Execution must produce a cell manifest
   linking each registered option set to its counts, weighted denominators,
   variance method, degrees of freedom, status, and failure reason.
5. **AI and environment provenance is clearer.** The record must identify the
   runtime and package versions, code commit, AI system and date of use, manual
   edits, automated checks, and researcher approval.

## Recommendations not adopted

- DAAF's post-result creative stress-testing tools were not used because COS
  requires this specification set to be chosen before alternative results are
  inspected.
- No fifth dimension was added. DAAF's scope and goal-backward checks support
  excluding tasks or choices that do not contribute to the stated estimand.
- The proposal does not claim to have run inside DAAF. Its current Python
  baseline was independently written and executed; DAAF supplied a review
  framework, not the analysis runtime.

## Result

The four substantive dimensions remain unchanged. The proposal is stronger at
the implementation boundary: it now states how to preserve the complex survey
design, when execution must stop, what artifacts every cell must produce, and
what human/AI provenance must be retained.
