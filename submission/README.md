# Final COS deliverables

This directory contains the final aggregate deliverables from the approved
ODMK robustness run completed on 2026-11-13:

- `results_ODMK.csv`: the 16 registered specifications in COS's required
  29-column format;
- `ODMK_robustness_analysis_report.docx`: the completed COS outcome-report
  template;
- `ODMK_robustness_analysis_report.pdf`: a convenience rendering of the same
  report; and
- `build_odmk_report.py`: the deterministic report builder. Install its two
  document-specific dependencies with
  `python3 -m pip install -r submission/requirements-reporting.txt`.

The analysis ran from commit
`0e796cbc4457020587c76ad39df906bfc37ecd66`. Native Python outputs and the
independent R baseline check are under `../outputs/`. Raw HINTS respondent data,
local render images, and expanded submission archives remain excluded from Git.
