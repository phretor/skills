# Industry venues

Loaded by `ph-seccon` industry mode. This table lists venues and focus only. Cache coverage (which years are cached, which are gaps) lives in `resources/manifest.json`; read it instead of trusting any list here.

| Venue | Manifest slug | Focus |
|---|---|---|
| DEF CON | `defcon` | Broad hacking, underground research |
| Black Hat USA | `blackhat-usa` | Advanced research, enterprise security |
| Black Hat EU | `blackhat-eu` | Same, European edition |
| Black Hat Asia | `blackhat-asia` | Same, Asian edition |
| OffensiveCon | `offensivecon` | Offensive research, exploitation |
| REcon | `recon` | Reverse engineering, binary analysis |
| hardwear.io | `hardwear` | Hardware, embedded, IoT security (YouTube RSS listings) |
| HITCON | `hitcon` | Asia-Pacific, CTF community |
| HITB | `hitb` | Hacking in the Box (KL/Amsterdam) |
| VB Conference | `vb` | Malware, threat intelligence |
| POC | `poc` | Power of Community, Korea |

Venues with an empty `cached` list in the manifest are uncached: report the gap and suggest the maintainer add them. RSA Conference (enterprise, policy, threat intel) is not tracked in the manifest and is uncached.

Academic venues (USENIX Security, IEEE S&P, CCS, NDSS, ACSAC, ACISP) are cached under `resources/academic/` and belong to academic mode. See `references/academic-rankings.md`.
