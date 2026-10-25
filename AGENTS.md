# Contributing Skills

This repo follows the [Trail of Bits plugin layout](https://github.com/trailofbits/skills). Skills follow the [Agent Skills spec](https://agentskills.io) so they run on Claude Code, Codex, Pi, OMP, Hermes, and any client supported by `npx skills`. Every plugin must conform to the structure below before being added to the root `marketplace.json`.

## Plugin Structure

Every plugin lives under `plugins/<plugin-name>/` and must contain:

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json             # Plugin metadata
├── skills/
│   └── ph-<skill-name>/
│       ├── SKILL.md            # Skill entry point (required)
│       ├── agents/openai.yaml  # Optional: Codex UI metadata
│       ├── references/         # Optional: detailed docs loaded on demand
│       ├── scripts/            # Optional: scripts the skill runs for users
│       │   └── <script>.py     #   PEP 723 inline deps + uv run
│       └── workflows/          # Optional: step-by-step guides
├── maintainer/                 # Optional: tooling for maintainers only
└── README.md                   # Human-facing documentation (required)
```

Only `plugin.json` belongs in `.claude-plugin/`. There is no `commands/` directory: skills are the only entry point. Tooling that only maintainers run (crawlers, cache builders, lockfiles) lives in `plugins/<plugin-name>/maintainer/`, outside `skills/`, so `npx skills` copies do not ship it.

## Naming

Every skill directory and its frontmatter `name` start with `ph-` (for example `ph-seccon`). Flat install targets (`~/.agents/skills`, `~/.hermes/skills`, `npx skills` agent directories) key skills by directory name, so unprefixed names collide with other skills. The Agent Skills spec requires `name` to equal the directory name. Plugin names carry no prefix.

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

### `skills/<skill-name>/SKILL.md`

Frontmatter must contain only `name`, `description`, and optionally `allowed-tools`, `compatibility`, `license`, `metadata`. Never put `version` or `author` here — those belong in `plugin.json`. `allowed-tools` is experimental in the spec and ignored by most harnesses; keep it for Claude Code but never rely on it for behavior.

```yaml
---
name: ph-<skill-name>
description: "Third-person. What it does and when to use it. Include specific trigger phrases."
allowed-tools: Read Bash WebFetch # optional; space-separated
compatibility: >-
  Requires uv and internet access. # optional; system dependencies
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

If a skill takes arguments, document them in the body as plain patterns (for example `<document-type> [text|file]`), not as a harness slash command.

### `README.md`

Human-facing. Must include: author, When to Use, When NOT to Use, What It Does. Add a `## Requirements` section when the skill needs system dependencies.

**Installation instructions are NOT placed here.** All installation and invocation instructions (Claude Code, Codex, Pi, OMP, Hermes, `npx skills`) live in the root `README.md` only.

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
```

## Harness-Neutral Wording

Shipped skill files (`SKILL.md`, `references/`, `workflows/`) must read the same on every harness.

- No harness invocation syntax: no `/skill:<name>`, `/<plugin>:<skill>`, `/ph:<command>`. Say "invoke `ph-seccon` with `help`".
- Refer to tools by function, not harness tool name: "fetch the URL", "run in a shell", "browser or visual tools". Never write `AskUserQuestion` or `WebFetch(...)` call syntax in the body.
- MCP tools are referenced by bare tool name (`get_entries`) with one note that harnesses may prefix them (`mcp__miniflux__get_entries` in Claude Code).
- No harness-specific configuration paths ("Claude Code settings"): say "your agent's MCP configuration".
- No absolute or home paths. Scripts and resources are referenced relative to the skill's directory (`uv run scripts/extract_deck.py <pdf>`).
- Runtime dependencies must work from a copied skill directory alone: run published tools with `uvx <package>`, never rely on a repo-root `uv sync`. Declare `uv` and system dependencies in `compatibility` and in the plugin README `## Requirements`.

## Versioning

Bump `version` in **both** `plugins/<plugin-name>/.claude-plugin/plugin.json` and the plugin's entry in the root `.claude-plugin/marketplace.json` on every substantive change, and add a `CHANGELOG.md` entry. Clients only update plugins when the version number increases. Keep both version numbers in sync — a mismatch will cause the plugin to stall at the old version.

Version fields and what they mean:

- Plugin version: `plugin.json` and the plugin's marketplace entry. Independent per plugin. Must match.
- Repository version: `package.json` `version` and marketplace `metadata.version`. One number for the repo as a whole; keep them equal and bump on repo-wide changes.
- `plugins/seccon/skills/ph-seccon/resources/manifest.json` `version`: the cache dataset version, bumped by `maintainer/write_manifest.py` when cache content changes. Independent of the plugin version.

`CHANGELOG.md` entries are headed `## <plugin> <version> - <date>` (repo-wide changes: `## repo <version> - <date>`). Every plugin's current version needs a section.

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
- **No hardcoded absolute paths**: use relative paths from the skill directory
- **Python scripts**: use PEP 723 inline dependency headers and `uv run`
- **System dependencies**: if you declare them in a SKILL.md `compatibility` field, also repeat them in `README.md` under a `## Requirements` section, and in the root `README.md` Requirements table
- **SKILL.md under 500 lines**: split overflow into `references/` or `workflows/`
- **Installation instructions centralized**: all install and invocation instructions for every plugin live in the root `README.md`, never duplicated in per-plugin `README.md` files
- **README kept in sync**: every addition or change to a plugin/skill must also update the root `README.md` — the Skills table, Requirements table, badges (Skills count), and any other relevant sections must reflect the new or changed plugin
- **No `:` in file names**: tracked paths must be valid on Windows checkouts

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
name: ph-seccon
description: "Looks up academic and industry security conferences."
allowed-tools: WebFetch Bash
compatibility: >-
  Requires internet access. Install pdftotext via `brew install poppler` or
  `apt-get install poppler-utils`.
---
```
