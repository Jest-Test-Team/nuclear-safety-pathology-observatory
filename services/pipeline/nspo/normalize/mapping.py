from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_MAPPINGS_DIR = ROOT / "configs" / "mappings"


class MappingError(ValueError):
    """Raised when a source mapping is missing or cannot resolve required fields."""


def load_mapping(source_id: str, mappings_dir: str | Path | None = None) -> dict[str, Any]:
    directory = Path(mappings_dir) if mappings_dir else DEFAULT_MAPPINGS_DIR
    path = directory / f"{source_id}.yaml"
    if not path.exists():
        raise MappingError(f"missing field mapping for source: {source_id} ({path})")
    with path.open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    if not isinstance(document, dict) or "fields" not in document:
        raise MappingError(f"invalid mapping document: {path}")
    return document


def resolve_field(payload: dict[str, Any], candidates: list[str]) -> Any | None:
    lowered = {str(key).strip().lower(): value for key, value in payload.items()}
    for candidate in candidates:
        value = payload.get(candidate)
        if value not in (None, ""):
            return value
        value = lowered.get(candidate.lower())
        if value not in (None, ""):
            return value
    return None


def observed_schema_hash(payload: dict[str, Any]) -> str:
    from hashlib import sha256

    material = "|".join(sorted(str(key) for key in payload.keys())).encode("utf-8")
    return f"sha256:{sha256(material).hexdigest()}"
