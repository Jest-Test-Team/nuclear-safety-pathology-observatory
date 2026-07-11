from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from statistics import mean
from typing import Any


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def compute_maturity_index(
    observations: list[dict[str, Any]],
    *,
    now: datetime | None = None,
    expected_schema_by_source: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Reproducible open-data observability maturity metrics (not safety scores)."""
    clock = now or datetime.now(timezone.utc)
    expected_schema_by_source = expected_schema_by_source or {}
    if not observations:
        return {
            "score": 0.0,
            "components": {
                "freshness_compliance": 0.0,
                "schema_stability": 0.0,
                "provenance_completeness": 0.0,
                "endpoint_availability_proxy": 0.0,
            },
            "source_count": 0,
            "observation_count": 0,
        }

    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in observations:
        by_source[str(item["source_id"])].append(item)

    freshness_scores: list[float] = []
    schema_scores: list[float] = []
    provenance_scores: list[float] = []
    availability_scores: list[float] = []

    for source_id, items in by_source.items():
        latest = max(items, key=lambda value: value["observed_at"])
        expected = float(latest.get("context", {}).get("expected_interval_seconds", 300))
        age = (clock - _parse_time(latest["observed_at"])).total_seconds()
        freshness_scores.append(1.0 if age <= expected * 3 else 0.0)

        mismatches = 0
        for item in items:
            expected_hash = item.get("context", {}).get("expected_schema_hash") or expected_schema_by_source.get(source_id)
            observed_hash = item.get("context", {}).get("observed_schema_hash")
            if expected_hash and observed_hash and expected_hash != observed_hash:
                mismatches += 1
        schema_scores.append(1.0 - (mismatches / len(items)))

        complete = 0
        for item in items:
            provenance = item.get("provenance") or {}
            if provenance.get("retrieved_at") and provenance.get("source_record_id") and provenance.get("content_hash"):
                complete += 1
        provenance_scores.append(complete / len(items))

        # Proxy: sources that produced at least one observation in the archive are "available".
        availability_scores.append(1.0)

    components = {
        "freshness_compliance": round(mean(freshness_scores), 4),
        "schema_stability": round(mean(schema_scores), 4),
        "provenance_completeness": round(mean(provenance_scores), 4),
        "endpoint_availability_proxy": round(mean(availability_scores), 4),
    }
    score = round(mean(components.values()), 4)
    return {
        "score": score,
        "components": components,
        "source_count": len(by_source),
        "observation_count": len(observations),
        "generated_at": clock.isoformat(),
        "disclaimer": "Maturity index describes public-data publication quality only; it is not a facility safety assessment.",
    }


def source_reliability_report(observations: list[dict[str, Any]], *, now: datetime | None = None) -> list[dict[str, Any]]:
    clock = now or datetime.now(timezone.utc)
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in observations:
        by_source[str(item["source_id"])].append(item)
    reports: list[dict[str, Any]] = []
    for source_id, items in sorted(by_source.items()):
        latest = max(items, key=lambda value: value["observed_at"])
        expected = float(latest.get("context", {}).get("expected_interval_seconds", 300))
        age = (clock - _parse_time(latest["observed_at"])).total_seconds()
        drift = sum(
            1
            for item in items
            if item.get("context", {}).get("expected_schema_hash")
            and item.get("context", {}).get("observed_schema_hash")
            and item["context"]["expected_schema_hash"] != item["context"]["observed_schema_hash"]
        )
        reports.append(
            {
                "source_id": source_id,
                "authority_country": items[0].get("country"),
                "observation_count": len(items),
                "latest_observed_at": latest["observed_at"],
                "age_seconds": age,
                "fresh": age <= expected * 3,
                "schema_drift_count": drift,
                "stations": sorted({item["station_id"] for item in items}),
            }
        )
    return reports
