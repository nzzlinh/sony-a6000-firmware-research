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
| `libWlanControlCommon.so` owns WLAN port initialization, driver installation/removal, firmware loading, and start/stop checks | `analysis/exports/firmware-3.21-network-stack-map.json` and `analysis/evidence/rea-wlan-initialize-port.json` | Confirmed locally as a static boundary |
| `WlanControlCommon::initializePort` opens `/dev/mem` and `/dev/gpio`, maps a 4 KiB register window, performs GPIO mode ioctls, adjusts control registers, waits, and records failures | `analysis/evidence/rea-wlan-initialize-port.json` | Confirmed locally from REA/Ghidra; exact register semantics remain unknown |
| `libWlanResource.so` provides higher-level WLAN resource orchestration, including start/stop requests, host-driver load/unload, target-board initialization, and a main thread | `analysis/exports/firmware-3.21-network-stack-map.json` and private ELF symbols/strings | Confirmed locally as symbol metadata; caller and product-mode selection remain unknown |
| `libInfraNetConnectionManager.so` exposes AP, WPS, group-owner, UPnP, auto-connect, saved-AP, completion, and event command boundaries | `analysis/exports/firmware-3.21-network-stack-map.json` and private ELF strings | Confirmed locally as symbol/string metadata |
| `NetServiceArbitrator::procAsyncReqStartFunc` uses MWF send/receive, command tracking, an internal function counter, and fake-completion recovery | `analysis/evidence/rea-net-start.json` | Confirmed locally from REA/Ghidra; message payload fields remain unknown |
| `libInfraMDnsControl.so` registers mDNS services from name, type, domain, TXT data, and port arguments, then tracks service records and IDs | `analysis/evidence/rea-mdns-register.json` | Confirmed locally from REA/Ghidra |
| `libInfraNetFunctionManager.so` coordinates UPnP start/stop and forwards messages to `InfraStreamingServer` | `analysis/exports/firmware-3.21-network-stack-map.json` and private ELF symbols/strings | Confirmed locally as symbol/import metadata; process ownership remains unknown |
| `libInfraRemoteControlNet.so` bridges network Web API requests to camera-state setters/getters and live-view state/URI operations | `analysis/exports/firmware-3.21-network-stack-map.json` and private ELF symbols | Confirmed locally as symbol metadata |
| `RcWebAPIStartLiveviewComeback` requires remote-control state and a live-view state bit before calling an internal recovery routine | `analysis/evidence/rea-remote-liveview.json` | Confirmed locally from REA/Ghidra; state value `4` is not yet assigned a public semantic name |
| `libInfraStreamingServer.so` contains live-view start/stop jobs, URL/port/filename lookup imports, JPEG content handlers, and network-service start/stop | `analysis/exports/firmware-3.21-network-stack-map.json` and private ELF symbols | Confirmed locally as symbol/import metadata |
| `ContentHandlerEEImpl::GetLiveViewJpeg` requests frames through a synchronous OSAL message and maps the returned JPEG by ID and size | `analysis/evidence/rea-stream-liveview.json` | Confirmed locally from REA/Ghidra; frame message fields remain unknown |
| `libNetService.so` exports TLS connection wrappers, AES-128-CBC helpers, RSA/PKCS#1 helpers, and software Rijndael encryption | `analysis/exports/firmware-3.21-network-stack-map.json` and private ELF symbols | Confirmed locally as a static crypto boundary |
| The AES-128-CBC wrapper processes 16-byte blocks with a 16-byte key and IV and has no visible byte-rate limiter | `analysis/evidence/rea-netservice-aes128-cbc-encrypt.json`, `analysis/evidence/rea-netservice-aes-encrypt.json` | Confirmed locally from REA/Ghidra; caller padding and runtime timing remain unknown |
| The TLS encryption wrapper allocates input length plus 300 bytes, while the decryption wrapper allocates three times input length plus 1500 bytes | `analysis/evidence/rea-netservice-tls-encrypt.json`, `analysis/evidence/rea-netservice-tls-decrypt.json` | Confirmed locally as allocation policy; these values are not transfer-rate limits |
| The TLS cipher-list wrapper forwards a caller-supplied cipher list; the selected AES-CBC/RSA suite is not recovered | `analysis/evidence/rea-netservice-tls-set-cipher.json` | Confirmed locally; `tlsv1_client_*` core routines are undefined imports |
| With SD-card reads excluded, static firmware evidence gives no numeric MB/s limit; throughput is bounded by WLAN/socket service, software AES/TLS processing, and the consuming producer/consumer path | `docs/08-network-stack.md` and the crypto REA dossiers | Confirmed as a static conclusion; camera-side benchmark still required |
| The pinned Sony-PMCA-RE host implementation uses Sony MTP operations `0x9280`–`0x9285` for extension write/read, reconnect, burst-shot, and AV-index operations | `analysis/exports/host-ptp-command-map.json`; external source commit `a82f5baaa8e9c3d9f28f94699e860fb2e48cc8e0` | Confirmed locally from read-only source |
| Sony extension requests use a 16-byte little-endian header with data size, command ID, direction, and eight reserved bytes | `analysis/exports/host-ptp-command-map.json` and pinned `pmca/usb/sony.py` | Confirmed locally from read-only source |
| The host maps `(6, 2)` to `LensCommunicator_GetMountedLensInfo` and retries MTP operations while response `0x2019` indicates device busy | `analysis/exports/host-ptp-command-map.json` | Confirmed locally from read-only source; camera response not captured |
| The previous public maps covered camera-control and JPEG delivery boundaries but did not cover the color/image processing implementation | `docs/06-subsystem-map.md`, `docs/07-usb-ptp-protocol-boundary.md`, `docs/08-network-stack.md`, `docs/10-image-processing.md` | Confirmed locally from the repository's documented scope |
| `libScalarDaemon.so` exports camera color/image parameter and filter boundaries, including RGB matrix, color depth, white-balance shift, contrast, saturation, sharpness, color space, picture effects, and extended gamma operations | `analysis/exports/firmware-3.21-image-processing-map.json`; `analysis/evidence/rea-image-scalar-rgbmatrix.json`; `analysis/evidence/rea-image-scalar-filter-art.json`; `analysis/evidence/rea-image-scalar-gamma.json` | Confirmed locally as symbol metadata; REA shows RGB-matrix, art-effect, and extended-gamma functions package typed parameters and emit events; downstream pixel effect is not yet traced |
| `CameraSettingInheritance::setWhiteBalanceParameters` normalizes a white-balance mode through parameter storage and may apply a model-derived offset before values are stored | `analysis/exports/firmware-3.21-image-processing-map.json`; `analysis/evidence/rea-image-scalar-wb-inherit.json` | Confirmed locally from REA/Ghidra; the later camera-event dispatch path remains separate |
| `dataflowInfraFramework.so` exports raw, YC state/colorimetry, effect, image-size, output-timing, display, camera, face, and movie-quality data records | `analysis/exports/firmware-3.21-image-processing-map.json`; private ELF dynamic symbols | Confirmed locally as a static data contract |
| `libStm.so` exposes image-instance operations and raw parsing, while `libmpr.so` exposes still encode, still write/read/playback, RAW development, record definition, and XvYCC metadata operations | `analysis/exports/firmware-3.21-image-processing-map.json`; `analysis/evidence/rea-image-stm-rawparse.json`; private ELF dynamic symbols | Confirmed locally as static boundaries; REA shows raw parsing issuing an asynchronous dataflow request and copying a bounded metadata response; MPR callers and parameter layouts remain unknown |
| `libBizFw.so` exposes `OBJAVBBCBASECLASS::SdfCh::decodeJpeg`; REA shows it validating a decode command and forwarding it through an AVBBC acknowledgement channel | `analysis/exports/firmware-3.21-image-processing-map.json`; `analysis/evidence/rea-image-bizfw-decodejpeg.json` | Confirmed locally as a service-channel wrapper; JPEG engine and payload selection remain downstream unknowns |
| A full REA/Ghidra pass over the 10.3 MiB `libmpr.so` exceeded the 330-second provider timeout while analyzing `MprIf::EncodeStill` | `analysis/exports/firmware-3.21-image-processing-map.json`; private REA timeout record | Tooling limitation; MPR's static boundary is confirmed, but its implementation and caller chain remain unresolved |
| The `nflasha15/sabin` inventory contains named JPEG, AVC, noise-reduction, sharpening, detection, panorama, and still/movie table payloads | `analysis/exports/firmware-3.21-image-processing-map.json`; private file inventory | Confirmed locally as payload filenames; loader and runtime roles remain unknown |
| `CAMERA_SCN_EXTERNAL_RAW_RECORD.so` is an explicit RAW-record scenario module, and neighboring media/object libraries expose diagnostic raw-YC/JPEG/display controls | `analysis/exports/firmware-3.21-image-processing-map.json`; private scenario and ELF metadata | Confirmed locally as scenario/diagnostic boundaries; ordinary RAW/JPEG production is not yet connected |

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
- Sony's network code appears layered from board bring-up through connection arbitration, service discovery, remote-control state, and live-view content delivery. The layer boundaries are confirmed; the complete process graph is still a hypothesis.
- `libInfraNetConnectionManager.so` likely arbitrates mutually exclusive network functions and synthesizes completions when a start request arrives while a function is already active. REA shows this behavior, but the policy table and all state meanings are not recovered.
- `libInfraNetFunctionManager.so` likely acts as the coordinator between UPnP/device description and the streaming server because it imports UPnP start/stop methods and exposes streaming-server message jobs.
- The most promising network porting seam is the remote-control/Web API and streaming boundary. WLAN bring-up is lower-level board code and should be deferred unless the feature changes radio behavior.
- `libNetService.so` is a likely TLS/crypto boundary for at least one network service because it owns TLS adapter wrappers and software AES/RSA helpers; the exact transfer caller remains unresolved.
- For a large file, RSA should be a handshake/key-management cost while AES-CBC scales linearly with payload bytes. If SD reads do not matter, the limiting term should be the minimum of effective WLAN throughput, software AES/TLS throughput, and the network-service producer/consumer path.
- `libScalarDaemon.so` likely provides the camera color/image setting control plane, while `libmpr.so` and `libStm.so` provide media and image-instance boundaries behind the shared YC/dataflow framework. REA confirms the scalar setter/event and STM request/response patterns; the exact sensor/ISP and accelerator paths remain open.
- The `sabin/` payload names likely represent lower-level image/video engines or tables. Their names identify useful REA targets, but they do not prove a loader, instruction set, or parameter ABI.

## Unknowns

- Which exact binaries and processes implement major camera features.
- Which firmware versions are practical for comparison.
- Which first feature offers the best value with the lowest camera risk.
- Which native helper writes each named NAND region, and how the action mode is selected by the update loader.
- Which processes load the feature libraries, and which `DT_NEEDED` or relocation edges connect the transport, command, camera-control, and lens layers.
- What the PTP extension command IDs, ORB message IDs, and lens message fields mean on a live camera.
- Whether the `libIMDB.so` and `orb-server` string references correspond to `dlopen`, a static registry, diagnostic data, or another startup mechanism.
- Which component consumes the `IMDB_find_entry` result and how target bits select optional Sony modules.
- How the host's `(6, 2)` lens command appears on USB and which response fields correspond to `MountedLensInfo`.
- Which process loads each network library, and in what order WLAN, connection manager, mDNS/UPnP, remote control, and streaming are started.
- Which callers provide mDNS service names, UPnP descriptors, ports, URLs, and TXT records.
- What the public network endpoint and framing protocol are for the `LiveViewLocator` and streaming content handlers.
- What the network-service, ORB, and OSAL message payload layouts and state values mean, and which values are stable across firmware versions.
- Which caller selects the TLS cipher list and whether the large-file path uses `TLS_RSA_WITH_AES_128_CBC_SHA` or another compatible suite.
- What CPU frequency/utilization and sustained MB/s the camera achieves for plaintext and TLS transfers at different application chunk sizes.
- Which `libScalarDaemon.so` event consumers carry RGB matrix, gamma, white balance, and image-effect values into the lower image graph.
- Which callers connect `libStm.so` raw parsing and `libmpr.so` `MprIf::EncodeStill` to the YC/dataflow records.
- Which process loads the `sabin/` payloads, and which still/movie/live-view modes select each payload.
- Where sensor readout, black-level correction, defect correction, Bayer conversion, color matrix, tone mapping, and JPEG quantization occur.

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
