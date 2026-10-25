# Changelog

## [Unreleased]

## 2.0.0

### Breaking
- Every skill is renamed with a `ph-` prefix (directory and frontmatter `name`) so flat install targets (`~/.agents/skills`, `~/.hermes/skills`, `npx skills` agent directories) cannot collide with other skills:
  - `stop-slop` → `ph-stop-slop` (`writing`)
  - `amazon-writing` → `ph-amazon-writing` (`writing`)
  - `seccon` → `ph-seccon` (`seccon`)
  - `speaker-coach` → `ph-speaker-coach` (`speaker-coach`)
  - `news-reader` → `ph-news-reader` (`news`)
- Removed the `commands/` shims `ph:write`, `ph:amazon-writing`, and `coach`. Skills are the only entry point; argument parsing guidance moved into the skill bodies.
- Removed the `news-chronicle` skill from the `news` plugin.
- All plugins bumped to 2.0.0. `npx skills` users must `npx skills remove <old-name>` and add the repository again.

### Changed
- Skill bodies use harness-neutral wording: no `/skill:` or `/ph:` invocation strings, no harness tool names.
- `ph-seccon` runs `paperhub-cli` through `uvx`; the repo-root `uv sync` is no longer required.
- Seccon maintainer tooling moved from the skill to `plugins/seccon/maintainer/` so installed copies do not ship crawlers and lockfiles.
- Added `agents/openai.yaml` (Codex UI metadata) to every skill.
- `AGENTS.md` is the contributor guide; `CLAUDE.md` imports it.
- Root `README.md` carries the install and invocation matrix for Claude Code, Codex, Pi, OMP, Hermes, and `npx skills`.

## 1.x

### Added
- `speaker-coach` plugin (v1.0.0): disciplined interview-style coaching for cybersecurity speakers. Three sub-modes via `/ph:coach`: `design` (forward, backwards-from-the-last-slide Socratic interview), `debug` (adversarial talk audit against a 12-metric rubric with venue-aware columns), `rehearse` (rehearsal critique + T-2-week readiness gate). Adapts to academic, industry, and grassroots venue norms. Persists a single markdown artifact per talk across sessions. Embeds the coaching and adversarial frameworks from the *Cybersecurity Supercommunicators* essays and *Payload Delivered* chapters/appendix.
- `writing` plugin (v1.0.0): imports the [stop-slop](https://github.com/hardikpandya/stop-slop) skill by Hardik Pandya — eliminates AI writing patterns from prose. Includes `stop-slop` skill with `ph:write` command and full reference docs (phrases, structures, examples).
