# Contributing Skills

This repo follows the [Trail of Bits plugin layout](https://github.com/trailofbits/skills). Every plugin must conform to the structure below before being added to the root `marketplace.json`.

## Plugin Structure

Every plugin lives under `plugins/<plugin-name>/` and must contain:

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json             # Plugin metadata
├── commands/
│   └── <command-name>.md       # Slash command (required)
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md            # Skill entry point (required)
│       ├── references/         # Optional: detailed docs loaded on demand
│       ├── scripts/            # Optional: utility scripts
│       │   ├── <script>.py     #   PEP 723 inline deps + uv run
│       │   └── pyproject.toml  #   per-skill dep declaration + ruff config
│       └── workflows/          # Optional: step-by-step guides
└── README.md                   # Human-facing documentation (required)
```

Only `plugin.json` belongs in `.claude-plugin/`. Scripts and their `pyproject.toml` live inside `skills/<name>/scripts/`, not at the plugin root.

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

Command names must use the `ph:` namespace prefix to avoid autocomplete collisions (e.g. `ph:con`, not `con`). The part after the colon should match the plugin name by default; a shorter alias is fine if it reads more naturally.

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

Frontmatter must contain only `name`, `description`, and (optionally) `allowed-tools`. If you add extra fields for compatibility with other harnesses, keep them YAML-safe and expect Claude-oriented validators to warn. Never put `version` or `author` here — those belong in `plugin.json`.

```yaml
---
name: <skill-name>
description: "Third-person. What it does and when to use it. Include specific trigger phrases."
allowed-tools: Read Bash WebFetch # optional; space-separated
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
- **Behavioral guidance over reference dumps**: explain _why_ and _when_, not just _what_
- **No hardcoded absolute paths**: use `{baseDir}` or relative paths
- **Python scripts**: use PEP 723 inline dependency headers and `uv run`
- **System dependencies**: if you declare them in a SKILL.md `compatibility` field for Pi, also repeat them in `README.md` under a `## Requirements` section
- **SKILL.md under 500 lines**: split overflow into `references/` or `workflows/`

## YAML Frontmatter Steering

YAML parse failures are easy to introduce in skill frontmatter. Before committing, sanity-check these rules:

- **Quote any scalar containing `:`**. Example: `description: "Looks up S&P: rankings and papers"`
- **Prefer quoted strings for all frontmatter prose**, even when not strictly required
- **For long values, use a block scalar** instead of a long plain string:

```yaml
compatibility: >-
  Requires internet access. System dependency: pdftotext (poppler) for extracting
  text from downloaded papers and frontmatter PDFs. Install with `brew install
  poppler` (macOS) or `apt-get install poppler-utils` (Linux).
```

- **Do not use unquoted plain scalars with embedded `:`**, because YAML may treat them as nested mappings
- **Keep frontmatter minimal**; move detailed prose into the body when possible
- **If a field is optional for one harness but noisy for another, prefer documenting it in README.md instead of frontmatter**

Safe pattern:

```yaml
---
name: seccon
description: "Looks up academic and industry security conferences."
allowed-tools: WebFetch WebSearch Bash
compatibility: >-
  Requires internet access. Install pdftotext via `brew install poppler` or
  `apt-get install poppler-utils`.
---
```
