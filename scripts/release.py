#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create a tag and GitHub Release for every plugin version that has no tag yet.

Usage:
    uv run scripts/release.py [--dry-run]

Tags are named `<plugin>@v<version>`. Release notes are the plugin's CHANGELOG.md
section; without one, the commits that touched the plugin since its previous tag.
Re-running with all tags present does nothing. Needs full git history with tags and,
unless --dry-run, an authenticated `gh`.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def run(root: Path, *argv: str) -> str:
    result = subprocess.run(list(argv), cwd=root, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(f"{' '.join(argv)} failed: {result.stderr.strip()}")
    return result.stdout


def changelog_section(changelog: str, plugin: str, version: str) -> str | None:
    pattern = rf"^## {re.escape(plugin)} {re.escape(version)}(?: - [^\n]*)?\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, changelog, re.DOTALL | re.MULTILINE)
    return match.group(1).strip() if match else None


def commit_list(root: Path, plugin: str, tags: list[str]) -> str:
    previous = tags[0] if tags else None
    rev = f"{previous}..HEAD" if previous else "HEAD"
    log = run(root, "git", "log", "--format=- %s (%h)", rev, "--", f"plugins/{plugin}")
    return log.strip() or "No changes recorded."


def plugin_versions(root: Path) -> list[tuple[str, str]]:
    versions = []
    for meta in sorted(root.glob("plugins/*/.claude-plugin/plugin.json")):
        data = json.loads(meta.read_text())
        versions.append((data["name"], data["version"]))
    return versions


def publish(root: Path, gh: str, tag: str, sha: str, title: str, notes: str) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".md") as handle:
        handle.write(notes + "\n")
        handle.flush()
        run(
            root,
            gh,
            "release",
            "create",
            tag,
            "--target",
            sha,
            "--title",
            title,
            "--notes-file",
            handle.name,
        )


def release(root: Path, gh: str, *, dry_run: bool) -> list[str]:
    created: list[str] = []
    changelog = (root / "CHANGELOG.md").read_text()
    sha = run(root, "git", "rev-parse", "HEAD").strip()
    for plugin, version in plugin_versions(root):
        tag = f"{plugin}@v{version}"
        existing = run(root, "git", "tag", "--list", f"{plugin}@v*", "--sort=-v:refname").split()
        if tag in existing:
            print(f"skip {tag}: tag exists")
            continue
        notes = changelog_section(changelog, plugin, version) or commit_list(root, plugin, existing)
        print(f"{'would create' if dry_run else 'create'} {tag}")
        if not dry_run:
            publish(root, gh, tag, sha, f"{plugin} {version}", notes)
        created.append(tag)
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--gh", default="gh", help="gh executable (tests substitute a fake)")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    release(args.root, args.gh, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
