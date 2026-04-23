---
name: con
description: Conference intelligence for security researchers — academic and industry venues. Invoke as `/con [academic|industry] <question>` or `/con [academic|industry] now` for upcoming conferences and live CFP deadlines. Academic mode uses an aggregate ranking derived from CORE 2023 (portal.core.edu.au) and Guofei Gu's security conference statistics (engr.tamu.edu), covering IEEE S&P, CCS, USENIX Security, NDSS, Crypto, Eurocrypt, ESORICS, RAID, ACSAC, PETS, EuroS&P, CHES, TCC, and more; uses confsearch.ethz.ch for live dates. Industry mode covers DEF CON, Black Hat, RSA, CanSecWest, REcon, Troopers, hardwear.io, Infiltrate, HITB, OffensiveCon, and more; uses cfptime.org for live CFP deadlines. Fetches conference programs and papers from open-access sources (USENIX, NDSS, IACR ePrint, arXiv, DEF CON media archive). Searches by author via DBLP and Semantic Scholar. Evaluates specific papers or talks on a standard rubric: TL;DR, tool/artifact release, reproducibility, CVEs, industry impact, academic impact, and known counterpart work. Use whenever the user mentions conference names, asks about paper rankings, acceptance rates, upcoming deadlines, or ongoing conferences; wants to find or evaluate a specific paper or talk; needs an author's publication record; or wants a cross-conference topic survey.
metadata:
  author: phretor
  version: "1.2"
  preferred-model: haiku
compatibility: Requires internet access. Run scripts/crawl_conferences.py annually to refresh year-specific URL lists in references/.
allowed-tools: WebFetch WebSearch Bash
---

# con — Conference Intelligence

Dispatches on the first argument:

- **`academic`** → peer-reviewed venues, TAMU tier rankings, paper search, live calendar via confsearch.ethz.ch
- **`industry`** → practitioner conferences, talk archives, live CFP calendar via cfptime.org

Infer the mode from context when unambiguous (e.g., "DEF CON" → industry, "IEEE S&P" → academic). Ask only when genuinely ambiguous.

The second argument can be **`now`** to trigger a live calendar query instead of a paper/talk search:
- `/con academic now` → upcoming and ongoing academic security conferences, sorted by date
- `/con industry now` → upcoming industry conferences with open CFPs, sorted by conference date
- `/con academic now <acronym>` → dates and deadlines for a specific conference (e.g., `/con academic now S&P`)

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

**For `/con academic now` (all upcoming security conferences):**
```
GET https://confsearch.ethz.ch/api/search-engine/?query=security
```
Also query with: `privacy`, `cryptography`, `network security` to broaden coverage.

Filter results to conferences in the embedded tier tables (Tier 1 and 2). Drop results with blank `start` dates or past end dates. Sort by `start` ascending.

**For `/con academic now <acronym>` (specific conference):**
```
GET https://confsearch.ethz.ch/api/search-engine/?query=<acronym>
```
Pick the top result matching the known acronym. Show all fields.

**Response fields used:** `acronym`, `name`, `location`, `deadline`, `notification`, `start`, `end`, `rank`, `www`

Note: the `rank` field is the CORE rank (A\*, A, B, C) — use it directly; no separate CORE lookup needed.

**Output format:**

| Conference | CORE | Dates | Location | Submission deadline | Website |
|---|---|---|---|---|---|
| CCS 2026 | A\* | Nov 15–19 2026 | The Hague, NL | Jan 14 / Apr 29 2026 | [link](…) |

Add a section for **open CFPs** (deadline in the future) and **upcoming conferences** (start date within 90 days). Note conferences where the CFP has closed but the event hasn't happened yet.

### Industry — `now`

Fetch from CFPTime. The API returns cybersecurity-focused industry conferences sorted by conference start date.

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

1. Semantic Scholar search filtered to security venues, sorted by year (or citation count)
2. IACR ePrint for crypto-adjacent topics
3. arXiv cs.CR for preprints in the last 2 years
4. Group by tier, newest first; one-line contribution per paper

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

### Cross-Conference Topic Scan (Industry)

Search the DEF CON and Black Hat archives by keyword. Also check:
- Slides on Speaker Deck / SlideShare
- Videos on YouTube (channel: "DEFCONConference", "Black Hat")
- Papers mentioned in talk abstracts → follow to academic venues

When a talk has a companion paper (common at Black Hat), cross-reference it via the academic rubric.

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
