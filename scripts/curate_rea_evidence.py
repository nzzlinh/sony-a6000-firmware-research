#!/usr/bin/env python3
"""Export a small, path-safe REA function dossier for public research notes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def scrub(value: Any) -> Any:
    """Remove local private artifact paths while keeping evidence readable."""

    if isinstance(value, str):
        return value.replace(
            "/home/zeelinh/sony-a6000-private",
            "<private-a6000-root>",
        )
    if isinstance(value, list):
        return [scrub(item) for item in value]
    if isinstance(value, dict):
        return {key: scrub(item) for key, item in value.items()}
    return value


def curate(source: dict[str, Any], label: str | None) -> dict[str, Any]:
    normalized = source.get("normalized_result") or {}
    subject = source.get("subject") or {}
    profile = source.get("analysis_profile") or {}

    selected = {
        "schema_version": 1,
        "evidence_id": source.get("evidence_id"),
        "subject": {
            "name": subject.get("name"),
            "sha256": (subject.get("digest") or {}).get("sha256"),
            "format": subject.get("format"),
            "architecture": subject.get("architecture"),
            "public_label": label or subject.get("name"),
        },
        "analysis": {
            "provider": profile.get("provider"),
            "profile_digest": profile.get("digest"),
            "operation": source.get("operation"),
            "parameters": source.get("parameters"),
            "confidence": source.get("confidence"),
            "authority": source.get("authority"),
        },
        "procedure": normalized.get("procedure"),
        "pseudocode": normalized.get("pseudocode"),
        "assembly": normalized.get("assembly"),
        "comments": normalized.get("comments"),
        "callees": normalized.get("callees"),
        "callers": normalized.get("callers"),
        "incoming_references": normalized.get("incoming_references"),
        "outgoing_references": normalized.get("outgoing_references"),
        "referenced_strings": normalized.get("referenced_strings"),
        "referenced_names": normalized.get("referenced_names"),
        "basic_blocks": normalized.get("basic_blocks"),
        "native_api": normalized.get("native_api"),
        "native_value_flow": normalized.get("native_value_flow"),
        "limitations": normalized.get("limitations") or source.get("limitations"),
    }
    return scrub(selected)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--label", default=None)
    args = parser.parse_args()

    source = json.loads(args.input.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(curate(source, args.label), indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
