# M6 — USB and PTP protocol boundary

This milestone connects the static firmware subsystem map to the PC-side protocol implementation in the pinned Sony-PMCA-RE checkout. It records an executable host-side description of the Sony extension-command envelope and the service IDs that can be matched against `libInfraMtpServer.so`, `libInfraPtpExtCmd.so`, and `libInfraLensCommunicator.so`.

The machine-readable record is [`host-ptp-command-map.json`](../analysis/exports/host-ptp-command-map.json). The external checkout is read-only input. Its remote, commit, and source-file hashes are included in that record so later work can tell whether a protocol observation came from the same host implementation.

## MTP transport

The host uses normal PTP session operations `0x1001` for device information, `0x1002` to open a session, and `0x1003` to close it. Sony camera detection requires the three extension operations below to appear in the camera's supported-operation list:

| Operation | Meaning in the host implementation |
| --- | --- |
| `0x9280` | Sony extension command with a write data phase |
| `0x9281` | Sony extension command with a read data phase |
| `0x9282` | Request camera reconnect or switch back to mass storage |
| `0x9283`–`0x9285` | Burst-shot and AV-index operations |

For a write, the host sends `0x9280` with the service ID as the PTP parameter and sends the extension header plus payload in the data phase. For a read, it sends `0x9281`, receives an extension header and payload, and keeps the declared `dataSize` bytes after the 16-byte header. Both paths retry while the PTP response is `0x2019` (`DeviceBusy`).

The Windows WPD adapter maps the same flow onto Sony's MTP extension command GUID. It uses WPD command IDs 12–17 for initial no-data, read-data, write-data, read transfer, write transfer, and end-transfer phases. This is useful when comparing a USB capture made through Windows with a libusb capture made on Linux.

## Sony extension envelope

The host packs this little-endian header before each service payload:

```text
offset  size  field
0x00    4     dataSize
0x04    2     cmd
0x06    2     direction
0x08    8     reserved
```

The helper sets `direction` to zero and pads the write buffer to `0x2000` bytes by default. It returns only the number of response bytes declared by `dataSize`. This header is a protocol boundary for feature work: a new service command needs a service ID, a command ID, request structure, response structure, and a correct busy/retry policy before it can be exercised from the PC.

## Known service IDs

The host maps `(service, command)` pairs to firmware communicator classes. The lens path is especially clear:

```text
(6, 1)  LensCommunicator_GetSupportedCommandIds
(6, 2)  LensCommunicator_GetMountedLensInfo
```

The same table includes device information, backup and power operations, scalar app-download mode, and network service information. The network service range includes Wi-Fi AP and live-streaming settings. These constants are independent evidence for the dynamic symbols found in the 3.21 user image; they do not prove that every command is enabled on an ILCE-6000 or that its payload layout is unchanged between firmware versions.

Mass-storage mode uses a different host envelope. The host sends SCSI-like command bytes beginning with operation `0x7a`, the command as a 32-bit little-endian value, and seven zero bytes. It retries the transport's busy sense tuple `(0x09, 0x81, 0x81)` before reading or writing the command data.

## How this guides research

The first passive capture should establish the normal MTP session and device-info exchange, then capture one read-only service such as `(6, 2)` for mounted-lens information. That gives a short path through the MTP operation, Sony extension header, `LensCommunicator::InitCmd`, synchronous message, and response parser.

The current repository contains no live USB capture and no camera-side execution. The next runtime artifact should be a packet trace with the camera model, firmware version, host repository commit, USB transport, timestamps, direction, lengths, and SHA-256 of any extracted payload. Keep credentials, backup contents, serial numbers, and personal media outside the public repository.
