# PR/FAQ (Press Release / Frequently Asked Questions) Format

The PR/FAQ is Amazon's primary Working Backwards tool. It is a future-looking framework that starts by defining the customer experience and iteratively works backwards to define what must be built. The PR/FAQ is the most well-known Amazon document format adopted externally.

## Purpose

Use a PR/FAQ when:

- Evaluating whether a new product or feature should be built
- Defining the customer experience before discussing implementation
- Forcing customer-first thinking on a product proposal
- Presenting a product idea to leadership for a build decision
- You need to answer both "what is this?" (PR) and "what about X?" (FAQ)

## Document Structure

A PR/FAQ consists of two distinct sections that together should not exceed six pages:

1. **Press Release (PR)**: Under one page. The customer-facing announcement.
2. **Frequently Asked Questions (FAQ)**: Up to five pages. Addresses stakeholder concerns.

The length constraint is a forcing function — it develops better thinkers and communicators.

## Part 1: Press Release

See `press-release.md` for the full press release format. The PR section follows that format exactly: headline, opening paragraph, leadership quote, customer problem, solution narrative, customer quote, and availability.

The PR portion answers: "What are we building and why should the customer care?"

## Part 2: Frequently Asked Questions

The FAQ addresses concerns from two audiences: customers and internal stakeholders. Structure FAQs in order of importance within each category.

### Customer FAQs

Answer the questions a customer would ask after reading the press release:

- **"Why is this better than what I do today?"** — The most important customer question. Answer with specific, evidence-based differentiation, not marketing language.
- **"How much does it cost / how do I get it?"** — Clear pricing and access information.
- **"What are the limitations?"** — Honest answer about what the product does not do. Builds credibility and preempts disappointment.
- **"Is my data safe / is this reliable?"** — Address trust concerns directly with specifics, not assurances.

### Internal / Stakeholder FAQs

Answer the questions leadership and partner teams will ask:

- **"Why are we building this now?"** — Strategic rationale with evidence. What changed in the market, customer base, or competitive landscape?
- **"What is the revenue opportunity?"** — Market size, revenue model, and key assumptions. Use `[RESEARCH NEEDED]` for unvalidated numbers rather than fabricating estimates.
- **"What are the risks?"** — Honest assessment with mitigation plans. Distinguish between mitigated and open risks.
- **"Why will customers switch from [competitor / current solution]?"** — Specific differentiation. Must be "meaningfully better (faster, easier, cheaper)" or create a "stepwise change in customer experience."
- **"What could kill this idea?"** — Biggest threats and how they are monitored. Leadership frequently asks "so what?" — products must demonstrate they are 10x better, not 10%.
- **"What are the key assumptions and how will we validate them?"** — List critical assumptions with risk levels and validation methods.
- **"What resources are needed?"** — Team, timeline, dependencies, budget.

## Writing Process

### Step 1: Start with the Customer

Define:
- Primary customer (specific persona and context, not "users")
- Core problem or opportunity
- Single most important customer benefit
- Current evidence (data, research, or gaps)

### Step 2: Write the Press Release First

Write the PR before the FAQ. This forces you to articulate the customer value before diving into objections and details. If you cannot write a compelling one-page press release, the idea is not ready.

### Step 3: Write the FAQ

Address every question you anticipate from both customers and stakeholders. Do not avoid hard questions — the FAQ is where you demonstrate rigor.

### Step 4: Critical Review

Evaluate across four dimensions:

| Dimension | Key Question | Rating |
|-----------|-------------|--------|
| **Value** | Will customers buy it or choose to use it? | Strong / Moderate / Weak / Unknown |
| **Usability** | Can users figure out how to use it? | Strong / Moderate / Weak / Unknown |
| **Feasibility** | Can we build it with current resources? | Strong / Moderate / Weak / Unknown |
| **Business Viability** | Does this work for our business? | Strong / Moderate / Weak / Unknown |

Challenge the document with:
- "Is this must-have or nice-to-have?"
- "What is the 10x differentiation?"
- "What evidence exists versus what is assumed?"
- "What could kill this idea?"
- "What is the simplest experiment for the riskiest assumption?"

### Step 5: Review and Revision

The PR/FAQ is reviewed in a meeting following the standard reading protocol:
1. All attendees read silently.
2. General feedback is solicited (senior attendees speak last to avoid anchoring bias).
3. Detailed line-by-line discussion follows.
4. Meeting minutes capture feedback.
5. The document is revised and resubmitted.

Teams typically produce ten or more drafts before leadership approval. Most PR/FAQs never reach launch — this is a feature, not a bug. The process filters ideas to preserve resources for highest-impact initiatives.

### Step 6: Living Document

The PR/FAQ remains a living document after approval. It is subject to ongoing edits as the product evolves and new information emerges.

## Data Integrity Rules

Never fabricate data, statistics, or competitive information in a PR/FAQ.

| Situation | Approach |
|-----------|----------|
| User provided data | Use directly with source attribution: `[USER PROVIDED]` |
| Missing quantitative data | Use `[RESEARCH NEEDED: specific question]` |
| Missing qualitative claims | Use conditional language and label as `[ASSUMPTION]` |
| Competitive information | Use `[RESEARCH NEEDED]` rather than inventing features or pricing |
| Logical inference | Label as `[ASSUMPTION]` with validation method |
| Web-sourced data | Cite with `[SOURCE: URL]` |

## Recommendation Output

Every PR/FAQ review concludes with one of four recommendations:

- **Build**: All dimensions strong or moderate. Clear path forward.
- **Investigate**: One or more weak areas. Need evidence before deciding.
- **Pivot**: Fundamental issues. Need to reframe the problem or solution.
- **Kill**: Fatal flaws. Pursue other opportunities.

## Common Mistakes

- Writing the FAQ before the PR — the customer value must come first
- Treating the PR as an internal document instead of a customer-facing announcement
- Avoiding hard questions in the FAQ
- Fabricating market data or competitive analysis
- Disguising assumptions as validated facts
- Generic value propositions ("best-in-class," "industry-leading")
- Optimistic projections without acknowledging risks
- Skipping competitive analysis entirely
