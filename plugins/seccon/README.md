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

| Arguments to `ph-seccon` | Behaviour |
|---|---|
| `academic <question>` | Paper search, author lookup, tier rankings, acceptance rates |
| `industry <question>` | Talk search, DEF CON/Black Hat archives, practitioner venues |
| `help` | Show quick-start help and example commands |
| `[academic\|industry] now` | Live calendar — upcoming conferences and open CFPs |
| `[academic\|industry] now <acronym>` | Dates and deadlines for one specific conference |
| `[academic\|industry] now [<acronym>] <topic>` | Live calendar filtered or prioritized by topic |
| `[academic\|industry] deadlines [topic]` | Open CFPs only, deadline-sorted, optionally topic-filtered |
| `[academic\|industry] latest <acronym> [topic]` | Latest edition of a venue, with optional topic-focused results |
| `academic compare <venue1> <venue2>` | Side-by-side academic venue comparison |
| `academic <year> <acronym>` | Shorthand venue-year lookup for papers, program pages, and quick venue context |

Rankings derived from CORE 2023 and Guofei Gu's security conference statistics.
Live data: [confsearch.ethz.ch](https://confsearch.ethz.ch) (academic) · [cfptime.org](https://www.cfptime.org) (industry).

## Disclaimer

`ph-seccon` primarily operates from a **curated cache** (`resources/`) of paper
and talk metadata collected from public-facing conference websites. Cache
updates are done in batch by the maintainer; the agent only fetches live
content in two cases:
- **Calendar queries** (`now`, `deadlines`) via dedicated APIs (CFPTime,
  ConfSearch) that expect programmatic access.
- **On-demand PDF fetching** when the user drills into a specific paper or
  talk — a single targeted request per paper.
- **Author search and enrichment** through `uvx paperhub-cli` (DBLP, Semantic Scholar, arXiv) when the cache cannot answer.

This design minimizes traffic to upstream sites. If a venue is unreachable
(Cloudflare, paywall, JS-rendered), it is marked as a gap in the manifest
rather than retried on every query. Use responsibly.

## Requirements

- **pdftotext** (poppler) — for extracting text from downloaded papers and ACM DL frontmatter PDFs:
  ```bash
  brew install poppler        # macOS
  apt-get install poppler-utils  # Debian/Ubuntu
  ```

- **uv** — runs `paperhub-cli` on demand via `uvx paperhub-cli` (multi-source academic paper search, read, and download: arXiv, DBLP, Semantic Scholar, IACR, and more). No separate install step.
- **Internet access** — live calendar queries (ConfSearch, CFPTime) and on-demand paper fetching.

## Examples

Arguments passed to `ph-seccon`:

```text
help
academic now CCS side channels
industry deadlines browser exploitation
academic compare CCS NDSS
academic 2024 CCS
```
