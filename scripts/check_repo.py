#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check repository structure against the rules in AGENTS.md.

Usage:
    uv run scripts/check_repo.py [--root PATH]

Exits 1 and prints one line per violation.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

PLUGIN_JSON_FIELDS = ("name", "version", "description", "author")
ALLOWED_SKILL_KEYS = {
    "name",
    "description",
    "allowed-tools",
    "compatibility",
    "license",
    "metadata",
}
SKILL_SECTIONS = ("## When to Use", "## When NOT to Use")
README_SECTIONS = ("## When to Use", "## When NOT to Use", "## What It Does")
MAX_SKILL_LINES = 500
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
BLOCK_SCALAR = re.compile(r"^[>|][+-]?$")
SHIPPED_SUFFIXES = {".md", ".yaml", ".yml", ".py"}
IGNORED_DIRS = {".git", "node_modules", ".venv", "__pycache__", ".ruff_cache"}
FORBIDDEN_IN_SKILLS = (
    (re.compile(r"~/"), "home-relative path"),
    (re.compile(r"/home/"), "absolute home path"),
    (re.compile(r"/Users/"), "absolute home path"),
    (re.compile(r"/ph:"), "harness slash-command invocation"),
    (re.compile(r"/skill:"), "harness slash-command invocation"),
    (re.compile(r"AskUserQuestion"), "harness tool name"),
    (re.compile(r"WebFetch\("), "harness tool call syntax"),
)


def load_json(path: Path, errors: list[str]) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path}: cannot read JSON: {exc}")
        return None


def split_frontmatter(text: str) -> tuple[str, str] | None:
    match = re.match(r"---\n(.*?)\n---\n(.*)", text, re.DOTALL)
    return (match.group(1), match.group(2)) if match else None


def frontmatter_keys(frontmatter: str) -> dict[str, str]:
    """Return top-level keys with the raw text that follows the colon."""
    keys: dict[str, str] = {}
    for match in re.finditer(r"^([A-Za-z][\w-]*):(.*)$", frontmatter, re.MULTILINE):
        keys[match.group(1)] = match.group(2).strip()
    return keys


def skill_dirs(root: Path) -> list[Path]:
    return sorted(p.parent for p in root.glob("plugins/*/skills/*/SKILL.md"))


def plugin_dirs(root: Path) -> list[Path]:
    return sorted(p for p in (root / "plugins").glob("*") if p.is_dir())


def check_plugin(plugin: Path) -> list[str]:
    errors: list[str] = []
    meta_dir = plugin / ".claude-plugin"
    extra = sorted(p.name for p in meta_dir.glob("*") if p.name != "plugin.json")
    if extra:
        errors.append(f"{meta_dir}: only plugin.json belongs here, found {extra}")
    if (plugin / "commands").exists():
        errors.append(f"{plugin}/commands: commands/ is not allowed; skills are the entry point")
    data = load_json(meta_dir / "plugin.json", errors)
    if data is not None:
        for field in PLUGIN_JSON_FIELDS:
            if not data.get(field):
                errors.append(f"{meta_dir}/plugin.json: missing '{field}'")
        if data.get("name") != plugin.name:
            errors.append(f"{meta_dir}/plugin.json: name {data.get('name')!r} != dir {plugin.name}")
        if not SEMVER.match(str(data.get("version", ""))):
            errors.append(f"{meta_dir}/plugin.json: version {data.get('version')!r} is not x.y.z")
    errors += check_plugin_readme(plugin / "README.md")
    return errors


def check_plugin_readme(readme: Path) -> list[str]:
    if not readme.is_file():
        return [f"{readme}: missing"]
    text = readme.read_text()
    errors = [f"{readme}: missing section '{s}'" for s in README_SECTIONS if s not in text]
    if not re.search(r"^\*\*Authors?:\*\*", text, re.MULTILINE):
        errors.append(f"{readme}: missing '**Author:**' line")
    if re.search(r"^#{1,6}\s+install", text, re.MULTILINE | re.IGNORECASE):
        errors.append(f"{readme}: installation docs belong in the root README only")
    return errors


def check_marketplace(root: Path) -> list[str]:
    errors: list[str] = []
    market = load_json(root / ".claude-plugin" / "marketplace.json", errors)
    if market is None:
        return errors
    entries = {e["name"]: e for e in market.get("plugins", [])}
    dirs = {p.name: p for p in plugin_dirs(root)}
    for name in sorted(set(entries) ^ set(dirs)):
        where = "marketplace.json" if name in entries else "plugins/"
        errors.append(f"{name}: only present in {where}")
    for name in sorted(set(entries) & set(dirs)):
        errors += compare_entry(entries[name], dirs[name])
    package = load_json(root / "package.json", errors)
    repo_version = market.get("metadata", {}).get("version")
    if package is not None and package.get("version") != repo_version:
        errors.append(
            f"package.json version {package.get('version')!r} != "
            f"marketplace metadata.version {repo_version!r}"
        )
    return errors


def compare_entry(entry: dict, plugin: Path) -> list[str]:
    errors: list[str] = []
    data = load_json(plugin / ".claude-plugin" / "plugin.json", errors)
    if data is None:
        return errors
    for field in ("name", "version", "description"):
        if entry.get(field) != data.get(field):
            errors.append(f"{plugin.name}: marketplace {field} != plugin.json {field}")
    if entry.get("source") != f"./plugins/{plugin.name}":
        errors.append(f"{plugin.name}: marketplace source must be ./plugins/{plugin.name}")
    return errors


def check_skill(skill: Path) -> list[str]:
    path = skill / "SKILL.md"
    text = path.read_text()
    errors: list[str] = []
    parts = split_frontmatter(text)
    if parts is None:
        return [f"{path}: missing frontmatter"]
    keys = frontmatter_keys(parts[0])
    for key in sorted(set(keys) - ALLOWED_SKILL_KEYS):
        errors.append(f"{path}: frontmatter key '{key}' not allowed")
    name = keys.get("name", "").strip("\"'")
    if name != skill.name:
        errors.append(f"{path}: name {name!r} != directory {skill.name!r}")
    if not skill.name.startswith("ph-"):
        errors.append(f"{path}: skill name must start with 'ph-'")
    description = keys.get("description")
    if description is None:
        errors.append(f"{path}: missing description")
    elif not (description[:1] in {'"', "'"} or BLOCK_SCALAR.match(description)):
        errors.append(f"{path}: description must be a quoted string or block scalar")
    errors += [f"{path}: missing section '{s}'" for s in SKILL_SECTIONS if s not in parts[1]]
    lines = text.count("\n") + 1
    if lines > MAX_SKILL_LINES:
        errors.append(f"{path}: {lines} lines exceeds {MAX_SKILL_LINES}")
    errors += check_shipped_text(skill)
    errors += check_pep723(skill / "scripts")
    return errors


def check_shipped_text(skill: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(skill.rglob("*")):
        if not path.is_file() or path.suffix not in SHIPPED_SUFFIXES:
            continue
        text = path.read_text()
        if path.name == "SKILL.md":
            parts = split_frontmatter(text)
            text = parts[1] if parts else text
        for number, line in enumerate(text.splitlines(), start=1):
            for pattern, label in FORBIDDEN_IN_SKILLS:
                if pattern.search(line):
                    errors.append(f"{path}:{number}: {label} ({pattern.pattern!r})")
    return errors


def check_pep723(scripts_dir: Path) -> list[str]:
    return [
        f"{path}: missing PEP 723 '# /// script' header"
        for path in sorted(scripts_dir.glob("*.py"))
        if "# /// script" not in path.read_text()
    ]


def check_root_readme(root: Path) -> list[str]:
    readme = root / "README.md"
    if not readme.is_file():
        return [f"{readme}: missing"]
    text = readme.read_text()
    skills = {p.name for p in skill_dirs(root)}
    errors: list[str] = []
    badge = re.search(r"badge/Skills-(\d+)-", text)
    if badge is None:
        errors.append("README.md: missing Skills count badge")
    elif int(badge.group(1)) != len(skills):
        errors.append(f"README.md: Skills badge says {badge.group(1)}, found {len(skills)} skills")
    section = re.search(r"^## Skills\n(.*?)(?=^## )", text, re.DOTALL | re.MULTILINE)
    if section is None:
        errors.append("README.md: missing '## Skills' table")
    else:
        listed = set(re.findall(r"^\|\s*\[`?([a-z0-9-]+)`?\]", section.group(1), re.MULTILINE))
        for name in sorted(skills - listed):
            errors.append(f"README.md: skill {name} missing from Skills table")
        for name in sorted(listed - skills):
            errors.append(f"README.md: Skills table lists unknown skill {name}")
    if not (root / "LICENSE").is_file():
        errors.append("LICENSE: missing")
    return errors


def check_changelog(root: Path) -> list[str]:
    changelog = root / "CHANGELOG.md"
    if not changelog.is_file():
        return [f"{changelog}: missing"]
    text = changelog.read_text()
    errors: list[str] = []
    for plugin in plugin_dirs(root):
        data = json.loads((plugin / ".claude-plugin" / "plugin.json").read_text())
        heading = f"## {data['name']} {data['version']}"
        if not re.search(rf"^{re.escape(heading)}( - .*)?$", text, re.MULTILINE):
            errors.append(f"CHANGELOG.md: missing section '{heading}'")
    return errors


def check_paths(root: Path) -> list[str]:
    errors: list[str] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for name in dirs + files:
            if ":" in name:
                errors.append(f"{Path(current) / name}: ':' in path is invalid on Windows")
    return errors


def check_maintainer_scripts(root: Path) -> list[str]:
    errors: list[str] = []
    for scripts_dir in [root / "scripts", *root.glob("plugins/*/maintainer")]:
        errors += check_pep723(scripts_dir)
    return errors


def check_seccon_cache(root: Path) -> list[str]:
    resources = root / "plugins/seccon/skills/ph-seccon/resources"
    manifest_path = resources / "manifest.json"
    if not manifest_path.is_file():
        return []
    errors: list[str] = []
    manifest = load_json(manifest_path, errors)
    if manifest is None:
        return errors
    low, high = manifest["cached_range"]["earliest"], manifest["cached_range"]["latest"]
    declared: set[tuple[str, int, str]] = set()
    for mode, section in manifest["coverage"].items():
        for venue, info in section["venues"].items():
            declared |= {(mode, year, venue) for year in info["cached"]}
            overlap = set(info["cached"]) & set(info["gaps"])
            if overlap:
                errors.append(f"manifest: {mode}/{venue} lists {sorted(overlap)} as cached and gap")
    on_disk = {
        (p.parts[-4], int(p.parts[-3]), p.parts[-2])
        for p in resources.glob("*/*/*/index.json")
        if p.parts[-3].isdigit()
    }
    for mode, year, venue in sorted(declared - on_disk):
        errors.append(f"manifest: {mode}/{year}/{venue} cached but index.json is missing")
    for mode, year, venue in sorted(on_disk - declared):
        errors.append(f"resources: {mode}/{year}/{venue}/index.json is not in manifest cached list")
    for mode, year, venue in sorted(on_disk):
        if not low <= year <= high:
            errors.append(f"resources: {mode}/{year}/{venue} outside cached_range {low}-{high}")
    return errors


def run_checks(root: Path) -> list[str]:
    errors: list[str] = []
    for plugin in plugin_dirs(root):
        errors += check_plugin(plugin)
    for skill in skill_dirs(root):
        errors += check_skill(skill)
    errors += check_marketplace(root)
    errors += check_root_readme(root)
    errors += check_changelog(root)
    errors += check_paths(root)
    errors += check_maintainer_scripts(root)
    errors += check_seccon_cache(root)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    errors = run_checks(args.root)
    for error in errors:
        print(error)
    if errors:
        print(f"\n{len(errors)} problem(s) found", file=sys.stderr)
        return 1
    print("repo checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
