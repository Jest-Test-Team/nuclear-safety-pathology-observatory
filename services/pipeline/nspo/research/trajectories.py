from __future__ import annotations

from collections import defaultdict
from typing import Any


def recovery_trajectories(observations: list[dict[str, Any]], findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Link post-event recovery findings to ordered observation evidence packages."""
    by_id = {item["observation_id"]: item for item in observations}
    trajectories: list[dict[str, Any]] = []
    for finding in findings:
        if finding.get("rule_id") != "post-event-recovery-delay":
            continue
        evidence = [by_id[evidence_id] for evidence_id in finding.get("supporting_evidence", []) if evidence_id in by_id]
        ordered = sorted(evidence, key=lambda item: item["observed_at"])
        trajectories.append(
            {
                "finding_id": finding["finding_id"],
                "station_id": finding.get("scope", {}).get("station_id"),
                "event": finding.get("scope", {}).get("event"),
                "evidence_observation_ids": [item["observation_id"] for item in ordered],
                "values": [{"observed_at": item["observed_at"], "value": item["value"], "baseline": item.get("context", {}).get("baseline")} for item in ordered],
                "uncertainty": finding.get("uncertainty"),
                "alternative_explanations": finding.get("alternative_explanations"),
                "limitations": finding.get("limitations"),
                "disclaimer": "Trajectory view is descriptive public-data evidence only.",
            }
        )
    return trajectories


def group_findings_by_rule(findings: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for finding in findings:
        grouped[str(finding.get("rule_id"))].append(finding)
    return dict(grouped)
