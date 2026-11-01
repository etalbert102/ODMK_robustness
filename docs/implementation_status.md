# Implementation status

The preregistered analysis is implemented and ready for COS review, but
production execution remains locked.

## Implemented

- automatic creation of the same 16 analyses from registry revision 7;
- checks for the exact source file, required variables, expected sample counts,
  and survey structure;
- both eligible-sample rules, both PPPCQ completion rules, and both Asian-group
  definitions;
- population-weighted group means and the direct Asian-minus-White difference;
- official 50-weight JK1 and Taylor standard errors;
- a retained row and explanation for any failed analysis, with no substitution
  after results are seen;
- stable CSV result files and JSON records describing each run;
- the registered 4 by 4 result display and item-completion and scoring-coverage
  diagnostics for reviewer use;
- required COS and researcher approvals, explicit command-line confirmation,
  the approved registry fingerprint, and no uncommitted Git changes; and
- all output files written together, with safeguards against replacing files
  that were not created by this program.

## Verification completed

- The registered production estimator reproduces the Table 2 baseline contrast,
  standard error, sample counts, and group means.
- Synthetic tests execute all 16 analyses and confirm that d08 changes uncertainty
  only, not point estimates.
- A hand-calculated two-stratum example verifies the Taylor variance formula.
- An independent example generated with R `survey` 4.5 verifies the Taylor
  group means and their difference.
- A second R `survey` 4.5 example verifies the JK1 group means, standard errors,
  and their difference.
- Tests cover registry structure, outcome scoring, routing, race definitions,
  approval failures and clean-Git success, protection against running real data
  as synthetic data, retained failure records, internally consistent statistics,
  approval and run records, and safe output writing.
- Tests must cover at least 80% of code paths. Continuous integration separately
  downloads the public HINTS file, verifies its fingerprints, runs the real
  baseline command, checks its output files, and requires the real-data baseline
  test. GitHub actions are pinned to exact revisions.

## Deliberately not completed

No nonbaseline HINTS estimate has been calculated. `config/execution.yaml`
still records COS and researcher approval as pending, and the production
command exits before reading the HINTS file while either status is pending.
