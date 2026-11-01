from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

from odmk.constants import RESULT_COLUMNS


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_MARKDOWN = sorted(
    [*ROOT.glob("*.md"), *ROOT.glob("docs/*.md"), *ROOT.glob("sources/*.md")]
    + [ROOT / "outputs" / "README.md"]
)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
MARKDOWN_HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*$", re.MULTILINE)


def _heading_anchors(document: Path) -> set[str]:
    """Return the GitHub-style anchors needed by this repository's headings."""

    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for heading in MARKDOWN_HEADING.findall(document.read_text(encoding="utf-8")):
        anchor = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        duplicate = counts.get(anchor, 0)
        counts[anchor] = duplicate + 1
        anchors.add(anchor if duplicate == 0 else f"{anchor}-{duplicate}")
    return anchors


def test_active_markdown_has_no_broken_local_links() -> None:
    broken: list[str] = []
    for document in ACTIVE_MARKDOWN:
        text = document.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().strip("<>")
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            relative_path, _, fragment = target.partition("#")
            linked_document = document.parent / unquote(relative_path) if relative_path else document
            if not linked_document.exists():
                broken.append(f"{document.relative_to(ROOT)} -> {target}")
                continue
            if fragment and linked_document.suffix == ".md":
                if unquote(fragment) not in _heading_anchors(linked_document):
                    broken.append(f"{document.relative_to(ROOT)} -> {target} (missing section)")

    assert not broken, "Broken local Markdown links:\n" + "\n".join(broken)


def test_active_markdown_has_no_trailing_whitespace_or_unclosed_fences() -> None:
    problems: list[str] = []
    for document in ACTIVE_MARKDOWN:
        lines = document.read_text(encoding="utf-8").splitlines()
        trailing = [
            str(number)
            for number, line in enumerate(lines, start=1)
            if line.rstrip() != line
        ]
        if trailing:
            problems.append(
                f"{document.relative_to(ROOT)} trailing whitespace on lines {', '.join(trailing)}"
            )
        if sum(line.startswith("```") for line in lines) % 2:
            problems.append(f"{document.relative_to(ROOT)} has an unclosed code fence")

    assert not problems, "Markdown hygiene failures:\n" + "\n".join(problems)


def test_output_schema_names_every_results_column() -> None:
    schema = (ROOT / "docs" / "output_schema.md").read_text(encoding="utf-8")
    missing = [column for column in RESULT_COLUMNS if f"`{column}`" not in schema]

    assert not missing, f"Output schema omits results columns: {missing}"


def test_baseline_table_uses_current_registered_white_estimate() -> None:
    baseline = (ROOT / "baseline_analysis.md").read_text(encoding="utf-8")

    assert "3.4457 (0.0242) | 3.3971–3.4944" in baseline
    assert "baseline validation tolerance of 0.011" in baseline
