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
- Hash-bound, metadata-only REA evidence records are published under [`analysis/evidence`](../analysis/evidence), with full REA output retained in the private research archive and the case study in [`04-updater-crc32-case.md`](04-updater-crc32-case.md).

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
- Private Ghidra pseudocode is a reconstruction, not Sony source code; the public evidence records now retain metadata only.
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

Status: **complete**

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

The static subsystem map is sufficient to begin M6. Remaining caller and load-order questions are carried forward as M6/M7 research questions.

### M5 follow-up — network stack map

Status: **complete for the static 3.21 slice**

### Question

How is the camera's network feature stack divided between WLAN hardware control, connection policy, discovery, remote control, and live-view delivery?

### Inputs and prompts

- Private `nflasha15` shared objects, bound by the hashes in [`firmware-3.21-network-stack-map.json`](../analysis/exports/firmware-3.21-network-stack-map.json).
- `readelf --dyn-syms --wide`, `readelf --dynamic`, and `strings -a` against the private network libraries.
- REA/Ghidra function analyses for `WlanControlCommon::initializePort`, `NetServiceArbitrator::procAsyncReqStartFunc`, `RcWebAPIStartLiveviewComeback`, `ContentHandlerEEImpl::GetLiveViewJpeg`, and `MDnsControl::RegisterOneService`.

### Achievements

- Separated WLAN board bring-up (`libWlanControlCommon.so`) from WLAN resource and product-mode orchestration (`libWlanResource.so`). The analyzed initialization path opens `/dev/mem` and `/dev/gpio`, maps registers, sets GPIO modes, and exposes explicit AR6000 driver/firmware paths.
- Mapped the connection-policy layer in `libInfraNetConnectionManager.so`, including AP, WPS, group-owner, UPnP, and auto-connect commands/events. REA confirmed MWF request/response, command tracking, and fake-completion recovery.
- Confirmed an mDNS registration boundary in `libInfraMDnsControl.so`; its analyzed function converts service arguments and calls `mDNS_RegisterService`, then assigns and tracks service IDs.
- Confirmed `libInfraNetFunctionManager.so` as an UPnP and streaming-function coordinator from its imported `StartUpnpDevice`/`StopUpnpDevice` methods and streaming-server message jobs.
- Mapped network remote control in `libInfraRemoteControlNet.so`, including Web API camera-state setters/getters, live-view URI/state, and a remote-state gate for live-view comeback.
- Mapped `libInfraStreamingServer.so` as the JPEG delivery boundary. REA confirmed an OSAL frame request, readiness loop, and JPEG mapping path; the library also imports URL, port, filename, and IP lookup methods.
- Mapped `libNetService.so` as a static TLS/crypto boundary. It contains TLS record wrappers, RSA/PKCS#1 helpers, software AES-128-CBC, and the Rijndael block routine.
- Confirmed that the AES-CBC wrapper has no visible byte-rate limiter. The TLS wrappers reserve `input + 300` bytes for encryption and `input * 3 + 1500` bytes for decryption; these are allocation policies rather than speed caps.
- Established the current throughput conclusion: with SD-card reads excluded, firmware alone does not yield a numeric MB/s limit. The bound is the minimum of effective WLAN/socket rate, software AES/TLS rate, and the network-service producer/consumer path.
- Kept the “AES-CBC-RSA” label conditional: RSA/PKCS#1 and AES-CBC support are confirmed, but the caller-selected cipher suite and undefined `tlsv1_client_*` provider are unresolved.
- Added the layered network reference note and machine-readable inventory.

### Confidence and limitations

- **Confirmed:** library identities, hashes, sizes, direct dependencies, exported symbols, selected message/state behavior, mDNS registration, and JPEG retrieval path.
- **Strong inference:** the layered graph and the upper network boundaries are practical porting seams.
- **Unknown:** process ownership, service metadata, endpoint/framing protocol, authentication, complete message layouts, and cross-version stability.
- **Not performed:** no camera was connected and no network or firmware write was issued.

### Exit evidence

- [`docs/08-network-stack.md`](08-network-stack.md)
- [`analysis/exports/firmware-3.21-network-stack-map.json`](../analysis/exports/firmware-3.21-network-stack-map.json)
- [`analysis/evidence/rea-wlan-initialize-port.json`](../analysis/evidence/rea-wlan-initialize-port.json)
- [`analysis/evidence/rea-net-start.json`](../analysis/evidence/rea-net-start.json)
- [`analysis/evidence/rea-mdns-register.json`](../analysis/evidence/rea-mdns-register.json)
- [`analysis/evidence/rea-remote-liveview.json`](../analysis/evidence/rea-remote-liveview.json)
- [`analysis/evidence/rea-stream-liveview.json`](../analysis/evidence/rea-stream-liveview.json)
- [`analysis/evidence/rea-netservice-tls-encrypt.json`](../analysis/evidence/rea-netservice-tls-encrypt.json)
- [`analysis/evidence/rea-netservice-tls-decrypt.json`](../analysis/evidence/rea-netservice-tls-decrypt.json)
- [`analysis/evidence/rea-netservice-tls-set-cipher.json`](../analysis/evidence/rea-netservice-tls-set-cipher.json)
- [`analysis/evidence/rea-netservice-aes128-cbc-encrypt.json`](../analysis/evidence/rea-netservice-aes128-cbc-encrypt.json)
- [`analysis/evidence/rea-netservice-aes-encrypt.json`](../analysis/evidence/rea-netservice-aes-encrypt.json)
- [`analysis/evidence/rea-netservice-crypto-cipher-encrypt.json`](../analysis/evidence/rea-netservice-crypto-cipher-encrypt.json)

### Next action

Recover callers and relocation edges for service metadata and endpoint construction, then compare the static map with a passive network capture if a camera is available.

### Publication and licensing boundary

Status: **complete for the current public tree**

### Question

Which project material can be openly licensed, and which firmware-derived material must remain outside that license?

### Achievements

- Added component-specific licensing: MIT for original scripts and CC BY 4.0 for original documentation.
- Added a root license policy, third-party notices, a publication policy, and an independent-project/trademark statement.
- Replaced the public REA JSON dossiers with 47 metadata-only, hash-bound records. They retain evidence IDs, input hashes, analysis provenance, procedure identity, and limitations while omitting pseudocode, assembly, strings, references, and native value-flow data.
- Archived the full REA dossiers in `/home/zeelinh/sony-a6000-private/` outside the repository.
- Rewrote the local and public Git history so the previous raw evidence files are no longer reachable from `main`; the public remote now points to the cleaned history.

### Exit evidence

- [`LICENSE`](../LICENSE)
- [`LICENSE-CODE`](../LICENSE-CODE)
- [`LICENSE-DOCS`](../LICENSE-DOCS)
- [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md)
- [`docs/09-licensing-and-publication.md`](09-licensing-and-publication.md)
- [`analysis/evidence/README.md`](../analysis/evidence/README.md)

### Limitations

- This is a publication-risk boundary, not a jurisdiction-specific legal opinion.
- Sony's exact ILCE-6000 EULA and the law applicable to each contributor still need to be checked before distributing firmware-derived material beyond the current metadata-only form.

## M6 — Runtime and protocol observation

Status: **in progress**

### Question

How does the PC-side Sony protocol reach the firmware service boundaries, and what is the smallest safe read-only exchange for validating the static map?

### Inputs and commands

- External source: `/home/zeelinh/Sony-PMCA-RE`, remote `https://github.com/ma1co/Sony-PMCA-RE.git`, commit `a82f5baaa8e9c3d9f28f94699e860fb2e48cc8e0`.
- Read-only source inspection: `pmca/usb/sony.py`, `pmca/usb/__init__.py`, `pmca/usb/driver/windows/wpd.py`, and `pmca/platform/backend/usb/transfer.py`.
- Reproduction commands: `git rev-parse HEAD`, `sha256sum <source files>`, and line-oriented inspection of the Sony MTP and extension-command classes.

### Achievements

- Recorded normal PTP operations `0x1001`–`0x1003` and Sony operations `0x9280`–`0x9285`.
- Documented the Sony extension header as a 16-byte little-endian structure containing `dataSize`, `cmd`, `direction`, and eight reserved bytes.
- Documented the MTP write/read sequences, PTP `DeviceBusy` retry code `0x2019`, and the mass-storage extension envelope beginning with operation `0x7a`.
- Recorded service IDs for the lens communicator, backup communicator, device information, and network-service commands.
- Connected the host comment identifying the MTP operation codes as defined by `libInfraMtpServer.so` to the firmware symbol map.
- Added a bounded first-capture procedure centered on the read-only `(6, 2)` mounted-lens command.

### Confidence and limitations

- **Confirmed:** host-side packet and structure encoding from the pinned source files and their hashes.
- **Strong inference:** `(6, 2)` is a useful static-to-wire lens path because it maps to both host command code and firmware `LensCommunicator` symbols.
- **Unknown:** actual ILCE-6000 response bytes, USB descriptors in the tested mode, command enablement on firmware 3.21, and any payload fields not defined by the host source.

### Exit evidence so far

- `docs/07-usb-ptp-protocol-boundary.md`
- `analysis/exports/host-ptp-command-map.json`

### Next action

If an explicitly authorized camera is available, capture a normal MTP session and one read-only mounted-lens request. Otherwise continue static reconstruction of the host candidate and firmware service callers without issuing camera commands.

## M7 — Cross-version comparison and porting boundaries

Status: **queued**

## M8 — Reference-quality porting guide

Status: **queued**

Each milestone will add a dated entry containing the question, inputs and hashes, commands or REA prompts, findings, confidence, limitations, artifacts, and next question.
