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
content for these operations:
- **Calendar queries** (`now`, `deadlines`) via dedicated APIs (CFPTime,
  ConfSearch) that expect programmatic access.
- **On-demand PDF fetching** when the user drills into a specific paper or
  talk — a single targeted request per paper.
- **Author search and enrichment** through `uvx paperhub-cli` only when the selected provider's current policy permits the operation; Crossref is an available metadata option.

Every live operation checks robots/AI restrictions and terms before access. Denials, challenges and rate limits are explicit unavailable results; browser impersonation and automatic denial retries are removed. DBLP XML/search, DEF CON media and YouTube RSS were policy-limited in the 2026-10-25 investigation. Calendar and enrichment coverage also depends on current source permission and availability.

The manifest separates file availability from content quality, acquisition age and the latest refresh result. Cached records are not a completeness claim. Unknown acquisition times stay unknown; imports preserve source provenance and derive abstract/slide availability from records. Topic matching includes both `abstract` and `description`.

Maintainer crawling shares an explicit/registry pipeline with bounded same-origin linked data, per-origin pacing/budgets, redirect checks, deferred publisher resolution, and IEEE S&P discovery. The populator accepts selected venues and years, defaults through the current calendar year, preserves earlier indexes on failure, and records unsupported adapters. Black Hat imports require authorized local exports; hardwear.io RSS is partial and has no Data API implementation. Existing indexes remain available, with suspect content marked for review.

See [maintenance limits and outcomes](skills/ph-seccon/references/maintenance.md). No automatic refresh is promised for a denied or unsupported source.

## Requirements

- **pdftotext** (poppler) — for extracting text from permitted, downloaded papers:
  ```bash
  brew install poppler        # macOS
  apt-get install poppler-utils  # Debian/Ubuntu
  ```

- **uv** — runs `paperhub-cli` on demand via `uvx paperhub-cli` (multi-source academic paper search, read, and download: arXiv, DBLP, Semantic Scholar, IACR, and more). No separate install step.
- **Internet access** — permitted live calendar queries (ConfSearch, CFPTime) and on-demand paper fetching.
- **Python 3.12+** — repository maintainer scripts use the standard library; no HTTP/browser-impersonation dependency is required.

## Examples

Arguments passed to `ph-seccon`:

```text
help
academic now CCS side channels
industry deadlines browser exploitation
academic compare CCS NDSS
academic 2024 CCS
```
