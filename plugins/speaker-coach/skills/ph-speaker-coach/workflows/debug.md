# Workflow: `debug` — Adversarial Talk Audit

Use when the speaker already has an artifact (abstract, outline, speaker notes, slide deck PDF, or rehearsal transcript). The audit is adversarial in voice — not gratuitous. Every callout names the underlying principle and quotes the offending line.

## Hard gates

1. Venue type identified.
2. Artifact ingested (file read, PDF extracted via `scripts/extract_deck.py`, or pasted text).
3. Speaker has stated, in their own words, what they think the takeaway is — *before* the coach reads the artifact.

The third gate matters. The audit's first job is to expose the **credibility–impact gap**: the distance between what the speaker thinks the artifact conveys and what it actually conveys.

## Step-by-step script

### Step 1 — Universal prelude (in SKILL.md)

Venue, talk slug, artifact path.

### Step 2 — Listening audit

Ask the speaker, *before reading the artifact*:

1. "In one sentence, what is the takeaway of this talk?"
2. "Who is the target audience subset?"
3. "What's the one thing you want them to do on Monday?"

Record their answers verbatim. Do **not** correct or coach yet.

### Step 3 — Read the artifact

Read the supplied file or pasted text. For PDFs, use `scripts/extract_deck.py`. Take notes on:

- What the actual takeaway sentence appears to be (if any).
- The opening (first slide / first paragraph / first 30 seconds).
- The closing (last slide / final paragraph).
- The implicit audience (who would understand this without prior context?).
- Visible anti-patterns (cross-reference `audit-anti-patterns.md`).

### Step 4 — Name the credibility–impact gap

Compare the speaker's stated takeaway (Step 2) against the artifact's apparent takeaway (Step 3). State the gap explicitly:

> "You said the takeaway is X. The artifact actually delivers Y. The gap is Z. Here's why: [evidence from the artifact, quoted]."

This is the central moment of the audit. Be specific. Quote lines. Do not soften.

### Step 5 — Myth check

Run the artifact through the *Cybersecurity Supercommunicators* myth list (`audit-anti-patterns.md` §Myth-level):

- "The data speaks for itself" — are charts present with no narrative caption?
- "If I'm accurate, they'll understand" — is there scaffolding for the non-expert?
- "I just need to survive the Q&A" — has the speaker designed for engagement or anticipated questions?
- "I have plenty of slides" — does the slide count match the story's actual needs?
- "Tool-first" — was the outline built before the deck?

For each myth that fires, name it and give one-line evidence.

### Step 6 — Anti-pattern scan

Walk `audit-anti-patterns.md` §Structural. For each pattern present, write one line:

```
[pattern name] — [quoted evidence] — [fix direction]
```

Common ones to look for first: ego intro, filler intro, agenda spoiler, wall of code, wall of text, monotone hook, no call-to-action, FUD, vendor pitch at hacker con, jargon minefield, no audience subset.

### Step 7 — Rubric scoring

Load `references/rubric.md`. Score each of the 12 metrics 1–5 using the **venue-appropriate column** from Step 1. For each metric:

- Write the score.
- Write one-line evidence quoting the artifact (or noting absence).
- Note the venue-appropriate target (e.g., "industry: Persuasiveness should be ≥4").

Refuse to fabricate scores. If the artifact lacks evidence for a metric (e.g., no transcript → no Engagement score), mark `N/A — needs rehearsal`.

### Step 8 — Surgical fixes (prioritized)

Produce a prioritized list:

1. **Block 1 (gating):** anything that prevents the takeaway from landing. Fix first.
2. **Block 2 (high-impact):** anti-patterns with high audience cost (wall of code, monotone hook, no CTA).
3. **Block 3 (polish):** smaller cuts.

For each item:

- State the fix in one sentence.
- Quote the relevant artifact line.
- Cite the principle (`design-principles.md` §N or `audit-anti-patterns.md`).
- Do **not** rewrite the speaker's content silently. Propose. Get approval. Then edit.

### Step 9 — Persist

Write the scorecard + diff/fixes section into the artifact (see SKILL.md artifact schema).

Tell the speaker:

- Total score / 60.
- Top three fixes to make before any rehearsal.
- Suggested next mode (`design` if the takeaway is broken, `rehearse` if it's a delivery-readiness audit).

## Anti-patterns for the coach in `debug` mode

- **Do not** start reading the artifact before the speaker has stated their own takeaway and audience.
- **Do not** fix the *how* (slide tweaks) before the *why* (takeaway, audience) is aligned. From the source: "If you're fixing the *how* before the *why*, you'll just make a prettier version of the same unclear message."
- **Do not** sugarcoat the credibility–impact gap. Name it. Quote it.
- **Do not** invent rubric evidence. If the artifact lacks the signal, score `N/A`.
- **Do not** rewrite the speaker's content without explicit approval.
- **Do not** use generic feedback ("be more engaging"). Always cite the metric and the principle.
