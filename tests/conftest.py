"""Make the repository scripts importable and share repo fixtures."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))


@pytest.fixture(autouse=True)
def isolated_git_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ignore the developer's global git config (signing, hooks) in throwaway repos."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", os.devnull)


@pytest.fixture
def repo_copy(tmp_path: Path) -> Path:
    """Copy of the working tree (tracked and untracked, not ignored) to mutate freely."""
    listing = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "-co", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    root = tmp_path / "repo"
    for name in listing:
        source = REPO / name
        if not source.is_file():
            continue
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return root
