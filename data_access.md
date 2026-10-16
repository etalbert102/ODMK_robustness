# Data and material access

## Canonical data release

The baseline uses the public HINTS 5 Cycle 2 Stata bundle currently distributed by the US National Cancer Institute (NCI):

- Data portal: <https://hints.cancer.gov/data/download-data.aspx>
- Canonical bundle: <https://hints.cancer.gov/dataset/HINTS-5_Cycle2_STATA_20240507.zip>
- Survey-materials portal: <https://hints.cancer.gov/data/survey-instruments.aspx>
- Data-remediation notice: <https://hints.cancer.gov/data/data-remediation.aspx>

The downloaded ZIP has SHA-256 `f204a161868056e243a3583ec343e3f4e4eb0b430a100e4d0e61996551a8b6ea`. The unmodified Stata member used in the analysis has SHA-256 `a727f1b7a56f293dc2212bb9cc8705cacdc4e57d6d8e5505012b713ecfd1531f`.

The current release is dated 2024-05-07. This matters because NCI's remediation page records removal of weighting-process variables not intended for analysis. The methodology report documents production hot-deck fields including `Age_I`, `GenderC_I`, `Education_I`, and `MaritalStatus_I`, but those `_I` fields are not present in the current Stata file. They are not treated as author analytic imputations. It remains unknown whether the authors used any derived field available in the release they analyzed, so public-release drift is an explicit possible contributor to the Table 3 mismatch. The final person weight, 50 replicate weights, and design variables required here remain present.

## Required files

The NCI bundle contains all required HINTS materials:

- `hints5_cycle2_public.dta` — 3,504 public-use respondent records;
- `HINTS 5 Cycle 2 Public Codebook.pdf` — variable names, response codes, skip criteria, and frequencies;
- `HINTS5_Cycle2_Annotated_Instrument_English.pdf` and the Spanish instrument — exact question wording and routing;
- `HINTS5 Cycle 2_Methodology Report.pdf` — sampling, weighting, nonresponse adjustment, raking, and JK1 construction;
- `HINTS 5 Cycle 2 Analytics Recommendation.pdf` — official examples for final weights, replicate weights, Taylor linearization, jackknife coefficient, and degrees of freedom;
- `HINTS 5 Cycle 2 History Document.pdf` — derived-variable history and release changes.

The source ledger in [`sources/source_manifest.csv`](sources/source_manifest.csv) records every copy, link, and checksum used. The article-access note is [`sources/ODMK_article_access_note.md`](sources/ODMK_article_access_note.md).

## Re-acquisition

From the project root:

```bash
curl -L --fail --retry 2 \
  'https://hints.cancer.gov/dataset/HINTS-5_Cycle2_STATA_20240507.zip' \
  -o sources/HINTS5_Cycle2_STATA_20240507.zip

unzip -j sources/HINTS5_Cycle2_STATA_20240507.zip \
  'hints5_cycle2_public.dta' -d data_raw
```

Before analysis, verify:

```bash
shasum -a 256 sources/HINTS5_Cycle2_STATA_20240507.zip \
  data_raw/hints5_cycle2_public.dta
```

`src/baseline_analysis.py` also refuses to run when the data hash differs, unless the analyst explicitly reviews a newer release and passes `--allow-hash-mismatch`.

## Survey design fields

The public file provides:

- `PERSON_FINWT0`: final person weight for population estimates;
- `PERSON_FINWT1`–`PERSON_FINWT50`: 50 JK1 replicate weights;
- `VAR_STRATUM` and `VAR_CLUSTER`: public design variables for Taylor-series variance estimation.

NCI recommends the 50 replicate weights for inference from one HINTS cycle, with JK coefficient 0.98 and 49 denominator degrees of freedom. NCI also documents Taylor linearization as a supported alternative using the final weight, `VAR_STRATUM`, and `VAR_CLUSTER`, with 98 denominator degrees of freedom for HINTS 5 Cycle 2. The final and replicate weights incorporate selection, nonresponse, and calibration adjustments; a weight-only robust standard error does not reconstruct that design.

## Access status and cost

The HINTS data and documentation are publicly obtainable and require no restricted-data application. Acquisition is therefore low risk and low cost. The article's version of record is paywalled, but an author-uploaded full-text page was available for inspection. If COS requires an archived publisher PDF in the submission package, the submitter should add a lawfully accessed copy; that is not needed to run the reconstruction.

## Data preservation rule

`data_raw/hints5_cycle2_public.dta` is never edited. All recoding is performed in `src/baseline_analysis.py`; the derived audit file is written to `data_processed/odmk_baseline_derived.csv.gz`. Generated estimates and QA records go to `outputs/`.
