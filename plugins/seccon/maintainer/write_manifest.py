# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Describe cache availability, record quality, acquisition age and refresh results."""

import argparse
import json
from datetime import date
from pathlib import Path

from cache_io import index_quality, write_json

RESOURCES = Path(__file__).parent.parent / "skills" / "ph-seccon" / "resources"
VERSION = "1.5.0"
EARLIEST_YEAR = 2021

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
    "pets": ("Privacy Enhancing Technologies Symposium", "PETS"),
    "eurosp": ("IEEE European Symposium on Security and Privacy", "EuroS&P"),
    "fc": ("Financial Cryptography and Data Security", "FC"),
    "raid": ("Recent Advances in Intrusion Detection", "RAID"),
    "imc": ("Internet Measurement Conference", "IMC"),
    "ches": ("Cryptographic Hardware and Embedded Systems", "CHES"),
    "acisp": ("Australasian Conference on Information Security and Privacy", "ACISP"),
    "dimva": ("Detection of Intrusions and Malware and Vulnerability Assessment", "DIMVA"),
}


INDUSTRY_SLUGS = [
    "defcon",
    "offensivecon",
    "recon",
    "blackhat-usa",
    "blackhat-eu",
    "blackhat-asia",
    "hardwear",
    "hitcon",
    "hitb",
    "vb",
    "poc",
]


def cached_years(resources: Path | None = None) -> list[int]:
    root = resources if resources is not None else RESOURCES
    return sorted(
        {int(p.parts[-3]) for p in root.glob("*/*/*/index.json") if p.parts[-3].isdigit()}
    )


def venue_coverage(root: Path, mode: str, slug: str, years: list[int]) -> dict:
    cached, quality, attempts = [], {}, {}
    for year in years:
        directory = root / mode / str(year) / slug
        index = directory / "index.json"
        if index.is_file():
            cached.append(year)
            quality[str(year)] = index_quality(index, year=year)
        refresh = directory / "refresh.json"
        if refresh.is_file():
            try:
                value = json.loads(refresh.read_text())
                if not isinstance(value, dict):
                    raise ValueError("Refresh result must be an object")
                attempts[str(year)] = value
            except (OSError, ValueError) as exc:
                attempts[str(year)] = {"outcome": "invalid-refresh-record", "reason": str(exc)}
    return {
        "cached": cached,
        "gaps": sorted(set(years) - set(cached)),
        "note": "Availability does not establish completeness or permission to refresh",
        "quality": quality,
        "refresh": attempts,
    }


def build_manifest(resources: Path | None = None) -> dict:
    """Preserve every cached edition and flag invalid content without deleting indexes."""
    root = resources if resources is not None else RESOURCES
    disk_years = cached_years(root)
    years = list(
        range(min([EARLIEST_YEAR, *disk_years]), max([date.today().year, *disk_years]) + 1)
    )
    manifest = {
        "version": VERSION,
        "generated": date.today().isoformat(),
        "cached_range": {"earliest": years[0], "latest": years[-1]},
        "coverage": {},
    }
    for mode, venues in (("academic", VENUE_NAMES), ("industry", INDUSTRY_SLUGS)):
        manifest["coverage"][mode] = {
            "venues": {slug: venue_coverage(root, mode, slug, years) for slug in sorted(venues)}
        }
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=RESOURCES, help="Resource cache root")
    args = parser.parse_args()
    manifest = build_manifest(args.output_dir)
    write_json(args.output_dir / "manifest.json", manifest)
    print(f"Manifest written to {args.output_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
