---
name: ph-seccon
description: "Looks up academic and industry security conference papers, authors, live CFP deadlines, topic-filtered calendars, venue comparisons, latest-edition lookups, and talk/paper evaluation. Operates from a curated cache (resources/) whose coverage is stated in resources/manifest.json. Use when the user wants to find papers or talks at specific venues (S&P, CCS, USENIX, NDSS, DEF CON, Black Hat…), needs an author's publication record, wants to survey a topic across venues, or asks what conferences are coming up. Invoke with `help`, `[academic|industry] now [acronym] [topic]`, `[academic|industry] deadlines [topic]`, `[academic|industry] latest [acronym] [topic]`, `academic compare <venue1> <venue2>`, or `academic <year> <acronym>`."
allowed-tools: WebFetch Bash
compatibility: >-
  Requires internet access and uv (paperhub-cli runs via `uvx paperhub-cli`).
  System dependency: pdftotext (poppler) for extracting text from downloaded
  papers and frontmatter PDFs — install with `brew install poppler` (macOS) or
  `apt-get install poppler-utils` (Linux).
---

# seccon — Security Conference Intelligence

This skill uses a **curated cache** (`resources/`) of paper/talk listings for top venues. The years covered are `cached_range` in `resources/manifest.json`; never assume a window from memory. The cache is populated by responsible crawling of venue-native pages — titles and abstracts only. Full-text PDFs are fetched **on-demand** only when the user drills into a specific paper or talk.

Dispatches on the first argument:

- **`academic`** → peer-reviewed venues, aggregate tier rankings (CORE 2023 + Guofei Gu), paper search, live calendar via confsearch.ethz.ch
- **`industry`** → practitioner conferences, talk archives, live CFP calendar via cfptime.org

Infer the mode from context when unambiguous (e.g., "DEF CON" → industry, "IEEE S&P" → academic). Ask only when genuinely ambiguous.

The second argument can be:
- **`help`** to show examples and supported shortcuts
- **`now`** to trigger a live calendar query
- **`deadlines`**, **`latest`**, **`compare`**, a **4-digit year**, or any free-form topic/query

Mandatory execution rules:
- Always start by reading `resources/manifest.json` to learn what is cached and what is missing.
- Search the cache first: filter `resources/{academic|industry}/{year}/{venue}/index.json` by title, speakers, or abstract.
- Only fetch full-text content (PDF) on-demand when the user asks about a specific paper or talk in detail.
- Use `uvx paperhub-cli` for enrichment after the cache returns no results and for author search. Never call DBLP,
  Semantic Scholar, arXiv, or any other metadata API directly — those are reachable only through paperhub-cli.
  Downloading the PDF of a specific paper from a documented open-access source (see PDF Extraction) is allowed.
- If a query targets a year outside `cached_range` in the manifest, refuse with: "This skill covers <earliest>–<latest>. Content from <year> is outside the cached window. Contact the maintainer to extend coverage."
- If a query targets a venue or year that is listed as a gap in manifest.json, say so and optionally offer a calendar-based lookup (for upcoming conferences).

## Anti-Patterns — What This Skill Must NOT Do

These are common mistakes agents make when running this skill. Memorize them:

1. **Never populate the cache yourself by calling DBLP, Semantic Scholar, or any API directly.**
   The cache is maintained by the maintainer with the scripts in the repository's
   `plugins/seccon/maintainer/` directory. If a venue-year is a gap, say so. Do not try to
   fill it at runtime by scraping DBLP XML, Semantic Scholar, or any other source.

2. **Never use `web_search` (Tavily, Brave, Google).**
   See IRON RULE below. This is the most commonly violated rule.

3. **Never use tools other than those explicitly listed (paperhub-cli, pdftotext, curl, and a URL-fetch tool).**
   Do not invoke external search APIs, academic indexers, or paper databases that aren't
   paperhub-cli. paperhub-cli is the only approved external paper search tool: it is the
   only route to DBLP, Semantic Scholar, and arXiv, used for enrichment after the cache has
   been exhausted and for author search.

4. **Never fabricate or hallucinate paper/talk metadata.**
   If the cache doesn't have a paper/talk listed, do not guess titles, authors, or DOIs.
   Say the data isn't available. The rubric dimensions (Tools/artifacts, Impact, etc.)
   must be sourced from actual content you fetched on-demand, not inferred.

5. **Never crawl conference pages mid-conversation.**
   Do not write ad-hoc `curl` or `httpx` calls to scrape venue pages.
   Fetch URLs only when they are explicitly documented in the skill (e.g., CFPTime,
   ConfSearch, a specific PDF the user asked about).

## IRON RULE — No Generic Web Search

This skill MUST NEVER call the `web_search` tool or any generic web search API
(e.g., Tavily, Brave, Google). The entire value of this skill is that it operates
exclusively on its curated cache (`resources/`), venue-native conference pages,
official program/schedule pages, proceedings archives, CFPTime, and ConfSearch.
If content is not in the cache and cannot be fetched on-demand via known venue
URLs, say so — do not fall back to generic web search.

Supported argument forms (invoke `ph-seccon` with one of these):
- `help` → concise help and examples
- `academic now` → upcoming and ongoing academic security conferences, sorted by date
- `industry now` → upcoming industry conferences with open CFPs, sorted by conference date
- `academic now <acronym>` → dates and deadlines for a specific conference
- `[academic|industry] now <topic>` → upcoming conferences filtered by topic
- `[academic|industry] now <acronym> <topic>` → specific conference + topic filter
- `[academic|industry] deadlines [topic]` → open CFPs only, sorted by deadline
- `[academic|industry] latest <acronym> [topic]` → latest edition from cache, with optional topic focus
- `[academic|industry] latest <topic>` → cross-conference topic scan across cached venues
- `academic compare <venue1> <venue2>` → compare rank, selectivity, focus
- `academic <year> <acronym>` → venue-year lookup from cache

## Help output

If the user invokes `help`, return a concise quick-start guide. Include:
- one-line explanation of academic vs industry mode
- note that the skill uses a cached index of papers/talks (state the `cached_range` from the manifest) and fetches full text on-demand
- the main quick forms
- 8–12 concrete examples
- a short note that mode can be inferred when obvious, but explicit mode is preferred

Suggested help examples: `academic now`, `academic now CCS side channels`, `industry now browser exploitation`, `academic deadlines crypto`, `academic latest USENIX fuzzing`, `academic compare CCS NDSS`, `academic 2024 CCS`.

---

## When to Use

- Finding papers published at a specific venue and year
- Evaluating a specific paper or talk (methodology, artifacts, CVEs, impact)
- Searching an author's publication record across top-tier security venues
- Surveying what's been published on a topic across multiple conferences
- Checking upcoming conference dates or open CFP deadlines
- Looking up the prestige or acceptance rate of a security conference

## When NOT to Use

- General web search for security news or vulnerability disclosures — use a search tool directly
- Finding CVE details or patch information — use a CVE database
- Broad programming or software engineering questions unrelated to academic/industry security research
- Content outside the manifest's `cached_range`

---

## Resource Cache (`resources/`)

All paper/talk metadata lives under `resources/` organized as:

```
resources/
├── manifest.json                    # Coverage map: what's cached, what's gaps
├── academic/{year}/{venue}/index.json
└── industry/{year}/{venue}/index.json
```

### `manifest.json`

Read this first on every query. It tells you which venues/years are cached and which are known gaps:

```json
{
  "version": "1.4.0",
  "generated": "2026-10-24",
  "cached_range": { "earliest": 2021, "latest": 2026 },
  "coverage": {
    "academic": {
      "venues": {
        "ccs": { "cached": [2022, 2023, 2024], "gaps": [2021, 2025, 2026], "note": "" }
      }
    },
    "industry": {
      "venues": {
        "hitb": { "cached": [], "gaps": [2021, 2022, 2023, 2024, 2025, 2026], "note": "Not yet crawled" }
      }
    }
  }
}
```

### `index.json` (per venue-year)

Each file lists all papers/talks for one venue edition:

```json
{
  "conference": {
    "name": "DEF CON 33",
    "acronym": "DEF CON",
    "year": 2025, "edition": 33,
    "url": "https://media.defcon.org/DEF%20CON%2033/"
  },
  "coverage": {
    "talks_count": 102,
    "has_abstracts": false,
    "has_slides": true,
    "last_crawled": "2026-04-24"
  },
  "talks": [
    {
      "id": "dc33-001",
      "title": "Invitation Is All You Need! ...",
      "speakers": ["Ben Nassi", "Or Yair", "Stav Cohen"],
      "slides_url": "https://media.defcon.org/.../...pdf"
    }
  ]
}
```

### Query Flow

1. **Read `resources/manifest.json`** — identify which venues/years are cached and which are gaps.
2. **Filter by year** — if outside `cached_range`, refuse. If a year is a known gap, say so.
3. **Filter by venue** — load matching `index.json` files. Filter by title/speaker/abstract keyword.
4. **Narrow to candidate papers/talks** — present the top matches with title, venue, year, and (when available) authors/speakers.
5. **Drill down on-demand** — when the user picks a specific paper/talk, fetch its full text:
   - Open-access PDF: download with `curl -sL <url> | pdftotext - -`
   - Paywalled: fetch the abstract with `uvx paperhub-cli read --id doi:<doi>`, and look for a preprint with `uvx paperhub-cli search --no-plan` (arXiv)
   - Open-access sources: `uvx paperhub-cli read --id doi:<doi> --full`
6. **Apply the Work Evaluation Rubric** for in-depth paper/talk evaluation.

---

## Work Evaluation Rubric

When asked about a specific paper or talk, always produce this block before any narrative:

**TL;DR**: ‹one sentence: what was done and the core claim›

| Dimension | Finding |
|---|---|
| Tools / artifacts | ✓ name + URL — or — ✗ Not released |
| Reproducibility | High / Medium / Low — reason |
| Vulns found or patched | CVE-YYYY-NNNNN … — or — None |
| Industry impact | e.g., "Patched in iOS 17.4", "Adopted by vendor X", "No known deployment" |
| Academic impact | Citation count; notable follow-on papers or systematization-of-knowledge work |
| Counterpart work | Academic parallel: [ref] — Industry parallel: [talk @ conf] — or — None known |

**How to assess each dimension:**

- *Tools/artifacts*: look for GitHub links, project sites, dataset DOIs, PoC code, firmware images, artifact evaluation badges.
- *Reproducibility*: open-source code, public datasets, detailed methodology, Docker/VM images, artifact badges (USENIX/IEEE/ACM).
- *Industry impact*: CVE assignments, vendor acknowledgments, patch notes, product integration, news coverage from Krebs/Wired/Ars.
- *Academic impact*: cite count via `uvx paperhub-cli` (source `semantic_scholar`); search for papers that cite this work in follow-on venues.
- *Counterpart*: search whether an industry talk preceded/followed an academic paper on the same topic, or vice versa.

---

## Live Calendar (`now`)

### Academic — `now`

Fetch from ConfSearch (ETH Zurich). The API returns CORE-ranked conferences with submission deadlines, notification dates, and conference dates.

If the user supplies an optional **topic** after `now`, use it to refine the calendar response:
- query ConfSearch with both the default broad terms (`security`, `privacy`, `cryptography`, `network security`) and the user topic
- keep the normal Tier 1/2 conference filtering
- reorder results to prioritize venues matching the topic
- add a short **Topic fit** note per row or as a bullet below the table

When calendar results show a venue-year that is NOT in the cache (a gap), note it:
> "💡 CCS 2026 is upcoming — not yet in the cache. Once the program is published, the maintainer can add it."

**For `academic now` (all upcoming security conferences):**
```
GET https://confsearch.ethz.ch/api/search-engine/?query=security
```
Also query with: `privacy`, `cryptography`, `network security` to broaden coverage.

Filter results to conferences in the tier table in `references/academic-rankings.md` (Tier 1 and 2). Drop results with blank `start` dates or past end dates. Sort by `start` ascending.

**For `academic now <acronym>` (specific conference):**
```
GET https://confsearch.ethz.ch/api/search-engine/?query=<acronym>
```
Pick the top result matching the known acronym. Show all fields.

**For `academic now <topic>` or `academic now <acronym> <topic>`:**
- first resolve whether the first token after `now` is a known acronym from the tier table
- present calendar results and note any gaps in cache coverage

**Response fields used:** `acronym`, `name`, `location`, `deadline`, `notification`, `start`, `end`, `rank`, `www`

Note: the `rank` field is the CORE rank (A\*, A, B, C) — use it directly.

**Output format:**

| Conference | CORE | Dates | Location | Submission deadline | Website |
|---|---|---|---|---|---|
| CCS 2026 | A\* | Nov 15–19 2026 | The Hague, NL | Jan 14 / Apr 29 2026 | website URL |

Add a section for **open CFPs** and **upcoming conferences** within 90 days.

### Industry — `now`

Fetch from CFPTime. The API returns cybersecurity-focused industry conferences sorted by conference start date.

If the user supplies an optional **topic** after `now`, use it to refine the calendar response:
- filter or prioritize conferences matching the topic
- when CFPTime fields are sparse, supplement with the conference website or CFP page
- add a short **Why it matches** note

**Upcoming conferences and open CFPs:**
```
GET https://api.cfptime.org/api/upcoming/
```

**New conference announcements (RSS):**
```
GET https://api.cfptime.org/rss
```

**Response fields used:** `name`, `cfp_deadline`, `conf_start_date`, `city`, `country`, `website`, `cfp_details`

**Output format:**

| Conference | Dates | Location | CFP deadline | Website |
|---|---|---|---|---|
| DEF CON 34 | Aug 2026 | Las Vegas, US | TBD | website URL |

Show CFP deadline relative to today. Highlight open CFPs. Omit conferences more than 12 months out unless explicitly asked.

### Deadlines shortcut

For `[academic|industry] deadlines [topic]`:
- return only conferences with open CFPs, sorted by deadline ascending
- if a topic is supplied, filter by topic fit
- include a relative deadline note such as `closes in 9 days`

### Latest shortcut

For `[academic|industry] latest <acronym> [topic]`:
- look up the latest cached edition of the venue from `resources/`
- if the latest cached year is marked as a gap, note that and check if an earlier year is available
- search within that edition for matching papers or talks by title/speaker/abstract
- present the best hits

For `[academic|industry] latest <topic>` (no acronym):
- perform a **cross-conference topic scan** across all cached venues in that mode
- for each venue-year that has data, filter `talks`/`papers` by title/speaker/abstract keyword
- present results grouped by venue
- note any venues/years that are gaps in the cache

Examples:
- `academic latest CCS`
- `academic latest USENIX fuzzing`
- `industry latest agentic vulnerability research`
- `academic latest LLM supply chain attacks`

### Compare shortcut

For `academic compare <venue1> <venue2>`:
- compare rank/tier, acceptance-rate trends, thematic focus, artifact culture
- use CORE + Guofei for venue standing
- present as a side-by-side table with a recommendation

### Academic Year + Acronym shorthand

For `academic <year> <acronym>`:
1. Normalize the acronym against the ranked conference table in `references/academic-rankings.md`
2. If the year is outside `cached_range`, refuse with the cache window message
3. Load the matching `index.json` from `resources/academic/{year}/{venue}/`
4. Return: conference full name, rank, edition URL, papers count, and 3–10 representative paper titles
5. If the venue-year is a gap, say so and suggest adding it

---

## Academic Mode

Rankings, aggregation rule, the ranked conference table, and acceptance-rate trends live in `references/academic-rankings.md`. Read it for tier lookups, venue comparison, `now` tier filtering, and acronym normalization.

Rankings derive from CORE 2023 and Guofei Gu's security conference statistics.

### Author Search

Route every lookup through `paperhub-cli` (sources `dblp` and `semantic_scholar`):

```bash
uvx paperhub-cli search --no-plan --author "<name>" --sources dblp,semantic_scholar --top-k 20 "<name>"
```

1. Run the search; providers may rate-limit (HTTP 429) or return empty results. Report the failure instead of calling DBLP or Semantic Scholar directly.
2. Cross-reference results against the cache by matching venue acronym + year.
3. Report: cached counts per venue, most-cited works, active co-authors, inferred themes.

---

## Industry Mode

Read `resources/manifest.json` for cached industry venue-years. Venue names, manifest slugs, and focus areas are in `references/industry-venues.md`.

### Cross-Conference Topic Scan (Industry)

Search every cached industry venue-year listed in the manifest (`resources/industry/{year}/{venue}/index.json`) by title/speaker/abstract. For venues with no cached years, note the gap and suggest the maintainer add them.

When a talk has a companion paper (common at Black Hat), cross-reference it via the academic rubric.

---

## PDF Extraction

When a paper or proceedings frontmatter is available as a PDF, extract text with `pdftotext` (poppler):

```bash
# From a URL — download then extract
curl -sL <pdf-url> -o paper.pdf && pdftotext paper.pdf -

# Direct pipe
curl -sL <pdf-url> | pdftotext - -
```

Open-access sources where full-text PDFs are available without auth:
- USENIX Security and SOUPS: linked from the technical sessions page
- NDSS: linked from the programme page
- IACR ePrint: `https://eprint.iacr.org/{YYYY}/{NNN}.pdf`
- arXiv cs.CR: `https://arxiv.org/pdf/{id}`
- DEF CON presentations: `media.defcon.org/DEF%20CON%20{N}/...presentations/`

ACM DL (CCS, AsiaCCS) and IEEEXplore (S&P) require authentication; fetch abstracts with `uvx paperhub-cli read --id doi:<doi>` and look for preprints through `uvx paperhub-cli search --no-plan` (arXiv) instead.

---

## paperhub-cli

`paperhub-cli` runs on demand through `uvx` (requires `uv`; no install step). It searches, reads, and downloads academic papers across multiple open providers.

**Always pass `--no-plan` to `search`.**

### When to use

**Enrichment** — after finding a paper in the cache, use paperhub to fetch the abstract, citation count, or related work:
```bash
uvx paperhub-cli search --no-plan "<paper title or topic>" \
  --sources arxiv,semantic_scholar \
  --top-k 5
```

**Full-text download** for open-access papers found in the cache:
```bash
uvx paperhub-cli read --id arxiv:<id> --full
uvx paperhub-cli download --id doi:<doi> --format md
```

---

## Cache Maintenance

`resources/` is populated by the maintainer scripts in the repository at `plugins/seccon/maintainer/` (not shipped with `npx skills` installs). Run from `plugins/seccon/` to refresh or extend coverage:

```bash
# Populate all accessible venues
uv run maintainer/populate_cache.py
```

Never populate `archive_url` in an `index.json`: each file already sits under `resources/{mode}/{year}/{venue}/`, so the archive URL is derivable from the path. The `slides_url` field is fine when a direct link to slides exists.

To add a new venue or year that is currently a gap, the maintainer can:
1. Find the venue's accepted-papers or program page URL
2. Add it to `maintainer/populate_cache.py`
3. Run the script
4. Update `resources/manifest.json` to mark the year as cached

The existing `maintainer/crawl_conferences.py` can still be used for ad-hoc
content crawling during development.
