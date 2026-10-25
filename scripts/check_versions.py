#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fail when plugin files change without a version bump.

Usage:
    uv run scripts/check_versions.py --base origin/main

Compares HEAD against the merge base with --base. For every plugin whose files
changed, requires a higher semver in both plugin.json and the marketplace entry,
and requires CHANGELOG.md to change.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
MARKETPLACE = ".claude-plugin/marketplace.json"


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def read_json_at(root: Path, ref: str, path: str) -> dict | None:
    result = subprocess.run(
        ["git", "-C", str(root), "show", f"{ref}:{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return json.loads(result.stdout) if result.returncode == 0 else None


def parse_semver(value: object) -> tuple[int, int, int] | None:
    match = SEMVER.match(str(value))
    return (int(match[1]), int(match[2]), int(match[3])) if match else None


def marketplace_version(market: dict | None, plugin: str) -> str | None:
    for entry in (market or {}).get("plugins", []):
        if entry.get("name") == plugin:
            return entry.get("version")
    return None


def check_plugin(root: Path, base: str, head: str, plugin: str) -> list[str]:
    plugin_json = f"plugins/{plugin}/.claude-plugin/plugin.json"
    head_meta = read_json_at(root, head, plugin_json)
    if head_meta is None:
        return []
    new = parse_semver(head_meta.get("version"))
    if new is None:
        return [f"{plugin}: version {head_meta.get('version')!r} is not x.y.z"]
    head_entry = marketplace_version(read_json_at(root, head, MARKETPLACE), plugin)
    if head_entry != head_meta["version"]:
        return [
            f"{plugin}: marketplace version {head_entry!r} != plugin.json {head_meta['version']}"
        ]
    base_meta = read_json_at(root, base, plugin_json)
    if base_meta is None:
        return []
    old = parse_semver(base_meta.get("version"))
    if old is not None and new <= old:
        return [
            f"{plugin}: files changed but version {head_meta['version']} "
            f"is not above base {base_meta['version']}"
        ]
    return []


def check(root: Path, base: str, head: str = "HEAD") -> list[str]:
    merge_base = git(root, "merge-base", base, head).strip()
    changed = git(root, "diff", "--name-only", merge_base, head).splitlines()
    plugins = sorted(
        {p.split("/")[1] for p in changed if p.startswith("plugins/") and "/" in p[8:]}
    )
    if not plugins:
        return []
    errors: list[str] = []
    for plugin in plugins:
        errors += check_plugin(root, merge_base, head, plugin)
    if "CHANGELOG.md" not in changed:
        errors.append(f"CHANGELOG.md not updated but plugin files changed: {', '.join(plugins)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, help="base ref, e.g. origin/main")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    errors = check(args.root, args.base, args.head)
    for error in errors:
        print(error)
    if errors:
        print(f"\n{len(errors)} problem(s) found", file=sys.stderr)
        return 1
    print("version gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
