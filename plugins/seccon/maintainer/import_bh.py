# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Import authorized Black Hat exports named bh{us|eu|asia}{yy}-sessions.json."""

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cache_io import coverage, timestamp, write_json

RESOURCES = Path(__file__).parent.parent / "skills" / "ph-seccon" / "resources"
EDITION_MAP = {"us": "blackhat-usa", "eu": "blackhat-eu", "asia": "blackhat-asia"}
EDITION_NAMES = {
    "blackhat-usa": "Black Hat USA",
    "blackhat-eu": "Black Hat Europe",
    "blackhat-asia": "Black Hat Asia",
}
FILENAME_PATTERN = re.compile(r"bh(us|eu|asia)(\d{2})-sessions\.json$")


def resolve_speaker(session_speakers: list, speakers_dict: dict) -> list[str]:
    names = []
    if not isinstance(session_speakers, list):
        raise ValueError("Session speakers must be a list")
    for speaker in session_speakers:
        if not isinstance(speaker, dict):
            raise ValueError("Each session speaker must be an object")
        info = speakers_dict.get(str(speaker.get("person_id")), {})
        if not isinstance(info, dict):
            raise ValueError("Speaker details must be objects")
        first, last = info.get("first_name", ""), info.get("last_name", "")
        if not isinstance(first, str) or not isinstance(last, str):
            raise ValueError("Speaker names must be strings")
        name = f"{first} {last}".strip() or speaker.get("role", "")
        if not isinstance(name, str):
            raise ValueError("Speaker role must be a string")
        if name.strip():
            names.append(name.strip())
    return names


def file_url(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("url", "")
    if not isinstance(value, str):
        raise ValueError("Attachment must be a URL string or an object containing url")
    return value


def parse_session(session: dict, sid: str, prefix: str, speakers: dict) -> dict | None:
    if not isinstance(session, dict) or not isinstance(session.get("title", ""), str):
        raise ValueError(f"Session {sid}: expected an object with a string title")
    title = session.get("title", "").strip()
    names = resolve_speaker(session.get("speakers", []), speakers)
    if not title or not names:
        return None
    description = session.get("description") or session.get("marketing_description") or ""
    files = session.get("bh_files") or {}
    if not isinstance(description, str) or not isinstance(files, dict):
        raise ValueError(f"Session {sid}: expected description string and bh_files object")
    talk = {"id": f"{prefix}-{sid}", "title": title, "speakers": names, "description": description}
    for kind, field in (("slides", "slides_url"), ("whitepaper", "whitepaper_url")):
        url = file_url(files.get(kind, ""))
        if url:
            talk[field] = url
    return talk


def parse_sessions(data: Any, prefix: str) -> list[dict]:
    """Validate an export before producing speaker-bearing talk records."""
    if not isinstance(data, dict) or not isinstance(data.get("sessions"), dict):
        raise ValueError("Expected JSON with a sessions object; HTML may indicate a denial")
    speakers = data.get("speakers", {})
    if not isinstance(speakers, dict):
        raise ValueError("Expected a speakers object")
    talks = []
    for sid, session in data["sessions"].items():
        talk = parse_session(session, sid, prefix, speakers)
        if talk:
            talks.append(talk)
    if not talks:
        raise ValueError("Export contains no speaker-bearing talks; previous cache retained")
    return talks


def import_file(path: str) -> tuple[str, int, int]:
    """Import one validated export, preserving source provenance and unknown acquisition age."""
    source = Path(path)
    match = FILENAME_PATTERN.fullmatch(source.name)
    if not match:
        raise ValueError(f"Filename must match bh(us|eu|asia)YY-sessions.json: {source.name}")
    edition, yy = match.groups()
    slug, year = EDITION_MAP[edition], 2000 + int(yy)
    raw = source.read_bytes()
    talks = parse_sessions(json.loads(raw), f"bh{edition}{yy}")
    metadata = coverage(talks, "talks", source=source.name)
    metadata.update(
        imported_at=timestamp(),
        source_sha256=hashlib.sha256(raw).hexdigest(),
        source_modified_at=datetime.fromtimestamp(source.stat().st_mtime, UTC).isoformat(),
    )
    index = {
        "conference": {
            "name": EDITION_NAMES[slug],
            "acronym": slug.upper(),
            "year": year,
            "url": f"https://blackhat.com/{edition}-{yy}/briefings/schedule/",
        },
        "coverage": metadata,
        "talks": talks,
    }
    write_json(RESOURCES / "industry" / str(year) / slug / "index.json", index)
    return slug, year, len(talks)


def main() -> None:
    global RESOURCES
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--output-dir", type=Path, default=RESOURCES, help="Resource cache root")
    args = parser.parse_args()
    RESOURCES = args.output_dir
    total, failed = 0, 0
    for path in args.paths:
        try:
            slug, year, count = import_file(path)
            total += count
            print(f"{Path(path).name}: {count} talks → {slug}/{year}")
        except (OSError, ValueError) as exc:
            failed += 1
            print(
                f"{Path(path).name}: import failed: {exc}; previous cache retained", file=sys.stderr
            )
    print(f"Total: {total} talks imported; {failed} file(s) failed")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
