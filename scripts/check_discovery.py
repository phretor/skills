#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare the skills `npx skills add . --list` discovers with plugins/*/skills/*/.

Usage:
    npx -y skills@<version> add . --list | uv run scripts/check_discovery.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
SKILL_LINE = re.compile(r"^│ {4}(\S+)\s*$")


def parse_discovered(output: str) -> set[str]:
    """Return skill names listed after the 'Available Skills' heading."""
    names: set[str] = set()
    listing = False
    for raw in output.splitlines():
        line = ANSI.sub("", raw)
        if "Available Skills" in line:
            listing = True
        elif listing and (match := SKILL_LINE.match(line)):
            names.add(match.group(1))
    return names


def expected_skills(root: Path) -> set[str]:
    return {path.parent.name for path in root.glob("plugins/*/skills/*/SKILL.md")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    discovered = parse_discovered(sys.stdin.read())
    expected = expected_skills(args.root)
    if not discovered:
        print("no skills found in `skills add --list` output")
        return 1
    for name in sorted(expected - discovered):
        print(f"not discovered by npx skills: {name}")
    for name in sorted(discovered - expected):
        print(f"discovered but not in plugins/*/skills/: {name}")
    if discovered != expected:
        return 1
    print(f"discovery matches: {', '.join(sorted(discovered))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
