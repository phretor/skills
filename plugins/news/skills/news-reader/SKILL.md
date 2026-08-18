---
name: news-reader
description: >
  Read, search, triage, and manage RSS feeds via the Miniflux MCP server.
  Use when the user wants to catch up on feeds, find or summarize articles,
  check what's unread, star/save articles, subscribe to a new feed, mark
  articles read, or manage feed categories. Triggers on: "what's in my feeds",
  "any unread RSS", "summarize this feed", "search my subscriptions for X",
  "check what's unread", "mark these read", "subscribe to <url>",
  "refresh my feeds", "news feeds", "RSS", "catch up on feeds",
  "unread articles", "star this article", "triage my feeds".
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
  mcp__miniflux__discover
  mcp__miniflux__create_feed
  mcp__miniflux__delete_feed
  mcp__miniflux__refresh_feed
  mcp__miniflux__refresh_all_feeds
  mcp__miniflux__refresh_category
  mcp__miniflux__create_category
  mcp__miniflux__update_category
  mcp__miniflux__delete_category
  mcp__miniflux__mark_feed_as_read
  mcp__miniflux__mark_category_as_read
  mcp__miniflux__save_entry
  mcp__miniflux__export
---

# News reader

Agent-facing reference for interacting with RSS feeds through the Miniflux
MCP server. Every operation below uses `mcp__miniflux__*` tools directly;
there is no CLI wrapper.

## Gate: verify Miniflux is reachable

Before doing anything else, call `mcp__miniflux__healthcheck`.

If it fails or the tool is not available, stop immediately:

> The Miniflux MCP server is not configured or not reachable.
> Add the `miniflux` MCP server to your Claude Code configuration
> before using this skill.

Do not fall back to any other tool or CLI. Miniflux MCP is the only
data source.

## Orientation

Start every feed session with orientation so the user (and you) know
the current state before diving in.

```
fetch_counters          → per-feed unread/read counts
get_categories          → category list with IDs
get_feeds               → all subscriptions (title, site_url, category)
```

Report a one-line summary: total feeds, total unread, categories with
their unread counts. This replaces a "home screen."

## Reading articles

### Listing entries

Use `get_entries` with filters. Always set `limit` (default 20, max 100)
to control token cost. The response includes a `total` field; report it
so the user knows how many entries match without paginating.

Common filter combinations:

| Intent | Parameters |
|--------|-----------|
| All unread | `status: "unread", limit: 20` |
| Unread in a category | `category_id: N, status: "unread", limit: 20` |
| Unread in a feed | `feed_id: N, status: "unread", limit: 20` |
| Starred | `starred: true, limit: 20` |
| Recent (any status) | `order: "published_at", direction: "desc", limit: 20` |
| Date range | `published_after: <unix>, published_before: <unix>` |

For per-feed or per-category listings, `get_feed_entries` and
`get_category_entries` also work and accept `status` and `limit`.

### Reading full content

`get_entry` returns the entry with its stored content. If the content
looks truncated or is just a summary, call `fetch_original_content` to
scrape the full article from the source URL.

Use `fetch_original_content` sparingly; it hits the origin server and
can be slow or blocked.

### Searching

`get_entries` accepts a `search` parameter for full-text search across
titles and content. Combine with other filters:

```
get_entries(search: "caliptra", status: "unread", limit: 20)
```

## Triage

### Marking read/unread

```
update_entry_status(entry_id: N, status: "read")
update_entry_status(entry_id: N, status: "unread")
```

Bulk: call `update_entry_status` for each entry ID. For an entire feed
or category, use `mark_feed_as_read` or `mark_category_as_read`.

### Starring

```
toggle_starred(entry_id: N)
```

This is a toggle; there is no "set starred = true" variant. If you need
to know current state, check the entry's `starred` field from
`get_entry` first.

### Saving

```
save_entry(entry_id: N)
```

Sends the entry to configured third-party services (Wallabag, Linkding,
etc.), if any are set up in Miniflux.

### Removing

```
update_entry_status(entry_id: N, status: "removed")
```

Removed entries no longer appear in feeds but are not permanently
deleted.

## Subscriptions

### Subscribing

1. `discover(url: "https://example.com")` to find available feeds at a URL.
2. Pick the right feed from the results.
3. `create_feed(feed_url: "...", category_id: N)` to subscribe.

If the user provides a direct feed URL, skip discovery and call
`create_feed` directly.

### Unsubscribing

```
delete_feed(feed_id: N)
```

This permanently removes the feed and all its entries. Confirm with
the user before calling.

### Refreshing

```
refresh_feed(feed_id: N)        # one feed
refresh_all_feeds()             # everything
refresh_category(category_id: N) # all feeds in a category
```

## Category management

```
get_categories()
create_category(title: "New Category")
update_category(category_id: N, title: "Renamed")
delete_category(category_id: N)
```

Deleting a category moves its feeds to the default category; it does
not delete feeds.

## OPML export

```
export()
```

Returns the full subscription list as OPML XML.

## Token budget

- Default `limit: 20` on all listing calls. Increase only if the user
  asks for more.
- Entry content from `get_entries` is usually sufficient. Only call
  `fetch_original_content` when the stored content is clearly
  incomplete.
- For large triage sessions (50+ articles), batch by category or feed
  rather than pulling everything at once.
- You are the language model. There is no summarize or digest command.
  Read the content directly and summarize it yourself.
