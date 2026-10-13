# M5 — Feature subsystem map

This milestone maps named feature boundaries in the ILCE-6000 3.21 user-space image. It begins with `nflasha15`, whose shipped libraries retain enough dynamic C++ symbols to identify service boundaries without publishing proprietary code.

The machine-readable inventory is [`firmware-3.21-feature-library-map.json`](../analysis/exports/firmware-3.21-feature-library-map.json). The source shared objects remain in the private extraction tree. Hashes in that inventory bind each public observation to one exact input. The companion [`firmware-3.21-feature-library-dependencies.json`](../analysis/exports/firmware-3.21-feature-library-dependencies.json) records selected `DT_NEEDED` and undefined-symbol observations.

## Evidence method

The first pass used `readelf --dyn-syms --wide` against the private extracted libraries. Names and ELF symbol values are metadata observations. Selected functions were then opened with REA's Ghidra provider. REA's normalized addresses are the addresses used by the analysis session; in this sample they are one less than the ELF value plus the `0x10000` load offset because the exported ARM functions carry Thumb entry bits.

The public REA dossiers are:

- [`rea-ptp-transport-init-socket.json`](../analysis/evidence/rea-ptp-transport-init-socket.json)
- [`rea-webapi-start-liveview-command.json`](../analysis/evidence/rea-webapi-start-liveview-command.json)
- [`rea-lens-init-command.json`](../analysis/evidence/rea-lens-init-command.json)

The private REA dossiers contain Ghidra pseudocode and evidence metadata. Public records retain only the evidence metadata; authorized researchers should check the private pseudocode against instructions and neighboring functions before treating it as an implementation specification.

## USB, PTP, MTP, and mass storage

The PTP control library exposes a common lifecycle with `PTPT_init`, `PTPT_open`, buffer allocation, data send/receive, event send, and matching USB, remote, and IP variants. This makes `libInfraPtpControl.so` the transport boundary to investigate when a feature is reachable from a USB or network PTP client.

Its IP helper is more specific. REA's `PtptIp::InitSocket` analysis shows allocation of a 64 KiB transfer buffer, initialization of an IPv4 socket structure, `socket(AF_INET, SOCK_STREAM, ...)`, `setsockopt`, `bind`, `listen`, and an asynchronous message that starts the connection path. That establishes a socket-based IP transport inside this library. It does not yet identify the listening address as a public protocol contract.

`libInfraPtpExtCmd.so` sits at the extension-command boundary. Its exported service names include command attachment, transfer requests, command processing, and response handling. `libInfraMtpServer.so` adds MTP lifecycle and filesystem/media mount jobs, while `libInfraMscServer.so` contains a separate mass-storage state machine with VBUS and media-change handlers. The dependency metadata adds a useful distinction: MTP directly declares `libptp.so`, while the PTP extension library declares `libUsbControl.so` and imports PTP packet helpers. These names give a practical call-graph order for later research:

```text
USB or IP transport
        |
        v
  libInfraPtpControl.so
        |
        +--> libInfraPtpExtCmd.so  -- extension commands
        +--> libInfraMtpServer.so  -- MTP sessions and media/filesystem jobs
        +--> libInfraMscServer.so  -- mass-storage mode and media changes
```

The graph is a research ordering, not proof that every arrow is a direct dynamic linker dependency. Direct dependencies and call sites still need to be checked with ELF relocation data and REA callers.

## Host candidates

Recursive string search found all six mapped library names in `libIMDB.so`. The library exports `IMDB_find_entry`, `IMDB_get_entries`, and `IMDB_find_target_bit`. REA shows `IMDB_find_entry` scanning fixed-size records for a 16-bit target ID and matching bitmask, while `IMDB_find_target_bit` scans target-name pointers and returns a bit position. This confirms a target-selection registry shape. REA also confirmed the `libInfraWebApi.so` string at normalized address `0x13d0a` and one reference at `0x1d750`, but Ghidra did not place that reference inside a recovered procedure.

`bin/orb-server` contains `/usr/lib/libInfraWebApi.so` at file offset `0x2f389c`. Its `DT_NEEDED` list does not include that library, so the current result is only a web API host hypothesis. Startup configuration and loader call sites are needed before assigning process ownership.

`libOnDemandLoader.so` is a separate component with `InfraOnDemandLoader` singleton initialization and program-load manager methods. It is a plausible firmware or program-loading boundary, but no current evidence connects it to the feature-library registry.

## Network camera control and live view

`libInfraWebApi.so` exports a large, regular job table. It includes command, event, and completion handlers for live view, still capture, movie recording, exposure compensation, shutter speed, focus, white balance, storage formatting, and camera-function selection.

The REA analysis of `wa_job_startLiveview_cmd` at normalized address `0x236e4` shows a small command handler. It logs the incoming message, response, URL, message ID, and parameter ID, copies the message header and payload into a new `WebApiIntMsg`, and calls `sendMsgToOrb`. The function is therefore a dispatch boundary into the camera's internal ORB service; it is not the live-view sensor implementation itself.

This gives feature researchers a useful split:

1. Use the web API job names to locate the externally reachable command and completion state machines.
2. Follow `sendMsgToOrb`, the corresponding event/completion handlers, and the message IDs to find the lower camera service.
3. Only then search for imaging, encoder, buffer, or media writers that implement the feature.

## Lens communication

`libInfraLensCommunicator.so` is small and has a clear command boundary. Its symbols include initialization, command initialization/finalization, event start, supported-command enumeration, mounted-lens information, backup reads, invalid-command handling, and transfer completion.

REA's `LensCommunicator::InitCmd` analysis shows the protocol shape at this boundary. It allocates a message from the OSAL message pool, fills a command value (`0x20000001`), copies the service handle, sets message fields including `0x2000`, sends it synchronously through `SndSyncMsg`, checks the response, stores a returned value in the communicator object, updates the caller's status, and releases the message. The field meanings remain unknown, but the function identifies the communicator as a synchronous command bridge rather than a lens driver implementation.

## Research value and limits

These libraries provide stable names for future cross-version comparison. They also suggest three low-risk static research tracks: protocol transport, camera-control message routing, and lens command routing. They do not yet prove process ownership, runtime load order, exported ABI compatibility, or whether a given symbol is used on every A6000 firmware build.

The next static step is to record relocation edges and use REA callers and string/reference searches to connect the boundaries to their host processes. Runtime work should start with passive USB/PTP observation and firmware-independent protocol logging. Any write, firmware replacement, or camera-side code execution requires a separately documented recovery path and a device explicitly authorized for that experiment.
