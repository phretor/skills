---
name: ph:amazon-writing
description: "Write or rewrite content in Amazon narrative memo style."
argument-hint: "<document-type> [text or file path]"
allowed-tools:
  - Read
  - Write
  - Edit
---

# Amazon writing

**Arguments:** $ARGUMENTS

Parse arguments:

1. **document-type** (required): One of `6-pager`, `1-pager`, `press-release`, or `prfaq`. If omitted, ask the user.
2. **text or file path** (optional): If a file path is provided, read the file first. If raw text is provided, treat it as the content to rewrite. If no argument is provided, ask the user to paste or specify the text.

Invoke the `amazon-writing` skill with these arguments for the full workflow.
