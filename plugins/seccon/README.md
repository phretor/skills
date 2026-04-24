# seccon

Security conference intelligence for security researchers — academic and industry venues.

**Author:** Federico Maggi

## When to Use

- Look up conference tier rankings or acceptance rates
- Find papers at specific venues (S&P, CCS, USENIX, NDSS, DEF CON, Black Hat…)
- Search an author's publication record across top-tier venues
- Evaluate a paper or talk: TL;DR, artifacts, CVEs, industry/academic impact
- Survey a research topic across conferences
- Check upcoming conferences and open CFP deadlines

## When NOT to Use

- General security news or vulnerability lookups — search the web directly
- CVE details or patch tracking — use a CVE database
- Non-security academic conferences

## What It Does

| Invocation | Behaviour |
|---|---|
| `/skill:seccon academic <question>` | Paper search, author lookup, tier rankings, acceptance rates |
| `/skill:seccon industry <question>` | Talk search, DEF CON/Black Hat archives, practitioner venues |
| `/skill:seccon help` | Show quick-start help and example commands |
| `/skill:seccon [academic\|industry] now` | Live calendar — upcoming conferences and open CFPs |
| `/skill:seccon [academic\|industry] now <acronym>` | Dates and deadlines for one specific conference |
| `/skill:seccon [academic\|industry] now [<acronym>] <topic>` | Live calendar filtered or prioritized by topic |
| `/skill:seccon [academic\|industry] deadlines [topic]` | Open CFPs only, deadline-sorted, optionally topic-filtered |
| `/skill:seccon [academic\|industry] latest <acronym> [topic]` | Latest edition of a venue, with optional topic-focused results |
| `/skill:seccon academic compare <venue1> <venue2>` | Side-by-side academic venue comparison |
| `/skill:seccon academic <year> <acronym>` | Shorthand venue-year lookup for papers, program pages, and quick venue context |

Rankings derived from CORE 2023 and Guofei Gu's security conference statistics.
Live data: [confsearch.ethz.ch](https://confsearch.ethz.ch) (academic) · [cfptime.org](https://www.cfptime.org) (industry).

## Requirements

- **pdftotext** (poppler) — for extracting text from downloaded papers and ACM DL frontmatter PDFs:
  ```bash
  brew install poppler        # macOS
  apt-get install poppler-utils  # Debian/Ubuntu
  ```

- **paperhub-cli** — multi-source academic paper search, read, and download (arXiv, DBLP, Semantic Scholar, IACR, and more). Installed automatically via `uv sync` from the repo root:
  ```bash
  uv sync
  ```

## Installation

### Pi

```bash
pi install https://github.com/phretor/skills
```

Then invoke:

```
/skill:seccon help
/skill:seccon academic now
/skill:seccon academic latest USENIX fuzzing
```

### Claude Code

```bash
/plugin install https://github.com/phretor/skills
```

Or from a local checkout:

```bash
/plugin install ./plugins/seccon
```

Then invoke directly in conversation (e.g., "find industry talks on agentic vulnerability research") or use the command:

```
/skill:seccon help
```

### Claude Desktop

1. Open Claude Desktop → Settings → Developer → Edit configuration
2. Add the repo as a plugin source in `claude_desktop_config.json`:

```json
{
  "plugins": {
    "sources": [
      {"url": "https://github.com/phretor/skills", "type": "github"}
    ]
  }
}
```

Or clone the repo and reference it locally:

```json
{
  "plugins": {
    "sources": [
      {"type": "local", "path": "/path/to/skills/plugins/seccon"}
    ]
  }
}
```

3. Restart Claude Desktop.

## Examples

```bash
/skill:seccon help
/skill:seccon academic now CCS side channels
/skill:seccon industry deadlines browser exploitation
/skill:seccon academic compare CCS NDSS
/skill:seccon academic 2024 CCS
```
