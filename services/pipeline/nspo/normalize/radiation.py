from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from typing import Any
from zoneinfo import ZoneInfo

from nspo.connectors.base import RawRecord
from nspo.normalize.mapping import MappingError, load_mapping, observed_schema_hash, resolve_field


def _parse_observed_at(value: Any, timezone_name: str) -> str:
    text = str(value).strip()
    if not text:
        raise MappingError("observed_at is required")
    # Accept ISO timestamps or YYYY-MM / YYYY-MM-DD monthly markers.
    if len(text) == 7 and text[4] == "-":
        text = f"{text}-01T00:00:00"
    elif len(text) == 10 and text[4] == "-" and text[7] == "-":
        text = f"{text}T00:00:00"
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(timezone_name))
    return dt.isoformat()


def _as_float(value: Any, field_name: str) -> float:
    try:
        return float(str(value).strip().replace(",", ""))
    except (TypeError, ValueError) as exc:
        raise MappingError(f"invalid numeric value for {field_name}: {value}") from exc


def normalize_radiation_record(
    raw: RawRecord,
    mapping: dict[str, Any] | None = None,
    *,
    station_lookup: dict[str, dict[str, float]] | None = None,
) -> dict[str, Any]:
    document = mapping or load_mapping(raw.source_id)
    fields = document["fields"]
    payload = raw.payload

    station_id = resolve_field(payload, list(fields.get("station_id", [])))
    observed_at = resolve_field(payload, list(fields.get("observed_at", [])))
    value = resolve_field(payload, list(fields.get("value", [])))
    if station_id in (None, "") or observed_at in (None, "") or value in (None, ""):
        raise MappingError(
            f"refuse to normalize {raw.source_id}: required fields unresolved from payload keys {sorted(payload)}"
        )

    unit = resolve_field(payload, list(fields.get("unit", []))) or document.get("default_unit")
    if not unit:
        raise MappingError("unit is required and no default_unit is configured")

    latitude = resolve_field(payload, list(fields.get("latitude", [])))
    longitude = resolve_field(payload, list(fields.get("longitude", [])))
    station_key = str(station_id).strip()
    if station_lookup and station_key in station_lookup:
        meta = station_lookup[station_key]
        latitude = latitude if latitude not in (None, "") else meta.get("latitude")
        longitude = longitude if longitude not in (None, "") else meta.get("longitude")

    expected_hash = str(document.get("schema_hash", ""))
    observed_hash = observed_schema_hash(payload)
    expected_fields = sorted({alias for aliases in fields.values() for alias in aliases})
    observed_fields = sorted(str(key) for key in payload.keys())

    observation_id = sha256(f"{raw.source_id}:{raw.source_record_id}:{raw.content_hash}".encode()).hexdigest()[:24]
    observation = {
        "observation_id": f"obs-{observation_id}",
        "source_id": raw.source_id,
        "station_id": station_key,
        "observed_at": _parse_observed_at(observed_at, str(document.get("timezone", "UTC"))),
        "metric": document.get("metric", "gamma-dose-rate"),
        "value": _as_float(value, "value"),
        "unit": str(unit).strip(),
        "country": document.get("country", "TW"),
        "public_data": True,
        "synthetic": False,
        "provenance": {
            "retrieved_at": raw.retrieved_at,
            "source_record_id": raw.source_record_id,
            "source_url": raw.source_url,
            "content_hash": raw.content_hash,
        },
        "context": {
            "expected_interval_seconds": document.get("expected_interval_seconds", 300),
            "expected_schema_hash": expected_hash,
            "observed_schema_hash": observed_hash,
            "expected_fields": expected_fields,
            "observed_fields": observed_fields,
            "retrieval_version": raw.retrieved_at,
        },
    }
    if latitude not in (None, ""):
        observation["latitude"] = _as_float(latitude, "latitude")
    if longitude not in (None, ""):
        observation["longitude"] = _as_float(longitude, "longitude")
    return observation


def build_station_lookup(records: list[RawRecord], mapping: dict[str, Any] | None = None) -> dict[str, dict[str, float]]:
    document = mapping
    lookup: dict[str, dict[str, float]] = {}
    for raw in records:
        doc = document or load_mapping(raw.source_id)
        fields = doc["fields"]
        station_id = resolve_field(raw.payload, list(fields.get("station_id", [])))
        latitude = resolve_field(raw.payload, list(fields.get("latitude", [])))
        longitude = resolve_field(raw.payload, list(fields.get("longitude", [])))
        if station_id in (None, "") or latitude in (None, "") or longitude in (None, ""):
            continue
        lookup[str(station_id).strip()] = {
            "latitude": _as_float(latitude, "latitude"),
            "longitude": _as_float(longitude, "longitude"),
        }
    return lookup
