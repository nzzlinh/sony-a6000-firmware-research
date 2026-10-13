# Network stack map

This note records the first static map of the ILCE-6000 3.21 network path. The input is the private `nflasha15` extraction; only hashes, ELF metadata, symbols, strings, and selected REA/Ghidra results are published. The machine-readable inventory is [`firmware-3.21-network-stack-map.json`](../analysis/exports/firmware-3.21-network-stack-map.json).

The main finding is that Sony split networking into several service boundaries. WLAN hardware bring-up, connection policy, service discovery, remote control, and live-view delivery are separate components joined by OSAL/MWF messages and state machines. This organization gives porting work useful seams: a new feature can often be studied at the network command/state boundary without starting inside the WLAN driver or image encoder.

## Stack overview

```text
WLAN board and drivers
  libWlanControlCommon.so
  libWlanResource.so
          |
          v
Connection policy and arbitration
  libInfraNetConnectionManager.so
  AP / WPS / group-owner / auto-connect state
          |
          +--> service discovery and device description
          |      libInfraMDnsControl.so
          |      libInfraNetFunctionManager.so
          |
          +--> network remote control
          |      libInfraRemoteControlNet.so
          |      libInfraWebApi.so
          |
          +--> live-view and image delivery
                 libInfraStreamingServer.so
                 LiveViewLocator / JPEG content handlers
```

The diagram is a research graph assembled from names, exported symbols, imported symbols, and selected decompiler traces. It is not a claim that every arrow is a direct dynamic-linker dependency. The exact process that loads each library and the startup order remain open.

## 1. WLAN hardware and driver lifecycle

`libWlanControlCommon.so` is the lowest network-facing boundary found in this pass. Its exported methods cover `initializePort`, `finalizePort`, port start/stop, driver installation and removal, firmware loading, and a start check. Its strings identify the Atheros AR6000 path, kernel modules, and target firmware files:

```text
/usr/kmod/ar6000.ko
/usr/kmod/mmcioWrapper.ko
/usr/wlan/ath/20110707_TypeTP_0707.bin
/usr/wlan/ath/otp.bin
/usr/wlan/ath/athtcmd_ram.bin
/usr/wlan/ath/athwlan_mobile.bin
/usr/wlan/ath/data.patch.hw3_0.bin
```

REA/Ghidra analysis of [`WlanControlCommon::initializePort`](../analysis/evidence/rea-wlan-initialize-port.json) makes the board-level work explicit. The function opens `/dev/mem`, maps a 4 KiB register window, opens `/dev/gpio`, performs repeated `ioctl` calls carrying `GPIO_CMD_SET_MODE`, reads board values through `Backup_read_4Byte`, writes control-register fields, waits between changes, and records an error for each failed operation. The decompiler also resolves calls to `open`, `mmap`, `ioctl`, `close`, and the library's network error recorder.

`libWlanResource.so` sits above this helper. It exports `initializeWlan`, `startWlan`, `stopWlan`, host-driver load/unload, target-board initialization, product-specific variants, and a `WlanResourceMainThread`. Its strings include `wlanMemoryAllocator.ko` and message IDs for asynchronous start and stop requests. This suggests a two-part design:

1. `libWlanControlCommon.so` performs board and driver operations.
2. `libWlanResource.so` owns resource policy, product variants, request handling, and the WLAN worker thread.

That division matters for porting. A feature that only needs a new network service should probably attach above `WlanResource`; changing `initializePort` would be board bring-up work with a larger recovery risk.

## 2. Connection policy and arbitration

`libInfraNetConnectionManager.so` is a message-driven connection-policy layer. Its symbol table contains `NetConnectionManager_init` and a `NetServiceArbitrator` with handlers for:

- connecting to and disconnecting from an access point;
- WPS start/cancel and group-owner WPS;
- starting and stopping a group owner;
- connecting to the last UPnP device or a selected UPnP device;
- automatic UPnP search;
- automatic AP connection and its search/authentication stages;
- saved AP information, RSSI, security type, and WPS PIN queries.

The corresponding command, completion, and event names are retained as strings in the library. This is stronger than a generic network-library name: Sony modeled connection policy as an explicit command/event state machine with separate asynchronous requests and completions.

REA analysis of [`procAsyncReqStartFunc`](../analysis/evidence/rea-net-start.json) shows the message mechanics. When the arbitrator is idle, it calls `MWF::EventWrapper::SendAndRecv`, stores the request in a `CommandTracker`, increments an internal function counter, and returns success. When a function is already active, it restores saved command data, sends a completion message through `ObjectRegisterer`, and rebuilds a fake completion from the stored request. The exact command IDs and payload fields are still unnamed, but the arbitration and retry/completion shape is confirmed.

The direct ELF dependencies are `libMWF.so` and `libNetCommon.so`. Those are the next libraries to inspect when mapping the message IDs to network interfaces and process ownership.

## 3. Service discovery: mDNS and UPnP

`libInfraMDnsControl.so` contains a full mDNS responder boundary. It exports initialization and worker-thread methods, service registration and deregistration, hostname and friendly-name accessors, the mDNS execution loop, and the underlying `mDNS_RegisterService`/`mDNS_DeregisterService` routines. It also retains global fields for service name, service type, domain, TXT data, port, service list, and service ID.

REA analysis of [`RegisterOneService`](../analysis/evidence/rea-mdns-register.json) shows the service-registration contract. It accepts a service name, service type, domain, TXT data, TXT length, and port. It allocates a service record, converts the name/type/domain into DNS labels, calls `mDNS_RegisterService`, assigns an incrementing service ID, and links the record into a service list. On failure it frees the record and returns the mDNS error. This gives a direct route for recovering advertised service metadata: find the callers and inspect the arguments passed into this function.

UPnP is represented alongside mDNS but appears to have a separate coordinator. `libInfraNetFunctionManager.so` exports `nfm_sub_job_StartUpnpServer`, `nfm_sub_job_StopUpnpServer`, `sendSsMsg`, and jobs that initialize/finalize and forward messages to `InfraStreamingServer`. Its undefined symbols include `DeviceDescUtil::StartUpnpDevice` and `DeviceDescUtil::StopUpnpDevice`. Strings identify live-view start/stop, connect/disconnect, and streaming-server command/completion message IDs.

The current evidence supports this division:

```text
libInfraMDnsControl.so       mDNS responder and service records
libInfraNetFunctionManager.so  UPnP/device-description and function FSM
libInfraStreamingServer.so   streaming service behind those network functions
```

It does not yet prove whether the camera advertises the same service through both protocols in every operating mode.

## 4. Network remote control and Web API

`libInfraRemoteControlNet.so` is the clearest network-to-camera-state bridge. It exports `RcWebAPIFunc`, initialization/finalization, `RcCameraStateSetParameterFromWebApi`, the larger `RcCameraStateSetParameter` dispatcher, parameter validation, supported-value getters, live-view state, live-view still URI, and commands for starting/stopping live view and taking a picture. Its supported-value methods cover shoot mode, still size, movie quality, exposure mode, white balance, shutter speed, focus, flash, self-timer, steady mode, view angle, camera function, beep, f-number, and storage.

REA analysis of [`RcWebAPIStartLiveviewComeback`](../analysis/evidence/rea-remote-liveview.json) shows a state gate before live-view recovery. The function asks `RcStateGetState` for the remote-control state, requires state value `4`, checks a live-view bit in the returned state details, and then calls an internal recovery routine. If the camera is not in the expected remote state, it logs and returns without starting the operation. This is evidence of a higher-level remote-control FSM, not evidence that value `4` is a universal public protocol constant.

`libInfraWebApi.so` provides the job layer already documented in the [subsystem map](06-subsystem-map.md). Its live-view command handler copies a `WebApiIntMsg` and sends it to the internal ORB service. Its imports include POSIX socket functions (`connect`, `socket`, `bind`, `listen`, and `accept`), while its direct library dependencies include `libMWF.so` and `libNetContUtil.so`. The useful porting boundary is therefore:

```text
network request
    -> Web API / remote-control message
    -> camera-state validation and state change
    -> ORB service message
    -> imaging or media implementation
```

The request syntax, URI paths, authentication/session behavior, and internal ORB message fields are not recovered yet. The symbol names identify where to continue, not a drop-in external API specification.

## 5. Live-view and image delivery

`libInfraStreamingServer.so` contains a distinct streaming service with its own initialization, worker thread, start/stop jobs, network-service start/stop functions, picture jobs, and content-handler classes. The exported names include `LiveViewLocator::GetSpecificUrl`, `GetPortNumber`, `GetFileName`, and `GetIpAddress` as imported methods from `libNetCommon.so`. The server also has JPEG-specific methods:

- `ContentHandlerEEImpl::GetLiveViewJpeg`;
- `ContentHandlerEEImpl::MmapLiveViewJpeg`;
- live-view header and payload-header builders;
- `jobGetLiveView`, `jobLiveViewStartCmd`, `jobLiveViewStopCmd`, and wait states;
- picture-content open/read/close handlers.

REA analysis of [`ContentHandlerEEImpl::GetLiveViewJpeg`](../analysis/evidence/rea-stream-liveview.json) shows the frame path. It prepares a 0x170-byte request/control area, sends a synchronous OSAL message with identifier `0x1718498`, waits for a usable frame while checking the returned status, and then maps the JPEG through `MmapLiveViewJpeg` using a frame identifier and size. A not-ready status is logged as `mode not ready`; the loop can retry up to 1001 times with a short sleep. This is strong evidence that the network server obtains JPEG frames from an internal producer through an OSAL message boundary.

The exact network framing is still unknown. `LiveViewLocator` proves that the server can construct or retrieve an IP/port/filename/URL tuple, while the content handlers prove JPEG delivery. The current static evidence does not distinguish HTTP, a Sony-specific HTTP-like stream, or another transport behind the content-handler framework.

## 6. TLS crypto and large-file throughput

`libNetService.so` contains the firmware's visible TLS adapter and a software crypto boundary. It exports wrappers for TLS initialization, handshake, record encryption/decryption, cipher-list selection, AES-128-CBC, RSA/PKCS#1 key operations, and the underlying `rijndaelEncrypt` routine. The wrapper evidence is [`rea-netservice-tls-encrypt.json`](../analysis/evidence/rea-netservice-tls-encrypt.json), [`rea-netservice-tls-decrypt.json`](../analysis/evidence/rea-netservice-tls-decrypt.json), [`rea-netservice-tls-set-cipher.json`](../analysis/evidence/rea-netservice-tls-set-cipher.json), [`rea-netservice-aes128-cbc-encrypt.json`](../analysis/evidence/rea-netservice-aes128-cbc-encrypt.json), and [`rea-netservice-crypto-cipher-encrypt.json`](../analysis/evidence/rea-netservice-crypto-cipher-encrypt.json).

The static image does **not** contain a fixed bytes-per-second limiter for this path. The AES-CBC wrapper initializes a 16-byte key schedule, copies a 16-byte IV, and processes the input in 16-byte blocks. The generic cipher loop likewise scales with the number of blocks and has no visible sleep, timer, or byte quota. The RSA helpers are PKCS#1 operations used around key setup or authentication; RSA is not applied to every byte of a large file, so its cost is amortized after the TLS handshake.

The TLS adapter does impose allocation policies, but these are not speed limits:

- outbound encryption allocates `input_length + 300` bytes;
- inbound decryption allocates `input_length * 3 + 1500` bytes.

For a large transfer, the useful static upper-bound model is therefore:

```text
sustained throughput <= min(
    effective WLAN/socket throughput,
    software AES-CBC + TLS record throughput,
    network-service consumer/producer throughput
)
```

If the camera sends the file, the encrypting wrapper is the relevant allocation path. If the camera receives it, the decrypting wrapper's larger temporary allocation can increase memory pressure and reduce throughput for oversized records or chunks. Neither direction has a firmware-derived MB/s value in this static evidence. Excluding SD-card reads removes one possible term from the minimum, but a numeric limit still requires a camera-side benchmark with CPU utilization, TLS enabled/disabled comparisons, and several application chunk sizes.

The phrase “AES-CBC-RSA” should be treated as shorthand here. The image proves RSA/PKCS#1 and AES-CBC support, but `tls_connection_set_cipher_list` forwards a caller-supplied list and the selected suite is not recovered. `TLS_RSA_WITH_AES_128_CBC_SHA` is therefore a plausible interpretation, not a confirmed 3.21 selection. The `tlsv1_client_*` core routines are undefined imports in this library, so their provider and complete record implementation remain unresolved. OpenSSL dependencies found in `wpa_supplicant` and other services do not prove that the large-file camera service uses OpenSSL.

## What this tells a feature porter

The safest practical extension points are the upper boundaries:

1. Add or trace a command at `libInfraRemoteControlNet.so` / `libInfraWebApi.so` when the feature is a camera-control operation.
2. Follow the resulting ORB message and completion path into the camera subsystem.
3. Reuse the existing `libInfraStreamingServer.so` content-handler and locator path when the feature returns JPEG or other media.
4. Use mDNS/UPnP registration only after the service name, port, URL, and session behavior are recovered from callers or a passive capture.
5. Treat `libWlanControlCommon.so` as platform bring-up code; it is a poor first target for ordinary feature work.

The main unknowns are now narrower: process ownership, caller arguments, service metadata, endpoint framing, selected TLS cipher suite, runtime TLS provider, measured crypto throughput, and the cross-version stability of the message IDs and data structures. These are the next static and runtime probes, rather than a need to reverse the entire WLAN driver first.

## Evidence and limitations

- **Confirmed:** the libraries, hashes, dynamic symbols, direct `DT_NEEDED` entries, mDNS registration flow, connection-arbitration message flow, remote live-view state gate, internal JPEG retrieval path, and `libNetService.so` TLS/AES/RSA boundary belong to the private ILCE-6000 3.21 extraction.
- **Strong inference:** the layered graph is how Sony organized the network feature stack, based on library names, imports, state-machine symbols, and selected REA traces.
- **Unknown:** process load order, public endpoint syntax, authentication/session details, service records, exact OSAL/ORB payload layouts, and cross-version ABI stability.
- **Not performed:** no camera was connected and no network command or firmware write was issued during this pass.

The public evidence dossiers contain reconstructed pseudocode. They should be checked against their instruction listings and neighboring callers before any implementation is attempted.
