# Output files

This directory contains two kinds of output. They are kept separate so that a
reviewer can distinguish historical baseline evidence from files produced by
the active Python package.

## Historical baseline evidence

The four tracked files at the top of this directory were generated on
2026-10-16 by the earlier baseline reconstruction:

- `baseline_summary.json`
- `exclusion_flow.csv`
- `qa_checks.json`
- `table2_reproduction.csv`

They are retained because the proposal cites them as baseline-only evidence.
They do not define the active analysis and are not the output format of the
current runner. Their numerical baseline agrees with the registered package.

## Active runner output

`make baseline` or `make verify-preapproval` writes the current baseline files
under `outputs/registered_baseline/`:

- `results.csv`
- `validation.json`
- `run_metadata.json`

That generated directory is ignored by Git because the files are reproducible
from the public HINTS source file.

`make verify-r-baseline` writes a separate independent cross-language check
under `outputs/independent_r_baseline/`. Its R results, runtime metadata,
30-row R-versus-Python comparison, and validation summary are also ignored
because they are reproducible from the public file.

After COS and researcher approval, `make multiverse` will write the 16 registered
analyses under `outputs/multiverse/`, together with the 4 by 4 specification
table, item-completion distribution, scoring-coverage table, validation record,
and run metadata. That command remains blocked while the approval record in
`config/execution.yaml` is pending.
