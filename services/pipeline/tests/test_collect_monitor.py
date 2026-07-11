from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from nspo.engine.collect import collect_source
from nspo.engine.monitor import monitor_source_health
from nspo.io.jsonio import load_json
from nspo.store import append_observations

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = Path(__file__).parent / "fixtures"


def _rules():
    with (ROOT / "rules/patterns.yaml").open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_append_observations_keeps_prior_retrieval_versions(tmp_path: Path):
    path = tmp_path / "obs.json"
    first = [
        {
            "observation_id": "obs-1",
            "source_id": "tw-nusc-radiation-monthly",
            "station_id": "TW-1",
            "observed_at": "2026-01-01T00:00:00+00:00",
            "metric": "gamma-dose-rate",
            "value": 40.0,
            "unit": "nSv/h",
            "public_data": True,
            "provenance": {"retrieved_at": "t1", "source_record_id": "row-1", "content_hash": "a"},
            "context": {"retrieval_version": "t1"},
        }
    ]
    second = [
        {
            **first[0],
            "observation_id": "obs-2",
            "value": 41.0,
            "provenance": {"retrieved_at": "t2", "source_record_id": "row-1", "content_hash": "b"},
            "context": {"retrieval_version": "t2"},
        }
    ]
    append_observations(path, first)
    append_observations(path, second)
    stored = load_json(path)
    assert len(stored) == 2
    append_observations(path, second)
    assert len(load_json(path)) == 2


def test_monitor_emits_schema_drift_and_stale_feed():
    observations = load_json(ROOT / "data/synthetic/faults/schema_drift.json")
    now = datetime.now(timezone.utc)
    for item in observations:
        item["observed_at"] = now.isoformat()
    findings = monitor_source_health(observations, _rules())
    assert {item["rule_id"] for item in findings} == {"schema-drift"}

    stale = load_json(ROOT / "data/synthetic/faults/stale_feed.json")
    past = now - timedelta(hours=2)
    for index, item in enumerate(stale):
        item["observed_at"] = (past + timedelta(minutes=index)).isoformat()
        item["context"]["expected_interval_seconds"] = 300
    findings = monitor_source_health(stale, _rules())
    assert "stale-feed" in {item["rule_id"] for item in findings}


def test_collect_monthly_appends_retrieval_versions(tmp_path: Path):
    first = collect_source(
        "tw-nusc-radiation-monthly",
        input_file=str(FIXTURES / "tw_nusc_monthly_sample.csv"),
        output_dir=tmp_path,
    )
    second = collect_source(
        "tw-nusc-radiation-monthly",
        input_file=str(FIXTURES / "tw_nusc_monthly_sample.csv"),
        output_dir=tmp_path,
    )
    assert first["appended_count"] == 2
    # Same content hash + different retrieval_version => retained as correction history.
    assert second["appended_count"] == 2
    stored = load_json(tmp_path / "tw-nusc-radiation-monthly.observations.json")
    assert len(stored) == 4


def test_collect_from_fixture_files(tmp_path: Path):
    manifest = collect_source(
        "tw-nusc-radiation-realtime",
        input_file=str(FIXTURES / "tw_nusc_radiation_sample.csv"),
        station_file=str(FIXTURES / "tw_nusc_stations_sample.csv"),
        output_dir=tmp_path,
    )
    assert manifest["normalized_count"] == 2
    assert manifest["appended_count"] == 2
    observations = load_json(tmp_path / "tw-nusc-radiation-realtime.observations.json")
    assert observations[0]["latitude"]
    assert observations[0]["context"]["retrieval_version"]
