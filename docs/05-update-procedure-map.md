# Firmware 3.21 update procedure map

The updater body combines a small XML procedure table, POSIX shell policy, and ARM helper binaries. The XML names the checks and actions; the shell scripts select paths, mounts, action modes, and error handling; native helpers operate on NAND, filesystems, backup data, and auxiliary firmware devices.

## Package structure

The extracted firmware tree uses numbered payload directories while `config/config.xml` refers to their logical names:

| Logical role | Extracted directory | Main contents |
| --- | --- | --- |
| configuration | `0100_config` | `mount.conf`, `big_backup.conf` |
| backup | `0110_backup` | regional `CX77500_*` and `CX77501_*` backup files |
| partition configuration | `0300_partconf` | `partinf.conf` |
| CA firmware | `0630_ca` | CA payloads, if present in a variant |
| Darwin firmware | `0640_darwin` | `darwin_core.bin` |
| private files | `0650_prfile` | PMBP files and licenses |
| partition images | `0700_part_image` | `dev/nflasha3`, `5`, `7`, `15`, and `16` |
| application | `0800_appli` | lens files, setting files, Android data, and temporary files |

The updater image itself is a separate `updater.img` payload containing the body shown in the table below. Some XML keys have no corresponding payload directory in this particular package because that procedure is optional or supplied only for other product variants.

## Declarative procedure table

The source is the extracted `updater.img_unpacked/config/config.xml` (9-byte `body_version` `41.01.28`, chassis `CXD90014`).

| XML key | First shell module | Additional action | Payload or target |
| --- | --- | --- | --- |
| `config_sum/config.sum` | `us_crc32sum.sh` | `chkfirm.sh`, `edit_mount.sh`, `keep_big_backup.sh` | configuration files and backup preservation |
| `updater_sum/updater.sum` | `us_crc32sum.sh` | none in XML | updater body |
| `appli_sum/appli.sum` | `us_crc32sum_appli.sh` | application-specific setting restore/mount handling | `0800_appli` |
| `part_image_sum/part_image.sum` | `us_crc32sum.sh` | none in XML | `0700_part_image/dev/*` |
| `partconf/partinf.conf` | `chknandcapa.elf` | none in XML | NAND layout declaration |
| `partconf_sum/partconf.sum` | `us_crc32sum.sh` | `us_mkfs.sh` | `0300_partconf` and filesystem formatting |
| `front_sum/front.sum` | `us_crc32sum.sh` | `us_front_firmup.sh` | front-device firmware |
| `ca_sum/ca.sum` | `us_crc32sum.sh` | `us_ca_firm.sh` | CA/AS firmware |
| `darwin_sum/darwin.sum` | `us_crc32sum.sh` | `us_darwin_firm.sh` | Darwin firmware |
| `prfile_sum/prfile.sum` | `us_crc32sumprfile.sh` | none in XML | `0650_prfile` |
| `backup_sum/backup.sum` | `us_crc32sum_backup.sh` | none in XML | `0110_backup` and `Backup.bin` |
| `accsy_sum/accsy.sum` | `us_crc32sum.sh` | none in XML | accessory payload |
| `loader_sum/loader.sum` | `us_crc32sum.sh` | `loader_writer.sh` | loader payload and NAND formatting |

The XML also marks CA, Darwin, and private-file procedures as threaded. This is a scheduling property of the updater procedure runner; it does not by itself prove that the underlying hardware writes are concurrent.

## Verified checksum boundary

`us_crc32sum.sh` checks that the target directory and sum file exist, changes into the target directory, and calls the shared `uc_crc32sum.elf` helper. Its `image` mode sets the target directory to `/` and adds `-s`; ordinary mode checks a directory under the extracted update root and uses `-c`. The CRC helper and its evidence are documented in [`04-updater-crc32-case.md`](04-updater-crc32-case.md).

The five shipped partition images are independently verified in [`firmware-3.21-part-image-verification.json`](../analysis/exports/firmware-3.21-part-image-verification.json). The `.sum` records also encode file type, CRC, size, mode, ownership, and path, which explains why the native verifier checks more than file contents.

## Mount and region policy

`0100_config/mount.conf` maps the device nodes to the runtime mount points and declares the same capacities recorded in [`03-region-map.md`](03-region-map.md):

| Device | Mount point | Type | Declared bytes |
| --- | --- | --- | ---: |
| `/dev/nflasha1` | none | vfat | 6,291,456 |
| `/dev/nflasha2` | `/setting` | vfat | 13,631,488 |
| `/dev/nflasha3` | `/system` | raw | 31,457,280 |
| `/dev/nflasha5` | `/wbi` | wbi | 62,914,560 |
| `/dev/nflasha7` | `/rootfs` | raw | 4,194,304 |
| `/dev/nflasha10` | `/tmp` | vfat | 5,242,880 |
| `/dev/nflasha11` | `/log` | vfat | 6,291,456 |
| `/dev/nflasha15` | `/usr` | raw | 104,857,600 |
| `/dev/nflasha16` | `/android/system` | raw | 86,769,664 |
| `/dev/nflasha17` | `/android/data` | vfat | 104,595,456 |
| `/dev/nflasha18` | `/lens` | vfat | 20,971,520 |
| `/dev/nflasha23` | `/PMBP` | prfile | 1,048,576 |

The remaining declared entries are zero-sized or reserved in this configuration. `mount.conf` and `partinf.conf` agree on the active regions, giving us two independent package-level descriptions of the layout.

## Action-mode behavior

The shared shell scripts define these action modes:

| Name | Value | Observed behavior |
| --- | ---: | --- |
| product | 1 | full filesystem preparation; normal end-of-update flow |
| loader/updater | 2 | full preparation unless `not_write_file/nwl` selects app mode |
| user | 3 | app mode; skips some destructive formatting |
| service | 4 | app mode; skips `edisx.elf` and exits after preparation |
| minor | 5 | app mode; skips `edisx.elf` and exits after preparation |
| MSCRYPT | 6 | app mode; exits after preparation |
| version skip | 7 | full preparation but exits before the product-only tail |

`us_mkfs.sh` calls `edisx.elf /dev/nflasha partinf.conf` for the modes that allow it, selects `uc_mkfs.elf -m full` or `-m app`, restores backup state with `ud_keep_backup.elf -s`, and calls `ud_wbi_drop.elf`. In the product path it then runs `dosfsck` on `nflasha2`, mounts the setting partition, and writes `sen/smode` as `UU`.

`startupdate.sh` preserves `Backup.bin` before the update when `/root/IAMUPDATER` is present. `endupdate.sh` rewrites backup data, erases the MPR partition through `ud_lerase.elf /dev/nflasha 4`, optionally formats user storage through `ud_fsys_format.elf`, and remounts the setting partition. These are static observations from the extracted scripts; no write path has been executed against a camera.

REA/Ghidra adds a native cross-check for `uc_mkfs.elf`. Its option parser at `0x8744` accepts `-m full|app` and `-f <mount.conf>`. The main routine at `0x893c` parses the configuration into a table, then runs the full-mode formatting passes. The formatter at `0x886c` constructs commands of the form `mkdosfs -f 1 -s <sectors> <device>` for entries marked as FAT-like. The mount configuration parser at `0x8a94` reads one line at a time, rejects too many entries, and reports malformed or inaccessible configuration files. These observations explain the shell-level `uc_mkfs.elf -m` selection without executing the formatter.

The public native evidence for this cross-check is [`analysis/evidence`](../analysis/evidence): `rea-uc-mkfs-0x8744.json`, `rea-uc-mkfs-0x886c.json`, `rea-uc-mkfs-0x893c.json`, and `rea-uc-mkfs-0x8a94.json`. The `edisx.elf` entry dossier is also archived there; its function pointer to the main routine was observed in the ARM startup sequence, while the main routine remains a follow-up because Ghidra did not register that indirect entry as a function in the ephemeral analysis.

## C++ procedure runner

The updater body library retains a large dynamic symbol table: 734 entries in `libupdaterbody.so`, including named C++ methods. This makes the body runner easier to map than the stripped command helpers.

REA/Ghidra reconstructed the following execution path:

1. `UpdaterBody::Execute` (`0x1f4c8`) creates a packed-firmware reader, flag handler, XML configuration handler, and mount-entry handler. It loads `config.xml`, parses packed file headers, selects a key-tag object from each entry's index, and calls the current tag's pre-execute, extract, and post-execute methods. At completion it joins threaded work, checks XML errors, calls the built-in end-update hook, and completes the firmware information update.
2. `XmlConfigHandler::Execute` (`0x237c4`) iterates procedure nodes. Nodes with `thread="yes"` are submitted to the thread plugin; other nodes go through `Plugin::Execute`.
3. `Plugin::Execute` (`0x2443c`) dispatches a node whose value is `run` to `DllPlugin::Execute`; all other nodes go to `ShellPlugin::Execute`.
4. `ShellPlugin::Execute` (`0x23f1c`) reads the `module` and optional `param` attributes, builds the environment with `EXTRACT_ROOT`, the updater `PATH`, and the numeric `UPDATER_ACTION_MODE`, then invokes the selected shell module through `system()`.
5. `PartitionImageKeyTag::Extract` (`0x20cc0`) creates a `NewFirmwareImageFile` from the packed entry after removing the image-key prefix and delegates extraction to the common file extractor. `ApplicationKeyTag::PreExecute` (`0x20890`) obtains the mount-entry handler and mounts the application workspace before extraction.

This confirms the design boundary suggested by the XML: the XML is interpreted by a C++ key-tag and plugin engine, while shell modules perform the product-specific update actions. The engine also separates extraction from procedure execution, so an application or partition entry can be unpacked before its post-extraction checksum or mount action runs.

The corresponding evidence dossiers are [`rea-body-0x1f4c8.json`](../analysis/evidence/rea-body-0x1f4c8.json), [`rea-body-0x237c4.json`](../analysis/evidence/rea-body-0x237c4.json), [`rea-body-0x2443c.json`](../analysis/evidence/rea-body-0x2443c.json), [`rea-body-0x23f1c.json`](../analysis/evidence/rea-body-0x23f1c.json), [`rea-body-0x20cc0.json`](../analysis/evidence/rea-body-0x20cc0.json), and [`rea-body-0x20890.json`](../analysis/evidence/rea-body-0x20890.json). The selected symbol inventory is [`firmware-3.21-updater-body-symbols.json`](../analysis/exports/firmware-3.21-updater-body-symbols.json).

## Native helper inventory

The relevant ARM EABI5 helpers are present in the updater body. Their public inventory records the following hashes:

| Helper | Role suggested by callers/strings | SHA-256 |
| --- | --- | --- |
| `edisx.elf` | partition layout and NAND setup | `156d2b32077f9d13a54e6e577c2abb1e15c8c80b68acd16eb1013be089af75ca` |
| `uc_mkfs.elf` | full/app filesystem formatting from `mount.conf` | `c422eaae45cb38ba5463cebbc945b5b993608633436e310b5d127b00748f102b` |
| `ud_wbi_drop.elf` | warm boot image handling from `partinf.conf` | `678d6baf9d4459d2706c937ba5bd31bf336541369ab2c1573292d9478ed3992b` |
| `ud_lerase.elf` | logical erase of an NAND partition | `da554ef4917d380ed965ee5ea098f5614811e445aada198e8e28adcd178cd8dd` |
| `ud_fsys_format.elf` | filesystem formatting through `libbackup.so` | `16656b83702b01c42ae86060895ebe894b72d408133e246867d1fcd5c3d907b2` |
| `pformat_normal.elf` | normal loader/NAND formatting | `e623339090c05081a293c48b31b0f83512e8717a558d0f4a2abd7cfe91ea483d` |
| `pformat_safe.elf` | safe loader/NAND formatting from a list | `02ea5b18e0355827f36a2affafd8f1ae4cc89fbf5abe1930ea7b065f66074d48` |

## M4 conclusion and next question

The package exposes a layered update design: checksum records guard each payload, shell scripts select mode and mount policy, and focused ARM programs perform NAND/filesystem/backup operations. The next static trace should follow `edisx.elf`, `uc_mkfs.elf`, and `ud_wbi_drop.elf` from their command-line inputs into ioctl or library calls, then compare that path with the three shipped raw partition images.
