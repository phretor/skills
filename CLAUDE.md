# Contributing Skills

This repo follows the Trail of Bits plugin layout. Every plugin must conform to the structure below before being added to the root `marketplace.json`.

## Plugin Structure

Every plugin lives under `plugins/<plugin-name>/` and must contain:

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json         # Plugin metadata
├── commands/
│   └── <command-name>.md   # Slash command (required; default name matches plugin)
├── skills/
│   └── <skill-name>/
│       └── SKILL.md        # Skill entry point (required)
├── README.md               # Human-facing documentation (required)
└── references/             # Optional: detailed docs loaded on demand
    scripts/                # Optional: utility scripts (PEP 723 headers, uv run)
    workflows/              # Optional: step-by-step guides
```

Only `plugin.json` belongs in `.claude-plugin/`. Component directories (`skills/`, `commands/`, `references/`, `scripts/`) go at the plugin root or inside `skills/<name>/`.

## Required Files

### `plugin.json`

```json
{
  "name": "<plugin-name>",
  "version": "1.0.0",
  "description": "One sentence, third-person, specific.",
  "author": {
    "name": "Your Name",
    "url": "https://github.com/<handle>"
  }
}
```

### `commands/<command-name>.md`

The command is a **thin shim** — it parses `$ARGUMENTS` and delegates to the skill. No logic lives here.

Default command name matches the plugin name. The creator may choose a different name if it reads more naturally (e.g., a plugin `http-client` might use command name `http`).

```markdown
---
name: <command-name>
description: "One-line description for the command palette."
argument-hint: "<required-arg> [optional-arg]"
allowed-tools:
  - WebFetch
  - Bash
---

# <Plugin Title>

**Arguments:** $ARGUMENTS

Parse arguments:
1. **<arg>** (required): ...
2. **<arg>** (optional): ...

Invoke the `<skill-name>` skill with these arguments for the full workflow.
```

### `skills/<skill-name>/SKILL.md`

Frontmatter must contain only `name`, `description`, and (optionally) `allowed-tools`. No `version`, `author`, or `metadata` — those belong in `plugin.json`.

```yaml
---
name: <skill-name>
description: "Third-person. What it does and when to use it. Include specific trigger phrases."
allowed-tools: Read Bash WebFetch   # optional; space-separated
---
```

**Required sections** (in this order, after any dispatch/overview block):

```markdown
## When to Use
[Specific scenarios — concrete, not vague]

## When NOT to Use
[Adjacent tasks better served by something else]
```

Keep SKILL.md under 500 lines. Move detailed reference material to `references/` and link to it.

### `README.md`

Human-facing. Must include: author, When to Use, When NOT to Use, What It Does, Installation one-liner.

```markdown
# <Plugin Name>

One-sentence summary.

**Author:** Name

## When to Use
...

## When NOT to Use
...

## What It Does
...

## Installation
/plugin install phretor/skills/plugins/<plugin-name>
```

## Versioning

Bump `version` in **both** `plugin.json` and the root `.claude-plugin/marketplace.json` on every substantive change. Clients only update plugins when the version number increases.

Keep both version numbers in sync — a mismatch will cause the plugin to stall at the old version.

## Root `marketplace.json`

Add a new entry for each plugin. The `source` must point to `./plugins/<plugin-name>`:

```json
{
  "name": "<plugin-name>",
  "version": "1.0.0",
  "description": "Same as plugin.json.",
  "author": { "name": "...", "url": "..." },
  "source": "./plugins/<plugin-name>"
}
```

## Quality Standards

- **Description triggers**: third-person voice, specific verbs, concrete trigger phrases — not "helps with X"
- **Behavioral guidance over reference dumps**: explain *why* and *when*, not just *what*
- **No hardcoded absolute paths**: use `{baseDir}` or relative paths
- **Python scripts**: use PEP 723 inline dependency headers and `uv run`
- **SKILL.md under 500 lines**: split overflow into `references/` or `workflows/`
