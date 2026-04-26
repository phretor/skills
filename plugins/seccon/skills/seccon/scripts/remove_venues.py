# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Remove specified venues from all seccon files.

Usage: uv run scripts/remove_venues.py
"""

import json
import re
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
MANIFEST = SKILL_DIR / "resources" / "manifest.json"
POPULATE = SKILL_DIR / "scripts" / "populate_cache.py"
WRITEMAN = SKILL_DIR / "scripts" / "write_manifest.py"

VENUES_TO_REMOVE = {
    "csf": "CSF",
    "asiacrypt": "Asiacrypt",
    "tcc": "TCC",
    "soups": "SOUPS",
    "acns": "ACNS",
    "ifip-sec": "IFIP SEC",
    "wisec": "WiSec",
    "icics": "ICICS",
    "securecomm": "SecureComm",
    "pst": "PST",
    "pkc": "PKC",
    "sac": "SAC",
}


def remove_from_manifest():
    data = json.loads(MANIFEST.read_text())
    for slug in VENUES_TO_REMOVE:
        if slug in data["coverage"]["academic"]["venues"]:
            del data["coverage"]["academic"]["venues"][slug]
            print(f"  manifest: removed {slug}")
    MANIFEST.write_text(json.dumps(data, indent=2))


def remove_from_populate_cache():
    """Remove slugs from DBLP_XML_URLS and VENUE_NAMES dicts."""
    path = POPULATE
    text = path.read_text()

    # Remove DBLP_XML_URLS entries
    for slug in VENUES_TO_REMOVE:
        # Match the line(s) for this slug in DBLP_XML_URLS
        pattern = rf'    "{re.escape(slug)}":.*\n'
        text = re.sub(pattern, "", text)

    # Remove VENUE_NAMES entries
    for slug in VENUES_TO_REMOVE:
        pattern = rf'    "{re.escape(slug)}":.*\n'
        text = re.sub(pattern, "", text)

    path.write_text(text)
    print(f"  populate_cache.py: cleaned {len(VENUES_TO_REMOVE)} slugs")


def remove_from_write_manifest():
    path = WRITEMAN
    text = path.read_text()

    for slug in VENUES_TO_REMOVE:
        pattern = rf'    "{re.escape(slug)}":.*\n'
        text = re.sub(pattern, "", text)

    path.write_text(text)
    print(f"  write_manifest.py: cleaned {len(VENUES_TO_REMOVE)} slugs")


def remove_from_skill_md():
    """Remove rows from the ranked conferences table."""
    path = SKILL_MD
    text = path.read_text()

    for slug, name in VENUES_TO_REMOVE.items():
        # Remove table rows containing this venue's abbreviation
        # Match any row that starts with | and contains the venue name
        pattern = rf'\| {re.escape(name)} .*\|.*\n'
        text = re.sub(pattern, "", text)

    path.write_text(text)
    print(f"  SKILL.md: cleaned {len(VENUES_TO_REMOVE)} venues")


def main():
    print("=== Removing venues ===\n")
    for slug, name in sorted(VENUES_TO_REMOVE.items(), key=lambda x: x[1]):
        print(f"  {name:20s} ({slug})")

    print("\n--- Manifest ---")
    remove_from_manifest()

    print("\n--- populate_cache.py ---")
    remove_from_populate_cache()

    print("\n--- write_manifest.py ---")
    remove_from_write_manifest()

    print("\n--- SKILL.md ---")
    remove_from_skill_md()

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
