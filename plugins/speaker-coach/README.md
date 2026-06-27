# speaker-coach

Disciplined, interview-style coaching for cybersecurity speakers — design, audit, and rehearse talks.

**Author:** [Federico Maggi](https://github.com/phretor)

## When to Use

- Designing a new cybersecurity talk from an idea (forward design, backwards from the last slide).
- Auditing an existing CFP abstract, outline, slide deck PDF, or rehearsal transcript adversarially.
- Scoring a rehearsal transcript against the 12-metric rubric.
- Walking a pre-talk readiness gate when the talk is 1–4 weeks away.
- Sharpening a weak takeaway into a 280-character tweet.
- Adapting the same material across academic, industry, and grassroots venues.

## When NOT to Use

- Non-cybersecurity speaking contexts (general TED-style coaching, sales pitches).
- Ghostwriting an abstract or generating slide content from scratch.
- Slide design / visual styling (font, color, layout).
- Prose copy-editing — use the `writing` plugin (`/ph:write`).
- Generating speaker bios.

## What It Does

Three sub-modes dispatched via `/ph:coach <mode>`:

- **`design`** — Socratic interview, one question per turn. Walks the speaker backwards from the last slide: target audience subset → 280-character takeaway → 3+ supporting sub-messages → narrative arcs → visual strategy → delivery considerations.
- **`debug`** — adversarial audit of an existing artifact (abstract, outline, speaker notes, slide-deck PDF, transcript). Names the credibility–impact gap, runs the myth check from *Cybersecurity Supercommunicators*, scans for structural anti-patterns (ego intro, agenda spoiler, wall of code, FUD, vendor pitch at hacker con), scores against the 12-metric rubric using the venue-appropriate column, and produces prioritized surgical fixes.
- **`rehearse`** — two sub-flows: rehearsal-transcript critique (clarity, engagement, narrative, filler-phrase density) or T-2-week readiness gate (walks the pre-talk checklist from messaging to seconds-before-going-on).

Every session writes a single markdown artifact at `./.coach/<slug>.md`, accumulating decisions and scores across iterations. Sub-sequent sessions read the file first and resume where the prior one left off.

Adapts automatically to **venue family** (academic / industry / grassroots) using the rubric column from `references/conf-norms.md`. The same metrics are interpreted differently for USENIX Security vs Black Hat vs DEF CON.

## Requirements

`pdftotext` (from the `poppler` package) is required only for slide-deck PDF ingestion. All other functionality works without it.

## Installation

See the [root README](../..) for installation instructions for all clients (Pi, Claude Code, etc.).
