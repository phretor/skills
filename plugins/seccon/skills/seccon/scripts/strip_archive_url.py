# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Remove archive_url from all index.json files and update related code."""
import json
from pathlib import Path

BASE = Path(__file__).parent.parent / "resources"

for f in BASE.rglob("index.json"):
    data = json.loads(f.read_text())
    changed = False

    # Remove archive_url from conference level
    if "archive_url" in data.get("conference", {}):
        del data["conference"]["archive_url"]
        changed = True

    # Remove archive_url from individual talks/papers
    for key in ("talks", "papers"):
        if key in data:
            for entry in data[key]:
                if "archive_url" in entry:
                    del entry["archive_url"]
                    changed = True

    if changed:
        f.write_text(json.dumps(data, indent=2))
        print(f"  cleaned: {f}")

print("Done.")
