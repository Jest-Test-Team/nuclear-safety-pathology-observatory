from __future__ import annotations

import json
from typing import Any

from nspo.config import accepted_units, forbidden_labels, load_app_config, required_finding_status


def validate_observations(observations: list[dict[str, Any]], config: dict[str, Any] | None = None) -> None:
    """Reject observations that violate public-data and unit invariants."""
    cfg = config or load_app_config()
    units = accepted_units(cfg)
    pipeline = cfg.get("pipeline", {})
    for item in observations:
        if pipeline.get("strict_public_data_only", True) and item.get("public_data") is not True:
            raise ValueError("all observations must be marked public_data=true")
        if pipeline.get("require_provenance", True) and not item.get("provenance"):
            raise ValueError("all observations require provenance")
        unit = item.get("unit")
        if units and unit not in units:
            raise ValueError(f"unsupported unit: {unit}")
        if pipeline.get("reject_direct_facility_control_fields", True):
            forbidden_fields = {"control_command", "actuator", "setpoint", "facility_control"}
            context_keys = set((item.get("context") or {}).keys())
            overlap = forbidden_fields & context_keys
            if overlap:
                raise ValueError(f"facility-control fields are not allowed: {sorted(overlap)}")


def validate_findings(findings: list[dict[str, Any]], config: dict[str, Any] | None = None) -> None:
    """Reject findings with forbidden labels or missing mandatory review fields."""
    cfg = config or load_app_config()
    status = required_finding_status(cfg)
    forbidden = forbidden_labels(cfg)
    require_alts = bool(cfg.get("findings", {}).get("require_alternative_explanations", True))
    require_limits = bool(cfg.get("findings", {}).get("require_limitations", True))
    for item in findings:
        if item.get("status") != status:
            raise ValueError(f"finding status must be {status}")
        if require_alts and not item.get("alternative_explanations"):
            raise ValueError("findings require alternative_explanations")
        if require_limits and not item.get("limitations"):
            raise ValueError("findings require limitations")
        text = json.dumps(item, ensure_ascii=False).lower()
        for label in forbidden:
            if label in text:
                raise ValueError(f"forbidden finding label present: {label}")
