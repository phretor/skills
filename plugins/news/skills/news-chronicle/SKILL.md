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

Skip these Miniflux categories entirely. Do not scan them for unread
entries, do not include their entries in gap-fill searches, and do not
surface their entries in the chronicle even if starred. Match by
case-insensitive substring (the category title must contain the string).

```
Security | Alerts and Advisories
Science
Tech | News
```

After calling `get_categories`, filter the result against this list
before any further gathering. An entry from a blocked category that
also appears in a non-blocked category (cross-posted) is still
excluded.

## Gate: verify Miniflux is reachable

Before doing anything else, call `mcp__miniflux__healthcheck`.

If it fails or the tool is not available, stop immediately:

> The Miniflux MCP server is not configured or not reachable.
> Add the `miniflux` MCP server to your Claude Code configuration
> before using this skill.

Do not fall back to any other tool or CLI. Miniflux MCP is the only
data source.

## Base path

```
CHRONICLE_BASE=~/Personal/Personal Notes/10 - Projects/lowtides
```

All file paths are relative to `CHRONICLE_BASE`.

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

## Gathering phase

All gathering uses Miniflux MCP tools. Compute Unix timestamps for the
relevant time window using the current date.

**First step for every cadence:** call `get_categories`, then remove any
category whose title matches the blocklist (case-insensitive substring).
All subsequent category scans and entry filtering use only the surviving
categories. Starred entries from blocked categories are also excluded:
after fetching starred entries, call `get_entry` to check the category
and drop any that belong to a blocked category.

### Daily

1. Starred entries from the last 24 hours (excluding blocked categories):
   ```
   get_entries(starred: true, published_after: <24h-ago-unix>, limit: 100)
   ```
   Drop entries whose feed belongs to a blocked category.

2. Scan non-blocked categories for unread entries:
   ```
   get_category_entries(category_id: N, status: "unread", limit: 20)
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
   get_entries(starred: true, published_after: <7d-ago-unix>, limit: 100)
   ```
   Filter out IDs already in child snapshots.

4. Category scan: check high-value categories for unread entries not
   already covered:
   ```
   get_category_entries(category_id: N, status: "unread", limit: 20)
   ```

5. Synthesize: re-rank merged daily summaries + gap-fill entries. Promote
   stories that appeared across multiple days. Add a "week in review"
   executive summary and a watch list.

If no daily snapshots exist, fall back to a full sweep of starred entries
from the last 7 days. Note this in the output.

### Monthly

1. Load weekly snapshots from the current month's directories.

2. Merge weekly summaries.

3. Gap-fill via search for entries missed by weeklies:
   ```
   get_entries(search: "caliptra OR root of trust", published_after: <30d-ago-unix>, limit: 50)
   get_entries(search: "bmc OR redfish OR openbmc", published_after: <30d-ago-unix>, limit: 50)
   get_entries(search: "spdm OR pldm OR attestation", published_after: <30d-ago-unix>, limit: 50)
   get_entries(search: "post-quantum OR cnsa", published_after: <30d-ago-unix>, limit: 50)
   get_entries(search: "firmware vulnerability OR bootkit", published_after: <30d-ago-unix>, limit: 50)
   get_entries(search: "gpu security OR confidential computing", published_after: <30d-ago-unix>, limit: 50)
   ```
   Exclude entries already in weekly snapshots by ID.

4. Trend analysis across merged weeklies:
   - Domains with increasing frequency
   - Stories that developed across multiple weeks
   - New vendors/products/CVEs appearing for the first time
   - Themes absent from weeklies but present in gap-fill

5. Synthesize: curated distillation, not concatenation. Re-rank, highlight
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

Always hyperlink article titles to the original URL. The URL is available
from the entry's `url` field. Every article reference must be a clickable
link.

### Chronicle structure

```markdown
# Platform security chronicle - {date or date range}

## Executive summary
{2-3 sentences: most important developments, any action items}

## {Domain name}
### [{Article title}](url)
{One-line summary}

**Significance:** {Why this matters}

**Source:** {Feed name} - [{Article title}](url)

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

- Daily: aim for under 30 entries read, 10-15 in the final chronicle
- Weekly: up to 60 entries (most from cached daily snapshots), 20-30
  in the chronicle
- Monthly: up to 120 entries (most from cached weekly snapshots), 30-50
  in the chronicle, plus trend analysis

If the starred count exceeds the budget, prioritize by domain relevance
(core domains: rot, bmc, firmware, attestation rank highest).

When composing from snapshots, the token savings are significant: reading
a daily snapshot's markdown is far cheaper than re-reading 15 original
entries. This is the main reason snapshots are mandatory.

You are the language model. There is no summarize or digest command. Read
entry content directly and synthesize it yourself.
