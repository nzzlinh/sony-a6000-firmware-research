#!/usr/bin/env python3
"""Create a public, byte-derived inventory of a private firmware tree."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def category(path: Path) -> str:
    name = path.name.lower()
    if name.endswith((".elf", ".so")):
        return "native"
    if name.endswith((".sh", ".conf", ".sum", ".xml", ".txt", ".yaml")):
        return "text-or-script"
    if "_unpacked" in path.parts:
        return "filesystem-content"
    return "binary-or-container"


def build_inventory(root: Path, label: str) -> dict:
    files = []
    total_bytes = 0
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        size = path.stat().st_size
        total_bytes += size
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size_bytes": size,
                "sha256": sha256(path),
                "category": category(path),
            }
        )

    return {
        "schema_version": 1,
        "source_label": label,
        "source_path_is_intentionally_omitted": True,
        "file_count": len(files),
        "total_file_bytes": total_bytes,
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="private extracted firmware directory")
    parser.add_argument("output", type=Path, help="public JSON output path")
    parser.add_argument("--label", required=True, help="public source label")
    args = parser.parse_args()

    if not args.root.is_dir():
        parser.error(f"firmware root does not exist: {args.root}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_inventory(args.root, args.label), indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
