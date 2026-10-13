# Sony α6000 firmware research

This repository is a reproducible research notebook for understanding the Sony ILCE-6000 firmware and finding practical extension points for new features.

The public repository contains documentation, hashes, derived maps, scripts, and analysis exports. Proprietary firmware images, decrypted firmware trees, raw camera dumps, recovered APKs, and personal camera data stay outside the repository unless distribution is authorized.

Start with the [research charter](docs/00-project-charter.md), then follow the [progress ledger](docs/PROGRESS.md) and [knowledge ledger](docs/KNOWLEDGE.md). The first native case study is [the updater CRC32 analysis](docs/04-updater-crc32-case.md), followed by the [update procedure map](docs/05-update-procedure-map.md), [feature subsystem map](docs/06-subsystem-map.md), [USB/PTP protocol boundary](docs/07-usb-ptp-protocol-boundary.md), and [network stack map](docs/08-network-stack.md).

The current baseline is Sony ILCE-6000 firmware 3.21. REA is used to guide evidence-backed investigations of extracted native images; durable results are exported into this repository so they do not depend on a live analysis session.

The project uses component-specific licenses. See [the publication policy](docs/09-licensing-and-publication.md), [LICENSE-CODE](LICENSE-CODE), [LICENSE-DOCS](LICENSE-DOCS), and [third-party notices](THIRD_PARTY_NOTICES.md). Sony product names identify the research subject; this project is independent and does not imply Sony endorsement.
