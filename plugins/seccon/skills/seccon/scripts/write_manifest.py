# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Generate manifest.json from current cache state."""
import json
from pathlib import Path

RESOURCES = Path(__file__).parent.parent / "resources"
MANIFEST = RESOURCES / "manifest.json"
YEARS = [2021, 2022, 2023, 2024, 2025]

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
    "csf": ("IEEE Computer Security Foundations Symposium", "CSF"),
    "asiacrypt": ("International Conference on Theory and Application of Cryptology", "Asiacrypt"),
    "tcc": ("Theory of Cryptography Conference", "TCC"),
    "fc": ("Financial Cryptography and Data Security", "FC"),
    "raid": ("Recent Advances in Intrusion Detection", "RAID"),
    "imc": ("Internet Measurement Conference", "IMC"),
    "ches": ("Cryptographic Hardware and Embedded Systems", "CHES"),
    "soups": ("Symposium on Usable Privacy and Security", "SOUPS"),
    "acns": ("Applied Cryptography and Network Security", "ACNS"),
    "acisp": ("Australasian Conference on Information Security and Privacy", "ACISP"),
    "ifip-sec": ("IFIP Information Security and Privacy Conference", "IFIP SEC"),
    "wisec": ("ACM Conference on Security and Privacy in Wireless and Mobile Networks", "WiSec"),
    "dimva": ("Detection of Intrusions and Malware and Vulnerability Assessment", "DIMVA"),
    "icics": ("International Conference on Information and Communications Security", "ICICS"),
    "securecomm": ("International Conference on Security and Privacy in Communication Networks", "SecureComm"),
    "pst": ("Privacy, Security and Trust", "PST"),
    "pkc": ("International Conference on Practice and Theory in Public-Key Cryptography", "PKC"),
    "sac": ("Selected Areas in Cryptography", "SAC"),
}

manifest = {
    "version": "1.3.0",
    "generated": "2026-04-24",
    "cached_range": {"earliest": 2021, "latest": 2025},
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
                  "hardwear", "infiltrate", "hitcon", "hitb", "vb", "poc"]
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
