---
name: news-chronicle
description: >
  Produce a domain-clustered platform security intelligence chronicle
  (daily, weekly, or monthly) from the user's Miniflux RSS feeds. Use when
  the user asks for a news digest, intelligence brief, chronicle, weekly
  roundup, feed summary, "what happened this week in security", "catch me up",
  "news briefing", "write my chronicle", "daily brief", "monthly recap",
  "security news summary", or "what did I miss". Also triggers on requests
  to synthesize RSS feed content into a structured report.
allowed-tools: >
  mcp__miniflux__healthcheck
  mcp__miniflux__get_categories
  mcp__miniflux__get_feeds
  mcp__miniflux__fetch_counters
  mcp__miniflux__get_entries
  mcp__miniflux__get_entry
  mcp__miniflux__get_feed
  mcp__miniflux__get_feed_entries
  mcp__miniflux__get_category_entries
  mcp__miniflux__get_category_feeds
  mcp__miniflux__fetch_original_content
  mcp__miniflux__update_entry_status
  mcp__miniflux__toggle_starred
  Read
  Write
  Edit
  Bash(mkdir:*)
  Bash(date:*)
  WebFetch
  AskUserQuestion
---

# Chronicle: platform security intelligence digest

## Category blocklist

Skip these Miniflux categories during unread scans and gap-fill
searches. Match by case-insensitive substring (the category title must
contain the string).

```
Security | Alerts and Advisories
Science
Tech | News
```

After calling `get_categories`, remove matching categories from the
scan list. Do not fetch unread entries from blocked categories, and
exclude blocked-category entries from gap-fill search results.

**Exception: starred entries always appear.** If the user explicitly
starred an entry in a blocked category, include it in the chronicle.
Starring is a deliberate signal that overrides the category filter.

## Gate: verify Miniflux is reachable

Before doing anything else, call `mcp__miniflux__healthcheck`.

If it fails or the tool is not available, stop immediately:

> The Miniflux MCP server is not configured or not reachable.
> Add the `miniflux` MCP server to your Claude Code configuration
> before using this skill.

Do not fall back to any other tool or CLI. Miniflux MCP is the only
data source.

## Base path

Resolve `CHRONICLE_BASE` by checking these paths in order. Use the
first one that exists:

1. `~/Personal/Personal Notes/10 - Projects/lowtides`
2. The first directory matching `lowtides` under `~/Notes`
   (use `find ~/Notes -type d -name lowtides -maxdepth 3` and take
   the first result)

If neither exists, ask the user for a path before proceeding.

All file paths below are relative to `CHRONICLE_BASE`.

---

Synthesize the user's Miniflux RSS feeds into a structured,
domain-clustered intelligence chronicle. The user is a firmware security
tech lead at a hyperscale cloud provider; the chronicle serves as both
personal knowledge capture and a shareable team briefing.

## Cadence

Accept one of three cadences (default: daily):

| Cadence | Time window | Depth |
|---------|------------|-------|
| `daily` | Last 24 hours | Starred entries + high-value category scan |
| `weekly` | Last 7 days | Compose from daily snapshots + new starred entries |
| `monthly` | Last 30 days | Compose from weekly snapshots + trend analysis + gap-fill |

If the user doesn't specify, infer from context ("what happened this week" =
weekly; bare "chronicle" = daily). Ask only if genuinely ambiguous.

## Weekly cadence nudges

When running a **daily** chronicle, check the current day of week
after resolving the base path and before gathering.

### Friday prompt

If today is Friday, after completing the daily chronicle and
post-chronicle triage, propose a weekly run:

> It's Friday. Want me to generate the weekly chronicle now? This
> will compose from this week's daily snapshots plus gap-fill.

Use `AskUserQuestion` with options:
1. **Yes, run weekly now (Recommended)**
2. **Skip for now**

If the user accepts, immediately run the weekly cadence for the
current ISO week.

### Missing weekly detection (Sat/Sun/Mon)

If today is Saturday, Sunday, or Monday, before starting the daily
gathering phase, check whether a weekly chronicle exists for the most
recent Friday's ISO week. The expected path is:

```
CHRONICLE_BASE/YYYY/MM/YYYY-WNN-weekly.md
```

where `WNN` is the ISO week number containing the most recent Friday
(zero-padded, e.g. `W05`).

If the file is missing, surface a callout before proceeding with the
daily:

> No weekly chronicle found for last week (W{NN}). Want me to
> generate it before today's daily? The daily snapshots from that
> week are available.

Use `AskUserQuestion` with options:
1. **Yes, generate last week's weekly first (Recommended)**
2. **Skip, just do today's daily**

If the user accepts, run the weekly cadence for that ISO week first,
then continue with the daily.

## Snapshot architecture

Chronicles cascade: higher cadences reuse lower-cadence snapshots as their
primary input, then layer on new material the lower cadence missed.

```
daily snapshots ──┐
                  ├──▶ weekly snapshot ──┐
daily snapshots ──┘                     │
                                        ├──▶ monthly snapshot
weekly snapshots ───────────────────────┘
  + gap-fill searches
  + trend analysis
```

### Save location

After generating the chronicle, ask the user where to save it. Present the
default path and let them override. Use `AskUserQuestion` with these options:

| Cadence | Default path | Pattern |
|---------|-------------|---------|
| `daily` | `CHRONICLE_BASE/YYYY/MM/DD/YYYY-MM-DD-daily.md` | Year/month/day tree |
| `weekly` | `CHRONICLE_BASE/YYYY/MM/YYYY-WNN-weekly.md` | ISO week number |
| `monthly` | `CHRONICLE_BASE/YYYY/MM/YYYY-MM-monthly.md` | Month-level roll-up |

Options to present (single-select):
1. **lowtides project (Recommended)** - the default path above
2. **Daily note** - append under a `## Chronicle` heading in `~/Personal/Personal Notes/30 - Daily/YYYY/YYYY-MM/YYYY-MM-DD.md` (daily only)
3. **Conversation only** - print the chronicle but don't save to disk

If the user picks "Other", accept an arbitrary path. Create intermediate
directories as needed.

### Snapshot storage

All snapshots live under `CHRONICLE_BASE`:

```
CHRONICLE_BASE/
  YYYY/
    MM/
      DD/
        YYYY-MM-DD-daily.md
      YYYY-WNN-weekly.md
      YYYY-MM-monthly.md
```

Frontmatter tracks lineage so higher cadences know what's already covered:

```yaml
---
type: chronicle
cadence: daily
date: "YYYY-MM-DD"
date_range: ["YYYY-MM-DD", "YYYY-MM-DD"]
domains: [rot, bmc, firmware]
entries_scanned: 42
entries_included: 12
entry_ids: [1234, 5678, 9012]
conferences_scanned: [blackhat-usa-2026, defcon-2025]
sources: []
---
```

The `entry_ids` field is the dedup key. When composing a higher-cadence
chronicle, entries already present in child snapshots are not re-read or
re-summarized; their summaries are carried forward.

Every chronicle invocation writes a snapshot. This is not optional; the
cascading model depends on snapshots existing.

## Domain taxonomy

Cluster articles into these domains. An article can appear in multiple.

| Domain | Keywords / signals |
|--------|-------------------|
| `rot` | Caliptra, DICE, root of trust, Boot Guard, TPM, Cerberus, silicon security |
| `bmc` | BMC, IPMI, Redfish, OpenBMC, baseboard management, DC-SCM, ASPEED, Nuvoton |
| `firmware` | UEFI, Secure Boot, firmware, BIOS, SMM, SPI flash, coreboot, bootkit |
| `attestation` | SPDM, PLDM, attestation, measured boot, MCTP, RATS, remote attestation |
| `pqc` | Post-quantum, CNSA, ML-KEM, ML-DSA, SLH-DSA, FIPS 203/204/205, Kyber, Dilithium |
| `supply-chain` | Supply chain, SBOM, code signing, binary transparency, firmware update |
| `gpu-ai-infra` | GPU security, confidential computing, TDX, SEV-SNP, NVLink, AI security |
| `server-arch` | DMA, IOMMU, PCIe, Thunderbolt, side channel, Rowhammer, CXL, NVSwitch |
| `ocp` | OCP SAFE, OCP SBI, streaming boot, Open Compute, DC-SCM |
| `fleet-ops` | Provisioning, fleet integrity, hardening, incident response, monitoring |
| `reversing` | Firmware reversing, binary analysis, RE tooling, Ghidra, IDA |
| `vulns` | CVE, advisory, exploit, vulnerability, zero-day, patch, disclosure |

Articles that don't match any domain go into `other` only if starred.

The `conference-material` pseudo-domain groups slides, papers, and
videos discovered by the conference material scan. Items here are
classified into their primary domain(s) from the taxonomy above but
rendered under a separate `## Conference material` heading so the
user sees what came from conference pages vs. RSS feeds.

## Platform ranking preference

When two articles compete for inclusion (space constraints, marginal
relevance, or tie-breaking within a domain), favor linux/server-side
content over windows/desktop content. This applies to:

- **Vulnerabilities:** a Linux kernel or server-firmware CVE ranks above
  a Windows desktop or browser CVE of similar severity.
- **Incidents/breaches:** server-side or infrastructure compromises rank
  above endpoint/desktop-focused incidents.
- **Tooling/research:** server hardening, fleet integrity, or
  datacenter-relevant research ranks above desktop AV or endpoint
  detection content.

This is an inclusion tiebreaker, not a filter. Windows/desktop articles
still appear when they are clearly significant (e.g. a supply-chain
attack affecting server builds, or a CVE in a component also used
server-side). The preference only kicks in when cutting marginal entries.

## Vendor patch rollup deprioritization

Recurring vendor patch rollup articles (Microsoft Patch Tuesday,
Adobe/Oracle/SAP quarterly updates, Chrome/Firefox stable releases)
are high-volume, low-signal for this chronicle's audience. Apply these
rules:

1. **Do not include** a patch rollup unless it contains at least one
   actively-exploited zero-day affecting a server-side, kernel, or
   infrastructure component (not just a desktop/browser/Office vuln).
2. When a qualifying zero-day exists, include **only the zero-day
   itself** as a short entry under `vulns`. Do not restate the full
   rollup statistics (CVE count, critical count, etc.) -- those belong
   in a vulnerability management dashboard, not an intelligence brief.
3. Patch rollups never appear in the executive summary unless the
   zero-day is firmware, kernel, or hypervisor level.
4. If a rollup entry is starred, include it (starring overrides), but
   keep the summary focused on the exploited or server-relevant subset.

## Publication date verification

Some feeds re-publish old content with a fresh `published_at`
timestamp (aggregator re-syndication, editorial re-promotion, feed
rebuilds). Before including any entry, verify its actual age:

1. **Compare `published_at` against `created_at`.** If the entry's
   `created_at` (when Miniflux first saw it) is within the time window
   but `published_at` is much older (>7 days before the window), the
   article is old content. Exclude it from the daily unless starred.
2. **Check for date signals in the title or content.** Titles
   containing explicit dates, year references, or version numbers from
   prior years (e.g., "2024 Threat Report" appearing in a 2026 feed)
   are likely re-publications. Flag and exclude.
3. **Check for future `published_at`.** Some academic feeds and
   preprint servers set `published_at` to conference dates months in
   the future. Treat these entries as available now but display their
   actual publication date, not the feed timestamp.
4. **When in doubt, check the article URL** with `fetch_original_content`
   and look for a byline date or "originally published" notice.

An entry that fails date verification is silently dropped (not flagged
to the user) unless it was starred.

## Mandatory signal: CISA KEV and ENISA EUVD

Every chronicle run must check for new additions to the CISA Known
Exploited Vulnerabilities (KEV) catalog and the ENISA EU Vulnerability
Database (EUVD) exploited list. These are authoritative signals that a
vulnerability is confirmed actively exploited, and they always appear
in the chronicle when new entries fall within the time window.

### CISA KEV

Fetch the full KEV catalog JSON:

```
WebFetch(url: "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
         prompt: "Return ONLY the vulnerabilities where dateAdded is within
                  the last {N} days (use today's date: {YYYY-MM-DD}).
                  For each, return: cveID, vendorProject, product,
                  vulnerabilityName, shortDescription, dateAdded,
                  dueDate, knownRansomwareCampaignUse, notes.
                  If none match, say NONE.")
```

Replace `{N}` with 1 for daily, 7 for weekly, 30 for monthly.

### ENISA EUVD

Fetch the ENISA EUVD exploited-vulnerabilities listing:

```
WebFetch(url: "https://euvd.enisa.europa.eu/homepage/exploited",
         prompt: "List all vulnerabilities shown on this page. For each,
                  return: CVE ID, description, vendor/product, CVSS score,
                  date published or date added. Only include entries from
                  the last {N} days (use today's date: {YYYY-MM-DD}).
                  If none match or the page is empty, say NONE.")
```

### Inclusion rules

1. **Always include.** KEV/EUVD additions are never deprioritized or
   dropped by platform-ranking, patch-rollup, or space constraints.
   They are the highest-confidence signal that a vulnerability is
   under active exploitation.
2. **Cross-reference with RSS entries.** If a KEV/EUVD CVE also
   appears in an RSS entry already gathered from Miniflux, merge: use
   the RSS article's richer content for the summary but add a
   `**KEV/EUVD:**` tag to mark it as confirmed-exploited.
3. **Standalone entry when no RSS match.** If a KEV/EUVD CVE has no
   corresponding RSS entry, create a standalone chronicle entry under
   `vulns` using the catalog metadata (description, vendor, product,
   due date).
4. **Domain classification.** Apply the domain taxonomy as usual. A
   KEV entry for a firmware, kernel, BMC, or server-infrastructure
   component also appears in the relevant domain section, not just
   `vulns`.
5. **Executive summary.** Any KEV/EUVD addition affecting server-side,
   kernel, firmware, or hypervisor components must be mentioned in the
   executive summary.

### Chronicle rendering

KEV/EUVD entries use this format:

```markdown
### [CVE-YYYY-NNNNN](https://nvd.nist.gov/vuln/detail/CVE-YYYY-NNNNN) (YYYY-MM-DD) [KEV]
{vendorProject} {product}: {shortDescription}

**Added to KEV:** {dateAdded} | **Remediation due:** {dueDate}
**Ransomware use:** {Yes/No/Unknown}

**Significance:** {Why this matters for the fleet}

> **LinkedIn:** {opinion}
>
> **Twitter/X:** {opinion}
```

For EUVD-only entries (not in KEV), use `[EUVD]` instead of `[KEV]`.
For entries in both, use `[KEV] [EUVD]`.

### Frontmatter

Add KEV/EUVD CVE IDs to the snapshot frontmatter for dedup across
cadences:

```yaml
kev_cves: [CVE-2026-XXXXX]
euvd_cves: [CVE-2026-YYYYY]
```

## Gathering phase

All gathering uses Miniflux MCP tools. Compute Unix timestamps for the
relevant time window using the current date.

**First step for every cadence:** call `get_categories`, then remove any
category whose title matches the blocklist (case-insensitive substring).
All subsequent category scans use only the surviving categories. Starred
entries are never filtered by category (starring overrides the blocklist).

### Daily

1. All starred entries (no category filter, no time filter, newest first):
   ```
   get_entries(starred: true, order: "published_at", direction: "desc")
   ```
   Partition results by age:
   - **Recent** (published within the last 24 hours): daily inclusion
     candidates, subject to the starred-entry inclusion rules below.
   - **Older**: carried forward for weekly/monthly compositing but not
     included in today's daily unless explicitly requested.

2. All unread entries from each non-blocked category (no limit):
   ```
   get_category_entries(category_id: N, status: "unread")
   ```

3. Deduplicate by entry ID.

4. **Publication date verification.** For every candidate entry, apply
   the date-verification rules above. Drop entries whose actual age
   falls outside the time window. In particular, watch for CVE feed
   aggregators and news re-syndicators that re-publish daily.

5. Read content: `get_entry` returns stored content. Use
   `fetch_original_content` only when the stored content is clearly
   truncated or insufficient.

6. **CISA KEV / ENISA EUVD check.** Fetch the KEV catalog and EUVD
   exploited list as described in the "Mandatory signal" section.
   Cross-reference new additions against already-gathered RSS entries.
   Create standalone entries for any KEV/EUVD CVEs not covered by
   feeds.

7. **Conference material scan.** Check recent conference web pages for
   newly published material (slides, papers, videos, proceedings) that
   may not appear in any RSS feed. See the "Conference material scan"
   section below for the full procedure.

### Weekly

1. Load child snapshots: find all daily chronicle files in the current
   week's directories under `CHRONICLE_BASE`. Read each, extract
   frontmatter (`entry_ids`, `domains`, summaries).

2. Merge daily summaries into a unified view grouped by domain.

3. Gap-fill: find newly starred entries not covered by any daily snapshot:
   ```
   get_entries(starred: true, published_after: <7d-ago-unix>)
   ```
   Filter out IDs already in child snapshots.

4. Adaptive gap-fill: read the watch list from each child daily snapshot.
   For each watch-list term not already covered by the domain taxonomy
   keywords, run an additional search:
   ```
   get_entries(search: "<watch-list-term>", published_after: <7d-ago-unix>)
   ```
   Exclude entries already gathered.

5. Category scan: check non-blocked categories for unread entries not
   already covered:
   ```
   get_category_entries(category_id: N, status: "unread")
   ```

6. **KEV/EUVD gap-fill.** Fetch the CISA KEV and ENISA EUVD exploited
   lists as described in the "Mandatory signal" section, using the 7-day
   window. Cross-reference against `kev_cves` and `euvd_cves` from each
   child daily snapshot's frontmatter. Include any CVEs added during the
   week that were missed by dailies (no daily ran that day, or the CVE
   was added after the daily ran).

7. Synthesize: re-rank merged daily summaries + gap-fill entries. Promote
   stories that appeared across multiple days. Add a "week in review"
   executive summary and a watch list.

If no daily snapshots exist, fall back to a full sweep of starred entries
from the last 7 days. Note this in the output.

### Monthly

1. Load weekly snapshots from the current month's directories.

2. Merge weekly summaries.

3. Gap-fill via search for entries missed by weeklies:
   ```
   get_entries(search: "caliptra OR root of trust", published_after: <30d-ago-unix>)
   get_entries(search: "bmc OR redfish OR openbmc", published_after: <30d-ago-unix>)
   get_entries(search: "spdm OR pldm OR attestation", published_after: <30d-ago-unix>)
   get_entries(search: "post-quantum OR cnsa", published_after: <30d-ago-unix>)
   get_entries(search: "firmware vulnerability OR bootkit", published_after: <30d-ago-unix>)
   get_entries(search: "gpu security OR confidential computing", published_after: <30d-ago-unix>)
   ```
   Exclude entries already in weekly snapshots by ID.

4. Adaptive gap-fill: read the watch list from each child weekly snapshot.
   For each watch-list term not already covered by the domain taxonomy
   keywords above, run an additional search:
   ```
   get_entries(search: "<watch-list-term>", published_after: <30d-ago-unix>)
   ```
   Exclude entries already gathered.

5. **KEV/EUVD gap-fill.** Fetch the CISA KEV and ENISA EUVD exploited
   lists as described in the "Mandatory signal" section, using the 30-day
   window. Cross-reference against `kev_cves` and `euvd_cves` from each
   child weekly snapshot's frontmatter. Include any CVEs added during the
   month that were missed by weeklies.

6. Trend analysis across merged weeklies:
   - Domains with increasing frequency
   - Stories that developed across multiple weeks
   - New vendors/products/CVEs appearing for the first time
   - Themes absent from weeklies but present in gap-fill

7. Synthesize: curated distillation, not concatenation. Re-rank, highlight
   the month's most significant developments, produce a "strategic outlook."

If no weekly snapshots exist, fall back to dailies, then to a full sweep.

## Conference material scan

Conference pages publish slides, papers, and videos outside RSS feeds.
Every chronicle run checks a curated set of conference web pages for
recently added material relevant to the domain taxonomy.

### Source: seccon skill resources

The conference URL list comes from the seccon skill's cached index files
at `~/dev/personal/skills/plugins/seccon/skills/seccon/resources/`.

At the start of each chronicle run (after the Miniflux gathering phase),
determine which conferences had their most recent edition within the
last 6 months. Read the `conference.url` field from each matching
`index.json`:

```
~/dev/personal/skills/plugins/seccon/skills/seccon/resources/industry/{year}/{venue}/index.json
~/dev/personal/skills/plugins/seccon/skills/seccon/resources/academic/{year}/{venue}/index.json
```

Pick the most recent cached edition of each venue. If the conference
URL is non-null and the conference took place within the last 6 months
(or is upcoming within the next 2 months), add it to the scan list.

### Scan procedure

For each conference URL on the scan list:

1. Fetch the page with `WebFetch`. Use the URL from the index.json
   `conference.url` field.
2. Scan the page content for links to new material: PDFs, slide decks,
   video recordings, or proceedings pages that were not present in the
   seccon cache's `index.json` for that venue-year (compare by title
   or URL).
3. Filter for domain relevance: only surface material matching the
   domain taxonomy keywords (firmware, BMC, root of trust, side
   channel, GPU, attestation, etc.).
4. For each new relevant item found, include it in the chronicle under
   a `## Conference material` domain section with:
   - Conference name and year
   - Talk/paper title (linked to slides/PDF/video)
   - One-line summary of relevance
   - Domain classification

### Cadence-specific behavior

- **Daily:** scan all conferences on the scan list. This catches
  slides published days after a conference ends.
- **Weekly:** only scan conferences not already covered by a daily
  snapshot's conference-material section.
- **Monthly:** skip (weekly snapshots carry conference material
  forward).

### Failure handling

If `WebFetch` fails for a conference URL (timeout, 403, redirect
loop), skip silently. Conference page checks are best-effort and must
not block the chronicle.

## Starred entry inclusion

Starred entries signal deliberate user interest and are always fetched
without a time filter so none are lost between runs. For daily
chronicles, recent starred entries (published within the last 24 hours)
default to inclusion but can be displaced:

1. **Include** when the entry fits a domain in the taxonomy and no
   higher-significance unstarred entry competes for the same slot.
2. **Exclude** when the entry has no domain fit, or a clearly more
   impactful unstarred entry covers the same domain. Significance is
   judged by active exploitation, fleet-wide risk, upstream breakage,
   or regulatory impact.
3. **Tie-break via interview.** When a recent starred entry and an
   unstarred entry are roughly equal in significance within the same
   domain, present both to the user via `AskUserQuestion` and let
   them decide which to include (or both).

Starred entries older than 24 hours are not included in daily
chronicles unless the user explicitly requests them. They remain in
the pool for weekly and monthly compositing.

In candidate lists, label starred entries with `[starred]` so the
user can spot them at a glance. Rank them by the same
domain-relevance criteria as unstarred entries, not auto-promoted
to the top.

## Synthesis phase

### Classification

Assign each entry to one or more domains from the taxonomy. "ASPEED AST2700
Caliptra integration" belongs in both `rot` and `bmc`.

### Per-article summary

For each entry:
- **One-line summary** of the finding/news (what happened)
- **Significance** for the user's work (why it matters to a firmware security
  team at a hyperscale cloud provider)
- **Source** with hyperlink (feed name + linked article title)
- **Proposed opinion** for social sharing (see "Social opinion" below)

Always hyperlink article titles to the original URL. The URL is available
from the entry's `url` field. Every article reference must be a clickable
link.

Always append the original publication date to article titles in the
chronicle output, formatted as `(YYYY-MM-DD)`. Use the entry's
`published_at` field. Example:
`### [Article title](url) (2026-08-25)`

### Social opinion

For every article included in the chronicle, draft a proposed opinion
written in the user's voice: a firmware security tech lead at a
hyperscaler, opinionated, connecting the news to real infrastructure
problems. Two variants:

- **LinkedIn:** 2-4 sentences. Can be slightly more formal and provide
  more context, since the audience may not be deep in the niche.
- **Twitter/X:** 1-2 sentences max (~250 chars target). Punchier,
  skip preamble, get to the take.

The opinion is a *take*, not a summary. It should express a position:
what this means for fleet operators, what vendors should be doing, what
the industry is getting wrong, what's underappreciated. Avoid neutral
restatements of the article.

Place the opinion block directly after the Source line for each article:

```markdown
> **LinkedIn:** {opinion}
>
> **Twitter/X:** {opinion}
```

### Chronicle structure

```markdown
# Platform security chronicle - {date or date range}

## Executive summary
{2-3 sentences: most important developments, any action items}

## {Domain name}
### [{Article title}](url) (YYYY-MM-DD)
{One-line summary}

**Significance:** {Why this matters}

**Source:** {Feed name} - [{Article title}](url)

> **LinkedIn:** {proposed opinion}
>
> **Twitter/X:** {proposed opinion}

{Repeat for each article in this domain}

## Conference material
### [{Talk/paper title}](slides-or-video-url) — {Conference Name YYYY}
{One-line summary}

**Domains:** {domain1, domain2}

{Repeat for each new item found. Omit this section if the scan found nothing new.}

## Watch list
{3-5 emerging themes, trends, or developing stories worth tracking}

## Statistics
- Entries scanned: {N}
- Entries included: {M}
- Domains covered: {list}
- Time window: {start} to {end}
- Child snapshots used: {count} ({cadence} snapshots)
- Gap-fill entries: {count}
```

Omit empty domain sections. Order domains by article count (most active
first).

For **weekly** chronicles, add after the watch list:

```markdown
## Week in review
{2-3 paragraph narrative connecting the week's developments. Which
domains were most active? What shifted?}
```

For **monthly** chronicles, replace "Week in review" with:

```markdown
## Strategic outlook
{Assessment of where each active domain is heading. Connect the month's
developments to team priorities. Flag anything that should become a
project, a ticket, or a conversation.}
```

## Post-chronicle triage

After generating the chronicle, offer to mark processed starred entries
as read:

```
update_entry_status(entry_id: N, status: "read")
```

Only do this with user confirmation.

## Token budget

Fetch all matching entries at every cadence (no artificial limits on
pulls). The chronicle itself is selective: not every fetched entry makes
the final output. Prioritize by domain relevance when deciding what to
include (core domains: rot, bmc, firmware, attestation rank highest).

When composing from snapshots, the token savings are significant: reading
a daily snapshot's markdown is far cheaper than re-reading original
entries. This is the main reason snapshots are mandatory.

You are the language model. There is no summarize or digest command. Read
entry content directly and synthesize it yourself.
