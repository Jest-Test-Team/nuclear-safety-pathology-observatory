from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCES = ROOT / "configs" / "sources.yaml"


def load_sources(path: str | Path | None = None) -> list[dict[str, Any]]:
    target = Path(path) if path else DEFAULT_SOURCES
    document = yaml.safe_load(target.read_text(encoding="utf-8"))
    sources = document.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("sources.yaml must contain a sources list")
    return sources


def get_source(source_id: str, path: str | Path | None = None) -> dict[str, Any]:
    for source in load_sources(path):
        if source.get("id") == source_id:
            return source
    raise KeyError(f"unknown source_id: {source_id}")
