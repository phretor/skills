# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Validate cache records and replace indexes without truncating an earlier cache."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def write_json(path: Path, value: dict) -> None:
    """Atomically replace JSON, retaining the previous file if writing fails."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def meaningful(record: Any) -> bool:
    if not isinstance(record, dict) or not isinstance(record.get("title"), str):
        return False
    people = record.get("speakers", record.get("authors", []))
    names = isinstance(people, list) and any(isinstance(p, str) and p.strip() for p in people)
    links = any(record.get(key) for key in ("doi", "session_url", "slides_url", "video_url"))
    return bool(record["title"].strip() and (names or links))


def coverage(records: list[dict], key: str, *, source: str, acquired_at: str | None = None) -> dict:
    """Derive availability from records; acquisition time stays unknown when unrecorded."""
    return {
        f"{key}_count": len(records),
        "has_abstracts": any(r.get("abstract") or r.get("description") for r in records),
        "has_slides": any(r.get("slides_url") for r in records),
        "source": source,
        "source_acquired_at": acquired_at,
        "last_crawled": acquired_at,
    }


def index_quality(path: Path, *, year: int) -> dict:
    """Describe content quality independently of file availability and refresh attempts."""
    data = {}
    metadata = {}
    try:
        data = json.loads(path.read_text())
        if not isinstance(data, dict):
            raise ValueError("Index must be an object")
        metadata = data.get("coverage", {})
        if not isinstance(metadata, dict) or not isinstance(data.get("conference"), dict):
            raise ValueError("Expected conference and coverage objects")
        key = "papers" if path.parts[-4] == "academic" else "talks"
        records = data.get(key)
        if not isinstance(records, list) or not records or not all(map(meaningful, records)):
            raise ValueError("No complete set of meaningful records; review cached content")
        if data.get("conference", {}).get("year") != year:
            raise ValueError("Conference year differs from index directory")
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        return {
            "outcome": "needs-review",
            "reason": str(exc),
            "last_crawled": metadata.get("last_crawled") if isinstance(metadata, dict) else None,
        }
    return {
        "outcome": "cached",
        "records_count": len(records),
        "has_slides": any(record.get("slides_url") for record in records),
        "has_abstracts": any(
            record.get("abstract") or record.get("description") for record in records
        ),
        "last_crawled": data.get("coverage", {}).get("last_crawled"),
        "source": data.get("coverage", {}).get("source", "unrecorded"),
        "completeness": "unverified",
    }


def timestamp() -> str:
    return datetime.now(UTC).isoformat()
