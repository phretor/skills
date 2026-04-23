# con

Conference intelligence for security researchers — academic and industry venues.

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
| `/con academic <question>` | Paper search, author lookup, tier rankings, acceptance rates |
| `/con industry <question>` | Talk search, DEF CON/Black Hat archives, practitioner venues |
| `/con [academic\|industry] now` | Live calendar — upcoming conferences and open CFPs |
| `/con [academic\|industry] now <acronym>` | Dates and deadlines for one specific conference |

Rankings derived from CORE 2023 and Guofei Gu's security conference statistics.
Live data: [confsearch.ethz.ch](https://confsearch.ethz.ch) (academic) · [cfptime.org](https://www.cfptime.org) (industry).

## Installation

```
/plugin install phretor/skills/plugins/con
```
