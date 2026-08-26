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

## Gathering phase

All gathering uses Miniflux MCP tools. Compute Unix timestamps for the
relevant time window using the current date.

**First step for every cadence:** call `get_categories`, then remove any
category whose title matches the blocklist (case-insensitive substring).
All subsequent category scans use only the surviving categories. Starred
entries are never filtered by category (starring overrides the blocklist).

### Daily

1. All starred entries from the last 24 hours (no category filter):
   ```
   get_entries(starred: true, published_after: <24h-ago-unix>)
   ```

2. All unread entries from each non-blocked category (no limit):
   ```
   get_category_entries(category_id: N, status: "unread")
   ```

3. Deduplicate by entry ID.

4. Read content: `get_entry` returns stored content. Use
   `fetch_original_content` only when the stored content is clearly
   truncated or insufficient.

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

6. Synthesize: re-rank merged daily summaries + gap-fill entries. Promote
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

5. Trend analysis across merged weeklies:
   - Domains with increasing frequency
   - Stories that developed across multiple weeks
   - New vendors/products/CVEs appearing for the first time
   - Themes absent from weeklies but present in gap-fill

6. Synthesize: curated distillation, not concatenation. Re-rank, highlight
   the month's most significant developments, produce a "strategic outlook."

If no weekly snapshots exist, fall back to dailies, then to a full sweep.

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

## Prioritization strategy

- Popularity: items/topics/stories that are repeated across multiple feeds
- Security events: big and impactful security incidents or vulnerabilities
- Updates from important venues: topics discussed at or discussing about cybersecurity conferences (industry and academic)
- Updates from major players, including but not limited to merger and aquisitions
- Launches and tools

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
