---
name: phretor:con
description: "Conference intelligence — academic and industry venues. Use as /phretor:con [academic|industry] <question> or /phretor:con [academic|industry] now [<acronym>]."
argument-hint: "[academic|industry] <question|now [acronym]>"
allowed-tools:
  - WebFetch
  - WebSearch
  - Bash
---

# Conference Intelligence

**Arguments:** $ARGUMENTS

Parse arguments:
1. **Mode** — `academic` or `industry`; infer from context when unambiguous (e.g. "DEF CON" → industry, "IEEE S&P" → academic)
2. **Subcommand** — `now` for live calendar, or any free-form question, topic, author name, or paper title
3. **Acronym** — optional, only with `now`: look up a specific conference (e.g. `/con academic now CCS`)

Invoke the `con` skill with these arguments for the full workflow.
