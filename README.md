<div align="center">

# phretor/skills

My agent skills.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Pi](https://img.shields.io/badge/Pi-%E2%9C%93-blue?logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlsaW5lIHBvaW50cz0iMjIgMTIgMTYgMTIgMTQgMyA2IDMgNCAxMSAxMCAxMSAxMiAyMCAyMCAyMCIvPjxsaW5lIHgxPSIyIiB5MT0iMTIiIHgyPSI4IiB5Mj0iMTIiLz48L3N2Zz4=&label=Pi)](https://agentskills.io)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%9C%93-blueviolet)](https://claude.ai)
[![Skills](https://img.shields.io/badge/Skills-5-2ea44f)](plugins/)

</div>

## Install

Pick **one** route per machine. Installing the same skill through a plugin marketplace and through `npx skills` leaves duplicates.

| Harness | Install | Invoke |
|---|---|---|
| Claude Code | `/plugin marketplace add phretor/skills`, then `/plugin install <plugin>@phretor-skills` | `/<plugin>:ph-<skill>`, e.g. `/seccon:ph-seccon help` |
| Codex | `npx skills@latest add phretor/skills -a codex` (alt: `codex plugin marketplace add phretor/skills`) | `$ph-seccon help` |
| Pi | `pi install git:github.com/phretor/skills` | `/skill:ph-seccon help` |
| OMP | `omp plugin marketplace add phretor/skills`, then `omp plugin install <plugin>@phretor-skills` | `/skill:ph-seccon help` |
| Hermes | `npx skills@latest add phretor/skills -a hermes-agent` (alt: `hermes skills install ...`) | `/ph-seccon help` |
| Others | `npx skills@latest add phretor/skills [--skill ph-seccon]` | harness-specific |

Plugins: `writing`, `seccon`, `speaker-coach`, `news`. `npx skills` installs skills individually and ignores plugin boundaries; add `-a <agent>` to pick the target, `--skill <name>` to install a subset, and `-g` to install into your home directory instead of the current project. List what the repo offers with `npx skills@latest add phretor/skills --list`.

Skills take arguments as plain text after the skill name; the examples above use `help`. Each skill's arguments are listed in the table below.

### Upgrading from 1.x

Version 2.0.0 renamed every skill with a `ph-` prefix, removed the `commands/` shims (`ph:write`, `ph:amazon-writing`, `coach`), and removed the `news-chronicle` skill. See [CHANGELOG.md](CHANGELOG.md) for the full list.

- **Claude Code / OMP:** update the marketplace (`/plugin marketplace update phretor-skills`), then update or reinstall each plugin.
- **`npx skills` (Codex, Hermes, others):** remove the old names, then add again: `npx skills remove stop-slop amazon-writing seccon speaker-coach news-reader news-chronicle`, then `npx skills add phretor/skills` (add `-g` to both if you installed globally).
- **Pi:** `pi remove git:github.com/phretor/skills`, then `pi install git:github.com/phretor/skills` again.
- Replace `/ph:write` with `ph-stop-slop`, `/ph:amazon-writing` with `ph-amazon-writing`, and `/ph:coach` with `ph-speaker-coach`. Nothing replaces `news-chronicle`.

## Requirements

Some skills need system dependencies. Each plugin's `README.md` repeats its own.

| Plugin | Dependency | Install |
|---|---|---|
| [seccon](plugins/seccon/) | pdftotext (poppler) | `brew install poppler` (macOS) / `apt-get install poppler-utils` (Debian/Ubuntu) |
| [seccon](plugins/seccon/) | [uv](https://docs.astral.sh/uv/) (runs `uvx paperhub-cli`) | `brew install uv` or see the uv docs |
| [seccon](plugins/seccon/) | Internet access (live CFP calendar, on-demand papers) | none |
| [speaker-coach](plugins/speaker-coach/) | uv (runs the bundled slide-deck extractor) | `brew install uv` or see the uv docs |
| [speaker-coach](plugins/speaker-coach/) | pdftotext (poppler) -- only for slide-deck PDF ingestion | `brew install poppler` (macOS) / `apt-get install poppler-utils` (Debian/Ubuntu) |
| [news](plugins/news/) | Miniflux MCP server | Add the `miniflux` server to your agent's MCP configuration |

## Skills

| Skill | Arguments | Description |
|---|---|---|
| [`ph-stop-slop`](plugins/writing/) | `[text\|file]` | Eliminate AI writing patterns: throat-clearing, passive voice, jargon, binary contrasts, adverbs, structural clichés. Scores prose on directness, rhythm, trust, authenticity, density. |
| [`ph-amazon-writing`](plugins/writing/) | `<document-type> [text\|file]` | Write or rewrite narrative memos in Amazon style: 6-pagers, 1-pagers, press releases, PRFAQs. Data over adjectives, active voice, the "so what" test. |
| [`ph-seccon`](plugins/seccon/) | `help`, `[academic\|industry] now\|deadlines\|latest …`, `academic compare <v1> <v2>`, `academic <year> <acronym>` | Security conference intelligence: rankings, paper/talk search, author lookup, live CFP calendar, topic-filtered `now`, `deadlines`, `latest`, venue comparison, and academic `<year> <acronym>` shorthand. |
| [`ph-speaker-coach`](plugins/speaker-coach/) | `<design\|debug\|rehearse> [artifact]` | Disciplined interview-style coaching for cybersecurity speakers: backwards-from-the-last-slide forward design, adversarial draft audit against a 12-metric rubric, rehearsal critique, and T-2-week readiness gate. Adapts to academic, industry, and grassroots venue norms. |
| [`ph-news-reader`](plugins/news/) | (none) | Read, search, triage, and manage RSS feeds via the Miniflux MCP server. |

> 💡 **Tip:** invoke `ph-seccon` with `help` for a quick-start guide with examples.

## Contributing

See [AGENTS.md](AGENTS.md) for plugin structure, required files, naming, and quality standards.

## License

MIT
