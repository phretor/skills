# phretor/skills

Public [Agent Skills](https://agentskills.io) for Pi.

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

## Contributing

See [CLAUDE.md](CLAUDE.md) for plugin structure, required files, and quality standards.

## License

MIT
