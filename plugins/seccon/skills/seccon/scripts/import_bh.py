# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Import Black Hat sessions.json exports into resources/ cache.

Usage:
    uv run scripts/import_bh.py /tmp/seccon/bhus25-sessions.json

This detects the edition and year from the filename pattern:
    bh{edition}{yy}-sessions.json
    edition = usa | eu | asia
    yy = 21 | 22 | 23 | 24 | 25
"""

import json
import re
import sys
from pathlib import Path

RESOURCES = Path(__file__).parent.parent / "resources"

EDITION_MAP = {
    "us": "blackhat-usa",
    "eu": "blackhat-eu",
    "asia": "blackhat-asia",
}

EDITION_NAMES = {
    "blackhat-usa": "Black Hat USA",
    "blackhat-eu": "Black Hat Europe",
    "blackhat-asia": "Black Hat Asia",
}

FILENAME_PATTERN = re.compile(r"bh(us|eu|asia)(\d{2})-sessions\.json$")


def resolve_speaker(session_speakers: list, speakers_dict: dict) -> list[str]:
    names = []
    for sp in session_speakers or []:
        pid = sp.get("person_id")
        if pid and str(pid) in speakers_dict:
            info = speakers_dict[str(pid)]
            first = info.get("first_name", "").strip()
            last = info.get("last_name", "").strip()
            if first or last:
                names.append(f"{first} {last}".strip())
            else:
                names.append(sp.get("role", "Speaker"))
        else:
            names.append(sp.get("role", "Speaker"))
    return names


def import_file(path: str) -> tuple[str, int, int]:
    """Import one BH sessions.json file. Returns (slug, year, count)."""
    path = Path(path)
    match = FILENAME_PATTERN.search(path.name)
    if not match:
        raise ValueError(f"Filename doesn't match pattern: {path.name}")

    edition_code = match.group(1)
    yy = int(match.group(2))
    year = 2000 + yy

    slug = EDITION_MAP[edition_code]
    full_name = EDITION_NAMES[slug]

    with open(path) as f:
        data = json.load(f)

    sessions = data.get("sessions", {})
    speakers_dict = data.get("speakers", {})

    talks = []
    for sid, s in sessions.items():
        title = s.get("title", "").strip()
        if not title:
            continue

        # Skip non-talk sessions (meals, breaks, registration)
        speakers_list = s.get("speakers", [])
        speaker_names = resolve_speaker(speakers_list, speakers_dict)
        if not speaker_names:
            continue
        description = s.get("description", "") or s.get("marketing_description", "") or ""
        bh_files = s.get("bh_files", {}) or {}

        talk = {
            "id": f"bh{edition_code}{yy}-{sid}",
            "title": title,
            "speakers": speaker_names,
            "description": description,
        }

        # Add slides URL if available
        slides = bh_files.get("slides", {})
        if isinstance(slides, dict) and slides.get("url"):
            talk["slides_url"] = slides["url"]
        elif isinstance(slides, str) and slides:
            talk["slides_url"] = slides

        # Add whitepaper URL if available
        wp = bh_files.get("whitepaper", {})
        if isinstance(wp, dict) and wp.get("url"):
            talk["whitepaper_url"] = wp["url"]

        talks.append(talk)

    if not talks:
        return slug, year, 0

    out_dir = RESOURCES / "industry" / str(year) / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    index = {
        "conference": {
            "name": full_name,
            "acronym": slug.upper(),
            "year": year,
            "url": f"https://blackhat.com/{edition_code}-{yy}/briefings/schedule/",
        },
        "coverage": {
            "talks_count": len(talks),
            "has_abstracts": True,
            "has_slides": False,
            "last_crawled": "2026-04-24",
        },
        "talks": talks,
    }

    (out_dir / "index.json").write_text(json.dumps(index, indent=2))
    return slug, year, len(talks)


def main():
    paths = sys.argv[1:]
    if not paths:
        # Default: scan /tmp/seccon/
        default_dir = Path("/tmp/seccon")
        if default_dir.exists():
            paths = sorted(str(p) for p in default_dir.glob("bh*-sessions.json"))
        else:
            print("Usage: uv run scripts/import_bh.py <path-to-sessions.json> [...]")
            sys.exit(1)

    total = 0
    results = []
    for p in paths:
        try:
            slug, year, count = import_file(p)
            results.append((slug, year, count))
            total += count
            print(f"  {Path(p).name}: {count} talks → {slug}/{year}")
        except Exception as e:
            print(f"  {Path(p).name}: error — {e}")

    print(f"\nTotal: {total} talks imported across {len(results)} files")


if __name__ == "__main__":
    main()
