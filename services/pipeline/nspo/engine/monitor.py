from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from nspo.engine.analyzer import analyze


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def freshness_candidates(observations: list[dict[str, Any]], *, now: datetime | None = None) -> list[dict[str, Any]]:
    """Build synthetic gap observations so stale-feed can evaluate latest publication age."""
    clock = now or datetime.now(timezone.utc)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in observations:
        grouped[(item["station_id"], item["metric"])].append(item)
    probes: list[dict[str, Any]] = []
    for (station_id, metric), items in grouped.items():
        latest = max(items, key=lambda value: value["observed_at"])
        expected = float(latest.get("context", {}).get("expected_interval_seconds", 300))
        # Inject a virtual "now" observation so analyzer gap logic can fire.
        probe = dict(latest)
        probe = {
            **latest,
            "observation_id": f"{latest['observation_id']}-freshness-probe",
            "observed_at": clock.isoformat(),
            "context": {
                **(latest.get("context") or {}),
                "expected_interval_seconds": expected,
                "freshness_probe": True,
            },
        }
        age = (clock - _parse_time(latest["observed_at"])).total_seconds()
        if age > expected * 3:
            probes.extend([latest, probe])
    return probes


def monitor_source_health(observations: list[dict[str, Any]], rules_document: dict[str, Any]) -> list[dict[str, Any]]:
    """Emit data-quality findings for freshness and schema-drift only."""
    quality_rules = {
        "version": rules_document.get("version"),
        "mode": rules_document.get("mode"),
        "rules": [rule for rule in rules_document.get("rules", []) if rule["id"] in {"stale-feed", "schema-drift"}],
    }
    monitored = list(observations) + freshness_candidates(observations)
    findings = analyze(monitored, quality_rules)
    return [item for item in findings if item["rule_id"] in {"stale-feed", "schema-drift"}]
