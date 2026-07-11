from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_APP_CONFIG = ROOT / "configs" / "app.yaml"


def load_app_config(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path else DEFAULT_APP_CONFIG
    with target.open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    if not isinstance(document, dict):
        raise ValueError("app config must be a mapping")
    return document


def accepted_units(config: dict[str, Any]) -> set[str]:
    units = config.get("pipeline", {}).get("accepted_units", [])
    return {str(item) for item in units}


def forbidden_labels(config: dict[str, Any]) -> set[str]:
    labels = config.get("findings", {}).get("forbidden_labels", [])
    return {str(item).lower() for item in labels}


def required_finding_status(config: dict[str, Any]) -> str:
    return str(config.get("findings", {}).get("required_status", "requires-expert-review"))
