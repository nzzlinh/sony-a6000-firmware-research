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
| The common updater extractor streams partition images into workspace files; the analyzed image extractor does not issue a NAND write itself | REA/Ghidra evidence at `BaseNewFirmwareFile::Extract`, `NewFirmwareImageFile::extractFile`, and `extractImageFile` | Confirmed locally |
| Mount entries resolve configured device nodes and call Linux `mount()` with `posix_attr` plus mode-dependent synchronization options | REA/Ghidra evidence in `libupdaterbody.so` and `libupdatercommon.so` | Confirmed locally |
| The updater checksum key post hook mounts the setting partition, removes `/tmp_updater/updater/current`, and unmounts it after a successful procedure | REA/Ghidra evidence at `0x20250` | Confirmed locally |
| `nflasha15` contains a PTP transport library with common, USB, remote, and IP init/data/event APIs | `analysis/exports/firmware-3.21-feature-library-map.json`; private `libInfraPtpControl.so` hash `8b9c77a835593d5a963c0b56dc59ebd202648bd4e361524f48f4f2849631b81c` | Confirmed locally |
| `PtptIp::InitSocket` allocates a 64 KiB buffer, creates an IPv4 stream socket, binds/listens, and posts an asynchronous message | REA/Ghidra evidence in `analysis/evidence/rea-ptp-transport-init-socket.json` | Confirmed locally; socket field semantics remain incomplete |
| `nflasha15` has separate PTP extension-command, MTP, and mass-storage server libraries with command, media, filesystem, and VBUS state-machine symbols | `analysis/exports/firmware-3.21-feature-library-map.json` and private ELF dynamic symbols | Confirmed locally as symbol metadata; direct call edges remain unverified |
| `libInfraWebApi.so` exports named command/event/completion jobs for live view, still capture, movie recording, exposure, shutter, focus, white balance, storage, and camera-function operations | `analysis/exports/firmware-3.21-feature-library-map.json` and private ELF dynamic symbols | Confirmed locally as symbol metadata |
| `wa_job_startLiveview_cmd` forwards a copied `WebApiIntMsg` to the internal ORB service after logging request fields | REA/Ghidra evidence in `analysis/evidence/rea-webapi-start-liveview-command.json` | Confirmed locally; ORB message field semantics remain unknown |
| `libInfraLensCommunicator.so` exposes lens command/event, supported-command, mounted-lens, backup, and transfer-completion boundaries | `analysis/exports/firmware-3.21-feature-library-map.json` and private ELF dynamic symbols | Confirmed locally as symbol metadata |
| `LensCommunicator::InitCmd` sends an initialized OSAL message synchronously and propagates the returned value/status | REA/Ghidra evidence in `analysis/evidence/rea-lens-init-command.json` | Confirmed locally; message field meanings remain unknown |
| MTP directly declares `libptp.so`; the PTP extension library directly declares `libUsbControl.so` and imports PTP packet helpers | `analysis/exports/firmware-3.21-feature-library-dependencies.json` | Confirmed locally from ELF metadata |
| `libIMDB.so` contains strings naming all six mapped feature libraries | `analysis/exports/firmware-3.21-feature-host-candidates.json` and `analysis/evidence/rea-imdb-feature-loader-trace.json` | Confirmed locally as string metadata; runtime loading is unproven |
| `libIMDB.so` exports target-selection functions; `IMDB_find_entry` scans records by target ID and mask, and `IMDB_find_target_bit` maps target names to bit positions | `analysis/evidence/rea-imdb-find-entry.json` and `analysis/evidence/rea-imdb-find-target-bit.json` | Confirmed locally; registry callers remain unknown |
| `bin/orb-server` contains `/usr/lib/libInfraWebApi.so` but does not list it in `DT_NEEDED` | `analysis/exports/firmware-3.21-feature-host-candidates.json` | Confirmed locally; host ownership is a working hypothesis |
| `libOnDemandLoader.so` contains singleton initialization and load-program manager methods | `analysis/exports/firmware-3.21-feature-host-candidates.json` and `analysis/evidence/rea-ondemand-loader-init.json` | Confirmed locally; relationship to feature-library loading is unknown |

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
- The PTP control, extension-command, MTP, and mass-storage libraries probably form a USB-facing service stack, but the current map only proves named interfaces and not direct runtime ownership.
- The web API job handlers probably form a stable message boundary for camera-control features; the live-view case shows forwarding into an internal ORB service, while the sensor and encoder implementation remains downstream.
- `libIMDB.so` may be a feature-library registry or selection point because it names all six libraries; the absence of a recovered loader procedure leaves this as a strong inference only.
- `orb-server` may consume the web API library through configuration or an indirect loader path because it contains the library pathname without a `DT_NEEDED` edge; this remains a working hypothesis.
- `libIMDB.so` likely stores target-selection metadata rather than directly loading every feature library; its exported lookup functions and fixed-size record scan support this narrower interpretation.

## Unknowns

- Which exact binaries and processes implement major camera features.
- Which firmware versions are practical for comparison.
- Which first feature offers the best value with the lowest camera risk.
- Which native helper writes each named NAND region, and how the action mode is selected by the update loader.
- Which processes load the feature libraries, and which `DT_NEEDED` or relocation edges connect the transport, command, camera-control, and lens layers.
- What the PTP extension command IDs, ORB message IDs, and lens message fields mean on a live camera.
- Whether the `libIMDB.so` and `orb-server` string references correspond to `dlopen`, a static registry, diagnostic data, or another startup mechanism.
- Which component consumes the `IMDB_find_entry` result and how target bits select optional Sony modules.

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
