from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from statistics import mean, pstdev
from typing import Any
from uuid import uuid4

REQUIRED_STATUS = "requires-expert-review"


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _finding(rule: dict[str, Any], evidence: list[dict[str, Any]], scope: dict[str, Any], uncertainty: float, missing: list[str]) -> dict[str, Any]:
    return {
        "finding_id": f"finding-{uuid4()}",
        "rule_id": rule["id"],
        "finding_type": rule["type"],
        "status": REQUIRED_STATUS,
        "created_at": _iso_now(),
        "scope": scope,
        "supporting_evidence": [item["observation_id"] for item in evidence],
        "missing_evidence": missing,
        "alternative_explanations": list(rule["alternatives"]),
        "limitations": list(rule["limitations"]),
        "uncertainty": max(0.0, min(1.0, uncertainty)),
        "synthetic": all(bool(item.get("synthetic")) for item in evidence),
    }



def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _stale_feed(rule: dict[str, Any], observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    multiplier = float(rule["parameters"]["multiplier"])
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in observations:
        grouped[(item["station_id"], item["metric"])].append(item)
    findings: list[dict[str, Any]] = []
    for (station_id, metric), items in grouped.items():
        ordered = sorted(items, key=lambda value: value["observed_at"])
        for previous, current in zip(ordered, ordered[1:]):
            expected = float(current.get("context", {}).get("expected_interval_seconds", 300))
            gap = (_parse_time(current["observed_at"]) - _parse_time(previous["observed_at"])).total_seconds()
            if gap > expected * multiplier:
                findings.append(_finding(rule, [previous, current], {"station_id": station_id, "metric": metric, "gap_seconds": gap, "expected_interval_seconds": expected}, 0.30, ["official maintenance notice", "upstream publication status"]))
                break
    return findings


def _constant_value(rule: dict[str, Any], observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    minimum = int(rule["parameters"]["minimum_count"])
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in observations:
        grouped[(item["station_id"], item["metric"])].append(item)
    findings: list[dict[str, Any]] = []
    for (station_id, metric), items in grouped.items():
        ordered = sorted(items, key=lambda value: value["observed_at"])
        if len(ordered) >= minimum and len({item["value"] for item in ordered[-minimum:]}) == 1:
            evidence = ordered[-minimum:]
            findings.append(_finding(rule, evidence, {"station_id": station_id, "metric": metric}, 0.55, ["instrument maintenance record", "independent comparison measurement"]))
    return findings


def _local_spatial_outlier(rule: dict[str, Any], observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest_by_station: dict[str, dict[str, Any]] = {}
    for item in observations:
        if item["metric"] != "gamma-dose-rate":
            continue
        current = latest_by_station.get(item["station_id"])
        if current is None or item["observed_at"] > current["observed_at"]:
            latest_by_station[item["station_id"]] = item
    items = list(latest_by_station.values())
    if len(items) < 3:
        return []
    values = [float(item["value"]) for item in items]
    sigma = pstdev(values)
    if sigma == 0:
        return []
    center = mean(values)
    threshold = float(rule["parameters"]["zscore_threshold"])
    findings = []
    for item in items:
        zscore = abs((float(item["value"]) - center) / sigma)
        if zscore >= threshold:
            findings.append(_finding(rule, [item], {"station_id": item["station_id"], "metric": item["metric"], "zscore": round(zscore, 3)}, 0.62, ["local weather context", "calibration record", "additional neighboring stations"]))
    return findings


def _multi_station(rule: dict[str, Any], observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_time: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in observations:
        if item["metric"] == "gamma-dose-rate":
            by_time[item["observed_at"]].append(item)
    minimum = int(rule["parameters"]["minimum_stations"])
    findings = []
    for observed_at, items in by_time.items():
        baseline = [float(i["context"].get("baseline", i["value"])) for i in items]
        deviating = [i for i in items if float(i["value"]) > float(i["context"].get("baseline", i["value"])) * 1.35]
        if len(deviating) >= minimum:
            findings.append(_finding(rule, deviating, {"observed_at": observed_at, "stations": [i["station_id"] for i in deviating], "baseline_mean": mean(baseline)}, 0.48, ["regional weather observations", "official event annotations", "independent measurement network"]))
    return findings



def _post_event_recovery(rule: dict[str, Any], observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tolerance = float(rule["parameters"]["baseline_tolerance_fraction"])
    window = int(rule["parameters"]["recovery_window_minutes"])
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in observations:
        grouped[(item["station_id"], item["metric"])].append(item)
    findings: list[dict[str, Any]] = []
    for (station_id, metric), items in grouped.items():
        ordered = sorted(items, key=lambda value: value["observed_at"])
        for index, event_item in enumerate(ordered):
            if not event_item.get("context", {}).get("event"):
                continue
            baseline = float(event_item.get("context", {}).get("baseline", event_item["value"]))
            deadline = _parse_time(event_item["observed_at"]).timestamp() + window * 60
            later = [item for item in ordered[index + 1:] if _parse_time(item["observed_at"]).timestamp() <= deadline]
            recovered = any(abs(float(item["value"]) - baseline) <= baseline * tolerance for item in later)
            event_deviates = abs(float(event_item["value"]) - baseline) > baseline * tolerance
            if event_deviates and not recovered:
                evidence = [event_item] + later
                findings.append(_finding(rule, evidence, {"station_id": station_id, "metric": metric, "event": event_item["context"]["event"], "recovery_window_minutes": window}, 0.58, ["observations after recovery window", "official event annotation", "instrument maintenance context"]))
                break
    return findings


def analyze(observations: list[dict[str, Any]], rules_document: dict[str, Any]) -> list[dict[str, Any]]:
    for item in observations:
        if item.get("public_data") is not True:
            raise ValueError("all observations must be marked public_data=true")
        if not item.get("provenance"):
            raise ValueError("all observations require provenance")

    handlers = {
        "stale-feed": _stale_feed,
        "constant-value": _constant_value,
        "local-spatial-outlier": _local_spatial_outlier,
        "multi-station-deviation": _multi_station,
        "post-event-recovery-delay": _post_event_recovery,
    }
    findings: list[dict[str, Any]] = []
    for rule in rules_document.get("rules", []):
        handler = handlers.get(rule["id"])
        if handler:
            findings.extend(handler(rule, observations))
    return findings
