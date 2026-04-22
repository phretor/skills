---
name: con
description: Conference intelligence for security researchers — academic and industry venues. Invoke as `/con [academic|industry] <question>`. Academic mode covers all TAMU-ranked tiers (IEEE S&P, CCS, USENIX Security, NDSS, Crypto, Eurocrypt, ESORICS, RAID, ACSAC, PETS, EuroS&P, CHES, TCC, and more); industry mode covers DEF CON, Black Hat, RSA, CanSecWest, REcon, Troopers, hardwear.io, Infiltrate, HITB, OffensiveCon, and more. Fetches live conference programs and papers from open-access sources (USENIX, NDSS, IACR ePrint, arXiv, DEF CON media archive). Searches by author via DBLP and Semantic Scholar. Evaluates specific papers or talks on a standard rubric: TL;DR, tool/artifact release, reproducibility, CVEs, industry impact, academic impact, and known counterpart work. Use whenever the user mentions conference names, asks about paper rankings or acceptance rates, wants to find or evaluate a specific paper or talk, needs an author's publication record, or wants a cross-conference topic survey.
metadata:
  author: phretor
  version: "1.0"
  preferred-model: haiku
compatibility: Requires internet access. Run scripts/crawl_conferences.py annually to refresh year-specific URL lists in references/.
allowed-tools: WebFetch WebSearch Bash
---

# con — Conference Intelligence

Dispatches on the first argument:

- **`academic`** → peer-reviewed venues, TAMU tier rankings, paper search
- **`industry`** → practitioner conferences, talk archives, DEF CON/Black Hat/REcon etc.

Infer the mode from context when unambiguous (e.g., "DEF CON" → industry, "IEEE S&P" → academic). Ask only when genuinely ambiguous.

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

## Academic Mode

### Conference Tier Rankings

Source: Guofei Gu, TAMU — https://people.engr.tamu.edu/guofei/sec_conf_stat.htm
*"Not official, only for reference." Biased toward network/system security. Crypto evaluated separately.*

For year-by-year acceptance rate tables, fetch the TAMU page live.

#### Tier 1

| Abbrev | Full Name | Org | Focus |
|---|---|---|---|
| IEEE S&P | IEEE Symposium on Security and Privacy ("Oakland") | IEEE | Systems & applied |
| CCS | ACM Conference on Computer and Communications Security | ACM | Broad |
| USENIX Security | USENIX Security Symposium | USENIX | Systems & applied |
| NDSS | Network and Distributed System Security Symposium | ISOC | Network & systems |
| Crypto | International Cryptology Conference | IACR | Cryptography |
| Eurocrypt | European Cryptology Conference | IACR | Cryptography |

#### Tier 2

| Abbrev | Full Name | Focus |
|---|---|---|
| ESORICS | European Symposium on Research in Computer Security | Broad |
| RAID | Recent Advances in Intrusion Detection | Intrusion detection, attacks |
| ACSAC | Annual Computer Security Applications Conference | Applied |
| DSN | Dependable Systems and Networks | Dependability |
| IMC | Internet Measurement Conference | Network measurement |
| ASIACCS | ACM Symposium on Info, Computer & Comms Security | Asia-Pacific |
| PETS | Privacy Enhancing Technologies Symposium | Privacy |
| EuroS&P | IEEE European Symposium on Security and Privacy | Broad |
| CSF | IEEE Computer Security Foundations Symposium | Formal methods |
| SOUPS | Symposium On Usable Privacy and Security | Usable security |
| Asiacrypt | Int'l Conference on Theory and Application of Cryptology | Cryptography |
| TCC | Theory of Cryptography Conference | Crypto theory |
| CHES | Cryptographic Hardware and Embedded Systems | Hardware crypto |
| FC | Financial Cryptography and Data Security | Financial crypto |

#### Tier 3 (selected)

SecureComm, CNS, DIMVA, ACNS, ACISP, ICICS, ISC, ICISC, SACMAT, IFIP SEC, WiSec, PST.

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
