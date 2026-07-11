from __future__ import annotations

from pathlib import Path

from nspo.connectors.base import RawRecord
from nspo.connectors.kr_public import KoreaPublicAPIConnector, _redact_url
from nspo.normalize import load_mapping, normalize_radiation_record
from nspo.schema_validate import validate_observation_records

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_korea_xml_and_json_fixtures():
    connector = KoreaPublicAPIConnector.__new__(KoreaPublicAPIConnector)
    connector.source_id = "kr-korad-radiation"
    xml_text = (FIXTURES / "kr_korad_radiation_sample.xml").read_text(encoding="utf-8")
    xml_records = connector._parse_xml(xml_text)
    assert len(xml_records) == 2
    assert xml_records[0]["resultCode"] == "00"
    assert xml_records[0]["stationId"] == "KR-RAD-1"

    json_text = (FIXTURES / "kr_khnp_weather_sample.json").read_text(encoding="utf-8")
    json_records = connector._parse_json(json_text)
    assert len(json_records) == 1
    assert json_records[0]["stationId"] == "KR-WX-1"


def test_normalize_korea_fixture_records():
    connector = KoreaPublicAPIConnector.__new__(KoreaPublicAPIConnector)
    connector.source_id = "kr-korad-radiation"
    xml_text = (FIXTURES / "kr_korad_radiation_sample.xml").read_text(encoding="utf-8")
    payloads = connector._parse_xml(xml_text)
    mapping = load_mapping("kr-korad-radiation")
    observations = [
        normalize_radiation_record(
            RawRecord.from_payload("kr-korad-radiation", str(payload["stationId"]), payload, "synthetic://kr"),
            mapping,
        )
        for payload in payloads
    ]
    validate_observation_records(observations)
    assert observations[0]["metric"] == "gamma-dose-rate"
    assert observations[0]["country"] == "KR"


def test_redact_service_key_from_source_url():
    url = "https://example.invalid/api?serviceKey=super-secret&page=1"
    redacted = _redact_url(url)
    assert "super-secret" not in redacted
    assert "REDACTED" in redacted
