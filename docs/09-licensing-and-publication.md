# Licensing and publication policy

This project separates original research work from material derived from Sony
firmware. The separation makes the reusable part of the reference clear while
avoiding a claim that the project can license Sony's software.

## Component licenses

| Path or material | Policy |
| --- | --- |
| `scripts/` | MIT; see [`LICENSE-CODE`](../LICENSE-CODE) |
| Original prose in `README.md` and `docs/` | CC BY 4.0; see [`LICENSE-DOCS`](../LICENSE-DOCS) |
| `analysis/exports/` | Derived research metadata; no blanket ownership claim over third-party-derived elements |
| `analysis/evidence/` | Metadata-only public records; no license granted over Sony-derived material |
| Sony firmware, updater, dumps, keys, and private camera data | Kept outside the repository and never covered by project licenses |

The root [`LICENSE`](../LICENSE) explains this component-specific structure.
The full attribution and third-party boundary are in
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).

## Public evidence format

REA can produce pseudocode, assembly, strings, references, and native value
flows from a binary. Those fields can reproduce or closely derive from the
binary under analysis. The public evidence records therefore retain only the
input hash, analysis provenance, procedure identity, limitations, and a note
pointing to the human-reviewed milestone document. Full REA results remain in
the private research archive.

This is a publication policy, not a conclusion that every individual fact or
short symbol name is protected by copyright. The project does not make a legal
determination about Sony's rights or the law of any particular jurisdiction.

## Review before publication

Before pushing a release, check that it contains no firmware bytes, executable
firmware images, decrypted filesystem, raw dump, personal data, credentials,
private keys, or long decompiler/assembly reproduction. Keep the source hash,
tool version, procedure, and a concise finding so another authorized researcher
can reproduce the work privately.
