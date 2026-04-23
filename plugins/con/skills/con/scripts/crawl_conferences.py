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
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import httpx

REFS_DIR = Path(__file__).parent.parent / "references"
CURRENT_YEAR = date.today().year

# Black Hat sessions.json — requires Chrome TLS impersonation via curl_cffi.
# Used as the existence probe; the stored URL is the human-facing schedule page.
_BH_SESSIONS_URL = "https://blackhat.com/{slug}/briefings/schedule/sessions.json"
_BH_SLUGS = {"usa": "us", "europe": "eu", "asia": "asia"}


@dataclass(frozen=True)
class Conf:
    name: str
    abbrev: str
    url_fn: object       # (year: int) -> str  — human-facing URL stored in references
    bh_slug: str = ""   # non-empty for Black Hat conferences; triggers curl_cffi check


# --- Academic URL generators ---


def _usenix(year: int) -> str:
    yy = str(year)[2:]
    return f"https://www.usenix.org/conference/usenixsecurity{yy}/technical-sessions"


def _ndss(year: int) -> str:
    return f"https://www.ndss-symposium.org/{year}-programme/"


def _ccs(year: int) -> str:
    return f"https://dl.acm.org/conference/ccs/proceedings-{year}"


def _asiaccs(year: int) -> str:
    return f"https://dl.acm.org/conference/asiaccs/proceedings-{year}"


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


# --- Industry URL generators ---


def _defcon(year: int) -> str:
    n = year - 1993 + 1  # DEF CON 1 = 1993
    return f"https://media.defcon.org/DEF%20CON%20{n}/"


def _blackhat(region: str, year: int) -> str:
    yy = str(year)[2:]
    slug = _BH_SLUGS[region]
    return f"https://www.blackhat.com/{slug}-{yy}/briefings/schedule/"


def _recon(year: int) -> str:
    return f"https://recon.cx/recon{year}/schedule/"


def _troopers(year: int) -> str:
    yy = str(year)[2:]
    return f"https://troopers.de/troopers{yy}/"


def _hardwear(year: int) -> str:
    return f"https://hardwear.io/netherlands-{year}/talks/"


def _offensivecon(year: int) -> str:
    return f"https://www.offensivecon.org/{year}/"


# --- Conference registries ---

ACADEMIC_CONFS: list[Conf] = [
    Conf("USENIX Security", "usenix-security", _usenix),
    Conf("NDSS", "ndss", _ndss),
    Conf("CCS", "ccs", _ccs),
    Conf("ASIACCS", "asiaccs", _asiaccs),
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
    Conf("DEF CON", "defcon", _defcon),
    Conf("Black Hat USA",  "blackhat-usa",  lambda y: _blackhat("usa",    y), bh_slug="us"),
    Conf("Black Hat EU",   "blackhat-eu",   lambda y: _blackhat("europe", y), bh_slug="eu"),
    Conf("Black Hat Asia", "blackhat-asia", lambda y: _blackhat("asia",   y), bh_slug="asia"),
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
    """Probe Black Hat sessions.json using curl_cffi Chrome TLS impersonation.

    blackhat.com is behind Cloudflare; standard httpx/curl requests get 403.
    curl_cffi spoofs Chrome's TLS fingerprint and passes the bot check.
    """
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
    async with httpx.AsyncClient() as client:
        results: dict[str, list[tuple[int, str]]] = {}
        for conf in confs:
            years = range(start, end + 1)
            if conf.bh_slug:
                # Sequential with a small delay — blackhat.com rate-limits parallel
                # curl_cffi requests even at low concurrency.
                checks: list[bool] = []
                for y in years:
                    checks.append(await asyncio.to_thread(_is_live_bh, conf.bh_slug, y))
                    await asyncio.sleep(0.5)
            else:
                candidates = [(y, conf.url_fn(y)) for y in years]
                checks = await asyncio.gather(
                    *[_is_live(client, url) for _, url in candidates]
                )
            results[conf.abbrev] = [
                (y, conf.url_fn(y)) for y, ok in zip(years, checks) if ok
            ]
            found = len(results[conf.abbrev])
            print(f"  {conf.name}: {found}/{len(list(years))} URLs live")
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
