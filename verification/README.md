# Independent R baseline verification

This directory contains a second implementation of the published Table 2
baseline. It is intentionally separate from the Python analysis package:
[`independent_r_baseline.R`](independent_r_baseline.R) reads the canonical Stata
file directly, reconstructs the seven-item PPPCQ score and baseline domain, and
uses R's `survey` package with the 50 official JK1 replicate weights.

The R script implements only the published baseline. It has no options for the
alternative sample, scoring, Asian-group, or variance choices, so running this
check cannot reveal a robustness result before approval.

## Requirements

- R and `Rscript`;
- the CRAN packages `digest`, `haven`, and `survey`; and
- the canonical public-use file at `data_raw/hints5_cycle2_public.dta`.

Install the R packages when needed:

```r
install.packages(c("digest", "haven", "survey"))
```

Package versions are not part of the Python production environment. Each R run
records its R and package versions in `metadata.csv`, and canonical continuous
integration installs and runs the same independent check.

## Run the check

From the repository root:

```bash
make verify-r-baseline
```

The command first regenerates the registered Python baseline. It then runs the R
implementation and requires agreement within `1e-9` for:

- all five official race/ethnicity group counts;
- all five weighted means, JK1 standard errors, and 95% intervals; and
- the Asian-minus-White difference, standard error, interval, and degrees of
  freedom.

The current implementations agree across all 30 checks; the largest absolute
difference is approximately `3.1e-14`.

## Generated output

The ignored `outputs/independent_r_baseline/` directory contains:

- `results.csv` — the five R group means and focal contrast;
- `metadata.csv` — source fingerprint, sample size, R/package versions, JK1
  coefficient, and design degrees of freedom;
- `comparison.csv` — one row for every R-versus-Python comparison; and
- `validation.json` — overall status, tolerance, and maximum difference.

The Python orchestration layer verifies the source fingerprint, compares the
two implementations, and publishes the four files together. It does not supply
R with derived variables or estimates.
