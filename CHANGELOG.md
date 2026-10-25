# Changelog

Entries are per plugin and version, headed `## <plugin> <version> - <date>`. The release workflow publishes the section matching each plugin's current version. `## repo <version>` sections cover repository-wide changes and are not released. Every plugin version in `plugin.json` needs a section here.

## [Unreleased]

## repo 2.0.0 - 2026-10-24

### Breaking
- Every skill is renamed with a `ph-` prefix (directory and frontmatter `name`) so flat install targets (`~/.agents/skills`, `~/.hermes/skills`, `npx skills` agent directories) cannot collide with other skills. See the plugin sections for the old → new names.
- The `commands/` shims are gone. Skills are the only entry point.
- All plugins are bumped to 2.0.0. `npx skills` users must `npx skills remove <old-name>` and add the repository again.

### Added
- `LICENSE` (MIT) and the upstream MIT license for the vendored `stop-slop` skill.
- `AGENTS.md` as the contributor guide; `CLAUDE.md` imports it.
- Root `README.md` carries the install and invocation matrix for Claude Code, Codex, Pi, OMP, Hermes, and `npx skills`, and a 1.x upgrade section.
- `agents/openai.yaml` (Codex UI metadata) for every skill.
- CI (`.github/workflows/ci.yml`): Agent Skills spec validation, `scripts/check_repo.py` structure checks, a pull-request version gate (`scripts/check_versions.py`), ruff and pytest, `npx skills` discovery check, actionlint and zizmor, offline link check, and a single `ci` job to require.
- Release workflow (`.github/workflows/release.yml`, `scripts/release.py`): tags `<plugin>@v<version>` and creates a GitHub Release from the plugin's CHANGELOG section when a version has no tag.
- Dependabot for GitHub Actions and the `uv` projects, a pull request template, `.editorconfig`, and a root `ruff.toml`.

### Changed
- Skill bodies use harness-neutral wording: no `/skill:`, `/ph:` or `/<plugin>:<skill>` invocation strings, no harness tool names.
- Repository version (`package.json`, marketplace `metadata.version`) tracks the repository as a whole; each plugin versions independently in `plugin.json` and its marketplace entry.
- The root `pyproject.toml` and `uv.lock` are removed: `paperhub-cli` runs through `uvx` and no project dependency remains.
- `.gitignore` no longer ignores `seccon/`, so new files under `plugins/seccon/` are tracked.

## writing 2.0.0 - 2026-10-24

### Breaking
- `stop-slop` is now `ph-stop-slop`; `amazon-writing` is now `ph-amazon-writing`.
- Removed the `ph:write` and `ph:amazon-writing` commands. Invoke the skills directly; the skill bodies document their arguments (`[text|file]`, `<document-type> [text|file]`).

### Changed
- `ph-stop-slop` ships the upstream MIT license; the plugin author lists both Hardik Pandya (stop-slop) and Federico Maggi (amazon-writing).
- `ph-amazon-writing` frontmatter description is quoted and third-person.

## writing 1.1.0 - 2026-08-11

### Added
- `amazon-writing` skill: narrative memos in Amazon style (6-pagers, 1-pagers, press releases, PRFAQs).

## writing 1.0.0 - 2026-06-07

### Added
- `stop-slop` skill imported from [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) by Hardik Pandya: eliminates AI writing patterns from prose, with phrase, structure, and example references.

## seccon 2.0.0 - 2026-10-24

### Breaking
- `seccon` is now `ph-seccon`. Pi/OMP `/skill:seccon …` forms become arguments to `ph-seccon` (`help`, `academic now`, …).

### Fixed
- Data-source policy no longer contradicts itself: author search, abstract enrichment, and citation counts go through `uvx paperhub-cli`; direct DBLP and Semantic Scholar calls are forbidden everywhere. `paperhub-cli read` examples use `--id doi:<doi>` (the `--doi` flag does not exist).
- The cache window comes from `resources/manifest.json` `cached_range` instead of hard-coded years. The manifest now includes the Black Hat USA 2026 listing and `write_manifest.py` derives years from the files on disk.
- Anti-pattern numbering, the tool list, and the "TAMU tier rankings" label (the ranking is CORE 2023 + Guofei Gu).
- Description grammar.

### Changed
- `paperhub-cli` runs through `uvx`; no repo-root `uv sync` is needed. `compatibility` declares `uv`.
- Ranked-conference tables and acceptance rates moved to `references/academic-rankings.md`; the industry venue list moved to `references/industry-venues.md` without cache counts (the manifest is the source of truth). `SKILL.md` is under 500 lines.
- The industry cross-conference scan covers every cached industry venue in the manifest, not only DEF CON and OffensiveCon.
- Maintainer scripts, their `pyproject.toml`, and `uv.lock` moved from the skill to `plugins/seccon/maintainer/`, so skill installs no longer ship crawlers. `populate_cache.py` regenerates the manifest through `write_manifest.py`.
- The crawling disclaimer moved from the root README to the plugin README.

## seccon 1.3.0 - 2026-04-26

### Added
- Curated resource cache (`resources/`) of academic papers (DBLP XML) and industry talks (DEF CON, Black Hat, OffensiveCon, REcon, hardwear.io), with a `manifest.json` coverage map and cache maintenance scripts.
- Live calendar via confsearch.ethz.ch (academic) and cfptime.org (industry); `now`, `deadlines`, `latest`, `compare`, and `<year> <acronym>` shortcuts.
- Aggregate ranking from CORE 2023 and Guofei Gu statistics; `paperhub-cli` for paper search and download.
- IRON RULE banning generic web search; anti-pattern list.

### Removed
- Venues outside the security scope (CSF, Asiacrypt, TCC, SOUPS, ACNS, IFIP SEC, WiSec, ICICS, SecureComm, PST, PKC, SAC, CanSecWest, Troopers, Infiltrate) and the `archive_url` field.

## speaker-coach 2.0.0 - 2026-10-24

### Breaking
- `speaker-coach` is now `ph-speaker-coach`. The `coach` command is removed; invoke the skill with `design`, `debug <artifact>`, or `rehearse [artifact]`.

### Changed
- Declares `uv` in `compatibility`; "visual-companion / browser tool" wording replaced with harness-neutral "browser or visual tools".
- Fixed "Sub-sequent" typo in the README.

## speaker-coach 1.0.0 - 2026-06-20

### Added
- Disciplined interview-style coaching for cybersecurity speakers. Three sub-modes: `design` (forward, backwards-from-the-last-slide Socratic interview), `debug` (adversarial talk audit against a 12-metric rubric with venue-aware columns), `rehearse` (rehearsal critique + T-2-week readiness gate). Adapts to academic, industry, and grassroots venue norms. Persists a single markdown artifact per talk across sessions. Embeds the coaching and adversarial frameworks from the *Cybersecurity Supercommunicators* essays and *Payload Delivered* chapters/appendix.

## news 2.0.0 - 2026-10-24

### Breaking
- `news-reader` is now `ph-news-reader`.
- Removed the `news-chronicle` skill (domain-clustered intelligence chronicles). Nothing replaces it.

### Changed
- Plugin description and README cover feed reading only; the README has the required Author, When to Use, When NOT to Use, and What It Does sections.
- `ph-news-reader` refers to Miniflux tools by bare name, declares the `miniflux` MCP dependency in `compatibility` and `agents/openai.yaml`, and gains When to Use / When NOT to Use sections.

## news 1.0.0 - 2026-08-18

### Added
- `news-reader` skill: read, search, triage, and manage RSS feeds through the Miniflux MCP server.
- `news-chronicle` skill: domain-clustered platform security intelligence chronicles from Miniflux feeds, with category blocklist, prioritization, date verification, and CISA KEV / ENISA EUVD signals (removed in 2.0.0).
