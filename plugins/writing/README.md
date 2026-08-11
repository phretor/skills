# writing

Writing quality tools: eliminate AI slop from prose and write narrative memos in Amazon style.

**Author:** [Hardik Pandya](https://hvpandya.com) (stop-slop), [Federico Maggi](https://github.com/phretor) (amazon-writing)

## When to Use

- Reviewing prose before publishing (blog posts, docs, reports, emails, commit messages)
- Editing drafts to remove predictable AI tells
- Writing or rewriting narrative memos, 6-pagers, 1-pagers, press releases, or PRFAQs in Amazon style
- User asks to "clean up," "tighten," "de-AI," or "improve" their writing
- User asks for "Amazon-style," "narrative memo," or names a specific document type (6-pager, PRFAQ, etc.)

## When NOT to Use

- Grammar and spelling correction only
- Style adaptation to a specific brand voice
- Code review or technical correctness
- Slide decks or presentation formats
- Technical documentation (API docs, READMEs, runbooks)

## What It Does

### stop-slop (`/ph:write`)

Applies the Stop Slop ruleset to prose:

1. Cuts throat-clearing openers, emphasis crutches, and all adverbs
2. Breaks formulaic structures: binary contrasts, negative listings, dramatic fragmentation
3. Converts passive voice to active, naming the human actor
4. Replaces business jargon with plain language
5. Eliminates false agency ("the decision emerges") and narrator-from-a-distance voice
6. Scores prose 1-10 across five dimensions (directness, rhythm, trust, authenticity, density); flags anything below 35/50 for revision

Detailed banned-phrase lists: [`skills/stop-slop/references/phrases.md`](skills/stop-slop/references/phrases.md)
Structural clichés: [`skills/stop-slop/references/structures.md`](skills/stop-slop/references/structures.md)
Before/after examples: [`skills/stop-slop/references/examples.md`](skills/stop-slop/references/examples.md)

### amazon-writing (`/ph:amazon-writing`)

Rewrites content following Amazon's narrative memo standards:

1. Applies six core rules: narrative structure, conciseness, data over adjectives, active voice, the "so what" test, respect the reader's time
2. Supports four document types: 6-pager, 1-pager, press release, PRFAQ
3. Loads document-specific guidelines from reference files for required sections and format constraints

Document-type references: [`skills/amazon-writing/references/`](skills/amazon-writing/references/)

## Installation

See [root README](../..) for installation instructions for all clients (Pi, Claude Code, etc.).
