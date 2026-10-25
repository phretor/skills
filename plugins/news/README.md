# news

Read, search, and triage RSS feeds through the Miniflux MCP server.

**Author:** [Federico Maggi](https://github.com/phretor)

## When to Use

- Catch up on unread feed entries, or summarize and search them
- Mark entries read, star, save, or remove them
- Subscribe to feeds, refresh feeds, manage categories, export OPML

## When NOT to Use

- Searching the web for news — use a search tool
- Fetching an arbitrary page that is not a Miniflux entry — fetch the URL directly
- Setups without a Miniflux instance

## What It Does

`ph-news-reader` drives the `miniflux` MCP server: orientation (counters, categories, feeds), filtered entry listing and full-text search, read/unread/star/save/remove triage, feed and category management, and OPML export. It checks the server with `healthcheck` first and stops with a configuration hint if the server is unreachable. Listing calls default to `limit: 20` to keep token cost down.

## Requirements

- A configured and reachable `miniflux` MCP server. The skill refers to its tools by bare name (`get_entries`); some harnesses prefix them (`mcp__miniflux__get_entries` in Claude Code).
