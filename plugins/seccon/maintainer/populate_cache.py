# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Refresh a bounded selection of resource indexes; report policy limits and retain old data."""

import argparse
import json
import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin

from cache_io import coverage, meaningful, timestamp, write_json
from fetch_policy import Fetcher, FetchResult, validate_content
from write_manifest import INDUSTRY_SLUGS, build_manifest
from write_manifest import VENUE_NAMES as ALL_VENUES

RESOURCES = Path(__file__).parent.parent / "skills" / "ph-seccon" / "resources"
FETCHER = Fetcher()
FETCHED: dict[str, FetchResult] = {}

# Retained DBLP XML adapter; acquisition is subject to current robots policy.
DBLP_XML_URLS = {
    "ieee-sp": "https://dblp.org/db/conf/sp/sp{year}.xml",
    "ccs": "https://dblp.org/db/conf/ccs/ccs{year}.xml",
    "usenix-security": "https://dblp.org/db/conf/uss/uss{year}.xml",
    "ndss": "https://dblp.org/db/conf/ndss/ndss{year}.xml",
    "crypto": "https://dblp.org/db/conf/crypto/crypto{year}.xml",
    "eurocrypt": "https://dblp.org/db/conf/eurocrypt/eurocrypt{year}.xml",
    "esorics": "https://dblp.org/db/conf/esorics/esorics{year}.xml",
    "acsac": "https://dblp.org/db/conf/acsac/acsac{year}.xml",
    "asiaccs": "https://dblp.org/db/conf/asiaccs/asiaccs{year}.xml",
    "eurosp": "https://dblp.org/db/conf/eurosp/eurosp{year}.xml",
    "fc": "https://dblp.org/db/conf/fc/fc{year}.xml",
    "raid": "https://dblp.org/db/conf/raid/raid{year}.xml",
    "imc": "https://dblp.org/db/conf/imc/imc{year}.xml",
    "ches": "https://dblp.org/db/conf/ches/ches{year}.xml",
    "acisp": "https://dblp.org/db/conf/acisp/acisp{year}.xml",
    "dimva": "https://dblp.org/db/conf/dimva/dimva{year}.xml",
}

VENUE_NAMES = {
    "ieee-sp": ("IEEE Symposium on Security and Privacy", "IEEE S&P"),
    "ccs": ("ACM Conference on Computer and Communications Security", "CCS"),
    "usenix-security": ("USENIX Security Symposium", "USENIX Security"),
    "ndss": ("Network and Distributed System Security Symposium", "NDSS"),
    "crypto": ("International Cryptology Conference", "Crypto"),
    "eurocrypt": ("European Cryptology Conference", "Eurocrypt"),
    "esorics": ("European Symposium on Research in Computer Security", "ESORICS"),
    "acsac": ("Annual Computer Security Applications Conference", "ACSAC"),
    "asiaccs": ("ACM Asia Conference on Computer and Communications Security", "AsiaCCS"),
    "eurosp": ("IEEE European Symposium on Security and Privacy", "EuroS&P"),
    "fc": ("Financial Cryptography and Data Security", "FC"),
    "raid": ("Recent Advances in Intrusion Detection", "RAID"),
    "imc": ("Internet Measurement Conference", "IMC"),
    "ches": ("Cryptographic Hardware and Embedded Systems", "CHES"),
    "acisp": ("Australasian Conference on Information Security and Privacy", "ACISP"),
    "dimva": ("Detection of Intrusions and Malware and Vulnerability Assessment", "DIMVA"),
}


class RefreshError(Exception):
    def __init__(self, result: FetchResult):
        self.result = result
        super().__init__(f"{result.outcome}: {result.effective_url or result.url}: {result.reason}")


def _fetch_body(url: str) -> str:
    """Use ordinary HTTP and stop on explicit policy, status or content failures."""
    years = re.findall(r"20\d{2}", url)
    year = int(years[0]) if years else None
    result = validate_content(FETCHER.fetch(url, year=year), year=year)
    FETCHED[url] = result
    if result.outcome != "ok":
        raise RefreshError(result)
    return result.body


def _defcon_edition(year: int) -> int:
    return year - 1992


def selected_years(years: list[int] | None, *, current_year: int | None = None) -> list[int]:
    """Select 2021 through this calendar year by default, allowing explicit next editions."""
    current = current_year if current_year is not None else date.today().year
    selected = sorted(set(years if years is not None else range(2021, current + 1)))
    if not selected or any(year < 2021 or year > current + 1 for year in selected):
        raise ValueError(f"Years must lie between 2021 and {current + 1}")
    return selected


def _write_index(out_dir: Path, index: dict, source: str) -> None:
    key = "papers" if "papers" in index else "talks"
    records = index[key]
    if not records or not all(map(meaningful, records)):
        raise ValueError(
            "Extraction produced no complete set of meaningful records; cache retained"
        )
    fetched = FETCHED.get(source)
    previous_source = index.get("coverage", {}).get("source")
    index["coverage"] = coverage(
        records, key, source=source, acquired_at=fetched.acquired_at if fetched else None
    )
    if fetched:
        index["coverage"].update(
            effective_url=fetched.effective_url,
            status=fetched.status,
            content_type=fetched.content_type,
        )
    if previous_source:
        index["coverage"]["source_scope"] = previous_source
        _check_partial_source(out_dir / "index.json", records, key, source)
    write_json(out_dir / "index.json", index)


def _check_partial_source(path: Path, records: list[dict], key: str, source: str) -> None:
    if not path.exists():
        return
    old = json.loads(path.read_text())
    old_titles = {record["title"] for record in old[key]}
    new_titles = {record["title"] for record in records}
    if not old_titles <= new_titles:
        raise RefreshError(
            FetchResult(
                source,
                outcome="needs-review",
                reason="Partial source would discard existing records; review required",
            )
        )


def parse_dblp_xml(xml: str) -> list[dict]:
    papers = []
    for entry in re.finditer(r"<inproceedings[^>]*>(.*?)</inproceedings>", xml, re.DOTALL):
        content = entry.group(1)
        title_match = re.search(r"<title>(.*?)</title>", content, re.DOTALL)
        if not title_match:
            continue
        title = title_match.group(1).strip()
        title = (
            title.replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&#38;", "&")
        )
        authors = re.findall(r"<author[^>]*>(.*?)</author>", content)
        doi_match = re.search(r"<ee>(https?://doi\.org/[^\s<]+)</ee>", content)
        doi = doi_match.group(1) if doi_match else ""
        url_match = re.search(r"<url>([^<]+)</url>", content)
        dblp_url = f"https://dblp.org/{url_match.group(1)}" if url_match else ""
        papers.append({"title": title, "authors": authors, "doi": doi, "dblp_url": dblp_url})
    return papers


def fetch_dblp_year(slug: str, year: int) -> tuple[str, int, list[dict] | None]:
    url_tmpl = DBLP_XML_URLS.get(slug)
    if not url_tmpl:
        return slug, year, None
    url = url_tmpl.replace("{year}", str(year))
    xml = _fetch_body(url)
    if not xml or "<inproceedings" not in xml:
        return slug, year, None
    papers = parse_dblp_xml(xml)
    return slug, year, papers if papers else None


def write_academic_index(slug: str, year: int, papers: list[dict]):
    full_name, acronym = VENUE_NAMES[slug]
    out_dir = RESOURCES / "academic" / str(year) / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    index = {
        "conference": {"name": full_name, "acronym": acronym, "year": year, "venue_slug": slug},
        "coverage": {
            "papers_count": len(papers),
            "has_abstracts": False,
        },
        "papers": [
            {
                "id": f"{slug}-{year}-{j + 1:03d}",
                "title": p["title"],
                "authors": p["authors"],
                "doi": p.get("doi", ""),
                "dblp_url": p.get("dblp_url", ""),
            }
            for j, p in enumerate(papers)
        ],
    }
    _write_index(out_dir, index, DBLP_XML_URLS[slug].format(year=year))


def crawl_defcon_year(year: int) -> int:
    edition = _defcon_edition(year)
    url = f"https://media.defcon.org/DEF%20CON%20{edition}/DEF%20CON%20{edition}%20presentations/"
    html = _fetch_body(url)
    if not html:
        return 0
    talks = []
    for match in re.finditer(r'href="([^"]*\.pdf)"', html):
        raw_name = unquote(match.group(1))
        name_no_ext = raw_name.replace(".pdf", "")
        parts = name_no_ext.split(" - ", 1)
        sp = parts[0].strip() if parts else ""
        title = parts[1].strip() if len(parts) > 1 else name_no_ext
        speakers = [s.strip() for s in re.split(r"\s+(?:and|&)\s+", sp) if s.strip()] or [sp]
        tid = f"dc{edition}-{len(talks) + 1:03d}"
        talks.append(
            {"id": tid, "title": title, "speakers": speakers, "slides_url": url + match.group(1)}
        )
    if not talks:
        return 0
    out_dir = RESOURCES / "industry" / str(year) / "defcon"
    out_dir.mkdir(parents=True, exist_ok=True)
    idx = {
        "conference": {
            "name": f"DEF CON {edition}",
            "acronym": "DEF CON",
            "year": year,
            "edition": edition,
            "url": url,
        },
        "coverage": {
            "talks_count": len(talks),
            "has_abstracts": False,
            "has_slides": True,
        },
        "talks": talks,
    }
    _write_index(out_dir, idx, url)
    return len(talks)


class AgendaParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.text: list[str] = []
        self.links: list[str] = []
        self.cells: list[tuple[str, list[str]]] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "div":
            if self.depth:
                self.depth += 1
            elif "col-sm-8" in attributes.get("class", "").split():
                self.depth = 1
                self.text, self.links = [], []
        if self.depth and tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        if self.depth and tag == "br":
            self.text.append(" ")

    def handle_data(self, data):
        if self.depth:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "div" and self.depth:
            self.depth -= 1
            if not self.depth:
                self.cells.append((" ".join("".join(self.text).split()), self.links))


def parse_offensivecon(html: str, year: int, url: str) -> list[dict]:
    """Extract speaker-bearing or session-linked cells, including nested inline markup."""
    parser = AgendaParser()
    parser.feed(html)
    talks = []
    for text, links in parser.cells:
        if re.match(
            r"^(registration|welcome|coffee|lunch|closing|opening party|pwn2own winners)\b",
            text,
            re.I,
        ):
            continue
        title, sep, people = text.rpartition(" by ")
        speakers = [name.strip() for name in re.split(r",|\s+(?:and|&)\s+", people) if name.strip()]
        session = next(
            (
                urljoin(url, link)
                for link in links
                if re.search(r"talk|session|keynote", link, re.I)
            ),
            "",
        )
        if not sep:
            title, speakers = text, []
        if not title or not (speakers or session):
            continue
        talk = {"id": f"oc{year}-{len(talks) + 1:03d}", "title": title, "speakers": speakers}
        if session:
            talk["session_url"] = session
        talks.append(talk)
    return talks


def crawl_offensivecon_year(year: int) -> int:
    url = f"https://www.offensivecon.org/agenda/{year}.html"
    html = _fetch_body(url)
    talks = parse_offensivecon(html, year, url)
    if not talks:
        return 0
    out_dir = RESOURCES / "industry" / str(year) / "offensivecon"
    out_dir.mkdir(parents=True, exist_ok=True)
    idx = {
        "conference": {
            "name": f"OffensiveCon {year}",
            "acronym": "OffensiveCon",
            "year": year,
            "url": url,
        },
        "coverage": {
            "talks_count": len(talks),
            "has_abstracts": False,
            "has_slides": False,
        },
        "talks": talks,
    }
    _write_index(out_dir, idx, url)
    return len(talks)


def crawl_recon_year(year: int) -> int:
    url = f"https://recon.cx/{year}/sessions.html"
    html = _fetch_body(url)
    if not html:
        return 0
    talks = []
    for m in re.finditer(r'<ul class="training-list">(.*?)</ul>', html, re.DOTALL):
        items = re.findall(r"<li>(.*?)</li>", m.group(1), re.DOTALL)
        for item in items:
            text = re.sub(r"<[^>]+>", " ", item).strip()
            text = re.sub(r"\s+", " ", text)
            if not text or len(text) < 10:
                continue
            parts = text.split(" - ", 1)
            title = parts[0].strip() if parts else text
            speaker = parts[1].strip() if len(parts) > 1 else ""
            speakers = [s.strip() for s in re.split(r"[,&]", speaker) if s.strip()]
            talks.append(
                {
                    "id": f"rc{year}-{len(talks) + 1:03d}",
                    "title": title,
                    "speakers": speakers or [speaker],
                }
            )
    if not talks:
        return 0
    out_dir = RESOURCES / "industry" / str(year) / "recon"
    out_dir.mkdir(parents=True, exist_ok=True)
    idx = {
        "conference": {"name": f"REcon {year}", "acronym": "REcon", "year": year, "url": url},
        "coverage": {
            "talks_count": len(talks),
            "has_abstracts": False,
            "has_slides": False,
        },
        "talks": talks,
    }
    _write_index(out_dir, idx, url)
    return len(talks)


def _rss_talk(content: str, year: int) -> dict | None:
    title_match = re.search(r"<title>(.*?)</title>", content, re.DOTALL)
    if not title_match or str(year) not in title_match.group(1):
        return None
    title = title_match.group(1).strip()
    for separator in (": ", " | ", ":"):
        parts = title.split(separator, 1)
        if len(parts) > 1 and "hardwear" in parts[0].lower():
            title = parts[1].strip()
            break
    speakers = []
    if " by " in title:
        title, people = title.rsplit(" by ", 1)
        speakers = [name.strip() for name in re.split(r"[,&]", people) if name.strip()]
    video_id = re.search(r"<yt:videoId>(.*?)</yt:videoId>", content)
    video_url = f"https://www.youtube.com/watch?v={video_id.group(1)}" if video_id else ""
    return {"title": title, "speakers": speakers, "video_url": video_url}


def crawl_hardwear_year(year: int) -> int:
    """Read the limited recent RSS window only when permitted; no Data API is implemented."""
    url = "https://www.youtube.com/feeds/videos.xml?channel_id=UChwYb9xc9tZXquQxu4G0l_g"
    xml = _fetch_body(url)
    talks = []
    for entry in re.finditer(r"<entry>(.*?)</entry>", xml, re.DOTALL):
        talk = _rss_talk(entry.group(1), year)
        if talk:
            talk["id"] = f"hw{year}-{len(talks) + 1:03d}"
            talks.append(talk)
    if not talks:
        return 0
    out_dir = RESOURCES / "industry" / str(year) / "hardwear"
    out_dir.mkdir(parents=True, exist_ok=True)
    idx = {
        "conference": {
            "name": "hardwear.io",
            "acronym": "hardwear.io",
            "year": year,
            "url": f"https://hardwear.io/netherlands-{year}/talks/",
        },
        "coverage": {
            "talks_count": len(talks),
            "has_abstracts": False,
            "has_slides": False,
            "source": "YouTube RSS (limited)",
        },
        "talks": talks,
    }
    _write_index(out_dir, idx, url)
    return len(talks)


def refresh_one(mode: str, slug: str, year: int) -> bool:
    """Record each refresh separately from the retained index, including policy failures."""
    handlers = {
        "defcon": crawl_defcon_year,
        "offensivecon": crawl_offensivecon_year,
        "recon": crawl_recon_year,
        "hardwear": crawl_hardwear_year,
    }
    attempt: dict = {"attempted_at": timestamp()}
    try:
        if mode == "academic" and slug in DBLP_XML_URLS:
            _, _, papers = fetch_dblp_year(slug, year)
            if papers:
                write_academic_index(slug, year, papers)
            count = len(papers or [])
        elif mode == "industry" and slug in handlers:
            count = handlers[slug](year)
        else:
            attempt.update(
                outcome="unsupported", reason="No population handler; import/adaptor required"
            )
            count = 0
        if "outcome" not in attempt:
            attempt.update(outcome="ok" if count else "empty-extraction", records_count=count)
    except RefreshError as exc:
        result = exc.result
        attempt.update(
            outcome=result.outcome,
            reason=result.reason,
            url=result.url,
            effective_url=result.effective_url,
            status=result.status,
            retry_after=result.retry_after,
        )
    except (OSError, ValueError) as exc:
        attempt.update(outcome="refresh-error", reason=str(exc))
    write_json(RESOURCES / mode / str(year) / slug / "refresh.json", attempt)
    print(f"{mode}/{year}/{slug}: {attempt['outcome']}; previous cache retained on failure")
    return attempt["outcome"] == "ok"


def main() -> None:
    global RESOURCES
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--year", type=int, action="append", help="Select one year; repeat for several"
    )
    parser.add_argument(
        "--venue", action="append", choices=sorted(set(ALL_VENUES) | set(INDUSTRY_SLUGS))
    )
    parser.add_argument("--output-dir", type=Path, default=RESOURCES, help="Resource cache root")
    args = parser.parse_args()
    try:
        years = selected_years(args.year)
    except ValueError as exc:
        parser.error(str(exc))
    RESOURCES = args.output_dir
    selected = set(args.venue) if args.venue else set(ALL_VENUES) | set(INDUSTRY_SLUGS)
    failed = False
    for mode, venues in (("academic", ALL_VENUES), ("industry", INDUSTRY_SLUGS)):
        for slug in sorted(set(venues) & selected):
            for year in years:
                failed |= not refresh_one(mode, slug, year)
    write_json(RESOURCES / "manifest.json", build_manifest(RESOURCES))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
