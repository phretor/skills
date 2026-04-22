# phretor/skills

Public [Agent Skills](https://agentskills.io) for Claude Code.

## Install

```bash
/plugin marketplace add phretor/skills
claude plugins install phretor-skills
```

## Skills

| Skill | Invoke | Description |
|---|---|---|
| [con](skills/con/) | `/con [academic\|industry] <ask>` | Conference intelligence: rankings, paper/talk search, author lookup, cross-conference scans, structured work evaluation |

## Maintaining URL lists

Run once a year after each conference season to refresh year-specific program URLs:

```bash
uv run skills/con/scripts/crawl_conferences.py
```

## License

MIT
