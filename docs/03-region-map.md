# Region map declared by firmware 3.21

The source for this table is Sony's extracted `0300_partconf/partinf.conf`. It is a declared NAND layout, not yet an independently verified raw camera dump. Offsets and sizes are hexadecimal byte values from the file.

| Device | Start | Size | Group | Label | Type |
| --- | ---: | ---: | --- | --- | ---: |
| `nflasha1` | `0x00040000` | `0x00600000` | System | Updater | `0x01` |
| `nflasha2` | `0x00640000` | `0x00D00000` | System | Setting | `0x01` |
| `nflasha3` | `0x01340000` | `0x01E00000` | System | Main | `0x03` |
| `nflasha4` | `0x03140000` | `0x00A00000` | System | MPR Flash Backup | `0x00` |
| `nflasha5` | `0x03B40000` | `0x03C00000` | System | Warm Boot Image | `0x02` |
| `nflasha6` | `0x07740000` | `0x00500000` | System | Jiritsu | `0x01` |
| `nflasha7` | `0x07C40000` | `0x00400000` | System | Rootfs | `0x03` |
| `nflasha10` | `0x08040000` | `0x00500000` | Work | Work | `0x01` |
| `nflasha11` | `0x08540000` | `0x00600000` | Work | Log | `0x01` |
| `nflasha15` | `0x08B40000` | `0x06400000` | User | User (cramfs) | `0x03` |
| `nflasha16` | `0x0EF40000` | `0x052C0000` | User | Android (system) | `0x03` |
| `nflasha17` | `0x14200000` | `0x063C0000` | User | Android (data) | `0x01` |
| `nflasha18` | `0x1A5C0000` | `0x01400000` | User | LensData | `0x01` |
| `nflasha23` | `0x1B9C0000` | `0x00100000` | Customer | PMBP | `0x01` |

The omitted device numbers are declared with size zero and are reserved in this version's configuration. The configuration also declares `nflasha8`, `nflasha9`, and `nflasha12`–`nflasha14` as zero-sized reserved entries before the user group, and `nflasha19`–`nflasha22` and `nflasha24`–`nflasha30` as zero-sized reserved entries after it.

## Images actually shipped in the updater

The extracted `0701_part_image_sum/part_image.sum` contains five image entries:

```text
nflasha3   11,489,040 bytes
nflasha5   42,293,120 bytes
nflasha7    3,324,495 bytes
nflasha15  84,042,977 bytes
nflasha16  59,013,103 bytes
```

Their sizes are smaller than the declared NAND partition capacities because the updater carries filesystem or image payloads rather than a complete raw NAND dump. The gap between declared layout and shipped images is a question for raw-dump verification.

## Initial architectural reading

The configuration separates the camera into at least four operational groups:

- **System**: updater, settings, main system, backup, warm boot, and rootfs regions.
- **Work**: working storage and logs.
- **User**: camera software, Android system/data, and lens data.
- **Customer**: PMBP content.

The updater XML runs separate checksum and update procedures for configuration, updater, application, partition images, partition configuration, front firmware, CA firmware, Darwin firmware, private files, backup, accessory, and loader material. This gives us a concrete next target: reconstruct the updater's state machine from its shell scripts and ARM helper binaries before analyzing camera capture logic.
