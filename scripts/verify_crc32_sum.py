#!/usr/bin/env python3
"""Verify Sony firmware ``*.sum`` CRC32 entries against extracted files."""

from __future__ import annotations

import argparse
import json
import sys
import zlib
from pathlib import Path


def crc32(path: Path) -> str:
    value = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value = zlib.crc32(block, value)
    return f"{value & 0xFFFFFFFF:08x}"


def verify(root: Path, sum_file: Path) -> list[dict[str, str | bool]]:
    results = []
    for line in sum_file.read_text(encoding="utf-8").splitlines():
        fields = line.split(",")
        if len(fields) < 12 or fields[0] != "0":
            continue
        expected = fields[1].lower()
        relative = fields[-2]
        path = root / relative
        actual = crc32(path) if path.is_file() else None
        results.append(
            {
                "path": relative,
                "expected_crc32": expected,
                "actual_crc32": actual,
                "match": actual == expected,
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="directory containing the paths in the sum file")
    parser.add_argument("sum_file", type=Path)
    parser.add_argument("--json", type=Path, help="write results as JSON")
    args = parser.parse_args()

    results = verify(args.root, args.sum_file)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    for result in results:
        status = "MATCH" if result["match"] else "MISMATCH"
        print(f"{status}\t{result['path']}\t{result['expected_crc32']}\t{result['actual_crc32']}")
    return 0 if results and all(result["match"] for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
