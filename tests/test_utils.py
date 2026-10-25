from pathlib import Path

import pytest

from odmk.exceptions import ODMKError
from odmk.utils import (
    OUTPUT_OWNERSHIP_CONTENT,
    OUTPUT_OWNERSHIP_MARKER,
    staged_output_directory,
)


def test_staged_output_directory_marks_first_published_set(tmp_path: Path) -> None:
    allowed_root = tmp_path / "outputs"
    destination = allowed_root / "results"

    with staged_output_directory(destination, allowed_root=allowed_root) as staging:
        (staging / "results.csv").write_text("new", encoding="utf-8")

    assert (destination / OUTPUT_OWNERSHIP_MARKER).read_text(
        encoding="utf-8"
    ) == OUTPUT_OWNERSHIP_CONTENT


def test_staged_output_directory_replaces_complete_artifact_set(tmp_path: Path) -> None:
    allowed_root = tmp_path / "outputs"
    destination = allowed_root / "results"
    destination.mkdir(parents=True)
    (destination / OUTPUT_OWNERSHIP_MARKER).write_text(
        OUTPUT_OWNERSHIP_CONTENT, encoding="utf-8"
    )
    (destination / "old.txt").write_text("old", encoding="utf-8")

    with staged_output_directory(destination, allowed_root=allowed_root) as staging:
        (staging / "results.csv").write_text("new", encoding="utf-8")
        (staging / "validation.json").write_text("{}", encoding="utf-8")

    assert not (destination / "old.txt").exists()
    assert (destination / OUTPUT_OWNERSHIP_MARKER).read_text(
        encoding="utf-8"
    ) == OUTPUT_OWNERSHIP_CONTENT
    assert (destination / "results.csv").read_text(encoding="utf-8") == "new"
    assert (destination / "validation.json").read_text(encoding="utf-8") == "{}"


def test_staged_output_directory_preserves_prior_set_on_failure(tmp_path: Path) -> None:
    allowed_root = tmp_path / "outputs"
    destination = allowed_root / "results"
    destination.mkdir(parents=True)
    (destination / OUTPUT_OWNERSHIP_MARKER).write_text(
        OUTPUT_OWNERSHIP_CONTENT, encoding="utf-8"
    )
    (destination / "old.txt").write_text("old", encoding="utf-8")

    with pytest.raises(RuntimeError, match="stop before publication"):
        with staged_output_directory(destination, allowed_root=allowed_root) as staging:
            (staging / "partial.csv").write_text("partial", encoding="utf-8")
            raise RuntimeError("stop before publication")

    assert (destination / "old.txt").read_text(encoding="utf-8") == "old"
    assert not (destination / "partial.csv").exists()


def test_staged_output_directory_rejects_path_outside_approved_root(
    tmp_path: Path,
) -> None:
    with pytest.raises(ODMKError, match="approved output root"):
        with staged_output_directory(
            tmp_path / "repository", allowed_root=tmp_path / "outputs"
        ):
            pass


def test_staged_output_directory_rejects_unowned_existing_directory(
    tmp_path: Path,
) -> None:
    allowed_root = tmp_path / "outputs"
    destination = allowed_root / "results"
    destination.mkdir(parents=True)
    (destination / "user-file.txt").write_text("preserve", encoding="utf-8")

    with pytest.raises(ODMKError, match="not owned"):
        with staged_output_directory(destination, allowed_root=allowed_root):
            pass

    assert (destination / "user-file.txt").read_text(encoding="utf-8") == "preserve"
