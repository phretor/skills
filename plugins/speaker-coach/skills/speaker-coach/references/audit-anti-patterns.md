# Audit Anti-patterns

Used by `debug` mode. When auditing an existing talk, name these explicitly with the **why** behind each (not just "this is bad"). Quote the offending line.

## Myth-level anti-patterns (call them by name)

These are the myths from *Cybersecurity Supercommunicators*. Each is a recurring failure mode that costs the speaker credibility-impact.

| Myth                                       | Why it fails                                                    | Audit signal                                                                          |
| ------------------------------------------ | --------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| "The data speaks for itself."              | People remember stories. Data is overwhelming without a hook.   | Slides are charts with no narrative caption. No "so what" follows the result.         |
| "If I'm accurate, they'll understand."     | Accuracy is table stakes; clarity is extra work.                | Sentence-level precision but no analogy, no scaffolding, no layered explanation.      |
| "I just need to survive the Q&A."          | The speaker is dodging engagement instead of designing for it.  | No anticipated questions list; Q&A treated as a chore.                                |
| "I have plenty of slides."                 | Slide count is not the question. Match the story's needs.       | Slide count chosen before story is locked.                                            |
| "I'm a procrastinator, deck's tonight."    | Self-deception or panic. Disrespects the audience's time.       | Visible rough edges; placeholders; unrehearsed transitions.                           |
| "Let me work on my deck — opens PowerPoint." | Tool-first means story-last.                                  | Outline is the deck itself. No prior written outline. No tweet.                       |

## Structural anti-patterns (audit signals in any draft)

| Pattern                              | Signal in the artifact                                                  | Fix direction                                                                  |
| ------------------------------------ | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **Ego intro**                        | First slide is "About Me" / "whoami" wall of credentials.               | Move credentials into the body via content. Open on the hook.                  |
| **Filler intro**                     | "Honored to be here," "thanks for coming," "let me thank organizers."   | Cut. Replace with the hook sentence (memorized).                                |
| **Agenda spoiler**                   | Slide 2 is a TOC listing all the sections.                              | Cut. Replace with "behind the scenes" or stakes-naming.                         |
| **Wall of code**                     | A slide with > 10 lines of code; speaker reads it.                      | Show 2–4 lines max; visually highlight the operative ones; cite the principle. |
| **Wall of text**                     | Bullets of full sentences; small font; speaker reads.                   | One sentence (or none) per slide. Keep the text in speaker notes.              |
| **Complex diagram unrolled at once** | A 12-node graph appears with no progressive reveal.                     | Sequence: duplicate the slide N times, reveal one element at a time.           |
| **Big-bang demo at the end**         | One 5-minute demo near the end, hoping audience remembers everything.   | Split into bite-sized clips throughout the talk.                               |
| **Monotone hook**                    | Hook is "let me talk about X today."                                    | Rewrite as a memorized, intentionally vivid opening sentence.                  |
| **No call-to-action**                | Last slide says "Thank you" or "Questions?"                             | Replace with the 280-char takeaway, an action prompt, or a provocative question. |
| **FUD / sensationalism**             | "This could end the internet"; "everyone is at risk."                   | Reframe with concrete risk, frequency, mitigation. Industry/grassroots penalize this. |
| **Jargon minefield**                 | Unexplained acronyms (JWT, ROP, SSRF) used at decision-maker venues.    | Define on first use or substitute with the working concept.                    |
| **Vendor pitch at hacker con**       | Tooling/product/marketing language at DEF CON / BSides / CCC.          | Cultural mismatch → score Cultural Fit 1–2. Strip vendor framing or change venue. |
| **No audience subset named**         | Speaker says "this talk is for everyone."                               | Force the speaker to name the subset (peers / press / customers / policy).     |
| **Transparency mishandled**          | Vague "we can't talk about it" with no replacement.                     | Say what *can* be shared (mitigation, detection), name the constraint reason.  |
| **Self-censorship**                  | Withholds important truths out of fear.                                 | Help the speaker frame responsibly, not hide.                                  |

## Coaching-pitfall self-check (for the coach itself)

From *Cybersecurity Supercommunicators*: "Jumping straight into 'add this slide / remove that detail' without aligning on the outcome they want from the talk."

If you (the coach) catch yourself recommending slide tweaks before the takeaway and audience subset are locked, **stop**. Restart the audit from message clarity.

## Sources

- F. Maggi, *Cybersecurity Supercommunicators* (Trustial, 2025-09-14) — myths and coaching pitfalls.
- F. Maggi, *Become a Cybersecurity Supercommunicator* (Trustial, 2026-01-24) — structural anti-patterns.
- F. Maggi, *Payload Delivered — Chapter 4: Unique Challenges of Speaking in Cybersecurity* (draft) — FUD, jargon, transparency.
