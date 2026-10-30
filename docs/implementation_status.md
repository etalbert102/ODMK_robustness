# Implementation status

Status as of 2026-10-28: the preregistered analysis is implemented and ready
for COS review, but production execution remains locked.

## Implemented

- deterministic expansion of registry revision 7 into 16 cells and eight
  point-estimate constructions;
- canonical-file hashing, schema checks, structural anchors, and design checks;
- both analytic-sample rules, both scale-completion rules, and both Asian
  category definitions;
- final-person weighted group means and the direct Asian-minus-White contrast;
- official 50-weight JK1 inference and Taylor-linearized inference;
- explicit records for failed cells without post-result substitutions;
- stable CSV outputs and JSON run provenance;
- COS approval, researcher approval, explicit CLI confirmation, and clean-Git
  production gates, plus an approved-registry checksum gate;
- transactional publication of each complete output artifact set within the
  repository output root, with ownership checks before replacement.

## Verification completed

- The registered production estimator reproduces the Table 2 baseline contrast,
  standard error, sample counts, and group means.
- Synthetic tests execute all 16 cells and confirm that d08 changes uncertainty
  only, not point estimates.
- A hand-calculated two-stratum example verifies the Taylor variance formula.
- A weighted, stratified domain fixture independently generated with R
  `survey` 4.5 verifies both Taylor group estimates and the contrast.
- Tests cover registry structure, outcome scoring, routing, race definitions,
  approval failures, data-scope protection, failed-cell retention, inferential
  consistency, and transactional output publication.
- The suite enforces at least 80% branch-aware coverage. CI separately acquires
  the public HINTS file, verifies its checksums, and requires the canonical
  baseline regression test.

## Deliberately not completed

No nonbaseline HINTS estimate has been calculated. `config/execution.yaml`
still records COS and researcher approval as pending, and the production
command exits before reading the HINTS file while either status is pending.
