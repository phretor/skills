"""Behavior tests for scripts/release.py with a fake gh that tags like the real one."""

from __future__ import annotations

import json
import stat
import subprocess
from pathlib import Path

import pytest
import release

CHANGELOG = """# Changelog

## alpha 1.1.0 - 2026-01-02

### Added
- second

## alpha 1.0.0 - 2026-01-01

- first
"""


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    meta = root / "plugins/alpha/.claude-plugin"
    meta.mkdir(parents=True)
    (meta / "plugin.json").write_text(json.dumps({"name": "alpha", "version": "1.1.0"}))
    (root / "CHANGELOG.md").write_text(CHANGELOG)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "t")
    git(root, "config", "commit.gpgsign", "false")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "Add alpha")
    return root


@pytest.fixture
def fake_gh(tmp_path: Path) -> Path:
    script = tmp_path / "gh"
    script.write_text(
        "#!/bin/sh\n"
        'echo "$@" >> "$FAKE_GH_LOG"\n'
        'for arg in "$@"; do prev="$arg"; done\n'
        'cp "$prev" "$FAKE_GH_NOTES"\n'
        'git tag "$3"\n'
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return script


def test_creates_release_with_changelog_section_then_is_idempotent(
    repo: Path, fake_gh: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    log, notes = tmp_path / "gh.log", tmp_path / "notes.md"
    monkeypatch.setenv("FAKE_GH_LOG", str(log))
    monkeypatch.setenv("FAKE_GH_NOTES", str(notes))
    assert release.release(repo, str(fake_gh), dry_run=False) == ["alpha@v1.1.0"]
    assert "release create alpha@v1.1.0 --target" in log.read_text()
    assert notes.read_text().strip() == "### Added\n- second"
    assert "alpha@v1.1.0" in git(repo, "tag", "--list")
    log.write_text("")
    assert release.release(repo, str(fake_gh), dry_run=False) == []
    assert log.read_text() == ""


def test_dry_run_creates_nothing(repo: Path, fake_gh: Path) -> None:
    assert release.release(repo, str(fake_gh), dry_run=True) == ["alpha@v1.1.0"]
    assert git(repo, "tag", "--list") == ""


def test_missing_changelog_section_falls_back_to_commits_since_previous_tag(
    repo: Path, fake_gh: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    git(repo, "tag", "alpha@v1.0.0")
    (repo / "plugins/alpha/new.md").write_text("x")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Touch alpha")
    meta = repo / "plugins/alpha/.claude-plugin/plugin.json"
    meta.write_text(json.dumps({"name": "alpha", "version": "1.2.0"}))
    git(repo, "commit", "-qam", "Bump alpha")
    notes = tmp_path / "notes.md"
    monkeypatch.setenv("FAKE_GH_LOG", str(tmp_path / "gh.log"))
    monkeypatch.setenv("FAKE_GH_NOTES", str(notes))
    assert release.release(repo, str(fake_gh), dry_run=False) == ["alpha@v1.2.0"]
    body = notes.read_text()
    assert "Touch alpha" in body
    assert "Bump alpha" in body
    assert "Add alpha" not in body


def test_changelog_section_extraction() -> None:
    assert release.changelog_section(CHANGELOG, "alpha", "1.0.0") == "- first"
    assert release.changelog_section(CHANGELOG, "alpha", "9.9.9") is None
    assert release.changelog_section(CHANGELOG, "beta", "1.0.0") is None


def test_gh_failure_aborts(repo: Path, tmp_path: Path) -> None:
    failing = tmp_path / "gh-fail"
    failing.write_text("#!/bin/sh\necho boom >&2\nexit 1\n")
    failing.chmod(failing.stat().st_mode | stat.S_IEXEC)
    with pytest.raises(SystemExit):
        release.release(repo, str(failing), dry_run=False)
