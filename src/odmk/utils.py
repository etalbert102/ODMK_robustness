"""Small deterministic I/O and provenance helpers."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .exceptions import ODMKError


OUTPUT_OWNERSHIP_MARKER = ".odmk-generated-output"
OUTPUT_OWNERSHIP_CONTENT = "ODMK generated analysis output; safe to replace.\n"


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.exists():
        shutil.rmtree(path)


@contextmanager
def staged_output_directory(destination: Path, *, allowed_root: Path) -> Iterator[Path]:
    """Publish a complete, application-owned directory beneath ``allowed_root``."""

    requested_destination = destination.absolute()
    if requested_destination.is_symlink():
        raise ODMKError("Output destination cannot be a symbolic link")
    destination = requested_destination.resolve(strict=False)
    allowed_root = allowed_root.absolute().resolve(strict=False)
    if destination == allowed_root or allowed_root not in destination.parents:
        raise ODMKError(
            f"Output destination must be a child of the approved output root: {allowed_root}"
        )
    if destination.exists():
        if not destination.is_dir():
            raise ODMKError("Existing output destination must be a directory")
        marker = destination / OUTPUT_OWNERSHIP_MARKER
        if not marker.is_file() or marker.read_text(encoding="utf-8") != OUTPUT_OWNERSHIP_CONTENT:
            raise ODMKError(
                "Refusing to replace an output directory not owned by the ODMK runner"
            )

    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.staging.", dir=destination.parent)
    )
    backup: Path | None = None
    try:
        yield staging
        atomic_write_text(
            staging / OUTPUT_OWNERSHIP_MARKER, OUTPUT_OWNERSHIP_CONTENT
        )
        if destination.exists() or destination.is_symlink():
            backup = destination.with_name(
                f".{destination.name}.backup.{uuid.uuid4().hex}"
            )
            os.replace(destination, backup)
        try:
            os.replace(staging, destination)
        except Exception:
            if backup is not None and backup.exists():
                os.replace(backup, destination)
            raise
        if backup is not None:
            _remove_path(backup)
    except Exception:
        _remove_path(staging)
        raise


def git_value(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, check=True, text=True, capture_output=True
    )
    return result.stdout.strip()


def git_state(root: Path) -> dict[str, Any]:
    try:
        commit = git_value(root, "rev-parse", "HEAD")
        porcelain = git_value(root, "status", "--porcelain")
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}
    return {"commit": commit, "dirty": bool(porcelain)}
