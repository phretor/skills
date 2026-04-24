# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx>=0.27", "curl_cffi>=0.7"]
# ///
"""Discover conference URLs and fetch raw conference pages.

Refresh URL references annually:

    uv run scripts/crawl_conferences.py
    uv run scripts/crawl_conferences.py --academic --start-year 2025 --end-year 2025
    uv run scripts/crawl_conferences.py --industry

Crawl one conference page and return the raw page content for agent-side reasoning.
Use --url for a page discovered by web search, or --conference/--year to use
built-in best-effort URL candidates and proceedings fallbacks:

    uv run scripts/crawl_conferences.py --crawl-content \
      --url https://www.sigsac.org/ccs/CCS2025/accepted-papers/
    uv run scripts/crawl_conferences.py --crawl-content --academic \
      --conference ccs --year 2025 --format json
    uv run scripts/crawl_conferences.py --crawl-content --industry \
      --conference defcon --year 2025 --format json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import signal
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

import httpx

REFS_DIR = Path(__file__).parent.parent / "references"
CURRENT_YEAR = date.today().year

_BH_SESSIONS_URL = "https://blackhat.com/{slug}/briefings/schedule/sessions.json"
_BH_SLUGS = {"usa": "us", "europe": "eu", "asia": "asia"}


@dataclass(frozen=True)
class Conf:
    name: str
    abbrev: str
    # url_fn(year) -> str: human-facing URL stored in references.
    # resolver(year) -> str | None: when set, replaces url_fn + liveness check —
    #   returns the discovered URL on success, None if the conference has no data
    #   for that year. Runs in asyncio.to_thread (must be sync).
    url_fn: object
    bh_slug: str = ""  # non-empty → BH sessions.json probe via curl_cffi
    resolver: object = None  # callable(year: int) -> str | None
    sequential: bool = False  # run resolver one year at a time with delay
    content_urls: object = None  # callable(year: int) -> list[str], tried before resolver for crawling


# --- Academic URL generators ---


def _usenix(year: int) -> str:
    yy = str(year)[2:]
    return f"https://www.usenix.org/conference/usenixsecurity{yy}/technical-sessions"


def _ndss(year: int) -> str:
    return f"https://www.ndss-symposium.org/ndss{year}/accepted-papers/"


def _dblp_acm_resolve(dblp_url: str, conf_abbrev: str, year: int) -> str | None:
    """Resolve ACM proceedings URL from DBLP and best-effort probe frontmatter."""
    import subprocess
    import tempfile

    from curl_cffi import requests as cf

    try:
        r = httpx.get(
            dblp_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
            follow_redirects=True,
        )
    except httpx.HTTPError:
        return None

    if r.status_code >= 400:
        return None

    dois = re.findall(r"https://doi\.org/(10\.1145/\d+)", r.text)
    if not dois:
        return None
    procs_doi = min(set(dois), key=len)
    procs_url = f"https://dl.acm.org/doi/proceedings/{procs_doi}"

    fm_url = f"https://dl.acm.org/action/showFmPdf?doi={procs_doi.replace('/', '%2F')}"
    try:
        session = cf.Session(impersonate="chrome124")
        session.get("https://dl.acm.org/", timeout=10)
        pdf_resp = session.get(fm_url, timeout=20)
        if pdf_resp.status_code == 200 and "pdf" in pdf_resp.headers.get(
            "content-type", ""
        ).lower():
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(pdf_resp.content)
                pdf_path = f.name
            result = subprocess.run(
                ["pdftotext", pdf_path, "-"], capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                print(
                    f"    [{conf_abbrev} {year}] extracted "
                    f"{len(result.stdout):,} chars from frontmatter"
                )
    except Exception:
        pass

    return procs_url


def _ccs_resolve(year: int) -> str | None:
    return _dblp_acm_resolve(f"https://dblp.org/db/conf/ccs/ccs{year}.html", "ccs", year)


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
    return _dblp_acm_resolve(dblp_url, "asiaccs", year)


def _raid_resolve(year: int) -> str | None:
    return _dblp_acm_resolve(f"https://dblp.org/db/conf/raid/raid{year}.html", "raid", year)


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
    """Fetch DEF CON edition root and discover the presentations directory."""
    from curl_cffi import requests as cf

    n = year - 1993 + 1
    root = f"https://media.defcon.org/DEF%20CON%20{n}/"
    try:
        r = cf.get(root, impersonate="chrome124", timeout=15)
        if r.status_code >= 400:
            return None
        hrefs = re.findall(r'href="([^"]*)"', r.text)
        for href in hrefs:
            if "presentations" in href.lower():
                return root + href if not href.startswith("http") else href
        return None
    except Exception:
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
    Conf("CCS", "ccs", _ccs_resolve, resolver=_ccs_resolve, sequential=True, content_urls=_ccs_content_urls),
    Conf("ASIACCS", "asiaccs", _asiaccs_resolve, resolver=_asiaccs_resolve, sequential=True),
    Conf("ACSAC", "acsac", _acsac),
    Conf("IACR Crypto", "iacr-crypto", _iacr_crypto),
    Conf("IACR Eurocrypt", "iacr-eurocrypt", _iacr_eurocrypt),
    Conf("IACR Asiacrypt", "iacr-asiacrypt", _iacr_asiacrypt),
    Conf("IACR TCC", "iacr-tcc", _iacr_tcc),
    Conf("IACR CHES", "iacr-ches", _iacr_ches),
    Conf("RAID", "raid", _raid_resolve, resolver=_raid_resolve, sequential=True),
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
    "sp": "s-p",
    "s&p": "s-p",
    "ieee-sp": "s-p",
    "ieee-s&p": "s-p",
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


async def _is_live(client: httpx.AsyncClient, url: str) -> bool:
    try:
        r = await client.head(url, follow_redirects=True, timeout=10.0)
        return r.status_code < 400
    except Exception:
        return False


def _is_live_bh(slug: str, year: int) -> bool:
    """Probe Black Hat sessions.json using curl_cffi Chrome TLS impersonation."""
    from curl_cffi import requests as cf

    yy = str(year)[2:]
    url = _BH_SESSIONS_URL.format(slug=f"{slug}-{yy}")
    try:
        resp = cf.get(url, impersonate="chrome124", timeout=15)
        return resp.status_code == 200 and bool(resp.json().get("sessions"))
    except Exception:
        return False


def _slug(value: str) -> str:
    value = value.lower().strip().replace("&", "-p")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def select_confs(
    confs: list[Conf], conference: str | None, *, strict: bool = True
) -> list[Conf]:
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
    resolver_sem = asyncio.Semaphore(3)

    async def _run_resolver(fn: object, year: int) -> str | None:
        async with resolver_sem:
            return await asyncio.to_thread(fn, year)

    async with httpx.AsyncClient() as client:
        results: dict[str, list[tuple[int, str]]] = {}
        for conf in confs:
            years = list(range(start, end + 1))

            if conf.resolver and conf.sequential:
                seq_results: list[tuple[int, str]] = []
                for y in years:
                    url = await asyncio.to_thread(conf.resolver, y)
                    if url:
                        seq_results.append((y, url))
                    await asyncio.sleep(1.0)
                results[conf.abbrev] = seq_results
            elif conf.resolver:
                resolved: list[str | None] = await asyncio.gather(
                    *[_run_resolver(conf.resolver, y) for y in years]
                )
                results[conf.abbrev] = [(y, url) for y, url in zip(years, resolved) if url]
            elif conf.bh_slug:
                bh_live: list[bool] = []
                for y in years:
                    bh_live.append(await asyncio.to_thread(_is_live_bh, conf.bh_slug, y))
                    await asyncio.sleep(0.5)
                results[conf.abbrev] = [
                    (y, conf.url_fn(y)) for y, ok in zip(years, bh_live) if ok
                ]
            else:
                checks = await asyncio.gather(
                    *[_is_live(client, conf.url_fn(y)) for y in years]
                )
                results[conf.abbrev] = [
                    (y, conf.url_fn(y)) for y, ok in zip(years, checks) if ok
                ]

            found = len(results[conf.abbrev])
            print(f"  {conf.name}: {found}/{len(years)} URLs live")
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
        "_Auto-generated by `scripts/crawl_conferences.py`. Do not edit manually._",
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


def fetch_text(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = httpx.get(url, headers=headers, timeout=25, follow_redirects=True)
        if r.status_code < 400 and r.text.strip():
            return r.text
    except Exception:
        pass

    try:
        from curl_cffi import requests as cf

        r = cf.get(url, impersonate="chrome124", timeout=25)
        if r.status_code < 400:
            return r.text
    except Exception:
        pass
    return ""


def candidate_content_urls(conf: Conf, year: int) -> list[str]:
    urls: list[str] = []
    if conf.content_urls:
        urls.extend(conf.content_urls(year))
    resolved = resolve_url(conf, year)
    if resolved:
        urls.append(resolved)
    # Preserve order while removing duplicates.
    return list(dict.fromkeys(urls))


def _append_linked_data(url: str, raw_page: str) -> str:
    """Append raw linked JSON assets referenced by JS-rendered conference pages.

    This is not filtering or interpretation. It preserves the fetched HTML and adds
    raw assets that the page itself loads client-side (e.g., accepted-papers.json).
    """
    asset_urls: list[str] = []
    patterns = [
        r'["\']([^"\']*accepted-papers\.json)["\']',
        r'["\']([^"\']*program[^"\']*\.json)["\']',
        r'["\']([^"\']*papers[^"\']*\.json)["\']',
        r'fetch\(["\']([^"\']+)["\']\)',
    ]
    for pattern in patterns:
        for match in re.findall(pattern, raw_page, flags=re.I):
            if match.endswith(".json"):
                asset_urls.append(urljoin(url, match))

    # Next.js pages often hide fetch URLs in JS chunks. Fetch same-origin chunks
    # and scan them for JSON assets, still without filtering content.
    for chunk in re.findall(r'(?:src=|["\'])([^"\']*_next/static/chunks/[^"\']+\.js)', raw_page):
        chunk_url = urljoin(url, chunk)
        chunk_body = fetch_text(chunk_url)
        for match in re.findall(r'["\']([^"\']+\.json)["\']', chunk_body, flags=re.I):
            asset_urls.append(urljoin(url, match))

    sections = [raw_page]
    for asset_url in dict.fromkeys(asset_urls):
        body = fetch_text(asset_url)
        if body:
            sections.append(f"\n\n<!-- RAW LINKED ASSET: {asset_url} -->\n{body}")
    return "".join(sections)


def crawl_raw_page(conf: Conf, year: int) -> tuple[str, str]:
    for url in candidate_content_urls(conf, year):
        raw_page = fetch_text(url)
        if raw_page:
            return url, _append_linked_data(url, raw_page)
    return "", ""


def print_raw_page(conf: Conf, year: int, url: str, raw_page: str, output_format: str) -> None:
    if output_format == "json":
        print(
            json.dumps(
                {
                    "conference": conf.abbrev,
                    "year": year,
                    "url": url,
                    "raw_page": raw_page,
                },
                indent=2,
            )
        )
        return

    print(raw_page)


def print_raw_url(label: str, year: int | None, url: str, raw_page: str, output_format: str) -> None:
    if output_format == "json":
        print(
            json.dumps(
                {
                    "conference": label,
                    "year": year,
                    "url": url,
                    "raw_page": raw_page,
                },
                indent=2,
            )
        )
        return
    print(raw_page)


async def run(args: argparse.Namespace) -> None:
    REFS_DIR.mkdir(parents=True, exist_ok=True)
    confs: list[Conf] = []
    if args.crawl_content:
        if args.academic:
            confs.extend(select_confs(ACADEMIC_CONFS, args.conference, strict=False))
        if args.industry:
            confs.extend(select_confs(INDUSTRY_CONFS, args.conference, strict=False))
    else:
        if args.academic:
            confs.extend(select_confs(ACADEMIC_CONFS, args.conference))
        if args.industry:
            confs.extend(select_confs(INDUSTRY_CONFS, args.conference))

    if args.crawl_content:
        if args.url:
            raw_page = fetch_text(args.url)
            used_url = args.url
            if not raw_page and args.conference and args.year and confs:
                used_url, raw_page = crawl_raw_page(confs[0], args.year)
            if not raw_page:
                raise SystemExit(f"Could not fetch URL: {args.url}")
            print_raw_url(args.conference or "url", args.year, used_url, raw_page, args.format)
            return
        if not args.conference:
            raise SystemExit("--crawl-content requires --conference or --url")
        if not args.year:
            raise SystemExit("--crawl-content with --conference requires --year")
        if not confs:
            raise SystemExit(f"Unknown conference '{args.conference}'")
        for conf in confs:
            url, raw_page = crawl_raw_page(conf, args.year)
            if not raw_page:
                raise SystemExit(f"Could not fetch page for {conf.abbrev} {args.year}")
            print_raw_page(conf, args.year, url, raw_page, args.format)
        return

    if args.academic:
        print("Checking academic conference URLs...")
        r = await discover(select_confs(ACADEMIC_CONFS, args.conference), args.start_year, args.end_year)
        if args.conference:
            print_discovered(r)
        else:
            write_md(REFS_DIR / "academic.md", "Academic Conference Program URLs", r)

    if args.industry:
        print("Checking industry conference URLs...")
        r = await discover(select_confs(INDUSTRY_CONFS, args.conference), args.start_year, args.end_year)
        if args.conference:
            print_discovered(r)
        else:
            write_md(REFS_DIR / "industry.md", "Industry Conference Talk URLs", r)


def main() -> None:
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--academic", action="store_true", help="Use academic conferences")
    parser.add_argument("--industry", action="store_true", help="Use industry conferences")
    parser.add_argument("--conference", help="Limit to one conference acronym/slug, e.g. ccs, usenix, defcon")
    parser.add_argument("--url", help="Explicit page URL to fetch with --crawl-content")
    parser.add_argument("--start-year", type=int, default=2020, metavar="YYYY")
    parser.add_argument("--end-year", type=int, default=CURRENT_YEAR, metavar="YYYY")
    parser.add_argument("--crawl-content", action="store_true", help="Fetch one resolved conference page and print the raw page")
    parser.add_argument("--year", type=int, metavar="YYYY", help="Conference year for --crawl-content")
    parser.add_argument("--format", choices=["raw", "json"], default="raw")
    args = parser.parse_args()

    if not args.academic and not args.industry:
        args.academic = args.industry = True

    asyncio.run(run(args))


if __name__ == "__main__":
    main()
