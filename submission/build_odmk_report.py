#!/usr/bin/env python3
"""Complete the COS outcome-report template from validated ODMK outputs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "sources/COS_outcome_report_template.docx"
RESULTS = ROOT / "outputs/multiverse/results.csv"
METADATA = ROOT / "outputs/multiverse/run_metadata.json"
R_METADATA = ROOT / "outputs/independent_r_baseline/metadata.csv"
R_VALIDATION = ROOT / "outputs/independent_r_baseline/validation.json"
OUTPUT = ROOT / "submission/ODMK_robustness_analysis_report.docx"


def _set_cell(cell, text: str) -> None:
    """Replace a form cell's answer while retaining its table formatting."""

    cell.text = text
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    for paragraph in cell.paragraphs:
        paragraph.paragraph_format.space_after = 0


def _keep_with_next(paragraph) -> None:
    """Keep a prompt with the one-cell answer table that follows it."""

    properties = paragraph._p.get_or_add_pPr()
    if properties.find(qn("w:keepNext")) is None:
        properties.append(OxmlElement("w:keepNext"))


def main() -> None:
    """Validate the run summaries and write the completed COS Word form."""

    results = pd.read_csv(RESULTS)
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    r_metadata = pd.read_csv(R_METADATA).set_index("field")["value"].to_dict()
    r_validation = json.loads(R_VALIDATION.read_text(encoding="utf-8"))

    if len(results) != 16 or not results["status"].eq("success").all():
        raise ValueError("The report requires 16 successful registered results")
    if int(results["is_baseline"].sum()) != 1:
        raise ValueError("The report requires exactly one registered baseline")
    if not (results["asian_minus_white_difference"] < 0).all():
        raise ValueError("The direction summary does not match every result row")
    if not (results["ci_high_95"] < 0).all():
        raise ValueError("The interval summary does not match every result row")
    if not r_validation["all_checks_pass"]:
        raise ValueError("The independent R baseline validation did not pass")

    estimate_min = results["asian_minus_white_difference"].min()
    estimate_max = results["asian_minus_white_difference"].max()
    se_min = results["standard_error_of_difference"].min()
    se_max = results["standard_error_of_difference"].max()
    p_min = results["two_sided_p_value"].min()
    p_max = results["two_sided_p_value"].max()
    closest_upper = results["ci_high_95"].max()

    document = Document(TEMPLATE)
    document.core_properties.title = "ODMK Robustness Analysis Report"
    document.core_properties.subject = "COS bounded-multiverse outcome report"
    document.core_properties.author = "Eli Talbert"

    study = document.tables[0]
    _set_cell(study.cell(0, 1), "Eli Talbert")
    _set_cell(study.cell(1, 1), "ODMK")
    _set_cell(study.cell(2, 1), "13 November 2026")
    _set_cell(study.cell(3, 1), "7 November 2026")

    document.paragraphs[4].text = (
        "☒  results_ODMK.csv, as set out in the Results File Specification"
    )
    document.paragraphs[5].text = "☒  Your code, as run"

    packages = metadata["package_versions"]
    software = (
        f"Python {metadata['python_version']}; pandas {packages['pandas']}; "
        f"NumPy {packages['numpy']}; SciPy {packages['scipy']}; and PyYAML "
        f"{packages['PyYAML']}. An independent baseline-only check used R "
        f"{r_metadata['r_version']} with survey {r_metadata['survey_version']}, "
        f"haven {r_metadata['haven_version']}, and digest "
        f"{r_metadata['digest_version']}."
    )
    _set_cell(document.tables[1].cell(0, 0), software)

    run_text = (
        "The analysis ran from clean public Git commit "
        f"{metadata['git']['commit']} using the hash-locked 2024-05-07 NCI "
        "HINTS 5 Cycle 2 Stata file. The code verified the approved registry and "
        "source-data hashes before opening the data, reproduced the published "
        "Table 2 anchors, and then ran the complete 2 × 2 × 2 × 2 design. Survey "
        "designs were created from the full 3,504-record file before restricting "
        "the focal domains. No random or iterative procedure was used."
    )
    _set_cell(document.tables[2].cell(0, 0), run_text)
    _set_cell(
        document.tables[3].cell(0, 0),
        "16. All registered combinations were run; none was excluded.",
    )
    _set_cell(
        document.tables[4].cell(0, 0),
        "0. Every row has status = ok.",
    )

    document.paragraphs[15].text = "☒  None — the study ran as registered"
    document.paragraphs[16].text = "☐  Differences, described below"
    differences = document.tables[5]
    _set_cell(differences.cell(1, 0), "None")
    _set_cell(differences.cell(1, 1), "The study ran as registered.")
    _set_cell(differences.cell(1, 2), "Not applicable")
    for column in range(3):
        _set_cell(differences.cell(2, column), "—")

    document.paragraphs[21].text = "☐  Yes"
    document.paragraphs[22].text = "☒  No"
    _set_cell(
        document.tables[6].cell(0, 0),
        "Not applicable. Before this robustness study, the analyst had not "
        "worked with this paper or HINTS 5 Cycle 2.",
    )

    document.paragraphs[26].text = "☒  Robust"
    document.paragraphs[27].text = "☐  Mixed"
    document.paragraphs[28].text = "☐  Not robust"
    assessment = (
        "All 16 reasonable, preregistered specifications supported the same "
        "conclusion: Asian respondents reported lower patient-provider "
        "communication quality than non-Hispanic White respondents. The "
        f"Asian-minus-White difference ranged from {estimate_min:.3f} to "
        f"{estimate_max:.3f} points on the 1–4 scale. Every 95% confidence "
        f"interval was below zero (the closest upper bound was {closest_upper:.3f}). "
        f"Standard errors ranged from {se_min:.3f} to {se_max:.3f}, and two-sided "
        f"p-values ranged from {p_min:.6f} to {p_max:.6f}. The inclusive any-Asian "
        "definition produced the largest shift in magnitude, while the partial-item "
        "scoring rule changed the estimate very little. The variance method changed "
        "uncertainty, as expected, but not point estimates."
    )
    _set_cell(document.tables[7].cell(0, 0), assessment)

    notes = (
        "The assigned result is the unadjusted Table 2 comparison, not the adjusted "
        "model in Table 3. The focal estimate is the survey-weighted Asian-minus-"
        "non-Hispanic-White PPPCQ mean difference. The published baseline used all "
        "five displayed race/ethnicity groups (N = 2,611); the COS results file's "
        "n_analytic field reports only respondents contributing to the focal two-group "
        "contrast (baseline: 105 Asian + 1,703 White = 1,808). Other records stayed "
        "in the full survey design object for variance estimation. The analysis used "
        "NCI's remediated 2024-05-07 public file, which reproduced the published "
        "Table 2 anchors. JK1 rows used 49 denominator degrees of freedom; Taylor "
        "rows used 98. The optional COS se_procedure, se_unit, and se_n_units fields "
        "are blank because each survey standard error was calculated directly by its "
        "registered estimator, not added later as a correction."
    )
    _set_cell(document.tables[8].cell(0, 0), notes)

    for index in (7, 9, 11, 13, 20, 24, 30, 32):
        _keep_with_next(document.paragraphs[index])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document.save(OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
