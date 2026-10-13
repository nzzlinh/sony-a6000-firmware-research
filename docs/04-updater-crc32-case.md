# Updater CRC32 case study

This is the first REA/Ghidra native-analysis record. It uses the extracted ARM helper `updater.img_unpacked/bin/uc_crc32sum.elf` to establish how Sony verifies update files before writing them.

## Inputs and tools

| Item | Value |
| --- | --- |
| Firmware | ILCE-6000 firmware 3.21 |
| Subject | `updater.img_unpacked/bin/uc_crc32sum.elf` |
| Subject SHA-256 | `8e368185be4a074034a3f86a7ff06123ba0936e5cb70fea963009f6f8628f4da` |
| Format | 32-bit little-endian ARM EABI5 ELF, stripped, dynamically linked |
| REA | `rea-agents` 6.4.0 |
| Native provider | Ghidra 12.1.4, headless, with JDK 21 |
| Compiler marker | `GCC: (20120717 (Sony CE Linux 8.2.1.1)) 4.5.1` |

The original ELF and full REA output remain in the private extracted firmware tree. Public evidence contains hash-bound metadata and human-written observations; it does not contain firmware bytes or raw decompiler output.

## Reproduction

Run REA with the Ghidra provider configured for the private toolchain:

```text
npx -y rea-agents@latest function \
  updater.img_unpacked/bin/uc_crc32sum.elf 0x8a94 \
  --provider ghidra --format json
```

The same operation was run for the entry path and related functions at `0x889c`, `0x8950`, `0x89c4`, `0x8a60`, `0x8a6c`, `0x8a94`, `0x8b0c`, and `0x8c64`. Hash-bound, metadata-only public records are in [`analysis/evidence/`](../analysis/evidence/), and the export helper is [`curate_rea_evidence.py`](../scripts/curate_rea_evidence.py). Full REA results remain in the private research archive.

## What the helper does

The command-line path is:

```text
uc_crc32sum.elf -c <sum-file>
```

The parser in `0x8950` accepts `-v`, `-s`, and `-c <file>`. The main routine in `0x89c4` performs a `stat` on the target path, requires a regular file for ordinary entries, then calls the verifier at `0x8b0c`. It reports `check sum OK` or `check sum NG`.

The verifier handles three entry types seen in the trace format:

- ordinary files: compare recorded size, calculate the CRC, compare the recorded CRC, then check permission bits;
- symbolic links: require a symlink, read its target, and compare the recorded target string;
- directories: require a directory, then check permission bits.

The file CRC routine at `0x8a94` opens the path, reads at most `0x20000` bytes per iteration, and passes each block to `0x8a6c`. The inner loop uses a 256-entry reflected CRC table. The first entries at virtual address `0x9408` are `0x00000000`, `0x77073096`, `0xee0e612c`, and `0x990951ba`, identifying the standard CRC-32/IEEE reflected polynomial table (`0xedb88320`). The accumulator starts at `0xffffffff` and is complemented before returning, matching the usual CRC-32/IEEE initialization and final XOR.

The parser at `0x8c64` reads a structured `.sum` file with twelve fields. It parses hexadecimal values for the recorded metadata, decimal values for size-like fields, and bounded strings for names, paths, and symlink targets. Each completed record is sent to `0x8b0c`.

## How this connects to the update flow

The updater XML assigns `us_crc32sum.sh` to the checksum procedures for configuration, the updater image, application files, partition images, partition configuration, front firmware, CA firmware, Darwin firmware, accessory files, and loader files. The shell wrapper selects `uc_crc32sum.elf -c` for ordinary file trees and `uc_crc32sum.elf -s -c` for image checks.

This gives us a confirmed integrity boundary: the updater is a collection of scripted procedures backed by small native helpers, with the same CRC verifier reused across several payload classes. It also explains why the extracted `part_image.sum` records can be checked independently before any camera interaction.

## Evidence and limits

The public records preserve the REA evidence IDs and analysis provenance:

- [`0x8950` parser options](../analysis/evidence/rea-uc-crc32-0x8950.json)
- [`0x89c4` main dispatch](../analysis/evidence/rea-uc-crc32-0x89c4.json)
- [`0x8a94` file CRC loop](../analysis/evidence/rea-uc-crc32-0x8a94.json)
- [`0x8a6c` table step](../analysis/evidence/rea-uc-crc32-0x8a6c.json)
- [`0x8b0c` record verifier](../analysis/evidence/rea-uc-crc32-0x8b0c.json)
- [`0x8c64` sum-file parser](../analysis/evidence/rea-uc-crc32-0x8c64.json)

The private decompiler output is evidence of control flow and data use, not Sony source code. The public records preserve only the input hash and analysis provenance. The CRC table confirms the algorithm family, while the exact `.sum` field semantics still need correlation with more checksum files and with the updater's shell inputs. No updater was run against a camera during this case study.

## Next question

Which script and native helper perform the transition from verified package contents to each NAND region write, and how do the updater action modes select those procedures?
