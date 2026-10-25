# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Generate manifest.json from current cache state."""
import json
from datetime import date
from pathlib import Path

RESOURCES = Path(__file__).parent.parent / "skills" / "ph-seccon" / "resources"
MANIFEST = RESOURCES / "manifest.json"
VERSION = "1.4.0"
EARLIEST_YEAR = 2021


def cached_years() -> list[int]:
    """Return every year that has at least one index.json on disk."""
    years = {
        int(path.parent.parent.name)
        for path in RESOURCES.glob("*/*/*/index.json")
        if path.parent.parent.name.isdigit()
    }
    return sorted(years)


YEARS = list(range(EARLIEST_YEAR, max(cached_years()) + 1))

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

manifest = {
    "version": VERSION,
    "generated": date.today().isoformat(),
    "cached_range": {"earliest": YEARS[0], "latest": YEARS[-1]},
    "coverage": {"academic": {"venues": {}}, "industry": {"venues": {}}},
}

for slug in sorted(VENUE_NAMES):
    cached = []
    for year in YEARS:
        idx = RESOURCES / "academic" / str(year) / slug / "index.json"
        if idx.exists():
            cached.append(year)
    gaps = sorted(set(YEARS) - set(cached))
    note = "DBLP unreachable from this environment" if not cached else ""
    manifest["coverage"]["academic"]["venues"][slug] = {"cached": sorted(cached), "gaps": gaps, "note": note}

# Industry venues — scan filesystem for what's cached
INDUSTRY_SLUGS = ["defcon", "offensivecon", "recon", "blackhat-usa", "blackhat-eu", "blackhat-asia",
                  "hardwear", "hitcon", "hitb", "vb", "poc"]
for slug in INDUSTRY_SLUGS:
    cached = []
    for year in YEARS:
        idx = RESOURCES / "industry" / str(year) / slug / "index.json"
        if idx.exists():
            cached.append(year)
    gaps = sorted(set(YEARS) - set(cached))
    note = ""
    if not cached:
        if slug in ("blackhat-usa", "blackhat-eu", "blackhat-asia"):
            note = "Cloudflare blocked"
        else:
            note = "Not yet crawled"
    manifest["coverage"]["industry"]["venues"][slug] = {"cached": sorted(cached), "gaps": gaps, "note": note}

MANIFEST.write_text(json.dumps(manifest, indent=2))

# Summary
total_ac = sum(len(v["cached"]) for v in manifest["coverage"]["academic"]["venues"].values())
total_ind = sum(len(v["cached"]) for v in manifest["coverage"]["industry"]["venues"].values())
print(f"Total: {total_ac} academic venue-years, {total_ind} industry venue-years")
print(f"Manifest written to {MANIFEST}")

# Count papers/talks
for mode in ("academic", "industry"):
    for slug in manifest["coverage"][mode]["venues"]:
        for year in manifest["coverage"][mode]["venues"][slug]["cached"]:
            idx = RESOURCES / mode / str(year) / slug / "index.json"
            if idx.exists():
                data = json.loads(idx.read_text())
                key = "papers" if mode == "academic" else "talks"
                count = data["coverage"].get(f"{key}_count", 0)
                print(f"  {mode:10s} {slug:20s} {year}: {count} {key}")
