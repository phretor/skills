---
name: seccon
description: "Looks up academic and industry security conferences papers, authors, live CFP deadlines, topic-filtered calendars, venue comparisons, latest-edition lookups, and talk/paper evaluation. Operates from a curated cache (resources/) covering the most recent 5 years. Use when the user asks about wants to find papers at specific venues (S&P, CCS, USENIX, NDSS, DEF CON, Black Hat…), needs an author's publication record, wants to survey a topic across venues, or asks what conferences are coming up. Invoke as /skill:seccon help, /skill:seccon [academic|industry] now [acronym] [topic], /skill:seccon [academic|industry] deadlines [topic], /skill:seccon [academic|industry] latest [acronym] [topic], /skill:seccon academic compare <venue1> <venue2>, or /skill:seccon academic <year> <acronym>."
allowed-tools: WebFetch Bash
compatibility: >-
  Requires internet access. System dependency: pdftotext (poppler) for extracting
  text from downloaded papers and frontmatter PDFs — install with `brew install
  poppler` (macOS) or `apt-get install poppler-utils` (Linux). Run
  scripts/populate_cache.py after refreshing to rebuild the resource cache.
---

# seccon — Security Conference Intelligence

This skill uses a **curated cache** (`resources/`) with 5 years of paper/talk listings (2021–2025) for top venues. The cache is populated by responsible crawling of venue-native pages — titles and abstracts only. Full-text PDFs are fetched **on-demand** only when the user drills into a specific paper or talk.

Dispatches on the first argument:

- **`academic`** → peer-reviewed venues, TAMU tier rankings, paper search, live calendar via confsearch.ethz.ch
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
- Use `paperhub-cli search --no-plan` ONLY as enrichment after the cache returns no results. Never use DBLP,
  Semantic Scholar, arXiv, or any other API directly — those are reachable only through paperhub-cli.
- If a query targets a year outside 2021–2025, refuse with: "This skill covers the most recent 5 years (2021–2025). Content from <year> is outside the cached window. Contact the maintainer to extend coverage."
- If a query targets a venue or year that is listed as a gap in manifest.json, say so and optionally offer a calendar-based lookup (for upcoming conferences).

## Anti-Patterns — What This Skill Must NOT Do

These are common mistakes agents make when running this skill. Memorize them:

1. **Never populate the cache yourself by calling DBLP, Semantic Scholar, or any API directly.**
   The cache is maintained by the maintainer via `scripts/populate_cache.py`. If a venue-year
   is a gap, say so. Do not try to fill it at runtime by scraping DBLP XML, Semantic Scholar,
   or any other source.

2. **Never use `web_search` (Tavily, Brave, Google).**
   See IRON RULE below. This is the most commonly violated rule.

3. **Never use tools other than those explicitly listed (paperhub-cli, pdftotext, curl, Bash, WebFetch).**
   Do not invoke external search APIs, academic indexers, or paper databases that aren't
   paperhub-cli. paperhub-cli is the only approved external paper search tool, and only for
   enrichment after the cache has been exhausted.

6. **Never populate `archive_url` in index.json.**
   The `archive_url` field is unnecessary bloat. Each venue-year's `index.json` is already
   organized under `resources/{mode}/{year}/{venue}/`, so the archive URL is derivable from
   the path. Do not add `archive_url` at the conference level or on individual talk/paper
   entries. The `slides_url` field is fine when a direct link to slides exists, but
   `archive_url` must never appear.

4. **Never fabricate or hallucinate paper/talk metadata.**
   If the cache doesn't have a paper/talk listed, do not guess titles, authors, or DOIs.
   Say the data isn't available. The rubric dimensions (Tools/artifacts, Impact, etc.)
   must be sourced from actual content you fetched on-demand, not inferred.

5. **Never crawl conference pages outside the `scripts/` crawlers.**
   Do not write ad-hoc `curl` or `httpx` calls to scrape venue pages mid-conversation.
   Use `WebFetch` only for URLs explicitly documented in the skill (e.g., CFPTime,
   ConfSearch, a specific PDF the user asked about).

## IRON RULE — No Generic Web Search

This skill MUST NEVER call the `web_search` tool or any generic web search API
(e.g., Tavily, Brave, Google). The entire value of this skill is that it operates
exclusively on its curated cache (`resources/`), venue-native conference pages,
official program/schedule pages, proceedings archives, CFPTime, and ConfSearch.
If content is not in the cache and cannot be fetched on-demand via known venue
URLs, say so — do not fall back to generic web search.

Supported quick forms:
- `/skill:seccon help` → concise help and examples
- `/skill:seccon academic now` → upcoming and ongoing academic security conferences, sorted by date
- `/skill:seccon industry now` → upcoming industry conferences with open CFPs, sorted by conference date
- `/skill:seccon academic now <acronym>` → dates and deadlines for a specific conference
- `/skill:seccon [academic|industry] now <topic>` → upcoming conferences filtered by topic
- `/skill:seccon [academic|industry] now <acronym> <topic>` → specific conference + topic filter
- `/skill:seccon [academic|industry] deadlines [topic]` → open CFPs only, sorted by deadline
- `/skill:seccon [academic|industry] latest <acronym> [topic]` → latest edition from cache, with optional topic focus
- `/skill:seccon [academic|industry] latest <topic>` → cross-conference topic scan across cached venues
- `/skill:seccon academic compare <venue1> <venue2>` → compare rank, selectivity, focus
- `/skill:seccon academic <year> <acronym>` → venue-year lookup from cache

## Help output

If the user runs `/skill:seccon help`, return a concise quick-start guide. Include:
- one-line explanation of academic vs industry mode
- note that the skill uses a cached index of papers/talks (2021–2025) and fetches full text on-demand
- the main quick forms
- 8–12 concrete examples
- a short note that mode can be inferred when obvious, but explicit mode is preferred

Suggested help examples: `/skill:seccon academic now`, `/skill:seccon academic now CCS side channels`, `/skill:seccon industry now browser exploitation`, `/skill:seccon academic deadlines crypto`, `/skill:seccon academic latest USENIX fuzzing`, `/skill:seccon academic compare CCS NDSS`, `/skill:seccon academic 2024 CCS`.

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
- Content from before 2021 — outside the cached window

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
  "version": "1.3.0",
  "cached_range": { "earliest": 2021, "latest": 2025 },
  "coverage": {
    "academic": {
      "venues": {
        "ieee-sp": { "cached": [], "gaps": [2021, 2022, 2023, 2024, 2025], "note": "IEEEXplore paywall" },
        "defcon": { "cached": [2025], "gaps": [2021, 2022, 2023, 2024], "note": "" }
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
2. **Filter by year** — if outside 2021–2025, refuse. If a year is a known gap, say so.
3. **Filter by venue** — load matching `index.json` files. Filter by title/speaker/abstract keyword.
4. **Narrow to candidate papers/talks** — present the top matches with title, venue, year, and (when available) authors/speakers.
5. **Drill down on-demand** — when the user picks a specific paper/talk, fetch its full text:
   - Open-access PDF: download with `curl -sL <url> | pdftotext - -`
   - Paywalled: fetch abstract via Semantic Scholar, look for preprint on arXiv/author site
   - Use `paperhub-cli read --doi <doi> --full` for open-access sources
6. **Apply the Work Evaluation Rubric** for in-depth paper/talk evaluation.

---

## Work Evaluation Rubric

When asked about a specific paper or talk, always produce this block before any narrative:

**TL;DR**: ‹one sentence: what was done and the core claim›

| Dimension | Finding |
|---|---|
| Tools / artifacts | ✓ [name](url) — or — ✗ Not released |
| Reproducibility | High / Medium / Low — reason |
| Vulns found or patched | CVE-YYYY-NNNNN … — or — None |
| Industry impact | e.g., "Patched in iOS 17.4", "Adopted by vendor X", "No known deployment" |
| Academic impact | Citation count; notable follow-on papers or systematization-of-knowledge work |
| Counterpart work | Academic parallel: [ref] — Industry parallel: [talk @ conf] — or — None known |

**How to assess each dimension:**

- *Tools/artifacts*: look for GitHub links, project sites, dataset DOIs, PoC code, firmware images, artifact evaluation badges.
- *Reproducibility*: open-source code, public datasets, detailed methodology, Docker/VM images, artifact badges (USENIX/IEEE/ACM).
- *Industry impact*: CVE assignments, vendor acknowledgments, patch notes, product integration, news coverage from Krebs/Wired/Ars.
- *Academic impact*: cite count via Semantic Scholar; search for papers that cite this work in follow-on venues.
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
> "💡 CCS 2026 is upcoming — not yet in the cache. Once the program is published, the maintainer can add it by running `scripts/populate_cache.py`."

**For `/skill:seccon academic now` (all upcoming security conferences):**
```
GET https://confsearch.ethz.ch/api/search-engine/?query=security
```
Also query with: `privacy`, `cryptography`, `network security` to broaden coverage.

Filter results to conferences in the embedded tier tables (Tier 1 and 2). Drop results with blank `start` dates or past end dates. Sort by `start` ascending.

**For `/skill:seccon academic now <acronym>` (specific conference):**
```
GET https://confsearch.ethz.ch/api/search-engine/?query=<acronym>
```
Pick the top result matching the known acronym. Show all fields.

**For `/skill:seccon academic now <topic>` or `/skill:seccon academic now <acronym> <topic>`:**
- first resolve whether the first token after `now` is a known acronym from the tier table
- present calendar results and note any gaps in cache coverage

**Response fields used:** `acronym`, `name`, `location`, `deadline`, `notification`, `start`, `end`, `rank`, `www`

Note: the `rank` field is the CORE rank (A\*, A, B, C) — use it directly.

**Output format:**

| Conference | CORE | Dates | Location | Submission deadline | Website |
|---|---|---|---|---|---|
| CCS 2026 | A\* | Nov 15–19 2026 | The Hague, NL | Jan 14 / Apr 29 2026 | [link](…) |

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
| DEF CON 34 | Aug 2026 | Las Vegas, US | TBD | [link](…) |

Show CFP deadline relative to today. Highlight open CFPs. Omit conferences more than 12 months out unless explicitly asked.

### Deadlines shortcut

For `/skill:seccon [academic|industry] deadlines [topic]`:
- return only conferences with open CFPs, sorted by deadline ascending
- if a topic is supplied, filter by topic fit
- include a relative deadline note such as `closes in 9 days`

### Latest shortcut

For `/skill:seccon [academic|industry] latest <acronym> [topic]`:
- look up the latest cached edition of the venue from `resources/`
- if the latest cached year is marked as a gap, note that and check if an earlier year is available
- search within that edition for matching papers or talks by title/speaker/abstract
- present the best hits

For `/skill:seccon [academic|industry] latest <topic>` (no acronym):
- perform a **cross-conference topic scan** across all cached venues in that mode
- for each venue-year that has data, filter `talks`/`papers` by title/speaker/abstract keyword
- present results grouped by venue
- note any venues/years that are gaps in the cache

Examples:
- `/skill:seccon academic latest CCS`
- `/skill:seccon academic latest USENIX fuzzing`
- `/skill:seccon industry latest agentic vulnerability research`
- `/skill:seccon academic latest LLM supply chain attacks`

### Compare shortcut

For `/skill:seccon academic compare <venue1> <venue2>`:
- compare rank/tier, acceptance-rate trends, thematic focus, artifact culture
- use CORE + Guofei for venue standing
- present as a side-by-side table with a recommendation

### Academic Year + Acronym shorthand

For `/skill:seccon academic <year> <acronym>`:
1. Normalize the acronym against the ranked conference table
2. If the year is outside 2021–2025, refuse with the cache window message
3. Load the matching `index.json` from `resources/academic/{year}/{venue}/`
4. Return: conference full name, rank, edition URL, papers count, and 3–10 representative paper titles
5. If the venue-year is a gap, say so and suggest adding it

---

## Academic Mode

### Conference Rankings

**Sources for aggregate rank:**
- CORE 2023: https://portal.core.edu.au/conf-ranks/?search=security&by=all&source=CORE2023&sort=arank
- Guofei Gu security conference statistics (acceptance rates + community standing): https://people.engr.tamu.edu/guofei/sec_conf_stat.htm

**Aggregation rule:**
| Aggregate | Criteria |
|---|---|
| **Top** | CORE A\* *or* Guofei T1 |
| **High** | CORE A *or* Guofei T2 |
| **Mid** | CORE B *or* Guofei T3 |
| **Low** | CORE C |

#### Ranked Conferences

| Abbrev | Full Name | CORE | Guofei | **Aggregate** | Focus |
|---|---|---|---|---|---|
| IEEE S&P | IEEE Symposium on Security and Privacy | A\* | T1 | **Top** | Systems & applied |
| CCS | ACM Conf. on Computer and Communications Security | A\* | T1 | **Top** | Broad |
| USENIX Security | USENIX Security Symposium | A\* | T1 | **Top** | Systems & applied |
| NDSS | Network and Distributed System Security Symposium | A\* | T1 | **Top** | Network & systems |
| Crypto | International Cryptology Conference (IACR) | — | T1 | **Top** | Cryptography |
| Eurocrypt | European Cryptology Conference (IACR) | — | T1 | **Top** | Cryptography |
| ESORICS | European Symposium on Research in Computer Security | A | T2 | **High** | Broad |
| ACSAC | Annual Computer Security Applications Conference | A | T2 | **High** | Applied |
| AsiaCCS | ACM Asia Conf. on Computer and Comms Security | A | T2 | **High** | Asia-Pacific |
| PETS | Privacy Enhancing Technologies Symposium | A | T2 | **High** | Privacy |
| EuroS&P | IEEE European Symposium on Security and Privacy | A | T2 | **High** | Broad |
| CSF | IEEE Computer Security Foundations Symposium | A | T2 | **High** | Formal methods |
| Asiacrypt | Int'l Conf. on Theory and Application of Cryptology | A | T2 | **High** | Cryptography |
| TCC | Theory of Cryptography Conference | A | T2 | **High** | Crypto theory |
| FC | Financial Cryptography and Data Security | A | T2 | **High** | Financial crypto |
| RAID | Recent Advances in Intrusion Detection | — | T2 | **High** | Intrusion detection |
| DSN | Dependable Systems and Networks | — | T2 | **High** | Dependability |
| IMC | Internet Measurement Conference | — | T2 | **High** | Network measurement |
| CHES | Cryptographic Hardware and Embedded Systems | — | T2 | **High** | Hardware crypto |
| SOUPS | Symposium On Usable Privacy and Security | B | T2 | **High** | Usable security |
| ACNS | Applied Cryptography and Network Security | B | T3 | **Mid** | Applied crypto |
| ACISP | Australasian Conf. on Information Security & Privacy | AusB | T3 | **Mid** | Australasian |
| IFIP SEC | IFIP Information Security & Privacy Conference | B | T3 | **Mid** | Broad |
| WiSec | ACM Conf. on Security and Privacy in Wireless/Mobile | B | T3 | **Mid** | Wireless |
| DIMVA | Detection of Intrusions and Malware & Vuln. Assess. | — | T3 | **Mid** | Malware, detection |
| ICICS | Int'l Conf. on Information and Communications Security | — | T3 | **Mid** | Broad |
| SecureComm | Int'l Conf. on Security and Privacy in Comm. Networks | C | T3 | **Mid** | Comms security |
| PST | Privacy, Security and Trust | C | T3 | **Mid** | Broad |
| PKC | Int'l Conf. on Practice and Theory in Public-Key Crypto | B | — | **Mid** | Public-key crypto |
| SAC | Selected Areas in Cryptography | B | T3 | **Mid** | Cryptography |

#### Recent Acceptance Rates

| Conference | Approx. Rate | Trend |
|---|---|---|
| IEEE S&P | 12–18% | Getting harder |
| CCS | 18–22% | Stable |
| USENIX Security | 16–19% | Getting harder |
| NDSS | 14–18% | Slightly harder |
| Crypto / Eurocrypt | 25–30% | Stable (scope-filtered) |

### Author Search

1. DBLP: `https://dblp.org/search/?q={name}` — complete publication list grouped by venue
2. Semantic Scholar: `https://api.semanticscholar.org/graph/v1/author/search?query={name}&fields=name,affiliations,papers,citationCount`
3. Cross-reference results against the cache by matching venue acronym + year
4. Report: cached counts per venue, most-cited works, active co-authors, inferred themes

---

## Industry Mode

Read `resources/manifest.json` for cached industry venue-years.

### Top Industry Security Conferences

| Conference | Focus | Cache status |
|---|---|---|
| DEF CON | Broad hacking, underground research | ✅ 2021–2025 (428 talks) |
| Black Hat USA | Advanced research, enterprise security | ✅ 2021–2026 (580 talks) |
| Black Hat EU | Same, European edition | ✅ 2021–2025 (257 talks) |
| Black Hat Asia | Same, Asian edition | ✅ 2021–2025 (209 talks) |
| OffensiveCon | Offensive research, exploitation | ✅ 2022–2025 (44 talks) |
| REcon | Reverse engineering, binary analysis | ✅ 2022–2025 (65 talks) |
| — Lower-tier / uncached — | | |
| USENIX Security | Academic — systems security | ✅ 2024–2025 (857 papers) |
| IEEE S&P | Academic — systems & applied | ✅ 2021, 2023, 2024 (575 papers) |
| CCS | Academic — broad | ✅ 2022–2024 (997 papers) |
| NDSS | Academic — network & systems | ✅ 2021 (87 papers) |
| ACSAC | Academic — applied | ✅ 2021–2023, 2025 (296 papers) |
| ACISP | Academic — Australasian | ✅ 2021–2023 (87 papers) |
| RSA Conference | Enterprise, policy, threat intel | ❌ Not cached |
| CanSecWest | Advanced technical, Pwn2Own | ❌ Not cached (JS-rendered) |
| REcon | Reverse engineering, binary analysis | ❌ Not cached |
| Troopers | Network security, ICS, Active Directory | ❌ Not cached |
| hardwear.io | Hardware, embedded, IoT security | ❌ Not cached |
| Infiltrate | Offensive research, exploit dev | ❌ Not cached |
| HITCON | Asia-Pacific, CTF community | ❌ Not cached |
| HITB | Hacking in the Box (KL/Amsterdam) | ❌ Not cached |
| VB Conference | Malware, threat intelligence | ❌ Not cached |
| POC | Power of Community, Korea | ❌ Not cached |

### Cross-Conference Topic Scan (Industry)

Search the cached `resources/industry/{year}/defcon/index.json` and
`resources/industry/{year}/offensivecon/index.json` files by title/speaker.
For uncached venues, note the gap and suggest the maintainer add them.

When a talk has a companion paper (common at Black Hat), cross-reference it via
the academic rubric.

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

ACM DL (CCS, AsiaCCS) and IEEEXplore (S&P) require authentication; fetch abstracts via Semantic Scholar and look for preprints on arXiv or author homepages instead.

---

## paperhub-cli

`paperhub-cli` is installed as a project dependency (`uv sync`) and available in the shell. It searches, reads, and downloads academic papers across multiple open providers.

**Always pass `--no-plan` to `search`.**

### When to use

**Enrichment** — after finding a paper in the cache, use paperhub to fetch the abstract, citation count, or related work:
```bash
paperhub-cli search --no-plan "<paper title or topic>" \
  --sources arxiv,semantic_scholar \
  --top-k 5
```

**Full-text download** for open-access papers found in the cache:
```bash
paperhub-cli read --id arxiv:<id> --full
paperhub-cli download --id doi:<doi> --format md
```

---

## Cache Maintenance

`resources/` is populated by `scripts/populate_cache.py`. Run it to refresh or extend coverage:

```bash
# Populate all accessible venues
uv run scripts/populate_cache.py
```

To add a new venue or year that is currently a gap, the maintainer can:
1. Find the venue's accepted-papers or program page URL
2. Add it to `scripts/populate_cache.py`
3. Run the script
4. Update `resources/manifest.json` to mark the year as cached

The existing `scripts/crawl_conferences.py` can still be used for ad-hoc
content crawling during development.
