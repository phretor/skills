# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Populate resources/ cache using curl for reliability."""

import concurrent.futures
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import unquote

RESOURCES = Path(__file__).parent.parent / "resources"
MANIFEST = RESOURCES / "manifest.json"
CURRENT_YEAR = 2025
YEARS = [2021, 2022, 2023, 2024, 2025]
MAX_WORKERS = 3  # keep low for rate limiting

# DBLP XML URLs (primary source, sometimes flaky)
DBLP_XML_URLS = {
    "ieee-sp":        "https://dblp.org/db/conf/sp/sp{year}.xml",
    "ccs":            "https://dblp.org/db/conf/ccs/ccs{year}.xml",
    "usenix-security": "https://dblp.org/db/conf/uss/uss{year}.xml",
    "ndss":           "https://dblp.org/db/conf/ndss/ndss{year}.xml",
    "crypto":         "https://dblp.org/db/conf/crypto/crypto{year}.xml",
    "eurocrypt":      "https://dblp.org/db/conf/eurocrypt/eurocrypt{year}.xml",
    "esorics":        "https://dblp.org/db/conf/esorics/esorics{year}.xml",
    "acsac":          "https://dblp.org/db/conf/acsac/acsac{year}.xml",
    "asiaccs":        "https://dblp.org/db/conf/asiaccs/asiaccs{year}.xml",
    "eurosp":         "https://dblp.org/db/conf/eurosp/eurosp{year}.xml",
    "csf":            "https://dblp.org/db/conf/csfw/csfw{year}.xml",
    "asiacrypt":      "https://dblp.org/db/conf/asiacrypt/asiacrypt{year}.xml",
    "tcc":            "https://dblp.org/db/conf/tcc/tcc{year}.xml",
    "fc":             "https://dblp.org/db/conf/fc/fc{year}.xml",
    "raid":           "https://dblp.org/db/conf/raid/raid{year}.xml",
    "imc":            "https://dblp.org/db/conf/imc/imc{year}.xml",
    "ches":           "https://dblp.org/db/conf/ches/ches{year}.xml",
    "soups":          "https://dblp.org/db/conf/soups/soups{year}.xml",
    "acns":           "https://dblp.org/db/conf/acns/acns{year}.xml",
    "acisp":          "https://dblp.org/db/conf/acisp/acisp{year}.xml",
    "ifip-sec":       "https://dblp.org/db/conf/sec/sec{year}.xml",
    "wisec":          "https://dblp.org/db/conf/wisec/wisec{year}.xml",
    "dimva":          "https://dblp.org/db/conf/dimva/dimva{year}.xml",
    "icics":          "https://dblp.org/db/conf/icics/icics{year}.xml",
    "securecomm":     "https://dblp.org/db/conf/securecomm/securecomm{year}.xml",
    "pst":            "https://dblp.org/db/conf/pst/pst{year}.xml",
    "pkc":            "https://dblp.org/db/conf/pkc/pkc{year}.xml",
    "sac":            "https://dblp.org/db/conf/sacrypt/sacrypt{year}.xml",
}

VENUE_NAMES = {
    "ieee-sp":        ("IEEE Symposium on Security and Privacy", "IEEE S&P"),
    "ccs":            ("ACM Conference on Computer and Communications Security", "CCS"),
    "usenix-security": ("USENIX Security Symposium", "USENIX Security"),
    "ndss":           ("Network and Distributed System Security Symposium", "NDSS"),
    "crypto":         ("International Cryptology Conference", "Crypto"),
    "eurocrypt":      ("European Cryptology Conference", "Eurocrypt"),
    "esorics":        ("European Symposium on Research in Computer Security", "ESORICS"),
    "acsac":          ("Annual Computer Security Applications Conference", "ACSAC"),
    "asiaccs":        ("ACM Asia Conference on Computer and Communications Security", "AsiaCCS"),
    "eurosp":         ("IEEE European Symposium on Security and Privacy", "EuroS&P"),
    "csf":            ("IEEE Computer Security Foundations Symposium", "CSF"),
    "asiacrypt":      ("International Conference on Theory and Application of Cryptology", "Asiacrypt"),
    "tcc":            ("Theory of Cryptography Conference", "TCC"),
    "fc":             ("Financial Cryptography and Data Security", "FC"),
    "raid":           ("Recent Advances in Intrusion Detection", "RAID"),
    "imc":            ("Internet Measurement Conference", "IMC"),
    "ches":           ("Cryptographic Hardware and Embedded Systems", "CHES"),
    "soups":          ("Symposium on Usable Privacy and Security", "SOUPS"),
    "acns":           ("Applied Cryptography and Network Security", "ACNS"),
    "acisp":          ("Australasian Conference on Information Security and Privacy", "ACISP"),
    "ifip-sec":       ("IFIP Information Security and Privacy Conference", "IFIP SEC"),
    "wisec":          ("ACM Conference on Security and Privacy in Wireless and Mobile Networks", "WiSec"),
    "dimva":          ("Detection of Intrusions and Malware and Vulnerability Assessment", "DIMVA"),
    "icics":          ("International Conference on Information and Communications Security", "ICICS"),
    "securecomm":     ("International Conference on Security and Privacy in Communication Networks", "SecureComm"),
    "pst":            ("Privacy, Security and Trust", "PST"),
    "pkc":            ("International Conference on Practice and Theory in Public-Key Cryptography", "PKC"),
    "sac":            ("Selected Areas in Cryptography", "SAC"),
}


def _curl(url: str, timeout: int = 15) -> str | None:
    """Fetch a URL via curl with retry logic for flaky connections."""
    for attempt in range(3):
        try:
            r = subprocess.run(
                ["curl", "-sL", "--max-time", str(timeout), url],
                capture_output=True, text=True, timeout=timeout + 5,
            )
            if r.returncode == 0 and r.stdout and len(r.stdout) > 100:
                return r.stdout
        except Exception:
            pass
        if attempt < 2:
            time.sleep(1)
    return None


def _defcon_edition(year: int) -> int:
    return 33 - (CURRENT_YEAR - year)


def parse_dblp_xml(xml: str) -> list[dict]:
    papers = []
    for entry in re.finditer(r'<inproceedings[^>]*>(.*?)</inproceedings>', xml, re.DOTALL):
        content = entry.group(1)
        title_match = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
        if not title_match:
            continue
        title = title_match.group(1).strip()
        title = title.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&#38;", "&")
        authors = re.findall(r'<author[^>]*>(.*?)</author>', content)
        doi_match = re.search(r'<ee>(https?://doi\.org/[^\s<]+)</ee>', content)
        doi = doi_match.group(1) if doi_match else ""
        url_match = re.search(r'<url>([^<]+)</url>', content)
        dblp_url = f"https://dblp.org/{url_match.group(1)}" if url_match else ""
        papers.append({"title": title, "authors": authors, "doi": doi, "dblp_url": dblp_url})
    return papers


def fetch_dblp_year(slug: str, year: int) -> tuple[str, int, list[dict] | None]:
    url_tmpl = DBLP_XML_URLS.get(slug)
    if not url_tmpl:
        return slug, year, None
    url = url_tmpl.replace("{year}", str(year))
    xml = _curl(url, timeout=15)
    if not xml or '<inproceedings' not in xml:
        return slug, year, None
    papers = parse_dblp_xml(xml)
    return slug, year, papers if papers else None


def write_academic_index(slug: str, year: int, papers: list[dict]):
    full_name, acronym = VENUE_NAMES[slug]
    out_dir = RESOURCES / "academic" / str(year) / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    index = {
        "conference": {"name": full_name, "acronym": acronym, "year": year, "venue_slug": slug},
        "coverage": {"papers_count": len(papers), "has_abstracts": False, "last_crawled": "2026-04-24"},
        "papers": [
            {"id": f"{slug}-{year}-{j+1:03d}", "title": p["title"], "authors": p["authors"],
             "doi": p.get("doi", ""), "dblp_url": p.get("dblp_url", "")}
            for j, p in enumerate(papers)
        ],
    }
    (out_dir / "index.json").write_text(json.dumps(index, indent=2))


def crawl_defcon_year(year: int) -> int:
    edition = _defcon_edition(year)
    url = f"https://media.defcon.org/DEF%20CON%20{edition}/DEF%20CON%20{edition}%20presentations/"
    html = _curl(url)
    if not html:
        return 0
    talks = []
    for match in re.finditer(r'href="([^"]*\.pdf)"', html):
        raw_name = unquote(match.group(1))
        name_no_ext = raw_name.replace(".pdf", "")
        parts = name_no_ext.split(" - ", 1)
        sp = parts[0].strip() if parts else ""
        title = parts[1].strip() if len(parts) > 1 else name_no_ext
        speakers = [s.strip() for s in re.split(r'\s+(?:and|&)\s+', sp) if s.strip()] or [sp]
        tid = f"dc{edition}-{len(talks) + 1:03d}"
        talks.append({"id": tid, "title": title, "speakers": speakers, "slides_url": url + match.group(1), "archive_url": url})
    if not talks:
        return 0
    out_dir = RESOURCES / "industry" / str(year) / "defcon"
    out_dir.mkdir(parents=True, exist_ok=True)
    idx = {
        "conference": {"name": f"DEF CON {edition}", "acronym": "DEF CON", "year": year, "edition": edition, "url": url},
        "coverage": {"talks_count": len(talks), "has_abstracts": False, "has_slides": True, "last_crawled": "2026-04-24"},
        "talks": talks,
    }
    (out_dir / "index.json").write_text(json.dumps(idx, indent=2))
    return len(talks)


def crawl_offensivecon_year(year: int) -> int:
    url = f"https://www.offensivecon.org/agenda/{year}.html"
    html = _curl(url)
    if not html:
        return 0
    talks = []
    for m in re.finditer(r'<div class="col-sm-8">([^<]+)</div>', html):
        c = m.group(1).strip()
        parts = c.split(" by ")
        title = parts[0].strip() if parts else c
        speaker = parts[1].strip() if len(parts) > 1 else ""
        talks.append({"id": f"oc{year}-{len(talks)+1:03d}", "title": title, "speakers": [speaker] if speaker else [], "archive_url": url})
    if not talks:
        return 0
    out_dir = RESOURCES / "industry" / str(year) / "offensivecon"
    out_dir.mkdir(parents=True, exist_ok=True)
    idx = {
        "conference": {"name": f"OffensiveCon {year}", "acronym": "OffensiveCon", "year": year, "url": url},
        "coverage": {"talks_count": len(talks), "has_abstracts": False, "has_slides": False, "last_crawled": "2026-04-24"},
        "talks": talks,
    }
    (out_dir / "index.json").write_text(json.dumps(idx, indent=2))
    return len(talks)


def crawl_recon_year(year: int) -> int:
    url = f"https://recon.cx/{year}/sessions.html"
    html = _curl(url)
    if not html:
        return 0
    talks = []
    for m in re.finditer(r'<ul class="training-list">(.*?)</ul>', html, re.DOTALL):
        items = re.findall(r'<li>(.*?)</li>', m.group(1), re.DOTALL)
        for item in items:
            text = re.sub(r'<[^>]+>', ' ', item).strip()
            text = re.sub(r'\s+', ' ', text)
            if not text or len(text) < 10:
                continue
            parts = text.split(' - ', 1)
            title = parts[0].strip() if parts else text
            speaker = parts[1].strip() if len(parts) > 1 else ""
            speakers = [s.strip() for s in re.split(r'[,&]', speaker) if s.strip()]
            talks.append({"id": f"rc{year}-{len(talks)+1:03d}", "title": title, "speakers": speakers or [speaker], "archive_url": url})
    if not talks:
        return 0
    out_dir = RESOURCES / "industry" / str(year) / "recon"
    out_dir.mkdir(parents=True, exist_ok=True)
    idx = {"conference": {"name": f"REcon {year}", "acronym": "REcon", "year": year, "url": url}, "coverage": {"talks_count": len(talks), "has_abstracts": False, "has_slides": False, "last_crawled": "2026-04-24"}, "talks": talks}
    (out_dir / "index.json").write_text(json.dumps(idx, indent=2))
    return len(talks)


def write_manifest(academic_cached: dict, industry_cached: dict):
    manifest = {
        "version": "1.3.0",
        "generated": "2026-04-24",
        "cached_range": {"earliest": 2021, "latest": 2025},
        "coverage": {"academic": {"venues": {}}, "industry": {"venues": {}}},
    }
    for slug in sorted(VENUE_NAMES):
        cached = sorted(academic_cached.get(slug, []))
        gaps = sorted(set(YEARS) - set(cached))
        manifest["coverage"]["academic"]["venues"][slug] = {"cached": cached, "gaps": gaps, "note": "DBLP unreachable from this environment" if not cached else ""}
    dc = sorted(industry_cached.get("defcon", []))
    oc = sorted(industry_cached.get("offensivecon", []))
    manifest["coverage"]["industry"]["venues"]["defcon"] = {"cached": dc, "gaps": sorted(set(YEARS) - set(dc)), "note": ""}
    manifest["coverage"]["industry"]["venues"]["offensivecon"] = {"cached": oc, "gaps": sorted(set(YEARS) - set(oc)), "note": ""}
    for bh in ("blackhat-usa", "blackhat-eu", "blackhat-asia"):
        manifest["coverage"]["industry"]["venues"][bh] = {"cached": [], "gaps": YEARS, "note": "Cloudflare blocked"}
    for o in ("rsec", "cansecwest", "recon", "troopers", "hardwear", "infiltrate", "hitcon", "hitb", "vb", "poc"):
        manifest["coverage"]["industry"]["venues"][o] = {"cached": [], "gaps": YEARS, "note": "Not yet crawled"}
    MANIFEST.write_text(json.dumps(manifest, indent=2))


def main():
    print("=== Populating resource cache ===\n")
    print("--- Academic venues (via DBLP XML, retries + low concurrency) ---\n")
    ac_cached = {}
    for slug in VENUE_NAMES:
        ac_cached[slug] = []

    tasks = [(slug, year) for slug in VENUE_NAMES for year in YEARS]
    total = len(tasks)
    done = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(fetch_dblp_year, slug, year): (slug, year) for slug, year in tasks}
        for f in concurrent.futures.as_completed(futures):
            slug, year, papers = f.result()
            done += 1
            if papers:
                ac_cached[slug].append(year)
                write_academic_index(slug, year, papers)
            cached_count = sum(len(v) for v in ac_cached.values())
            sys.stdout.write(f"\r  {done}/{total} — {cached_count} venue-years cached")
            sys.stdout.flush()
    print()

    # Print summaries per venue
    print()
    for slug in sorted(VENUE_NAMES):
        cached = ac_cached.get(slug, [])
        if cached:
            print(f"  ✓ {VENUE_NAMES[slug][1]:20s}: {', '.join(str(y) for y in sorted(cached))}")
    for slug in sorted(VENUE_NAMES):
        failed = [y for y in YEARS if y not in ac_cached.get(slug, [])]
        if failed:
            print(f"  ✗ {VENUE_NAMES[slug][1]:20s}: years {', '.join(str(y) for y in failed)}")

    print("\n--- Industry venues ---")
    ind = {}
    print("  DEF CON...")
    dc = []
    for y in YEARS:
        c = crawl_defcon_year(y)
        dc.append(y) if c else None
        print(f"    DEF CON {_defcon_edition(y)} ({y}): {c or 'unreachable'}")
    ind["defcon"] = dc

    print("  OffensiveCon...")
    oc = []
    for y in YEARS:
        c = crawl_offensivecon_year(y)
        oc.append(y) if c else None
        print(f"    OffensiveCon {y}: {c or 'unreachable'}")
    ind["offensivecon"] = oc

    print("\n  REcon...")
    rc = []
    for y in [2022, 2023, 2024, 2025]:
        c = crawl_recon_year(y)
        rc.append(y) if c else None
        print(f"    REcon {y}: {c or 'unreachable'}")
    ind["recon"] = rc

    print("\n--- Updating manifest ---")
    write_manifest(ac_cached, ind)

    # Clean empty dirs
    for p in list(RESOURCES.rglob("*")):
        if p.is_dir() and not any(True for _ in p.iterdir()):
            p.rmdir()

    total_ac = sum(len(v) for v in ac_cached.values())
    total_ind = sum(len(v) for v in ind.values())
    print(f"\n=== Done: {total_ac} academic venue-years, {total_ind} industry venue-years ===")


if __name__ == "__main__":
    main()
