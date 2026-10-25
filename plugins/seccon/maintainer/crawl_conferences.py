# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Discover conference URLs and fetch raw conference pages.

Refresh URL references annually:

    uv run maintainer/crawl_conferences.py
    uv run maintainer/crawl_conferences.py --academic --start-year 2025 --end-year 2025
    uv run maintainer/crawl_conferences.py --industry

Crawl one conference page and return the raw page content for agent-side reasoning.
Use --url for a page discovered by web search, or --conference/--year to use
built-in best-effort URL candidates and proceedings fallbacks:

    uv run maintainer/crawl_conferences.py --crawl-content \
      --url https://www.sigsac.org/ccs/CCS2025/accepted-papers/
    uv run maintainer/crawl_conferences.py --crawl-content --academic \
      --conference ccs --year 2025 --format json
    uv run maintainer/crawl_conferences.py --crawl-content --industry \
      --conference defcon --year 2025 --format json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import signal
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

from fetch_policy import STOP_OUTCOMES, Fetcher, FetchResult, origin, validate_content

FETCHER = Fetcher()

REFS_DIR = Path(__file__).parent / "references"
CURRENT_YEAR = date.today().year

_BH_SESSIONS_URL = "https://blackhat.com/{slug}/briefings/schedule/sessions.json"
_BH_SLUGS = {"usa": "us", "europe": "eu", "asia": "asia"}


@dataclass(frozen=True)
class Conf:
    name: str
    abbrev: str
    url_fn: Callable[[int], str | None]
    bh_slug: str = ""
    resolver: Callable[[int], str | None] | None = None
    content_urls: Callable[[int], list[str]] | None = None


# --- Academic URL generators ---


def _usenix(year: int) -> str:
    yy = str(year)[2:]
    return f"https://www.usenix.org/conference/usenixsecurity{yy}/technical-sessions"


def _ndss(year: int) -> str:
    return f"https://www.ndss-symposium.org/ndss{year}/accepted-papers/"


def _dblp_acm_resolve(dblp_url: str, year: int) -> str | None:
    """Resolve proceedings metadata through permitted DBLP HTML, without warm-up probes."""
    result = FETCHER.fetch(dblp_url, year=year)
    if result.outcome != "ok":
        raise AcquisitionError(result)
    dois = re.findall(r"https://doi\.org/(10\.1145/\d+)", result.body)
    if not dois:
        return None
    return f"https://dl.acm.org/doi/proceedings/{min(set(dois), key=len)}"


def _ccs_resolve(year: int) -> str | None:
    return _dblp_acm_resolve(f"https://dblp.org/db/conf/ccs/ccs{year}.html", year)


def _ccs_content_urls(year: int) -> list[str]:
    return [
        f"https://www.sigsac.org/ccs/CCS{year}/accepted-papers/",
        f"https://www.sigsac.org/ccs/CCS{year}/program/",
        f"https://dblp.org/db/conf/ccs/ccs{year}.html",
    ]


def _asiaccs_resolve(year: int) -> str | None:
    dblp_url = (
        f"https://dblp.org/db/conf/asiaccs/asiaccs{year}.html"
        if year >= 2021
        else f"https://dblp.org/db/conf/ccs/asiaccs{year}.html"
    )
    return _dblp_acm_resolve(dblp_url, year)


def _raid_resolve(year: int) -> str | None:
    return _dblp_acm_resolve(f"https://dblp.org/db/conf/raid/raid{year}.html", year)


def _acsac(year: int) -> str:
    return f"https://www.acsac.org/{year}/"


def _iacr_crypto(year: int) -> str:
    return f"https://crypto.iacr.org/{year}/"


def _iacr_eurocrypt(year: int) -> str:
    return f"https://eurocrypt.iacr.org/{year}/"


def _iacr_asiacrypt(year: int) -> str:
    return f"https://asiacrypt.iacr.org/{year}/"


def _iacr_tcc(year: int) -> str:
    return f"https://tcc.iacr.org/{year}/"


def _iacr_ches(year: int) -> str:
    return f"https://ches.iacr.org/{year}/"


def _pets(year: int) -> str:
    return f"https://petsymposium.org/{year}/"


def _euros_p(year: int) -> str:
    return f"https://www.ieee-security.org/TC/EuroSP{year}/"


# --- Industry URL generators and resolvers ---


def _defcon_resolve(year: int) -> str | None:
    """Discover a presentation directory only when source policy permits access."""
    n = year - 1992
    root = f"https://media.defcon.org/DEF%20CON%20{n}/"
    result = FETCHER.fetch(root, year=year)
    if result.outcome != "ok":
        raise AcquisitionError(result)
    for href in re.findall(r'href="([^"]*)"', result.body):
        if "presentations" in href.lower():
            return urljoin(result.effective_url, href)
    return None


def _blackhat(region: str, year: int) -> str:
    yy = str(year)[2:]
    slug = _BH_SLUGS[region]
    return f"https://www.blackhat.com/{slug}-{yy}/briefings/schedule/"


def _recon(year: int) -> str:
    return f"https://recon.cx/{year}/sessions.html"


def _troopers(year: int) -> str:
    yy = str(year)[2:]
    return f"https://troopers.de/troopers{yy}/"


def _hardwear(year: int) -> str:
    return f"https://hardwear.io/netherlands-{year}/talks/"


def _offensivecon(year: int) -> str:
    return f"https://www.offensivecon.org/agenda/{year}.html"


# --- Conference registries ---

ACADEMIC_CONFS: list[Conf] = [
    Conf("USENIX Security", "usenix-security", _usenix),
    Conf("NDSS", "ndss", _ndss),
    Conf("IEEE S&P", "ieee-sp", lambda y: f"https://www.ieee-security.org/TC/SP{y}/program.html"),
    Conf(
        "CCS",
        "ccs",
        _ccs_resolve,
        resolver=_ccs_resolve,
        content_urls=_ccs_content_urls,
    ),
    Conf("ASIACCS", "asiaccs", _asiaccs_resolve, resolver=_asiaccs_resolve),
    Conf("ACSAC", "acsac", _acsac),
    Conf("IACR Crypto", "iacr-crypto", _iacr_crypto),
    Conf("IACR Eurocrypt", "iacr-eurocrypt", _iacr_eurocrypt),
    Conf("IACR Asiacrypt", "iacr-asiacrypt", _iacr_asiacrypt),
    Conf("IACR TCC", "iacr-tcc", _iacr_tcc),
    Conf("IACR CHES", "iacr-ches", _iacr_ches),
    Conf("RAID", "raid", _raid_resolve, resolver=_raid_resolve),
    Conf("PETS", "pets", _pets),
    Conf("EuroS&P", "eurosp", _euros_p),
]

INDUSTRY_CONFS: list[Conf] = [
    Conf("DEF CON", "defcon", _defcon_resolve, resolver=_defcon_resolve),
    Conf("Black Hat USA", "blackhat-usa", lambda y: _blackhat("usa", y), bh_slug="us"),
    Conf("Black Hat EU", "blackhat-eu", lambda y: _blackhat("europe", y), bh_slug="eu"),
    Conf("Black Hat Asia", "blackhat-asia", lambda y: _blackhat("asia", y), bh_slug="asia"),
    Conf("REcon", "recon", _recon),
    Conf("Troopers", "troopers", _troopers),
    Conf("hardwear.io", "hardwear", _hardwear),
    Conf("OffensiveCon", "offensivecon", _offensivecon),
]

ALIASES = {
    "sp": "ieee-sp",
    "s-p": "ieee-sp",
    "ieee-s-p": "ieee-sp",
    "s&p": "ieee-sp",
    "ieee-sp": "ieee-sp",
    "ieee-s&p": "ieee-sp",
    "usenix": "usenix-security",
    "usenix-security": "usenix-security",
    "usenixsecurity": "usenix-security",
    "eurosp": "eurosp",
    "euro-s-p": "eurosp",
    "euro-s&p": "eurosp",
    "asia-ccs": "asiaccs",
    "asiaccs": "asiaccs",
    "blackhat": "blackhat-usa",
    "black-hat": "blackhat-usa",
    "bhusa": "blackhat-usa",
    "bheu": "blackhat-eu",
    "bhasia": "blackhat-asia",
    "def-con": "defcon",
    "defcon": "defcon",
}


class AcquisitionError(Exception):
    def __init__(self, result: FetchResult):
        self.result = result
        super().__init__(f"{result.outcome}: {result.effective_url or result.url}: {result.reason}")


def _slug(value: str) -> str:
    value = value.lower().strip().replace("&", "-")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def select_confs(confs: list[Conf], conference: str | None, *, strict: bool = True) -> list[Conf]:
    if not conference:
        return confs
    wanted = ALIASES.get(_slug(conference), _slug(conference))
    matches = [
        c
        for c in confs
        if wanted in {_slug(c.abbrev), _slug(c.name), c.abbrev, ALIASES.get(_slug(c.abbrev), "")}
    ]
    if not matches and strict:
        known = ", ".join(sorted(c.abbrev for c in confs))
        raise SystemExit(f"Unknown conference '{conference}'. Known: {known}")
    return matches


def resolve_url(conf: Conf, year: int) -> str | None:
    if conf.resolver:
        return conf.resolver(year)
    return conf.url_fn(year)


async def discover(confs: list[Conf], start: int, end: int) -> dict[str, list[tuple[int, str]]]:
    results: dict[str, list[tuple[int, str]]] = {}
    for conf in confs:
        entries = []
        for year in range(start, end + 1):
            result = await asyncio.to_thread(crawl_raw_page, conf, year)
            if result.outcome == "ok":
                entries.append((year, result.effective_url))
            else:
                print(f"{conf.abbrev} {year}: {result.outcome}: {result.reason}", file=sys.stderr)
        results[conf.abbrev] = entries
    return results


def print_discovered(results: dict[str, list[tuple[int, str]]]) -> None:
    for abbrev, entries in sorted(results.items()):
        print(f"## {abbrev}")
        for year, url in sorted(entries, reverse=True):
            print(f"- {year}: {url}")
        if not entries:
            print("- no live URLs found")


def write_md(path: Path, title: str, results: dict[str, list[tuple[int, str]]]) -> None:
    lines = [
        f"# {title}",
        "",
        "_Auto-generated by `maintainer/crawl_conferences.py`. Do not edit manually._",
        "",
    ]
    for abbrev, entries in sorted(results.items()):
        if not entries:
            continue
        lines += [f"## {abbrev}", ""]
        for year, url in sorted(entries, reverse=True):
            lines.append(f"- [{year}]({url})")
        lines.append("")
    path.write_text("\n".join(lines))
    total = sum(len(v) for v in results.values())
    print(f"Wrote {path} ({total} URLs across {len(results)} conferences)")


def candidate_content_urls(conf: Conf, year: int) -> list[str]:
    """Return native candidates without eagerly invoking publisher resolvers."""
    if conf.content_urls:
        return list(dict.fromkeys(conf.content_urls(year)))
    if conf.bh_slug:
        return [_BH_SESSIONS_URL.format(slug=f"{conf.bh_slug}-{str(year)[2:]}")]
    url = None if conf.resolver else conf.url_fn(year)
    return [url] if url else []


def _json_has_records(body: str) -> bool:
    try:
        value = json.loads(body)
    except ValueError:
        return False
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            if isinstance(item.get("title"), str) and item["title"].strip():
                return True
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
    return False


def _asset_links(base: str, body: str, extension: str) -> list[str]:
    pattern = r'["\']([^"\']+\.' + extension + r')["\']'
    links = []
    for match in re.findall(pattern, body, re.I):
        link = urljoin(base, match)
        try:
            same_origin = origin(link) == origin(base)
        except ValueError:
            same_origin = False  # Non-HTTP and credential-bearing assets are forbidden.
        if same_origin and link not in links:
            links.append(link)
    return links


def _chunk_json_links(result: FetchResult) -> list[str]:
    if "javascript" in result.content_type or result.content_type == "text/plain":
        return _asset_links(result.effective_url, result.body, "json")
    return []


def _append_linked_data(result: FetchResult) -> FetchResult:
    """Follow at most eight unique same-origin program assets, including redirects."""
    base = result.effective_url
    assets = _asset_links(base, result.body, "json")
    chunks = [
        link for link in _asset_links(base, result.body, "js") if "_next/static/chunks/" in link
    ]
    chunks.sort(key=lambda link: "app/" not in link)
    seen = set()
    sections = [result.body]
    useful = False
    outcomes = []
    queue = assets + chunks
    while queue and len(seen) < 8:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        fetched = FETCHER.fetch(url, allowed_origin=origin(base))
        outcomes.append(
            {
                "url": url,
                "effective_url": fetched.effective_url,
                "outcome": fetched.outcome,
                "reason": fetched.reason,
                "status": fetched.status,
                "content_type": fetched.content_type,
                "retry_after": fetched.retry_after,
            }
        )
        if fetched.outcome != "ok":
            if fetched.outcome in STOP_OUTCOMES:
                return replace(
                    result,
                    outcome=fetched.outcome,
                    reason=f"Linked asset {url}: {fetched.reason}",
                    assets=tuple(outcomes),
                )
            continue
        if url.endswith(".js"):
            queue = _chunk_json_links(fetched) + queue
        elif "json" in fetched.content_type and _json_has_records(fetched.body):
            sections.append(
                f"\n\n<!-- RAW LINKED ASSET: {fetched.effective_url} -->\n{fetched.body}"
            )
            useful = True
    combined = replace(result, body="".join(sections), assets=tuple(outcomes))
    if useful:
        return combined
    checked = validate_content(result)
    return replace(combined, outcome=checked.outcome, reason=checked.reason)


def crawl_url(url: str, year: int | None = None) -> FetchResult:
    """Use the same policy, edition and linked-data path for all CLI URL sources."""
    result = FETCHER.fetch(url, year=year)
    checked = validate_content(result, year=year)
    if checked.outcome not in {"ok", "shell"}:
        return checked
    if "html" in result.content_type:
        return _append_linked_data(result)
    if "json" in result.content_type and not _json_has_records(result.body):
        return replace(checked, outcome="empty-data", reason="No program records in valid JSON")
    return checked


def crawl_raw_page(conf: Conf, year: int) -> FetchResult:
    last = FetchResult("", outcome="no-source", reason="No supported candidate for this edition")
    for url in candidate_content_urls(conf, year):
        last = crawl_url(url, year)
        if last.outcome == "ok" or last.outcome in STOP_OUTCOMES:
            return last
    if conf.resolver:
        try:
            resolved = resolve_url(conf, year)
        except AcquisitionError as exc:
            return exc.result
        if resolved:
            return crawl_url(resolved, year)
    return last


def print_result(label: str, year: int | None, result: FetchResult, output_format: str) -> None:
    if output_format == "json":
        payload = asdict(result)
        payload.pop("headers")
        payload.update(conference=label, year=year, raw_page=payload.pop("body"))
        print(json.dumps(payload, indent=2))
    elif result.outcome == "ok":
        print(result.body)
    else:
        print(
            f"{result.outcome}: {result.effective_url or result.url}: {result.reason}",
            file=sys.stderr,
        )


def run_content(args: argparse.Namespace, confs: list[Conf]) -> None:
    if args.url:
        result = crawl_url(args.url, args.year)
        print_result(args.conference or "url", args.year, result, args.format)
        if result.outcome != "ok":
            raise SystemExit(1)
        return
    if not args.conference or not args.year:
        raise SystemExit("--crawl-content requires --url or --conference and --year")
    failed = False
    for conf in confs:
        result = crawl_raw_page(conf, args.year)
        print_result(conf.abbrev, args.year, result, args.format)
        failed |= result.outcome != "ok"
    if failed:
        raise SystemExit(1)


async def run(args: argparse.Namespace) -> None:
    registries = [(args.academic, ACADEMIC_CONFS), (args.industry, INDUSTRY_CONFS)]
    confs = [
        conf
        for enabled, registry in registries
        if enabled
        for conf in select_confs(registry, args.conference, strict=False)
    ]
    if args.conference and not confs and not args.url:
        raise SystemExit(f"Unknown conference '{args.conference}'")
    if args.crawl_content:
        run_content(args, confs)
        return
    results = await discover(confs, args.start_year, args.end_year)
    if args.conference:
        print_discovered(results)
        return
    REFS_DIR.mkdir(parents=True, exist_ok=True)
    for mode, registry in (("academic", ACADEMIC_CONFS), ("industry", INDUSTRY_CONFS)):
        subset = {c.abbrev: results[c.abbrev] for c in registry if c.abbrev in results}
        if subset:
            write_md(REFS_DIR / f"{mode}.md", f"{mode.title()} Conference Program URLs", subset)


def main() -> None:
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--academic", action="store_true", help="Use academic conferences")
    parser.add_argument("--industry", action="store_true", help="Use industry conferences")
    parser.add_argument(
        "--conference", help="Limit to one conference acronym/slug, e.g. ccs, usenix, defcon"
    )
    parser.add_argument("--url", help="Explicit page URL to fetch with --crawl-content")
    parser.add_argument("--start-year", type=int, default=2020, metavar="YYYY")
    parser.add_argument("--end-year", type=int, default=CURRENT_YEAR, metavar="YYYY")
    parser.add_argument(
        "--crawl-content",
        action="store_true",
        help="Fetch one resolved conference page and print the raw page",
    )
    parser.add_argument(
        "--year", type=int, metavar="YYYY", help="Conference year for --crawl-content"
    )
    parser.add_argument("--format", choices=["raw", "json"], default="raw")
    args = parser.parse_args()

    if not args.academic and not args.industry:
        args.academic = args.industry = True

    asyncio.run(run(args))


if __name__ == "__main__":
    main()
