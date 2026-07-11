from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schema"


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


def validator_for(name: str) -> Draft202012Validator:
    schema = load_schema(name)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_observation_records(observations: list[dict[str, Any]]) -> None:
    validator = validator_for("observation.schema.json")
    for item in observations:
        validator.validate(item)


def validate_finding_records(findings: list[dict[str, Any]]) -> None:
    validator = validator_for("finding.schema.json")
    for item in findings:
        validator.validate(item)
