# Cybersecurity Speaker Evaluation Rubric

Twelve metrics, each scored 1–5. Each metric is interpreted differently across three venue types: **academic**, **industry**, **grassroots/hacker**. Always cite the metric name and the score when invoking this rubric.

## Quick venue routing

| Venue type   | Examples                                  | Reward                                | Penalize                               |
| ------------ | ----------------------------------------- | ------------------------------------- | -------------------------------------- |
| academic     | USENIX Security, CCS, NDSS, IEEE S&P      | precision, methodology, contribution  | sensationalism, vague scoping          |
| industry     | Black Hat, RSA, HITB, Troopers            | applicability, business impact, story | FUD, vendor pitch, no actionable item  |
| grassroots   | DEF CON, BSides, CCC, RomHack, Hack.lu    | authenticity, demos, hacker ethos     | polish-over-substance, gatekeeping     |

## Cross-venue interpretation table

| Category                | Criterion                          | Academic                                                   | Industry                                                | Grassroots/Hacker                                            |
| ----------------------- | ---------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------ |
| Generic Communication   | Clarity                            | Technical rigor, definitions, precise scoping              | Clear problem-solution framing, practical implications  | Technically dense but hands-on and informal clarity          |
|                         | Audience Engagement                | Structured flow, diagrams, pacing to reduce cognitive load | Strong opening, visual support, real-world stakes       | Humor, live demos, irreverence, participatory tone           |
|                         | Persuasiveness / Message Power     | Framed contribution within prior work                      | Clear business/research value, actionable takeaways     | Clear purpose or call-to-action, no corporate fluff          |
|                         | Storytelling / Narrative Strength  | Logical progression from problem to contribution           | Real-world stories, incident narratives, analogies      | War stories, hacks, cultural nods, curiosity-driven arc      |
| Cybersecurity-Specific  | Managing Technical Complexity      | Layered explanations for mixed-tech audiences              | Simplified but accurate model of threat/defense         | Raw detail OK, but context still matters                     |
|                         | Audience Diversity Awareness       | Considerations for reviewers from subfields                | Balance between technical detail and CISO/analyst value | Hacker-first; avoid exclusionary language or gatekeeping     |
|                         | Balancing Transparency and Secrecy | Disclosure of limits, redactions for double-blind          | NDAs, embargoed content, responsible disclosure cues    | Openness preferred, but anonymity/OPSEC respected            |
|                         | Avoiding FUD / Self-Censorship     | Stay neutral, clinical, avoid sensational claims           | Avoid fear-based selling or buzzwords                   | Call out FUD; prefer evidence and transparency               |
|                         | Credibility and Ethical Framing    | Cite prior work, admit limitations, avoid hype             | Attribution, ethical implications of tools/results      | Community trust, openness about motives, DIY reproducibility |
| Conference-Specific     | Problem Framing                    | Clear research question, gaps in literature                | Real-world problem definition, business/ops relevance   | Personal itch to scratch, hacker motivation                  |
|                         | Takeaway Value                     | Insightful findings and future work                        | Actionable practices, defenses, indicators              | Hackable idea, mindset shift, or tool demo                   |
|                         | Cultural Fit                       | Fits peer-review norms, no marketing                       | Fits professional tone, no vendor pitch                 | Respects hacker ethos, informal but technical                |

## Generic Communication

### Clarity

| Score | Definition                                               | Example                                                                                                           |
| ----- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 1     | Confusing, unstructured, full of unexplained jargon.     | "So basically, the firmware uses JTAG over UART to unlock the chip, but you all know that."                       |
| 2     | Hard to follow; assumes too much prior knowledge.        | "We bypassed ASLR using a return-to-libc chain, but I won't go into the specifics because it's very technical."   |
| 3     | Understandable but occasionally unclear.                 | "We built a fuzzer for CAN bus, and found some crashes. Here's one crash log."                                    |
| 4     | Clear explanations and good structure.                   | "We used a stateful fuzzer tailored to the CAN protocol. Here's how it differs from common fuzzers…"              |
| 5     | Elegant, accessible explanation of complex ideas.        | "Imagine trying every possible key to a locked door — our fuzzer does this, but only on valid signals cars expect." |

### Audience Engagement

| Score | Definition                                              | Example                                                                                  |
| ----- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 1     | Monotonous and disengaging.                             | Speaker reads bullet points for 20 minutes in a monotone.                                |
| 2     | Sporadic attempts at engagement.                        | "Let's look at some graphs." (with no commentary)                                        |
| 3     | Some engagement, inconsistently applied.                | "This reminds me of an incident at a SOC I worked at. Anyway…"                           |
| 4     | Well-used stories, visuals, or pacing.                  | "Here's a real-world breach we walked into — and the strange behavior that tipped us off." |
| 5     | Captivates audience with strong hooks and storytelling. | "If you've ever plugged in a random USB stick — this talk is for you."                   |

### Persuasiveness / Message Power

| Score | Definition                                   | Example                                                                                      |
| ----- | -------------------------------------------- | -------------------------------------------------------------------------------------------- |
| 1     | No clear message.                            | "So yeah… it's kind of cool, I guess."                                                       |
| 2     | Weakly framed or implied message.            | "We think our tool might be useful, but it's still early."                                   |
| 3     | Understandable message, not fully developed. | "We built a tool to detect rogue DNS requests in enterprise logs."                           |
| 4     | Strong, clear message with evidence.         | "Our tool detects exfiltration over DNS — even when encrypted — before most EDRs would flag it." |
| 5     | Memorable, resonant message.                 | "Your DNS logs are telling you when you're being watched."                                   |

### Storytelling / Narrative Strength

| Score | Definition                                        | Example                                                                                                           |
| ----- | ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 1     | Flat structure, no story.                         | "Here's our intro, methods, results, and conclusion."                                                             |
| 2     | Disconnected or shallow narrative.                | "We had a bug once… anyway, the mitigation is in slide 17."                                                       |
| 3     | Basic chronological or causal flow.               | "We discovered the issue in a pen test, then tried reproducing it in a lab…"                                      |
| 4     | Structured narrative with examples or escalation. | "At first, it looked like a fluke. But then, every system we checked had the same backdoor."                      |
| 5     | Vivid, emotionally resonant story arc.            | "It started with a tweet. One screenshot. That's all it took to unravel a zero-day used by a nation-state actor." |

## Cybersecurity-Specific

### Managing Technical Complexity

| Score | Definition                                   | Example                                                                                                 |
| ----- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| 1     | Too dense or oversimplified.                 | "It's just math. You either get it or you don't."                                                       |
| 2     | Inaccessible explanations.                   | "We used elliptic curves — no need to explain, everyone here's technical."                              |
| 3     | Complexity mostly managed, but inconsistent. | "Here's the architecture — don't worry about the details if you're not familiar."                       |
| 4     | Well-managed abstraction and detail.         | "Each transaction has a 'curve signature' — like a fingerprint unique to the sender."                   |
| 5     | Elegantly layered explanations.              | "Let's break this down: memory access, privilege escalation, and how they interact in sandbox escapes." |

### Audience Diversity Awareness

| Score | Definition                                    | Example                                                                                              |
| ----- | --------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 1     | Speaks only to one subgroup.                  | "This is for kernel devs only. Everyone else can leave."                                             |
| 2     | Acknowledges others but doesn't include them. | "It's super technical, sorry CISOs."                                                                 |
| 3     | Partial awareness of audience variety.        | "There's some business impact here, but let's stay focused on the exploit."                          |
| 4     | Includes multiple roles and backgrounds.      | "For analysts: here's how it logs. For engineers: here's the trace."                                 |
| 5     | Unifies and includes diverse audience types.  | "Whether you're a red teamer or a policymaker, this bug breaks your trust model. Let's explore how." |

### Balancing Transparency and Secrecy

| Score | Definition                                               | Example                                                                                         |
| ----- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 1     | Vague, uninformative, or evasive.                        | "We found a serious bug, but we can't say anything. Trust us."                                  |
| 2     | Withholds too much, awkward transitions.                 | "We disclosed this to the vendor, but can't talk about it further. Anyway…"                     |
| 3     | Cautiously transparent, with minor disruptions.          | "We can't share the PoC, but we'll show a trace."                                               |
| 4     | Explains limits clearly and responsibly.                 | "Due to NDA, we'll show the mitigation path, not the actual exploit chain."                     |
| 5     | Builds trust while respecting ethical/legal constraints. | "We're withholding details for safety, but here's how to detect or mitigate the vulnerability." |

### Avoiding FUD / Self-Censorship

| Score | Definition                                          | Example                                                                                |
| ----- | --------------------------------------------------- | -------------------------------------------------------------------------------------- |
| 1     | Alarmist or manipulative tone.                      | "This could end the internet as we know it. You should panic."                         |
| 2     | Avoids important truths out of fear.                | "It's scary, but let's not get into the details — it's too sensitive."                 |
| 3     | Balanced, but occasionally hesitant or unclear.     | "There are serious implications, but it depends on how widespread this is."            |
| 4     | Realistic, composed risk framing.                   | "It's a subtle flaw, and though not wormable, the insider abuse potential is real."    |
| 5     | Clear, confident, and evidence-based communication. | "We don't do scare-talk here. Let's focus on what the data shows, and why it matters." |

### Credibility and Ethical Framing

| Score | Definition                               | Example                                                                                        |
| ----- | ---------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1     | Unethical or careless tone.              | "We don't really care what happens — this was just a fun hack."                                |
| 2     | Avoids or downplays ethical concerns.    | "Sure, someone could abuse this, but that's not our problem."                                  |
| 3     | Ethics mentioned briefly, without depth. | "We notified the vendor. That's all I'll say."                                                 |
| 4     | Responsible and thoughtful framing.      | "This attack vector is rare, but with IoT adoption, we felt disclosure was essential."         |
| 5     | Strong ethical voice and integrity.      | "We disclosed, waited for a fix, and now we're here to educate — because this affects everyone." |

## Conference-Specific Needs

### Problem Framing

| Score | Definition                                   | Example                                                                                                       |
| ----- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| 1     | No problem or purpose defined.               | "I just wanted to show you this thing I found."                                                               |
| 2     | Vague or minor framing.                      | "I mean, this is kind of a bug, I guess."                                                                     |
| 3     | Clear problem, but not compelling.           | "Some embedded devices crash when scanned a certain way."                                                     |
| 4     | Meaningful and well-scoped issue.            | "Firmware update mechanisms in consumer routers are routinely exploitable — here's why that matters."         |
| 5     | Urgent, sharply framed, and deeply relevant. | "If you trust over-the-air updates, your assumptions may be dangerously outdated. Let's dismantle that myth." |

### Takeaway Value

| Score | Definition                                    | Example                                                                                |
| ----- | --------------------------------------------- | -------------------------------------------------------------------------------------- |
| 1     | No clear insight or takeaway.                 | Audience leaves confused, wondering "so what?"                                         |
| 2     | Limited or impractical takeaway.              | "We built a thing. Might be useful."                                                   |
| 3     | One moderately useful or interesting insight. | "Here's our GitHub. Try it if you're curious."                                         |
| 4     | Clear, applicable takeaways.                  | "Use this YARA rule to detect similar threats."                                        |
| 5     | Inspires action or mindset shift.             | "This changes how you think about USB devices — and here's how to audit your own stack." |

### Cultural Fit

| Score | Definition                              | Example                                                           |
| ----- | --------------------------------------- | ----------------------------------------------------------------- |
| 1     | Wildly off-tone for the event.          | A vendor gives a sales pitch at DEF CON.                          |
| 2     | Aware of mismatch but poorly adapted.   | "I know this is a bit polished for this crowd, but bear with me…" |
| 3     | Acceptable, but not natural or aligned. | Mostly technical, but stiff or overly corporate tone.             |
| 4     | Good match in tone and structure.       | Raw slides, direct explanations, open-source sharing.             |
| 5     | Embodies the event's values and energy. | Live demo, hacker ethos, tool drop, audience respect.             |

## Source

Adapted from F. Maggi, *Payload Delivered — Appendix B: Cybersecurity Speaker Evaluation Rubric* (draft).
