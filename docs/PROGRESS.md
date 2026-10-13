# Progress ledger

Last updated: 2026-10-13

Milestones are complete only when their exit condition in the charter is satisfied. Findings are recorded with their evidence and limitations rather than only in commit messages.

## M0 — Charter and research ledger

Status: **complete**

### Achievements

- Confirmed the research workspace was empty and initialized it as a Git repository.
- Defined the target, scope, safety rules, publication policy, and evidence vocabulary.
- Chosen Sony ILCE-6000 firmware 3.21 as the baseline.
- Added the research README, charter, progress ledger, knowledge ledger, artifact manifest, and private-artifact ignore rules.
- Found the existing local `Sony-PMCA-RE` repository and recorded it as an external tool dependency. It contains A6000 `CXD90014` updater metadata, including `ILCE-6000.hdr`.
- Identified existing public A6000 firmware research as prior art. Its results remain hypotheses until reproduced here.

### M0 evidence

- Workspace: `/home/zeelinh/sony-a6000-reverse-engineering-study`
- Initial state: empty directory, no Git metadata.
- External tool repository: `/home/zeelinh/Sony-PMCA-RE`
- Local tool repository status: pre-existing untracked `.venv/`; no changes made to it.

## M1 — Reproducible acquisition

Status: **complete**

### Question

Can we obtain the official ILCE-6000 3.21 updater, record its provenance and hash, and preserve it privately for extraction?

### Achievements

- Resolved the official Sony redirect to the Sony CDN.
- Downloaded the macOS updater into `/home/zeelinh/sony-a6000-private/firmware-3.21/`.
- Recorded the 214,920,547-byte file and its SHA-256 in `analysis/artifact-manifest.json`.
- Kept the proprietary updater outside this repository.
- Confirmed the host has Python 3.12 and ADB, but no Java/Ghidra, 7-Zip, binwalk, unblob, or installed crypto module.
- Added the package extraction method and resulting payload hash to the extraction record.
- Kept only derived metadata and hashes in the public repository.

## M2 — Verified extraction

Status: **complete**

### Completed so far

- Verified the updater is a DMG containing an HFS+ filesystem.
- Extracted the private `FirmwareData_ILCE6000V321.dat` payload.
- Recorded the payload size and SHA-256 in the artifact manifest.
- Ran `fwtool.py` commit `cdba742b73eed5981480c326aeb30033aabf0223` against the payload.
- Produced a private decrypted tree containing 1,398 files and 1,181,012,182 bytes after recursive filesystem expansion.
- Published a derived file inventory without copying firmware bytes into this repository.
- Verified all five entries in `0701_part_image_sum/part_image.sum` with independent Python CRC32 calculations.
- Published the declared region map from Sony's `0300_partconf/partinf.conf`.

### Evidence

- `analysis/exports/firmware-3.21-inventory.json`
- `analysis/exports/firmware-3.21-part-image-verification.json`
- `docs/02-extraction.md`
- `docs/03-region-map.md`

## M3 — REA/native-analysis baseline

Status: **complete**

### Question

Can we establish a repeatable native-analysis workflow for the ARM updater and archive one useful native case study?

### Current findings

- The updater contains ARM EABI5 ELF helpers and shell scripts.
- The extracted updater has separate procedures for configuration, updater image, application, partition image, partition configuration, front firmware, CA firmware, Darwin firmware, private files, backup, accessory, and loader material.
- A private Node 24, JDK 21, Ghidra 12.1.4, and REA's native-analysis Python environment now pass the REA Ghidra doctor checks. The durable setup result is [rea-ghidra-doctor.json](../analysis/evidence/rea-ghidra-doctor.json).
- REA/Ghidra analyzed `uc_crc32sum.elf`, an ARM EABI5 updater helper with SHA-256 `8e368185be4a074034a3f86a7ff06123ba0936e5cb70fea963009f6f8628f4da`.
- The helper's call path is documented from option parsing (`0x8950`) through dispatch (`0x89c4`), file CRC calculation (`0x8a94` and `0x8a6c`), record validation (`0x8b0c`), and sum-file parsing (`0x8c64`).
- The CRC implementation is confirmed as CRC-32/IEEE: reflected table, initial accumulator `0xffffffff`, 128 KiB maximum read blocks, and final complement.
- The updater XML and shell wrappers show that the same verifier is reused for multiple payload classes before update procedures run.
- Curated, path-safe REA evidence is archived under [`analysis/evidence`](../analysis/evidence), with the case study in [`04-updater-crc32-case.md`](04-updater-crc32-case.md).

### Exit evidence

- `analysis/evidence/rea-ghidra-doctor.json`
- `docs/04-updater-crc32-case.md`
- `analysis/evidence/rea-uc-crc32-0x8950.json`
- `analysis/evidence/rea-uc-crc32-0x89c4.json`
- `analysis/evidence/rea-uc-crc32-0x8a6c.json`
- `analysis/evidence/rea-uc-crc32-0x8a94.json`
- `analysis/evidence/rea-uc-crc32-0x8b0c.json`
- `analysis/evidence/rea-uc-crc32-0x8c64.json`

### Limitations

- The analysis is static and offline; no updater was run against a camera.
- Ghidra pseudocode is a reconstruction, not Sony source code.
- The checksum record's full field semantics still need correlation across more `.sum` files.

## M4 — Platform map

Status: **in progress**

### Question

How does Sony's updater package connect verification, action modes, NAND regions, and the native helpers that write or format those regions?

### Current findings

- `config/config.xml` defines twelve named updater procedures. Most begin with a checksum shell wrapper; several then invoke a subsystem-specific writer or formatter.
- `us_crc32sum.sh` selects ordinary-file mode or image mode, and calls the shared `uc_crc32sum.elf` verifier.
- `startupdate.sh` preserves `Backup.bin` from the setting partition before the update when the camera is in updater mode.
- `endupdate.sh` rewrites backup material, erases the MPR partition, optionally formats user storage, and remounts the setting partition. Its action-mode constants include product, loader/updater, user, service, minor, MSCRYPT, and version-skip modes.
- The package declares a `body_version` of `41.01.28` and chassis `CXD90014` for this updater body.
- `libupdaterbody.so` retains 734 dynamic symbols, including the C++ XML, plugin, key-tag, mount, and packed-file classes.
- `UpdaterBody::Execute` parses packed entries and routes them through key tags; `XmlConfigHandler::Execute` sends threaded XML procedures to a thread plugin and serial procedures to `Plugin::Execute`.
- `Plugin::Execute` dispatches `run` nodes to a DLL plugin and other nodes to `ShellPlugin::Execute`; the shell plugin constructs `EXTRACT_ROOT`, `PATH`, and `UPDATER_ACTION_MODE` before calling `system()`.
- `PartitionImageKeyTag::Extract` delegates image extraction to the common firmware-file extractor, while `ApplicationKeyTag::PreExecute` mounts the application workspace.
- `uc_mkfs.elf` parses `mount.conf` and emits `mkdosfs` commands for FAT-like entries in full mode.
- The common extractor streams both ordinary files and partition image files into the updater workspace; the image extractor does not itself issue a NAND write.
- The mount handler resolves configured device nodes and calls the Linux `mount()` path with `posix_attr` plus mode-dependent sync options.
- The updater checksum key post hook mounts `/dev/nflasha2`, removes `/tmp_updater/updater/current`, and unmounts the setting partition after a successful procedure.

### Next action

Trace the component that consumes workspace images after `PartitionImageKeyTag` extraction and the native helpers that write or format NAND regions, beginning with `edisx.elf`, `pformat_*`, and `ud_wbi_drop.elf`. Then connect those static paths to an authorized read-only runtime observation if suitable hardware is available.

## M5–M8

### M5 — Feature subsystem map

Status: **in progress**

### Question

Which user-space libraries form practical boundaries for USB/PTP, camera-control, live view, and lens research?

### Inputs and prompts

- Firmware input: private `nflasha15` extraction from ILCE-6000 3.21. Every library input is bound by the SHA-256 values in `analysis/exports/firmware-3.21-feature-library-map.json`.
- Symbol inventory: `readelf --dyn-syms --wide <private-a6000-root>/firmware-3.21/fwtool-output/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/<library>`.
- PTP search: `npx -y rea-agents@latest search <private-a6000-root>/.../libInfraPtpControl.so PTPT_init --kind procedures --provider ghidra --format json`.
- PTP function: `npx -y rea-agents@latest function <private-a6000-root>/.../libInfraPtpControl.so PtptIp::InitSocket --provider ghidra --format json`.
- Web API search/function: search `wa_job_startLiveview`, then analyze `WebApiUser::WebApi::wa_job_startLiveview_cmd` with the same REA provider and output format.
- Lens search/function: search `LensCommunicator`, then analyze `LensCommunicator::InitCmd` with the same REA provider and output format.

### Achievements

- Mapped six named libraries from the private `nflasha15` image and published their sizes, SHA-256 digests, roles, and selected dynamic symbols in `analysis/exports/firmware-3.21-feature-library-map.json`.
- Confirmed separate PTP transport entry points for USB, remote, and IP modes in `libInfraPtpControl.so`.
- Used REA/Ghidra on `PtptIp::InitSocket`; the reconstructed path allocates a 64 KiB buffer, creates an IPv4 stream socket, binds and listens, then posts an asynchronous message.
- Mapped the PTP extension-command layer, MTP server, and mass-storage server as adjacent USB-facing research targets from their retained symbols.
- Mapped the web API job layer, including live view, still capture, movie recording, exposure, shutter, focus, white balance, storage, and camera-function handlers.
- Used REA/Ghidra on `wa_job_startLiveview_cmd`; it logs the request, copies a `WebApiIntMsg`, and forwards it to the internal ORB service through `sendMsgToOrb`.
- Mapped the lens communicator's initialization, command/event, supported-command, mounted-lens, backup, and transfer-completion boundaries.
- Used REA/Ghidra on `LensCommunicator::InitCmd`; it allocates and fills an OSAL message, sends it synchronously, checks the response, stores a returned value, and releases the message.
- Recorded `DT_NEEDED` and selected undefined-symbol metadata for all six libraries. This distinguishes direct library dependencies such as MTP → `libptp.so` and extension-command → `libUsbControl.so` from broader process-level symbol sharing.
- Found all six mapped library names in `libIMDB.so` and found `/usr/lib/libInfraWebApi.so` in `bin/orb-server`; recorded both as host candidates with explicit limitations because string presence does not prove runtime loading.
- REA evidence now shows `libIMDB.so` is a target-selection registry candidate: `IMDB_find_entry` matches a 16-bit target ID and bitmask in fixed-size records, and `IMDB_find_target_bit` maps target names to bit positions.
- Identified `libOnDemandLoader.so` as a separate program-load component with singleton initialization and load-program manager methods; its relationship to feature libraries is still unknown.
- Added a public subsystem map with confidence and limitations. Static symbol presence is treated as confirmed; call-graph ownership and runtime use remain open questions.

### Confidence and limitations

- **Confirmed:** the named libraries, sizes, hashes, exported symbols, and the three analyzed function bodies belong to the private 3.21 extraction.
- **Strong inference:** the PTP, extension-command, MTP, and mass-storage libraries form adjacent USB-facing service boundaries; direct `DT_NEEDED` edges are recorded, while caller and load-order edges remain incomplete.
- **Unknown:** host process ownership, runtime load order, protocol field meanings, and cross-version stability.

### Exit evidence so far

- `docs/06-subsystem-map.md`
- `analysis/exports/firmware-3.21-feature-library-map.json`
- `analysis/exports/firmware-3.21-feature-library-dependencies.json`
- `analysis/exports/firmware-3.21-feature-host-candidates.json`
- `analysis/evidence/rea-ptp-transport-init-socket.json`
- `analysis/evidence/rea-webapi-start-liveview-command.json`
- `analysis/evidence/rea-lens-init-command.json`
- `analysis/evidence/rea-imdb-feature-loader-trace.json`
- `analysis/evidence/rea-imdb-find-entry.json`
- `analysis/evidence/rea-imdb-find-target-bit.json`
- `analysis/evidence/rea-ondemand-loader-init.json`

### Next action

Record relocation and caller edges for the PTP, web API, and lens libraries. Then inspect startup configuration and compare the same symbol families across another official firmware package before attempting passive protocol observation.

## M6 — Runtime and protocol observation

Status: **queued**

## M7 — Cross-version comparison and porting boundaries

Status: **queued**

## M8 — Reference-quality porting guide

Status: **queued**

Each milestone will add a dated entry containing the question, inputs and hashes, commands or REA prompts, findings, confidence, limitations, artifacts, and next question.
