<div align="center">

# phretor/skills

Public Agent Skills for Pi (and Claude).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Pi](https://img.shields.io/badge/Pi-%E2%9C%93-blue?logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlsaW5lIHBvaW50cz0iMjIgMTIgMTYgMTIgMTQgMyA2IDMgNCAxMSAxMCAxMSAxMiAyMCAyMCAyMCIvPjxsaW5lIHgxPSIyIiB5MT0iMTIiIHgyPSI4IiB5Mj0iMTIiLz48L3N2Zz4=&label=Pi)](https://agentskills.io)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%9C%93-blueviolet)](https://claude.ai)
[![Skills](https://img.shields.io/badge/Skills-1-2ea44f)](plugins/)

</div>

## Install

### Pi

```bash
pi install https://github.com/phretor/skills
```

Or from a local checkout:

```bash
pi install .
```

### Claude Code

```bash
/plugin install https://github.com/phretor/skills
```

Or install an individual plugin from a local checkout:

```bash
/plugin install ./plugins/seccon
```

## Requirements

Some plugins require system dependencies. See each plugin's `README.md` or `SKILL.md` for details.

| Plugin | Dependency | Install |
|---|---|---|
| [seccon](plugins/seccon/) | pdftotext (poppler) | `brew install poppler` (macOS) / `apt-get install poppler-utils` (Debian/Ubuntu) |

Paper search plugins also use `paperhub-cli`, installed automatically via `uv sync` from the repo root.

## Skills

| Skill | Command | Description |
|---|---|---|
| [seccon](plugins/seccon/) | `/skill:seccon help` | Security conference intelligence: rankings, paper/talk search, author lookup, live CFP calendar, topic-filtered `now`, `deadlines`, `latest`, venue comparison, and academic `<year> <acronym>` shorthand |

> 💡 **Tip:** run `/skill:seccon help` for a quick-start guide with examples.

## Contributing

See [CLAUDE.md](CLAUDE.md) for plugin structure, required files, and quality standards.

## Disclaimer

Using these skills causes the agent to fetch content from public-facing
conference websites (program pages, proceedings archives, CFP APIs). The
crawler caches aggressively to minimize requests, but repeated use may still
trigger rate limits or temporary IP bans from upstream sites. This is inherent
to the kind of data this repo provides. Use responsibly.

## License

MIT
