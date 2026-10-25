# Venue Norms — Academic vs Industry vs Grassroots

Routes the rubric and the coaching tone. Always ask venue type in the prelude; if the speaker isn't sure, ask which examples in the table their venue resembles.

## Quick-classify table

| Family       | Examples                                                        | What it expects                                            |
| ------------ | --------------------------------------------------------------- | ---------------------------------------------------------- |
| **Academic** | USENIX Security, CCS, NDSS, IEEE S&P, ACSAC, EuroS&P, RAID, WOOT, BAR | Novelty, rigor, methodology, contribution, reproducibility |
| **Industry** | Black Hat (US/EU/Asia), RSA, HITB, Troopers, REcon, OffensiveCon, Hardwear.io, HackInBo, No Hat, RomHack, Nullcon, ZeroNights, GNU Radio Conference | Applicability, real-world impact, story, business/ops relevance |
| **Grassroots** | DEF CON, CCC, BSides (global), Hack.lu                       | Authenticity, technical curiosity, demos, hacker ethos     |

If a venue lives at the boundary (e.g., Troopers, HITB) ask what the speaker thinks the dominant audience is, and route from there. When in doubt for a recorded talk, treat the broader recording audience as the target.

## What each venue rewards / penalizes

### Academic

- **Rewards:** precision, scoped claims, citations, openly stated limitations, structured visuals, controlled pacing.
- **Penalizes:** sensationalism, vague scoping, marketing tone, unbacked claims, FUD.
- **Clarity:** define terms; expect "under what threat model?" pushback.
- **Engagement:** subtle — cognitive-load management, slow build-ups, well-labeled diagrams. Humor is rare.
- **Persuasion:** by significance and embedding in literature.
- **Storytelling:** the *method* is the story.
- **Complexity:** layer for mixed subfields in the room.
- **Diversity:** acknowledge reviewers from adjacent subfields.
- **Transparency:** redactions for double-blind; openly state limitations.
- **FUD:** intellectual red flag.
- **Credibility:** humility, citations, sober treatment of implications.
- **Problem framing:** research gap.
- **Takeaway:** conceptual / methodological.
- **Cultural fit:** no overt branding; scholarly tone.

### Industry

- **Rewards:** clear problem-solution framing, real-world stakes, strong opening, compelling visuals, actionable takeaways.
- **Penalizes:** FUD-driven marketing, vendor pitch, jargon without context, no actionable item.
- **Clarity:** practical relevance — what does this mean for detection latency, patch cycles, headcount?
- **Engagement:** strong opening, real incidents, professional pacing.
- **Persuasion:** utility — "here's how this improves SOC workflows."
- **Storytelling:** incidents, breaches, weird logs, postmortems.
- **Complexity:** accurate simplification for CISO + analyst + engineer simultaneously.
- **Diversity:** balance high-level impact with technical depth.
- **Transparency:** signal what *can't* be shared; provide mitigation/detection anyway.
- **FUD:** burns credibility; avoid buzzwords like "zero-day apocalypse."
- **Credibility:** credit collaborators; responsible disclosure; operational ethics.
- **Problem framing:** operational pain.
- **Takeaway:** something applicable tomorrow.
- **Cultural fit:** professional tone, honest, never a veiled pitch.

### Grassroots / Hacker

- **Rewards:** authenticity, demos, war stories, tool drops, transparency, community spirit.
- **Penalizes:** polish-over-substance, vendor pitch, gatekeeping, corporate tone.
- **Clarity:** plain talk + analogies + showing your work.
- **Engagement:** storytelling, attitude, irreverence, participation.
- **Persuasion:** conviction — say what matters, don't market.
- **Storytelling:** personal — "my printer kept rebooting."
- **Complexity:** raw detail OK; pace it; don't gatekeep.
- **Diversity:** hacker-first; inclusive of newcomers; no "only kernel devs will care."
- **Transparency:** assumed unless OPSEC reason; if holding back, say why.
- **FUD:** called out as a cultural offense.
- **Credibility:** community trust, openness about motives, DIY reproducibility.
- **Problem framing:** "scratch-your-own-itch" is valid.
- **Takeaway:** hackable idea, tool drop, or mindset shift.
- **Cultural fit:** informal but principled; truth, community, curiosity, sharing.

## Cross-venue insider edges

- **Academic:** Q&A responses can matter as much as slides. Anticipate the toughest peer question.
- **Industry:** connect work to current threat trends; have executive-friendly one-pagers ready for hallway conversations.
- **Grassroots:** sharing partial failures or "what didn't work" earns credibility. Release slides/code/tools on GitHub immediately.

## Recorded talks

The audience extends beyond the room. If a recording will circulate, decide which subset you're addressing and be explicit if mid-talk you pivot to "for folks watching this recorded…"

## Sources

- F. Maggi, *Payload Delivered — Chapter 5: The Cybersecurity Conference Panorama* (draft).
- F. Maggi, *Payload Delivered — Chapter 11: One Rubric, Many Stages* (draft, in repo as `Chapter 10 - Putting it All Together`).
