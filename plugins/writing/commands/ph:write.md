---
name: ph:write
description: "Review and clean prose for AI writing patterns."
argument-hint: "[text or file path]"
allowed-tools:
  - Read
---

# Stop Slop

**Arguments:** $ARGUMENTS

Parse arguments:

1. **text or file path** (optional): If a file path is provided, read the file first. If raw text is provided, treat it as the prose to review. If no argument is provided, ask the user to paste or specify the text.

Invoke the `stop-slop` skill with these arguments for the full review workflow.
