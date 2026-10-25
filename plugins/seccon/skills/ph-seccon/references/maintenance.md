# Maintenance limits and outcomes

Check each source's robots directives and terms before acquisition. The tools identify themselves as `ph-seccon` and also honor GPTBot, ChatGPT-User, OAI-SearchBot and ClaudeBot restrictions. They use ordinary HTTP, with no browser impersonation, TLS disguise, challenge solving or authentication fallback.

Each command permits at most 24 requests per origin (including robots), at least one second apart or the site's longer crawl delay/request-rate interval. There are no automatic retries. A 429 records Retry-After and stops further access to that origin for the command. Re-run only when permitted after that interval. A challenge/401/403 stops that origin too. Robots errors, challenges, rate limits and redirects fail closed; a missing robots file (404) permits a terms-checked public path. Canonical robots redirects require manual policy review rather than automatic target access.

Every target redirect receives a policy check before access. Redirects changing year or region stop before the new edition is requested. Canonical same-edition redirects are accepted; a changed host requires review. Conflicting titles are retained as `needs-review`, not silently relabeled. These checks are conservative signals, not proof of program completeness or identity.

For client-rendered pages the crawler follows at most eight unique same-origin JS/JSON assets, with policy checks and host pacing. External/credential-bearing assets and cross-origin asset redirects are refused. Exhausted budgets and incomplete shells remain explicit outcomes. Native candidates precede publisher resolution; a denial never triggers publisher/provider escalation.

## Source capabilities

- Academic population retains its DBLP XML adapter, but the observed robots rules deny XML and search. It reports `policy-denied` with zero target requests. Native academic pages remain ad-hoc content sources, not automatic population adapters.
- IEEE S&P uses the native `program.html` candidate; accepted-paper templates can carry stale titles.
- CCS explicit and registered URLs both follow permitted native linked JSON before considering a publisher resolver.
- OffensiveCon uses structured agenda text, preserving inline markup/entities and splitting speakers; administrative rows are excluded. REcon retains its static sessions adapter.
- DEF CON media currently denies AI agents. Keep cached lookup and report the refresh limit.
- Black Hat/ACM may challenge ordinary requests. An explicit unavailable result is expected; never defeat the challenge. The Black Hat importer accepts authorized local JSON exports and exits nonzero on any requested-file failure, including partial batches.
- hardwear.io RSS contains only recent uploads, not complete historical or regional coverage; its observed feed policy denies crawling. Setting an API key does not activate any implementation. Do not replace a fuller index with a partial RSS result without maintainer review.
- Other manifest venues without a population handler return `unsupported`. No venue or cached index is removed.
- Calendar and paperhub requests also require policy checks. Wrapper access does not override upstream restrictions; unavailable providers limit author/enrichment results. Crossref metadata does not guarantee abstracts, citations or full text.

## Cache metadata

`cached` records index availability. The manifest separately derives `quality` from content and exposes each edition's latest `refresh` record. Meaningless or malformed caches remain on disk with `needs-review`; they must not be presented as complete programs. Quality flags derive from records, including `description` and direct slides links, rather than trusting historical hardcoded flags. Completeness remains unverified even when records validate.

Successful acquisitions store their source, status, effective URL, content type and actual acquisition timestamp. Imports record filename, SHA-256, file modification time and import time. Import time is not acquisition time: unknown acquisition dates stay null. A failed/empty refresh keeps the earlier index and its acquisition age. Replacement writes are atomic.

Population writes per-edition `refresh.json` records and returns nonzero if any requested refresh fails or lacks an implemented handler. Manifest generation is offline and preserves existing future editions. Resource exports can be directed to a scratch root for verification. No maintenance command bypasses source restrictions to close a gap.
