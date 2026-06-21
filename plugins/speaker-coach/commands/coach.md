---
name: ph:coach
description: "Coach a cybersecurity speaker through forward design, adversarial audit, or rehearsal/readiness critique of a talk."
argument-hint: "<design|debug|rehearse> [artifact path or note]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
---

# Cybersecurity Speaker Coach

**Arguments:** $ARGUMENTS

Parse arguments:

1. **mode** (required): one of `design`, `debug`, `rehearse`. If missing or unrecognized, ask the user to pick before proceeding. Do not guess.
   - `design` — forward design from idea to outline, backwards from the last slide.
   - `debug` — adversarial audit of an existing abstract, outline, slides, or transcript.
   - `rehearse` — rehearsal-transcript critique or T-2-week readiness gate.
2. **artifact path or note** (optional): file path (markdown, text, or PDF slide deck) or freeform note about the talk. Used by `debug` and `rehearse` to seed the audit.

Invoke the `speaker-coach` skill with these arguments. The skill enforces a universal prelude (venue type, target audience subset, artifact path for the persisted design doc + scorecard) before dispatching to the sub-mode workflow.
