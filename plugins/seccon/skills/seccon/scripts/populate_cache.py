# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Populate the resources/ cache by crawling accessible venue pages.

Run from the skill directory:

    uv run scripts/populate_cache.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

RESOURCES = Path(__file__).parent.parent / "resources"
MANIFEST = RESOURCES / "manifest.json"
CURRENT_YEAR = 2025


def _curl(url: str, timeout: int = 30) -> str | None:
    """Fetch a URL via curl. Returns None on failure."""
    try:
        r = subprocess.run(
            ["curl", "-sL", "--max-time", str(timeout), url],
            capture_output=True, text=True, timeout=timeout + 5
        )
        if r.returncode == 0 and r.stdout:
            return r.stdout
        return None
    except Exception:
        return None


def _defcon_edition(year: int) -> int:
    return 33 - (CURRENT_YEAR - year)


def populate_defcon():
    for year in [2025, 2024, 2023, 2022, 2021]:
        edition = _defcon_edition(year)
        slug = "defcon"
        url = f"https://media.defcon.org/DEF%20CON%20{edition}/DEF%20CON%20{edition}%20presentations/"

        html = _curl(url)
        if not html:
            print(f"  DEF CON {edition} ({year}): unreachable")
            continue

        talks = []
        for match in re.finditer(r'href="([^"]*\.pdf)"', html):
            raw_name = unquote(match.group(1))
            name_no_ext = raw_name.replace(".pdf", "")
            parts = name_no_ext.split(" - ", 1)
            speakers_part = parts[0].strip() if parts else ""
            title = parts[1].strip() if len(parts) > 1 else name_no_ext

            speakers = [s.strip() for s in re.split(r'\s+(?:and|&)\s+', speakers_part) if s.strip()]
            if not speakers:
                speakers = [speakers_part]

            talk_id = f"dc{edition}-{len(talks) + 1:03d}"
            talks.append({
                "id": talk_id,
                "title": title,
                "speakers": speakers,
                "slides_url": url + match.group(1),
                "archive_url": url,
            })

        if not talks:
            print(f"  DEF CON {edition} ({year}): no talks found")
            continue

        out_dir = RESOURCES / "industry" / str(year) / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        index = {
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
                "last_crawled": "2026-04-24",
            },
            "talks": talks,
        }
        (out_dir / "index.json").write_text(json.dumps(index, indent=2))
        print(f"  DEF CON {edition} ({year}): {len(talks)} talks cached")


def populate_offensivecon():
    for year in [2025, 2024, 2023, 2022]:
        slug = "offensivecon"
        url = f"https://www.offensivecon.org/agenda/{year}.html"

        html = _curl(url)
        if not html:
            print(f"  OffensiveCon {year}: unreachable")
            continue

        talks = []
        for match in re.finditer(r'<div class="col-sm-8">([^<]+)</div>', html):
            content = match.group(1).strip()
            parts = content.split(" by ")
            title = parts[0].strip() if parts else content
            speaker = parts[1].strip() if len(parts) > 1 else ""

            talk_id = f"oc{year}-{len(talks) + 1:03d}"
            talks.append({
                "id": talk_id,
                "title": title,
                "speakers": [speaker] if speaker else [],
                "archive_url": url,
            })

        if not talks:
            print(f"  OffensiveCon {year}: no talks found")
            continue

        out_dir = RESOURCES / "industry" / str(year) / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        index = {
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
                "last_crawled": "2026-04-24",
            },
            "talks": talks,
        }
        (out_dir / "index.json").write_text(json.dumps(index, indent=2))
        print(f"  OffensiveCon {year}: {len(talks)} talks cached")


def update_manifest():
    """Mark now-cached venues in manifest.json."""
    manifest = json.loads(MANIFEST.read_text())
    ind_cov = manifest["coverage"]["industry"]["venues"]

    for year in [2025, 2024, 2023, 2022, 2021]:
        dc_index = RESOURCES / "industry" / str(year) / "defcon" / "index.json"
        if dc_index.exists():
            ind_cov["defcon"]["cached"].append(year)
            ind_cov["defcon"]["gaps"] = [y for y in ind_cov["defcon"]["gaps"] if y != year]

    for year in [2025, 2024, 2023, 2022]:
        oc_index = RESOURCES / "industry" / str(year) / "offensivecon" / "index.json"
        if oc_index.exists():
            ind_cov["offensivecon"]["cached"].append(year)
            ind_cov["offensivecon"]["gaps"] = [y for y in ind_cov["offensivecon"]["gaps"] if y != year]

    manifest["generated"] = "2026-04-24"
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print("  manifest.json updated")


def main():
    print("=== Populating resource cache ===\n")

    print("--- DEF CON ---")
    populate_defcon()

    print("\n--- OffensiveCon ---")
    populate_offensivecon()

    print("\n--- Updating manifest ---")
    update_manifest()

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
