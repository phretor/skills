"""Behavior tests for scripts/check_versions.py using throwaway git repositories."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import check_versions
import pytest


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def write_plugin(root: Path, name: str, version: str) -> None:
    meta = root / "plugins" / name / ".claude-plugin"
    meta.mkdir(parents=True, exist_ok=True)
    (meta / "plugin.json").write_text(json.dumps({"name": name, "version": version}))
    (root / "plugins" / name / "README.md").write_text(f"# {name}\n")


def write_marketplace(root: Path, versions: dict[str, str]) -> None:
    market = root / ".claude-plugin"
    market.mkdir(exist_ok=True)
    entries = [{"name": n, "version": v} for n, v in versions.items()]
    (market / "marketplace.json").write_text(json.dumps({"plugins": entries}))


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "t")
    git(root, "config", "commit.gpgsign", "false")
    write_plugin(root, "alpha", "1.0.0")
    write_marketplace(root, {"alpha": "1.0.0"})
    (root / "CHANGELOG.md").write_text("# Changelog\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "base")
    git(root, "checkout", "-q", "-b", "feature")
    return root


def commit(root: Path) -> None:
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "change")


def test_plugin_file_change_without_bump_fails(repo: Path) -> None:
    (repo / "plugins/alpha/README.md").write_text("# alpha\nmore\n")
    commit(repo)
    errors = check_versions.check(repo, "main")
    assert any(
        "alpha: files changed but version 1.0.0 is not above base 1.0.0" in e for e in errors
    )
    assert any("CHANGELOG.md not updated" in e for e in errors)


def test_bump_in_both_manifests_and_changelog_passes(repo: Path) -> None:
    (repo / "plugins/alpha/README.md").write_text("# alpha\nmore\n")
    write_plugin(repo, "alpha", "1.0.1")
    write_marketplace(repo, {"alpha": "1.0.1"})
    (repo / "CHANGELOG.md").write_text("# Changelog\n## alpha 1.0.1\n")
    commit(repo)
    assert check_versions.check(repo, "main") == []


def test_bump_only_in_plugin_json_fails(repo: Path) -> None:
    write_plugin(repo, "alpha", "1.0.1")
    (repo / "CHANGELOG.md").write_text("# Changelog\nx\n")
    commit(repo)
    errors = check_versions.check(repo, "main")
    assert any("marketplace version '1.0.0' != plugin.json 1.0.1" in e for e in errors)


def test_bump_only_in_marketplace_fails(repo: Path) -> None:
    (repo / "plugins/alpha/README.md").write_text("changed\n")
    write_marketplace(repo, {"alpha": "1.0.1"})
    (repo / "CHANGELOG.md").write_text("# Changelog\nx\n")
    commit(repo)
    errors = check_versions.check(repo, "main")
    assert any("marketplace version '1.0.1' != plugin.json 1.0.0" in e for e in errors)


def test_bump_without_changelog_fails(repo: Path) -> None:
    write_plugin(repo, "alpha", "1.1.0")
    write_marketplace(repo, {"alpha": "1.1.0"})
    commit(repo)
    assert check_versions.check(repo, "main") == [
        "CHANGELOG.md not updated but plugin files changed: alpha"
    ]


def test_version_decrease_fails(repo: Path) -> None:
    write_plugin(repo, "alpha", "0.9.0")
    write_marketplace(repo, {"alpha": "0.9.0"})
    (repo / "CHANGELOG.md").write_text("# Changelog\nx\n")
    commit(repo)
    assert any("not above base" in e for e in check_versions.check(repo, "main"))


def test_change_outside_plugins_needs_no_bump(repo: Path) -> None:
    (repo / "README.md").write_text("docs\n")
    commit(repo)
    assert check_versions.check(repo, "main") == []


def test_new_plugin_with_matching_entry_passes(repo: Path) -> None:
    write_plugin(repo, "beta", "1.0.0")
    write_marketplace(repo, {"alpha": "1.0.0", "beta": "1.0.0"})
    (repo / "CHANGELOG.md").write_text("# Changelog\n## beta 1.0.0\n")
    commit(repo)
    assert check_versions.check(repo, "main") == []


def test_non_semver_version_fails(repo: Path) -> None:
    write_plugin(repo, "alpha", "latest")
    (repo / "CHANGELOG.md").write_text("# Changelog\nx\n")
    commit(repo)
    assert any("is not x.y.z" in e for e in check_versions.check(repo, "main"))


def test_unknown_base_ref_exits(repo: Path) -> None:
    with pytest.raises(SystemExit):
        check_versions.check(repo, "does-not-exist")
