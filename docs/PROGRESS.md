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

### Next action

Trace the post-extraction key-tag hooks and native helpers that write or format NAND regions, beginning with `PartitionImageKeyTag`, `MountEntryHandler`, `edisx.elf`, `pformat_*`, and `ud_wbi_drop.elf`. Then connect those static paths to an authorized read-only runtime observation if suitable hardware is available.

## M5–M8

Status: **queued**

Each milestone will add a dated entry containing the question, inputs and hashes, commands or REA prompts, findings, confidence, limitations, artifacts, and next question.
