#!/usr/bin/env python3
"""Export a metadata-only REA evidence record for public research notes.

The full REA result can contain decompiler pseudocode, assembly, strings, and
reference data derived from a proprietary firmware image. Those fields stay in
the private research archive. This exporter deliberately publishes only the
hash-bound subject metadata and analysis provenance.
"""

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
    digest = subject.get("digest") or {}
    profile = source.get("analysis_profile") or source.get("analysis") or {}
    provider = profile.get("provider")
    if isinstance(provider, dict):
        provider = {
            key: provider.get(key)
            for key in ("id", "name", "version")
            if provider.get(key) is not None
        }
    else:
        provider = provider
    procedure = normalized.get("procedure") or source.get("procedure") or {}

    selected = {
        "schema_version": 1,
        "evidence_id": source.get("evidence_id"),
        "subject": {
            "name": subject.get("name"),
            "sha256": subject.get("sha256") or digest.get("sha256"),
            "format": subject.get("format"),
            "architecture": subject.get("architecture"),
            "public_label": label or subject.get("public_label") or subject.get("name"),
        },
        "analysis": {
            "provider": provider,
            "profile_digest": profile.get("digest") or profile.get("profile_digest"),
            "operation": source.get("operation") or profile.get("operation"),
            "confidence": source.get("confidence") or profile.get("confidence"),
            "authority": source.get("authority") or profile.get("authority"),
        },
        "procedure": {
            key: procedure.get(key)
            for key in ("address", "name")
            if procedure.get(key) is not None
        },
        "redaction": {
            "status": "metadata-only",
            "excluded_fields": [
                "pseudocode",
                "assembly",
                "comments",
                "callees",
                "callers",
                "incoming_references",
                "outgoing_references",
                "referenced_strings",
                "referenced_names",
                "basic_blocks",
                "native_api",
                "native_value_flow",
            ],
            "reason": "These fields may reproduce or closely derive from proprietary firmware code or data.",
        },
        "public_note": "The full REA result is retained in private research storage. Human-reviewed findings are documented in the milestone notes.",
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
