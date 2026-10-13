# Firmware 3.21 extraction record

This is the reproducible extraction record for Sony ILCE-6000 firmware 3.21. Source firmware remains in the private artifact directory.

## Inputs

| Artifact | Size | SHA-256 |
| --- | ---: | --- |
| `Update_ILCE6000V321.dmg` | 214,920,547 bytes | `844349ff7edddc294c0fddd90a454848eeda8987b6bf043c9757982b3a42ba3e` |
| `FirmwareData_ILCE6000V321.dat` | 212,988,056 bytes | `29aef21ab9b5c2e98388974ac9749c2cbfb1815273b444e62f2e41398aa8892f` |

The DMG was downloaded from Sony's official redirect on 2026-10-13 and stored at:

```text
/home/zeelinh/sony-a6000-private/firmware-3.21/
```

## Extraction tools

- 7-Zip 23.01, extracted locally from the Ubuntu `7zip` package.
- `fwtool.py` from `ma1co/fwtool.py`, cloned into the private tools directory at commit `cdba742b73eed5981480c326aeb30033aabf0223`.
- Python 3.12.3 with `pycryptodomex` and `pyyaml` in a private virtual environment.

The package, payload, and region hashes are in [`artifact-manifest.json`](../analysis/artifact-manifest.json). Proprietary source paths and expanded firmware trees stay outside this repository.

## Procedure

The DMG was opened as an HFS+ archive. Its firmware data member was extracted, then unpacked with:

```text
python fwtool.py unpack \
  -f FirmwareData_ILCE6000V321.dat \
  -o firmware-3.21-fwtool-output
```

The unpacker reported a CXD90014 image, decrypted the FDAT container, extracted `firmware.tar`, expanded the firmware tree, unpacked the five published partition images, and unpacked the updater image.

## Derived inventory

The public inventory is [firmware-3.21-inventory.json](../analysis/exports/firmware-3.21-inventory.json). It contains paths, sizes, SHA-256 values, and coarse categories; it contains no firmware bytes.

Current inventory totals:

- 1,398 files.
- 1,181,012,182 bytes after recursive expansion.
- 521 files categorized as native by the inventory heuristic (`.elf` or `.so`).
- An updater image recognized as Linux CramFS, containing ARM EABI5 executables and shell scripts.
- Linux ext2 images for `nflasha15`, `nflasha16`, and `nflasha7`.
- A FAT image for `nflasha3`.

The expanded size is larger than the updater payload because it includes both packed images and their unpacked filesystem contents.

## CRC verification

Sony's `0701_part_image_sum/part_image.sum` contains CRC32 entries for the five partition image files shipped in the updater. The public verifier is [verify_crc32_sum.py](../scripts/verify_crc32_sum.py).

All five entries matched the extracted files:

| Image | Expected CRC32 | Result |
| --- | --- | --- |
| `nflasha3` | `0c047870` | match |
| `nflasha5` | `9cb10112` | match |
| `nflasha7` | `b969856d` | match |
| `nflasha15` | `df198ecd` | match |
| `nflasha16` | `c77af80c` | match |

The per-file result is [firmware-3.21-part-image-verification.json](../analysis/exports/firmware-3.21-part-image-verification.json).
