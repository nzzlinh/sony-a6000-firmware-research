# Knowledge ledger

This ledger separates information verified in this repository from external information that still needs reproduction.

## Confirmed baseline facts

| Claim | Evidence | Status |
| --- | --- | --- |
| Sony lists ILCE-6000 firmware 3.21 as a firmware download released on 2019-03-19 | [Sony support](https://www.sony.com/electronics/support/e-mount-body-ilce-6000-series/ilce-6000/downloads) | Confirmed external; package not yet hashed here |
| REA supports firmware workflows and native analysis through Ghidra, Hopper, or IDA | [REA repository](https://github.com/morluto/rea), [REA setup guide](https://rea.tools/get-started/) | Confirmed external; Ghidra provider reproduced locally |
| REA native investigations combine pseudocode with instructions, callers, references, and constants | [REA native guide](https://rea.tools/guides/native/) | Confirmed external; workflow adopted |
| The local Sony-PMCA-RE checkout contains CXD90014 metadata for `ILCE-6000` | `/home/zeelinh/Sony-PMCA-RE/updatershell/fdat/CXD90014/ILCE-6000.hdr` | Confirmed locally |
| The official 3.21 macOS updater is 214,920,547 bytes and hashes to `844349ff7edddc294c0fddd90a454848eeda8987b6bf043c9757982b3a42ba3e` | `analysis/artifact-manifest.json` and private source file | Confirmed locally |
| The updater body is version `41.01.28` for chassis `CXD90014` | Extracted updater `config/body_version` and `config/chassis` | Confirmed locally |
| `uc_crc32sum.elf` is a stripped ARM EABI5 dynamically linked updater helper built with Sony CE Linux GCC 4.5.1 | REA/Ghidra evidence for the private ELF, archived under `analysis/evidence/` | Confirmed locally |
| The updater's file verifier uses CRC-32/IEEE with a reflected table, `0xffffffff` initial state, and final complement | REA/Ghidra assembly at `0x8a6c` and `0x8a94`, plus table bytes at virtual `0x9408` | Confirmed locally |
| The updater XML reuses the CRC wrapper across configuration, updater, application, partition image, partition configuration, front, CA, Darwin, private-file, backup, accessory, and loader procedures | Extracted updater `config/config.xml` and shell wrappers | Confirmed locally |
| The updater preserves and rewrites backup material around updates and can erase/format selected work or user storage depending on action mode | Extracted `startupdate.sh` and `endupdate.sh` | Confirmed locally; write behavior has not been executed |
| The updater body is a C++ procedure runner with key-tag classes for configuration, application, backup, partition images, updater checksums, and private files | `libupdaterbody.so` dynamic symbols and REA/Ghidra analysis of `UpdaterBody::Execute` | Confirmed locally |
| XML procedure nodes with `thread="yes"` are sent to a thread plugin; other nodes are dispatched synchronously | REA/Ghidra analysis of `XmlConfigHandler::Execute` at `0x237c4` | Confirmed locally |
| Shell modules receive `EXTRACT_ROOT`, the updater body path in `PATH`, and a numeric `UPDATER_ACTION_MODE` before execution | REA/Ghidra analysis of `ShellPlugin::Execute` at `0x23f1c` and extracted shell environment | Confirmed locally |
| Partition image extraction is delegated from `PartitionImageKeyTag` to the common packed-file extractor; application pre-execution mounts the application workspace | REA/Ghidra evidence at `0x20cc0` and `0x20890` | Confirmed locally |

## Prior-art findings awaiting reproduction

[CliffVale's A6000 firmware research](https://github.com/CliffVale/sony-a6000-firmware-research) reports that:

- the published 3.21 updater can be extracted into a firmware tree;
- the tree contains partition images and an updater image;
- an authorized `nflasha` dump can be compared against published partitions;
- the camera contains Android-related runtime material;
- the raw dump includes personal data and should remain private.

These are starting hypotheses. They become findings of this repository only after we record our own input hash, procedure, and verification result.

## Working hypotheses

- A user-space service or application boundary may be more portable than a core imaging function.
- Stable feature signatures will be more useful across firmware versions than absolute addresses.
- A complete platform map will require both updater/package analysis and runtime observations.
- The updater XML is a declarative procedure graph, while shell scripts provide the action-mode and device-mount policy around native helper binaries. This is a strong inference from the XML-to-shell call structure and should be checked against the updater entrypoint.
- `libupdaterbody.so` probably represents the stable control plane of the updater body, with product-specific behavior implemented by key tags, built-in plugins, shell modules, and optional DLL plugins. The class inventory and call path support this interpretation; the dynamic plugin set still needs enumeration.

## Unknowns

- Which exact binaries and processes implement major camera features.
- Which firmware versions are practical for comparison.
- Which first feature offers the best value with the lowest camera risk.
- Which native helper writes each named NAND region, and how the action mode is selected by the update loader.

## Claim record format

```text
Claim:
Status:
Firmware version:
Input artifact and SHA-256:
Binary / partition:
File offset:
Image-relative address:
Virtual address:
Evidence:
Reproduction command or REA prompt:
Limitations:
Next question:
```
