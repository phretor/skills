---
name: seccon
description: "Looks up academic and industry security conferences papers, authors, live CFP deadlines, topic-filtered calendars, venue comparisons, latest-edition lookups, and talk/paper evaluation. Use when the user asks about wants to find papers at specific venues (S&P, CCS, USENIX, NDSS, DEF CON, Black Hat…), needs an author's publication record, wants to survey a topic across venues, or asks what conferences are coming up. Invoke as /skill:seccon help, /skill:seccon [academic|industry] now [acronym] [topic], /skill:seccon [academic|industry] deadlines [topic], /skill:seccon [academic|industry] latest [acronym] [topic], /skill:seccon academic compare <venue1> <venue2>, or /skill:seccon academic <year> <acronym>."
allowed-tools: WebFetch Bash
compatibility: >-
  Requires internet access. System dependency: pdftotext (poppler) for extracting
  text from downloaded papers and frontmatter PDFs — install with `brew install
  poppler` (macOS) or `apt-get install poppler-utils` (Linux). Run
  scripts/crawl_conferences.py annually to refresh year-specific URL lists.
---

# seccon — Security Conference Intelligence

Dispatches on the first argument:

- **`academic`** → peer-reviewed venues, TAMU tier rankings, paper search, live calendar via confsearch.ethz.ch
- **`industry`** → practitioner conferences, talk archives, live CFP calendar via cfptime.org

Infer the mode from context when unambiguous (e.g., "DEF CON" → industry, "IEEE S&P" → academic). Ask only when genuinely ambiguous.

The second argument can be:
- **`help`** to show examples and supported shortcuts
- **`now`** to trigger a live calendar query instead of a paper/talk search
- **`deadlines`**, **`latest`**, **`compare`**, a **4-digit year**, or any free-form topic/query

Mandatory execution rules:
- For `/skill:seccon academic "<topic>"` or any topic scan, use this skill's conference workflow; do not switch to generic ad-hoc Semantic Scholar/DBLP scripts as the primary path.
- Prefer venue-native raw pages: read `references/academic.md`, crawl conference pages with `uv run scripts/crawl_conferences.py --crawl-content ...`, then reason over the raw content yourself.
- Use Semantic Scholar, DBLP, arXiv, or `paperhub-cli` only as fallback/enrichment after venue-native crawling fails or is incomplete.

## IRON RULE — No Generic Web Search

This skill MUST NEVER call the `web_search` tool or any generic web search API
(e.g., Tavily, Brave, Google). The entire value of this skill is that it operates
exclusively on curated venue-native sources: conference home pages, official
program/schedule pages, proceedings archives, CFPTime, ConfSearch, and the
`uv run scripts/crawl_conferences.py` crawler. Any search for a topic must be
done by crawling the raw venue pages listed in `references/` and the embedded
tier tables, then reasoning over that content. If a venue page cannot be
crawled, say so — do not fall back to generic web search.

Supported quick forms:
- `/skill:seccon help` → concise help and examples
- `/skill:seccon academic now` → upcoming and ongoing academic security conferences, sorted by date
- `/skill:seccon industry now` → upcoming industry conferences with open CFPs, sorted by conference date
- `/skill:seccon academic now <acronym>` → dates and deadlines for a specific conference (e.g., `/skill:seccon academic now S&P`)
- `/skill:seccon [academic|industry] now <topic>` → accepted content in upcoming conferences prioritized and filtered by <topic> (e.g., `/skill:seccon industry now browser exploitation` will show current/upcoming conferences that have papers/talks on that topic, even if the conference isn't solely focused on it)
- `/skill:seccon [academic|industry] now <acronym> <topic>` → like the previous form but for a specific conference (e.g., `/skill:seccon academic now CCS side channels`)
- `/skill:seccon [academic|industry] deadlines [topic]` → open CFPs only, sorted by deadline, optionally topic-filtered
- `/skill:seccon [academic|industry] latest <acronym> [topic]` → latest edition of a venue, plus topic-focused papers or talks when requested
- `/skill:seccon [academic|industry] latest <topic>` → cross-conference topic scan across the latest editions of all major venues in that mode (all industry or all academic conferences)
- `/skill:seccon academic compare <venue1> <venue2>` → compare rank, selectivity, focus, and typical paper styles
- `/skill:seccon academic <year> <acronym>` → shorthand for venue-year lookup (program URL, papers, metadata, and quick venue context), e.g. `/skill:seccon academic 2024 CCS`

## Help output

If the user runs `/skill:seccon help`, return a concise quick-start guide instead of doing research. Include:
- one-line explanation of academic vs industry mode
- the main quick forms below
- 8–12 concrete examples
- a short note that mode can be inferred when obvious, but explicit mode is preferred

Suggested help examples: `/skill:seccon academic now`, `/skill:seccon academic now CCS side channels`, `/skill:seccon industry now browser exploitation`, `/skill:seccon academic deadlines crypto`, `/skill:seccon academic latest USENIX fuzzing`, `/skill:seccon academic compare CCS NDSS`, `/skill:seccon academic 2024 CCS`, `/skill:seccon academic acceptance rate S&P`.

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
- reorder results to prioritize venues where the title, acronym, CFP text, or known venue focus best matches the topic
- add a short **Topic fit** note per row or as a bullet below the table
- if the topic is too narrow for ConfSearch alone, supplement with a brief web search of the conference CFP page

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
- first resolve whether the first token after `now` is a known acronym from the tier table; if yes, treat remaining tokens as the topic, otherwise treat the whole tail as the topic
- before crawling, do a web search for the specific conference/year accepted-papers or program page; then fetch that exact raw page with `uv run scripts/crawl_conferences.py --crawl-content --url <url>`
- if the searched conference page has no accepted content, fall back to `uv run scripts/crawl_conferences.py --crawl-content --academic --conference <acronym> --year <YYYY>` so the script tries built-in conference pages and proceedings fallbacks
- do all topic filtering and relevance reasoning yourself from the raw page content; the crawler must not pre-filter
- if a specific conference/year page cannot be crawled, stop and say the program/content is not available yet instead of guessing

**Response fields used:** `acronym`, `name`, `location`, `deadline`, `notification`, `start`, `end`, `rank`, `www`

Note: the `rank` field is the CORE rank (A\*, A, B, C) — use it directly; no separate CORE lookup needed.

**Output format:**

| Conference | CORE | Dates | Location | Submission deadline | Website |
|---|---|---|---|---|---|
| CCS 2026 | A\* | Nov 15–19 2026 | The Hague, NL | Jan 14 / Apr 29 2026 | [link](…) |

Add a section for **open CFPs** (deadline in the future) and **upcoming conferences** (start date within 90 days). Note conferences where the CFP has closed but the event hasn't happened yet.

### Industry — `now`

Fetch from CFPTime. The API returns cybersecurity-focused industry conferences sorted by conference start date.

If the user supplies an optional **topic** after `now`, use it to refine the calendar response:
- filter or prioritize conferences whose names, CFP details, or known focus areas align with the topic
- when the CFPTime fields are sparse, supplement with the conference website or CFP page
- add a short **Why it matches** note for the top results

**Upcoming conferences and open CFPs:**
```
GET https://api.cfptime.org/api/upcoming/
```

**New conference announcements (RSS):**
```
GET https://api.cfptime.org/rss
```
Parse the RSS XML to extract `<title>`, `<link>`, `<description>` (contains CFP text), and `<pubDate>`.

**Response fields used:** `name`, `cfp_deadline`, `conf_start_date`, `city`, `country`, `website`, `cfp_details`

**Output format:**

| Conference | Dates | Location | CFP deadline | Website |
|---|---|---|---|---|
| DEF CON 33 | Aug 2026 | Las Vegas, US | TBD | [link](…) |

Show CFP deadline relative to today (e.g., "closes in 14 days", "closed"). Highlight conferences where the CFP is still open. Omit conferences more than 12 months out unless explicitly asked.

### Deadlines shortcut

For `/skill:seccon [academic|industry] deadlines [topic]`:

- treat this as a focused form of `now`
- return only conferences with open CFPs or imminently closing deadlines
- sort by deadline ascending, not conference start date
- if a topic is supplied, prioritize or filter by topic fit using the same topic-handling rules as `now`
- include a relative deadline note such as `closes in 9 days`

### Latest shortcut

For `/skill:seccon [academic|industry] latest <acronym> [topic]`:

- resolve the most recent edition of the venue from `references/academic.md`, `references/industry.md`, conference archives, or the venue home page
- return the latest canonical program/archive URL first
- if a topic is supplied, search within that edition for matching papers or talks and show the best hits
- if the latest edition is upcoming and has no program yet, say so and fall back to the most recent completed edition for content

For `/skill:seccon [academic|industry] latest <topic>` (no acronym):

- no acronym was given — treat all remaining tokens as the topic
- perform a **cross-conference topic scan** across the latest editions of ALL major venues in that mode
  - **industry**: crawl the latest completed edition of every conference in the industry table (DEF CON, Black Hat USA, Black Hat EU, Black Hat Asia, CanSecWest, REcon, Troopers, hardwear.io, OffensiveCon, HITB, etc.) using `uv run scripts/crawl_conferences.py --crawl-content --url <archive-or-schedule-url>`
  - **academic**: crawl the latest completed edition of every Tier 1 and Tier 2 conference from the ranked table using the same crawler
- for each venue that has a program/page available, check for talks or papers matching the topic
- present results as a table or list grouped by venue, showing talk/paper title, venue, year, and URL
- if a specific venue's latest page cannot be crawled, say so for that venue and move on to the next
- do NOT fall back to web search, Semantic Scholar, or paperhub-cli as a primary path

Examples:
- `/skill:seccon academic latest CCS`
- `/skill:seccon academic latest USENIX fuzzing`
- `/skill:seccon industry latest DEF CON browser exploitation`
- `/skill:seccon industry latest agentic vulnerability research` — cross-conference scan across all industry venues
- `/skill:seccon academic latest LLM supply chain attacks` — cross-conference scan across all top academic venues

### Compare shortcut

For `/skill:seccon academic compare <venue1> <venue2>`:

- compare rank/tier, acceptance-rate trends when available, thematic focus, artifact culture, and the kind of papers each venue tends to favor
- use CORE + Guofei for venue standing, and venue-native pages for scope/style when possible
- present the answer as a side-by-side table followed by a short recommendation for when each venue is the better fit

Examples:
- `/skill:seccon academic compare CCS NDSS`
- `/skill:seccon academic compare USENIX S&P`
- `/skill:seccon academic compare PETS SOUPS`

### Academic Year + Acronym shorthand

For `/skill:seccon academic <year> <acronym>`:

1. Normalize the acronym against the ranked conference table and `references/academic.md`
2. Resolve the venue-year URL from `references/academic.md` when available
3. Return a compact answer with:
   - conference full name
   - rank / tier context
   - canonical venue-year URL
   - whether full text is open access or metadata-only
   - 3–10 representative papers, or the accepted-paper/program page if that is more reliable
4. Prefer venue-native sources first (USENIX, NDSS, IACR, conference site), then Semantic Scholar / DBLP, then `paperhub-cli --no-plan` as fallback

Example intents:
- `/skill:seccon academic 2024 CCS` → accepted papers / proceedings / representative papers for CCS 2024
- `/skill:seccon academic 2025 USENIX` → USENIX Security 2025 program and papers
- `/skill:seccon academic 2026 EuroS&P` → upcoming venue page, deadlines if relevant, and available program info

## Examples

Use these as preferred interpretations for terse commands:

- `/skill:seccon help`
- `/skill:seccon academic now`
- `/skill:seccon academic now CCS`
- `/skill:seccon academic now CCS side channels`
- `/skill:seccon industry now browser exploitation`
- `/skill:seccon academic deadlines`
- `/skill:seccon academic deadlines malware`
- `/skill:seccon industry deadlines cloud security`
- `/skill:seccon academic latest S&P`
- `/skill:seccon academic latest USENIX fuzzing`
- `/skill:seccon industry latest DEF CON embedded security`
- `/skill:seccon industry latest agentic vulnerability research`
- `/skill:seccon academic latest LLM supply chain attacks`
- `/skill:seccon academic compare CCS NDSS`
- `/skill:seccon academic compare PETS SOUPS`
- `/skill:seccon academic 2024 CCS`
- `/skill:seccon academic 2025 USENIX`

---

## Academic Mode

### Conference Rankings

**Sources for aggregate rank:**
- CORE 2023: https://portal.core.edu.au/conf-ranks/?search=security&by=all&source=CORE2023&sort=arank
- Guofei Gu security conference statistics (acceptance rates + community standing): https://people.engr.tamu.edu/guofei/sec_conf_stat.htm *("not official, only for reference"; biased toward network/system security)*

**Aggregation rule:**
| Aggregate | Criteria |
|---|---|
| **Top** | CORE A\* *or* Guofei T1 |
| **High** | CORE A *or* Guofei T2 (use Guofei when CORE has no entry) |
| **Mid** | CORE B *or* Guofei T3 |
| **Low** | CORE C |

When reasoning about prestige, cite the individual sources (CORE rank + community standing) rather than the aggregate alone. For year-by-year acceptance rate data, fetch the Guofei page live — that data is unique to that source.

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

To re-check or extend rankings live:
```
GET https://portal.core.edu.au/conf-ranks/?search=<term>&by=all&source=CORE2023&sort=arank&page=1
```

#### Recent Acceptance Rates

| Conference | Approx. Rate | Trend |
|---|---|---|
| IEEE S&P | 12–18% | Getting harder |
| CCS | 18–22% | Stable |
| USENIX Security | 16–19% | Getting harder |
| NDSS | 14–18% | Slightly harder |
| Crypto / Eurocrypt | 25–30% | Stable (scope-filtered) |

### Paper Sources

Read `references/academic.md` for the current list of year-specific program URLs (updated by `scripts/crawl_conferences.py`).

**Open-access — fetch full text:**
- USENIX Security: `https://www.usenix.org/conference/usenixsecurity{YY}/technical-sessions`
- NDSS: `https://www.ndss-symposium.org/{YYYY}-programme/`
- IACR ePrint (Crypto, Eurocrypt, TCC, CHES, PKC, Asiacrypt): `https://eprint.iacr.org/search?query={terms}`
- arXiv cs.CR: `https://arxiv.org/search/?searchtype=all&query={terms}&start=0`
- SOUPS: via USENIX, same URL pattern

**Cross-venue search (metadata + abstracts):**
- Semantic Scholar: `https://api.semanticscholar.org/graph/v1/paper/search?query={terms}&fields=title,abstract,year,venue,authors,citationCount,externalIds&limit=20`
- Filter `venue` against the tier tables above.

**Paywalled — abstract/metadata only:**
- IEEE S&P (IEEEXplore): `https://ieeexplore.ieee.org/xpl/conhome/1000646/all-proceedings`
- CCS (ACM DL): `https://dl.acm.org/conference/ccs`
- ESORICS (Springer LNCS): use Semantic Scholar for metadata

When full text is unavailable, note it and mention that a preprint is often on arXiv or the author's homepage.

### Author Search

1. DBLP: `https://dblp.org/search/?q={name}` — complete publication list grouped by venue
2. Semantic Scholar: `https://api.semanticscholar.org/graph/v1/author/search?query={name}&fields=name,affiliations,papers,citationCount`
3. Filter by tier; report: Tier-1 count and list, Tier-2 count and list, most-cited works, active co-authors, inferred research themes.

### Cross-Conference Topic Scan

For `/skill:seccon academic "<topic>"`, do not start with generic APIs. First use `references/academic.md` to pick relevant recent/top venues and crawl raw venue pages with `uv run scripts/crawl_conferences.py --crawl-content --academic --conference <acronym> --year <YYYY>` or `--url <accepted-papers-or-program-url>`. Reason over those raw pages to identify matching papers. If a specific venue/year page cannot be crawled, say so for that venue/year and continue only with other crawlable venue pages. Use Semantic Scholar, DBLP, arXiv, IACR ePrint, or `paperhub-cli --no-plan` only after this venue-native pass to enrich missing metadata, citations, PDFs, or preprints.

---

## Industry Mode

Read `references/industry.md` for year-specific talk archive URLs (updated by `scripts/crawl_conferences.py`).

### Top Industry Security Conferences

| Conference | Focus | Archive / Schedule |
|---|---|---|
| DEF CON | Broad hacking, underground research | https://media.defcon.org/ |
| Black Hat USA | Advanced research, enterprise security | `https://www.blackhat.com/us-{YY}/briefings/schedule/` |
| Black Hat EU | Same, European edition | `https://www.blackhat.com/eu-{YY}/briefings/schedule/` |
| Black Hat Asia | Same, Asian edition | `https://www.blackhat.com/asia-{YY}/briefings/schedule/` |
| RSA Conference | Enterprise, policy, threat intel | https://www.rsaconference.com/library |
| CanSecWest | Advanced technical, Pwn2Own | https://cansecwest.com/ |
| REcon | Reverse engineering, binary analysis | https://recon.cx/ |
| Troopers | Network security, ICS, Active Directory | https://troopers.de/ |
| hardwear.io | Hardware, embedded, IoT security | https://hardwear.io/ |
| Infiltrate | Offensive research, exploit dev | https://www.infiltratecon.com/ |
| HITCON | Asia-Pacific, CTF community | https://hitcon.org/ |
| OffensiveCon | Offensive research, exploitation | https://www.offensivecon.org/ |
| HITB | Hacking in the Box (KL/Amsterdam) | https://conference.hitb.org/ |
| VB Conference | Malware, threat intelligence | https://www.virusbulletin.com/conference/ |
| POC | Power of Community, Korea | https://powerofcommunity.net/ |

DEF CON media archive uses numbered editions (DEF CON 1 = 1993):
`https://media.defcon.org/DEF%20CON%20{N}/`

### Black Hat Sessions JSON

Black Hat schedule pages are Handlebars.js shells. The actual session data
(title, speakers, description, track, format, files) is loaded from a `sessions.json`
endpoint. Fetch the JSON directly instead of crawling the HTML page:

```
https://blackhat.com/us-{YY}/briefings/schedule/sessions.json
https://blackhat.com/eu-{YY}/briefings/schedule/sessions.json
https://blackhat.com/asia-{YY}/briefings/schedule/sessions.json
```

**JSON structure:** the top-level `sessions` array contains objects with:
- `title`, `description`, `full_description` — talk title and abstract
- `speakers` — array with `person_id`, `role`, first/last name, company
- `track_1`, `track_2` — topic track names
- `format`, `duration` — session format metadata
- `bh_files` — object with `slides`, `whitepaper`, `source_code` URLs
- `public_tags.tag` — array of topic tags (`{name, id}`)
- `time_display`, `room`, `additional_dates` — scheduling info

**Cloudflare protection:** the JSON endpoint is behind Cloudflare and may
return 403. The crawler uses `curl_cffi` with Chrome TLS impersonation
and a 60s timeout. Even a full headless Chromium via Playwright with
stealth tricks (overriding `navigator.webdriver`, `plugins`, `languages`)
and Firefox were tested — all blocked. This is an IP-level block, not a
TLS fingerprint or User-Agent issue. If blocked, note that Black Hat data
is unavailable from the current environment and fall back to the DEF CON
media archive or other accessible venues.

If blocked, note that Black Hat data is unavailable from the current
environment and fall back to the DEF CON media archive or other venues.

### Cross-Conference Topic Scan (Industry)

Search the DEF CON and Black Hat archives by keyword. For Black Hat, fetch the
`sessions.json` endpoint directly (see "Black Hat Sessions JSON" above) and
filter the JSON — the HTML schedule page is a Handlebars.js shell, not the
actual data. Also check:
- Slides on Speaker Deck / SlideShare
- Videos on YouTube (channel: "DEFCONConference", "Black Hat")
- Papers mentioned in talk abstracts → follow to academic venues

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

**Always pass `--no-plan` to `search`.** The `seccon` skill owns planning and reasoning; skipping paperhub's LLM decomposition phase keeps responses fast and deterministic.

### When to use

**Fallback** — when primary sources (USENIX, NDSS, IACR ePrint, Semantic Scholar, DBLP) return no results for a query:
```bash
paperhub-cli search --no-plan "<query>" \
  --sources arxiv,dblp,semantic_scholar,iacr \
  --recent-years 5
```

**Enrichment** — after returning results from primary sources, use paperhub to find related preprints, check citation counts, or confirm a finding:
```bash
paperhub-cli search --no-plan "<paper title or topic>" \
  --sources arxiv,semantic_scholar \
  --top-k 5
```

Author-scoped search:
```bash
paperhub-cli search --no-plan "<topic>" --author "<Name>" \
  --sources dblp,semantic_scholar
```

### Provider selection for security research

| Provider | Strength | Use for |
|---|---|---|
| `arxiv` | Full — reliable, open PDFs | cs.CR preprints, recent work |
| `dblp` | Full metadata | CCS, S&P, USENIX, NDSS, RAID proceedings |
| `semantic_scholar` | Full + OA PDFs | Citation counts, related work |
| `iacr` | Best-effort | Crypto papers (Crypto, Eurocrypt, CHES, TCC) |
| `openalex` | Full — broad | Obscure venues, long-tail coverage |

Default for most security queries: `--sources arxiv,dblp,semantic_scholar,iacr`

### Reading and downloading papers

```bash
# Abstract only
paperhub-cli read --id arxiv:<id>
paperhub-cli read --id doi:<doi>

# Full text (open access only)
paperhub-cli read --id arxiv:<id> --full
paperhub-cli read --id doi:<doi> --full

# Download as Markdown (best for reading in context)
paperhub-cli download --id arxiv:<id> --format md
paperhub-cli download --id doi:<doi> --format txt
```

Paper IDs follow the format `provider:id`, e.g. `arxiv:2405.01234`, `doi:10.1145/3658644`, `openalex:W2741809807`.

---

## URL Maintenance

`references/academic.md` and `references/industry.md` are auto-generated. Refresh them:

```bash
# Refresh all
uv run scripts/crawl_conferences.py

# Academic only, current year
uv run scripts/crawl_conferences.py --academic --start-year 2025 --end-year 2025

# Industry only
uv run scripts/crawl_conferences.py --industry
```
