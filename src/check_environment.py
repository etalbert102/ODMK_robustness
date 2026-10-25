#!/usr/bin/env python3
"""Verify the runtime and pinned analysis dependencies."""

from __future__ import annotations

from odmk.environment import assert_frozen_environment


def main() -> None:
    environment = assert_frozen_environment()
    print(f"Python {environment['python']}; all pinned analysis dependencies match.")


if __name__ == "__main__":
    main()
