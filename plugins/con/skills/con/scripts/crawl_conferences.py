# /// script
# requires-python = ">=3.13"
# dependencies = ["httpx>=0.27", "curl_cffi>=0.7"]
# ///
"""Discover live conference program URLs and write references/academic.md and references/industry.md.

Run annually after each conference season, or when a new year is missing:

    uv run scripts/crawl_conferences.py
    uv run scripts/crawl_conferences.py --academic --start-year 2025 --end-year 2025
    uv run scripts/crawl_conferences.py --industry
"""

from __future__ import annotations

import argparse
import asyncio
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

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


# --- Academic URL generators ---


def _usenix(year: int) -> str:
    yy = str(year)[2:]
    return f"https://www.usenix.org/conference/usenixsecurity{yy}/technical-sessions"


def _ndss(year: int) -> str:
    return f"https://www.ndss-symposium.org/ndss{year}/accepted-papers/"


def _ccs(year: int) -> str:
    return f"https://www.sigsac.org/ccs/CCS{year}/accepted-papers.html"


def _asiaccs_dblp_url(year: int) -> str:
    # DBLP moved AsiaCCS from conf/ccs/ to conf/asiaccs/ after 2020
    if year >= 2021:
        return f"https://dblp.org/db/conf/asiaccs/asiaccs{year}.html"
    return f"https://dblp.org/db/conf/ccs/asiaccs{year}.html"


def _asiaccs_resolve(year: int) -> str | None:
    """Discover AsiaCCS proceedings URL via a multi-step pipeline.

    1. Fetch DBLP year page → extract top-level proceedings DOI (shortest 10.1145/N)
    2. Try ACM DL frontmatter PDF via curl_cffi → extract text with pdftotext
       (ACM DL blocks most programmatic access; this step is best-effort)
    3. Return the canonical ACM proceedings URL regardless of step 2 outcome.

    DBLP is the authoritative, open source. ACM DL blocks curl_cffi as of 2025,
    so the frontmatter PDF step will typically fail gracefully.
    """
    import subprocess
    import tempfile

    from curl_cffi import requests as cf

    dblp_url = _asiaccs_dblp_url(year)
    r = httpx.get(dblp_url, headers={"User-Agent": "Mozilla/5.0"},
                  timeout=10, follow_redirects=True)
    if r.status_code >= 400:
        return None

    # Extract all 10.1145/NNNNNNN DOIs; the proceedings DOI is the shortest
    # (paper DOIs append a suffix: 10.1145/NNNNNNN.MMMMMMM)
    dois = re.findall(r'https://doi\.org/(10\.1145/\d+)', r.text)
    if not dois:
        return None
    procs_doi = min(set(dois), key=len)
    procs_url = f"https://dl.acm.org/doi/proceedings/{procs_doi}"

    # Step 2: attempt frontmatter PDF (best-effort — ACM DL blocks most bots)
    fm_url = f"https://dl.acm.org/action/showFmPdf?doi={procs_doi.replace('/', '%2F')}"
    try:
        session = cf.Session(impersonate="chrome124")
        session.get("https://dl.acm.org/", timeout=10)
        pdf_resp = session.get(fm_url, timeout=20)
        ct = pdf_resp.headers.get("content-type", "")
        if pdf_resp.status_code == 200 and "pdf" in ct.lower():
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(pdf_resp.content)
                pdf_path = f.name
            result = subprocess.run(
                ["pdftotext", pdf_path, "-"], capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                print(f"    [asiaccs {year}] extracted {len(result.stdout):,} chars from frontmatter")
    except Exception:
        pass  # ACM DL access silently skipped

    return procs_url


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


def _raid(year: int) -> str:
    return f"https://raid{year}.github.io/"


def _pets(year: int) -> str:
    return f"https://petsymposium.org/{year}/"


def _euros_p(year: int) -> str:
    return f"https://www.ieee-security.org/TC/EuroSP{year}/"


# --- Industry URL generators and resolvers ---


def _defcon_resolve(year: int) -> str | None:
    """Fetch the DEF CON edition root, find the presentations subdirectory link.

    DC28 (2020 "Safe Mode") used non-standard directory naming, so we discover
    the presentations href from the listing rather than constructing it.
    media.defcon.org requires curl_cffi (HARICA cert, incompatible with httpx).
    """
    from curl_cffi import requests as cf

    n = year - 1993 + 1
    root = f"https://media.defcon.org/DEF%20CON%20{n}/"
    try:
        r = cf.get(root, impersonate="chrome124", timeout=15)
        if r.status_code >= 400:
            return None
        # Find href containing "presentations" (case-insensitive)
        hrefs = re.findall(r'href="([^"]*)"', r.text)
        for href in hrefs:
            if "presentations" in href.lower():
                # href is relative (e.g. "DEF%20CON%2032%20presentations/")
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
    Conf("CCS", "ccs", _ccs),
    Conf("ASIACCS", "asiaccs", _asiaccs_resolve, resolver=_asiaccs_resolve),
    Conf("ACSAC", "acsac", _acsac),
    Conf("IACR Crypto", "iacr-crypto", _iacr_crypto),
    Conf("IACR Eurocrypt", "iacr-eurocrypt", _iacr_eurocrypt),
    Conf("IACR Asiacrypt", "iacr-asiacrypt", _iacr_asiacrypt),
    Conf("IACR TCC", "iacr-tcc", _iacr_tcc),
    Conf("IACR CHES", "iacr-ches", _iacr_ches),
    Conf("RAID", "raid", _raid),
    Conf("PETS", "pets", _pets),
    Conf("EuroS&P", "eurosp", _euros_p),
]

INDUSTRY_CONFS: list[Conf] = [
    Conf("DEF CON", "defcon", _defcon_resolve, resolver=_defcon_resolve),
    Conf("Black Hat USA", "blackhat-usa", lambda y: _blackhat("usa", y), bh_slug="us"),
    Conf("Black Hat EU", "blackhat-eu", lambda y: _blackhat("europe", y), bh_slug="eu"),
    Conf(
        "Black Hat Asia",
        "blackhat-asia",
        lambda y: _blackhat("asia", y),
        bh_slug="asia",
    ),
    Conf("REcon", "recon", _recon),
    Conf("Troopers", "troopers", _troopers),
    Conf("hardwear.io", "hardwear", _hardwear),
    Conf("OffensiveCon", "offensivecon", _offensivecon),
]


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


async def discover(
    confs: list[Conf], start: int, end: int
) -> dict[str, list[tuple[int, str]]]:
    # Cap concurrent resolver calls per conference to avoid triggering rate limits
    # on servers like media.defcon.org that drop connections under parallel load.
    resolver_sem = asyncio.Semaphore(3)

    async def _run_resolver(fn: object, year: int) -> str | None:
        async with resolver_sem:
            return await asyncio.to_thread(fn, year)

    async with httpx.AsyncClient() as client:
        results: dict[str, list[tuple[int, str]]] = {}
        for conf in confs:
            years = list(range(start, end + 1))

            if conf.resolver:
                resolved: list[str | None] = await asyncio.gather(
                    *[_run_resolver(conf.resolver, y) for y in years]
                )
                results[conf.abbrev] = [
                    (y, url) for y, url in zip(years, resolved) if url
                ]
            elif conf.bh_slug:
                # Sequential + delay: blackhat.com rate-limits parallel curl_cffi threads.
                bh_live: list[bool] = []
                for y in years:
                    bh_live.append(
                        await asyncio.to_thread(_is_live_bh, conf.bh_slug, y)
                    )
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


async def run(args: argparse.Namespace) -> None:
    REFS_DIR.mkdir(parents=True, exist_ok=True)

    if args.academic:
        print("Checking academic conference URLs...")
        r = await discover(ACADEMIC_CONFS, args.start_year, args.end_year)
        write_md(REFS_DIR / "academic.md", "Academic Conference Program URLs", r)

    if args.industry:
        print("Checking industry conference URLs...")
        r = await discover(INDUSTRY_CONFS, args.start_year, args.end_year)
        write_md(REFS_DIR / "industry.md", "Industry Conference Talk URLs", r)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--academic", action="store_true", help="Refresh academic URLs")
    parser.add_argument("--industry", action="store_true", help="Refresh industry URLs")
    parser.add_argument("--start-year", type=int, default=2020, metavar="YYYY")
    parser.add_argument("--end-year", type=int, default=CURRENT_YEAR, metavar="YYYY")
    args = parser.parse_args()

    if not args.academic and not args.industry:
        args.academic = args.industry = True

    asyncio.run(run(args))


if __name__ == "__main__":
    main()
