from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
START = datetime(2026, 7, 11, 0, 0, tzinfo=timezone.utc)


def obs(station: str, minute: int, value: float, baseline: float, index: int) -> dict:
    observed_at = START + timedelta(minutes=minute)
    raw = f"{station}:{observed_at.isoformat()}:{value}".encode()
    return {
        "observation_id": f"obs-{index:03d}",
        "source_id": "synthetic-demo",
        "station_id": station,
        "observed_at": observed_at.isoformat(),
        "metric": "gamma-dose-rate",
        "value": value,
        "unit": "nSv/h",
        "latitude": 25.0 + index / 1000,
        "longitude": 121.5 + index / 1000,
        "country": "ZZ",
        "public_data": True,
        "synthetic": True,
        "provenance": {
            "retrieved_at": observed_at.isoformat(),
            "source_record_id": f"synthetic-{index:03d}",
            "source_url": "synthetic://nspo/demo",
            "content_hash": sha256(raw).hexdigest(),
        },
        "context": {"baseline": baseline, "event": "synthetic-weather-front" if minute == 25 else None, "expected_interval_seconds": 300},
    }


records = []
index = 1
for minute in (0, 5, 10, 15, 20, 25):
    for station, baseline in (("ZZ-A", 42.0), ("ZZ-B", 43.0), ("ZZ-C", 41.5), ("ZZ-D", 42.5), ("ZZ-E", 40.0)):
        value = baseline
        if station == "ZZ-D":
            value = 180.0 if minute == 25 else baseline
        if minute == 25 and station in {"ZZ-A", "ZZ-B", "ZZ-C"}:
            value = baseline * 1.5
        records.append(obs(station, minute, value, baseline, index))
        index += 1

# A deliberately sparse feed for freshness testing.
for minute in (0, 25):
    records.append(obs("ZZ-F", minute, 43.0, 43.0, index))
    index += 1

path = ROOT / "data/synthetic/observations.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
print(f"wrote {len(records)} synthetic observations")
