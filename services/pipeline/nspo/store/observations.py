from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nspo.io.jsonio import load_json, write_json


def append_observations(path: str | Path, new_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Append observations without silently overwriting prior retrieval versions."""
    target = Path(path)
    existing: list[dict[str, Any]] = []
    if target.exists():
        loaded = load_json(target)
        if not isinstance(loaded, list):
            raise ValueError(f"observation store must be a JSON array: {target}")
        existing = loaded

    existing_keys = {
        (
            item.get("source_id"),
            item.get("provenance", {}).get("source_record_id"),
            item.get("context", {}).get("retrieval_version"),
            item.get("provenance", {}).get("content_hash"),
        )
        for item in existing
    }
    appended: list[dict[str, Any]] = []
    for item in new_records:
        key = (
            item.get("source_id"),
            item.get("provenance", {}).get("source_record_id"),
            item.get("context", {}).get("retrieval_version"),
            item.get("provenance", {}).get("content_hash"),
        )
        if key in existing_keys:
            continue
        existing.append(item)
        existing_keys.add(key)
        appended.append(item)
    write_json(target, existing)
    return appended


def write_retrieval_manifest(path: str | Path, manifest: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
