from __future__ import annotations

import csv
from pathlib import Path

import pytest

from nspo.connectors.base import RawRecord
from nspo.normalize import MappingError, build_station_lookup, load_mapping, normalize_radiation_record
from nspo.schema_validate import validate_observation_records

FIXTURES = Path(__file__).parent / "fixtures"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_load_mapping_requires_file():
    with pytest.raises(MappingError):
        load_mapping("does-not-exist")


def test_normalize_radiation_with_chinese_headers():
    mapping = load_mapping("tw-nusc-radiation-realtime")
    rows = _rows(FIXTURES / "tw_nusc_radiation_sample.csv")
    raw = RawRecord.from_payload("tw-nusc-radiation-realtime", "row-1", dict(rows[0]), "synthetic://fixture")
    observation = normalize_radiation_record(raw, mapping)
    validate_observation_records([observation])
    assert observation["station_id"] == "TW-DEMO-1"
    assert observation["unit"] == "nSv/h"
    assert observation["public_data"] is True
    assert observation["provenance"]["source_record_id"] == "row-1"


def test_refuse_normalize_without_required_fields():
    mapping = load_mapping("tw-nusc-radiation-realtime")
    raw = RawRecord.from_payload("tw-nusc-radiation-realtime", "row-x", {"unexpected": "1"}, "synthetic://fixture")
    with pytest.raises(MappingError):
        normalize_radiation_record(raw, mapping)


def test_station_metadata_join_fills_coordinates():
    station_rows = _rows(FIXTURES / "tw_nusc_stations_sample.csv")
    station_records = [
        RawRecord.from_payload("tw-nusc-station-metadata", f"row-{index}", dict(row), "synthetic://stations")
        for index, row in enumerate(station_rows, start=1)
    ]
    lookup = build_station_lookup(station_records)
    mapping = load_mapping("tw-nusc-radiation-realtime")
    radiation_row = _rows(FIXTURES / "tw_nusc_radiation_sample.csv")[0]
    # Drop coordinates from radiation payload to require join.
    payload = {key: value for key, value in radiation_row.items() if key not in {"緯度", "經度"}}
    raw = RawRecord.from_payload("tw-nusc-radiation-realtime", "row-1", payload, "synthetic://fixture")
    observation = normalize_radiation_record(raw, mapping, station_lookup=lookup)
    assert observation["latitude"] == pytest.approx(25.1234)
    assert observation["longitude"] == pytest.approx(121.5678)
