# Workflow: `rehearse` — Rehearsal Critique + Readiness Gate

Two sub-flows. Ask the speaker which they need at the top:

- **Rehearsal critique** — speaker has a transcript or notes from a recent rehearsal; coach scores and gives line-level feedback.
- **Readiness gate** — speaker has a talk in the next 1–4 weeks; coach walks the pre-talk checklist.

If the speaker is unsure, ask: "How many days until the talk? Do you have a transcript I can read?" Route from there.

## Sub-flow A — Rehearsal critique

### Hard gates

1. Venue type identified.
2. Transcript or rehearsal notes available (pasted text or file).
3. Speaker can name the takeaway and audience subset before the coach reads the transcript.

### Steps

1. **Pre-read interview.** Ask: "What was the goal of this rehearsal? What did you feel went well? What felt rough?"
2. **Read transcript.** Note: opening sentence; filler-phrase density ("um," "uh," "honored," "let me thank," "a bit about myself"); jargon density vs venue; transitions between sub-messages; hook-to-takeaway alignment.
3. **Score relevant rubric metrics.** From `references/rubric.md`:
   - **Clarity** — definitions, scoping, layered explanations.
   - **Audience Engagement** — hook strength, real-world stakes, pacing cues.
   - **Storytelling / Narrative Strength** — arc presence, escalation, climax.
   - **Managing Technical Complexity** — layered scaffolding for the venue's audience mix.
   - **Persuasiveness / Message Power** — does the message land memorably?
   - **Takeaway Value** — does the closing leave an action or mindset shift?

   Use the venue column. Cite the score line and quote evidence.

4. **Filler-phrase callouts.** Flag every instance of:
   - Throat-clearing openers: "honored," "thanks for coming," "humbled," "excited."
   - Self-deflecting transitions: "anyway," "moving on."
   - Apologetics: "sorry, this is technical," "bear with me."
   - "Um" / "uh" / "like" / "you know" — count and report rate per minute (estimate from transcript length).

5. **Body-language proxies in text.** A transcript can't show body, but listen for:
   - References to slides ("as you can see here") → speaker is facing the screen.
   - Long silences → unscripted hesitation, not designed pause.
   - Reading aloud from slides → wall-of-text fix needed in deck.

   Flag and note in the scorecard with `[delivery]` prefix.

6. **Surgical fixes.** Write 5–10 prioritized line-level rewrites. Quote the original; propose the replacement; cite the metric/principle. Do not rewrite the whole transcript.

7. **Persist.** Write the rehearsal score + fixes into the artifact.

## Sub-flow B — Readiness gate

### Hard gates

1. Venue type identified.
2. Days-until-talk known.
3. Talk slug + artifact file path.

### Steps

1. **Calendar context.** Ask "Days until the talk?" Route to the appropriate checklist phase in `references/rehearsal-routine.md`:
   - > 30 days → start at "Messaging."
   - 15–30 days → start at "Core material drafted."
   - 8–14 days → start at "Content finalized."
   - 3–7 days → start at "Environment + tech."
   - 1–2 days → "Day before / day-of."
   - < 1 day → "2 hours before" countdown.
2. **Walk the checklist for the current phase + all earlier phases.** For each item, ask the speaker to confirm one of: **done / in-progress / not started / N/A**.
   - Do not bundle. One phase at a time.
   - For "not started" items in a phase that should already be done, name the risk and the recovery path.
3. **Verdict.** At the end, state:
   - **Green** — all gating items are "done" for the current phase and earlier; speaker is on track.
   - **Yellow** — 1–3 gating items behind; name them and the minimum recovery actions.
   - **Red** — more than 3 gating items behind, *or* core messaging not locked; recommend rescoping or pulling the talk if feasible.

   Refuse to give "green" if the takeaway and 3+ sub-messages are not both locked. Route to `design` mode instead.
4. **Day-of routine.** If the talk is < 48 hours away, walk the 2-hour / 1-hour / 30-min / 10-min / 5-min / seconds-before drill (`references/rehearsal-routine.md`). Speaker can save it as a personal checklist.
5. **Persist.** Update the artifact's readiness section with the phase status and the recovery actions.

## Anti-patterns for the coach in `rehearse` mode

- **Do not** give a "green" verdict if message clarity is unlocked. Always route to `design`.
- **Do not** rewrite the rehearsal transcript wholesale. Surgical fixes only.
- **Do not** score Engagement or Storytelling from a deck alone — those need a transcript or recording. Mark `N/A`.
- **Do not** lecture about body language for sub-flow A unless the transcript surfaces a specific signal.
- **Do not** allow slide changes after the day-of rehearsal, except for legal-mandated updates.
