"""Behavior tests for scripts/check_discovery.py."""

from __future__ import annotations

import check_discovery

SAMPLE = """
\x1b[?25l│
◇  Found 2 skills
\x1b[?25h
│
◇  Available Skills
│
│    ph-one
│
│      Description text that is not a name.
│
│    ph-two
│
│      Another description.

│
└  Use --skill <name> to install specific skills
"""


def test_parse_discovered_reads_names_not_descriptions() -> None:
    assert check_discovery.parse_discovered(SAMPLE) == {"ph-one", "ph-two"}


def test_parse_discovered_ignores_output_before_heading() -> None:
    assert check_discovery.parse_discovered("│    ph-early\n") == set()


def test_parse_discovered_empty_output() -> None:
    assert check_discovery.parse_discovered("") == set()
