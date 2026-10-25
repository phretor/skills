"""Behavior tests for scripts/check_repo.py against mutated copies of the repo."""

from __future__ import annotations

import json
from pathlib import Path

import check_repo

SKILL = "plugins/writing/skills/ph-stop-slop"


def problems(root: Path) -> list[str]:
    return check_repo.run_checks(root)


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    assert old in text, f"{old!r} not in {path}"
    path.write_text(text.replace(old, new, 1))


def edit_json(path: Path, mutate) -> None:
    data = json.loads(path.read_text())
    mutate(data)
    path.write_text(json.dumps(data, indent=2))


def test_clean_repo_passes(repo_copy: Path) -> None:
    assert problems(repo_copy) == []


def test_new_skill_missing_from_readme_table_fails(repo_copy: Path) -> None:
    skill = repo_copy / "plugins/writing/skills/ph-extra"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        '---\nname: ph-extra\ndescription: "Extra."\n---\n\n'
        "## When to Use\n\nx\n\n## When NOT to Use\n\ny\n"
    )
    found = problems(repo_copy)
    assert any("ph-extra missing from Skills table" in p for p in found)
    assert any("badge says 5, found 6" in p for p in found)


def test_skill_without_ph_prefix_fails(repo_copy: Path) -> None:
    skill = repo_copy / SKILL
    edit(skill / "SKILL.md", "name: ph-stop-slop", "name: stop-slop")
    found = problems(repo_copy)
    assert any("name 'stop-slop' != directory 'ph-stop-slop'" in p for p in found)


def test_unquoted_description_fails_but_block_scalar_passes(repo_copy: Path) -> None:
    path = repo_copy / SKILL / "SKILL.md"
    text = path.read_text()
    start = text.index("description:")
    end = text.index("\n", start)
    path.write_text(text[:start] + "description: Plain text description." + text[end:])
    assert any("description must be a quoted string" in p for p in problems(repo_copy))
    path.write_text(text[:start] + "description: >\n  Folded text." + text[end:])
    assert problems(repo_copy) == []


def test_disallowed_frontmatter_key_fails(repo_copy: Path) -> None:
    edit(repo_copy / SKILL / "SKILL.md", "license: MIT", "license: MIT\nversion: 1.0.0")
    assert any("frontmatter key 'version' not allowed" in p for p in problems(repo_copy))


def test_skill_over_500_lines_fails(repo_copy: Path) -> None:
    path = repo_copy / SKILL / "SKILL.md"
    path.write_text(path.read_text() + "\nline\n" * 500)
    assert any("exceeds 500" in p for p in problems(repo_copy))


def test_skill_missing_when_not_to_use_fails(repo_copy: Path) -> None:
    edit(repo_copy / SKILL / "SKILL.md", "## When NOT to Use", "## Skip")
    assert any("missing section '## When NOT to Use'" in p for p in problems(repo_copy))


def test_commands_dir_fails(repo_copy: Path) -> None:
    (repo_copy / "plugins/writing/commands").mkdir()
    assert any("commands/ is not allowed" in p for p in problems(repo_copy))


def test_extra_file_in_claude_plugin_dir_fails(repo_copy: Path) -> None:
    (repo_copy / "plugins/news/.claude-plugin/extra.json").write_text("{}")
    assert any("only plugin.json belongs here" in p for p in problems(repo_copy))


def test_harness_syntax_in_skill_body_fails(repo_copy: Path) -> None:
    path = repo_copy / SKILL / "SKILL.md"
    path.write_text(path.read_text() + "\nRun /skill:ph-stop-slop now.\n")
    assert any("harness slash-command invocation" in p for p in problems(repo_copy))


def test_harness_syntax_in_frontmatter_allowed_tools_is_ignored(repo_copy: Path) -> None:
    edit(repo_copy / SKILL / "SKILL.md", "allowed-tools: Read", "allowed-tools: WebFetch(x)")
    assert problems(repo_copy) == []


def test_home_path_in_reference_fails(repo_copy: Path) -> None:
    path = repo_copy / SKILL / "references/examples.md"
    path.write_text(path.read_text() + "\nSee ~/notes.\n")
    assert any("home-relative path" in p for p in problems(repo_copy))


def test_marketplace_version_mismatch_fails(repo_copy: Path) -> None:
    def bump(data: dict) -> None:
        data["plugins"][0]["version"] = "9.9.9"

    edit_json(repo_copy / ".claude-plugin/marketplace.json", bump)
    found = problems(repo_copy)
    assert any("marketplace version != plugin.json version" in p for p in found)


def test_repo_version_mismatch_fails(repo_copy: Path) -> None:
    edit_json(repo_copy / "package.json", lambda d: d.update(version="0.0.1"))
    assert any("package.json version" in p for p in problems(repo_copy))


def test_plugin_missing_from_marketplace_fails(repo_copy: Path) -> None:
    edit_json(
        repo_copy / ".claude-plugin/marketplace.json",
        lambda d: d.update(plugins=[p for p in d["plugins"] if p["name"] != "news"]),
    )
    assert any("news: only present in plugins/" in p for p in problems(repo_copy))


def test_plugin_readme_install_section_fails(repo_copy: Path) -> None:
    path = repo_copy / "plugins/news/README.md"
    path.write_text(path.read_text() + "\n## Installation\n\nRun it.\n")
    assert any("installation docs belong in the root README" in p for p in problems(repo_copy))


def test_plugin_readme_missing_author_fails(repo_copy: Path) -> None:
    edit(repo_copy / "plugins/news/README.md", "**Author:**", "By")
    assert any("missing '**Author:**'" in p for p in problems(repo_copy))


def test_colon_in_path_fails(repo_copy: Path) -> None:
    (repo_copy / "plugins/writing/ph:write.md").write_text("x")
    assert any("':' in path" in p for p in problems(repo_copy))


def test_script_without_pep723_header_fails(repo_copy: Path) -> None:
    script = repo_copy / "plugins/speaker-coach/skills/ph-speaker-coach/scripts/extra.py"
    script.write_text("print('x')\n")
    assert any("missing PEP 723" in p for p in problems(repo_copy))


def test_changelog_missing_plugin_version_fails(repo_copy: Path) -> None:
    edit(repo_copy / "CHANGELOG.md", "## news 2.0.0", "## news 2.0.9")
    assert any("missing section '## news 2.0.0'" in p for p in problems(repo_copy))


def test_manifest_cached_year_without_file_fails(repo_copy: Path) -> None:
    resources = repo_copy / "plugins/seccon/skills/ph-seccon/resources"
    (resources / "academic/2022/ccs/index.json").unlink()
    assert any("cached but index.json is missing" in p for p in problems(repo_copy))


def test_index_file_not_in_manifest_fails(repo_copy: Path) -> None:
    resources = repo_copy / "plugins/seccon/skills/ph-seccon/resources"
    target = resources / "industry/2026/defcon"
    target.mkdir(parents=True)
    (target / "index.json").write_text("{}")
    assert any("not in manifest cached list" in p for p in problems(repo_copy))


def test_index_year_outside_cached_range_fails(repo_copy: Path) -> None:
    resources = repo_copy / "plugins/seccon/skills/ph-seccon/resources"
    edit_json(
        resources / "manifest.json",
        lambda d: d["cached_range"].update(latest=2025),
    )
    assert any("outside cached_range" in p for p in problems(repo_copy))


def test_missing_license_fails(repo_copy: Path) -> None:
    (repo_copy / "LICENSE").unlink()
    assert "LICENSE: missing" in problems(repo_copy)
