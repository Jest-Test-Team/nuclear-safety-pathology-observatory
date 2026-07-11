from __future__ import annotations

import argparse
import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from nspo.connectors.base import ConnectorError, RawRecord
from nspo.connectors.kr_public import KoreaPublicXMLConnector
from nspo.connectors.tw_nusc import TaiwanNUSCCSVConnector
from nspo.engine.monitor import monitor_source_health
from nspo.io.jsonio import write_json
from nspo.normalize import MappingError, build_station_lookup, load_mapping, normalize_radiation_record
from nspo.safety import validate_observations
from nspo.schema_validate import validate_observation_records
from nspo.sources import get_source
from nspo.store import append_observations, write_retrieval_manifest

ROOT = Path(__file__).resolve().parents[4]
RUNTIME = ROOT / "data" / "runtime"


def _connector_for(source: dict[str, Any]):
    source_id = source["id"]
    if source_id.startswith("tw-nusc-"):
        return TaiwanNUSCCSVConnector(source_id, source["endpoint_env"])
    if source_id.startswith("kr-"):
        return KoreaPublicXMLConnector(source_id, source["endpoint_env"], source.get("credential_env", "NSPO_KOREA_SERVICE_KEY"))
    raise ConnectorError(f"no connector registered for {source_id}")


def _records_from_file(source_id: str, path: Path) -> list[RawRecord]:
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".json":
        payload = json.loads(text)
        if isinstance(payload, list):
            return [
                RawRecord.from_payload(source_id, str(item.get("id") or index), dict(item), path.as_uri())
                for index, item in enumerate(payload, start=1)
            ]
        raise ConnectorError("JSON fixture must be an array of objects")
    reader = csv.DictReader(io.StringIO(text))
    return [RawRecord.from_payload(source_id, f"row-{index}", dict(row), path.as_uri()) for index, row in enumerate(reader, start=1)]


def collect_source(
    source_id: str,
    *,
    input_file: str | None = None,
    station_file: str | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    source = get_source(source_id)
    out = output_dir or RUNTIME
    out.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()

    if input_file:
        raw_records = _records_from_file(source_id, Path(input_file))
    else:
        connector = _connector_for(source)
        raw_records = list(connector.fetch())

    station_lookup = None
    if station_file:
        station_source = get_source("tw-nusc-station-metadata")
        station_raw = _records_from_file(station_source["id"], Path(station_file))
        station_lookup = build_station_lookup(station_raw)

    mapping = None
    if source.get("mapping_file") or source_id.startswith("tw-nusc-radiation"):
        mapping = load_mapping(source_id)

    observations: list[dict[str, Any]] = []
    errors: list[str] = []
    for raw in raw_records:
        try:
            if source_id == "tw-nusc-station-metadata":
                continue
            obs = normalize_radiation_record(raw, mapping, station_lookup=station_lookup)
            obs["context"]["retrieval_version"] = retrieved_at
            if source.get("expected_interval_seconds"):
                obs["context"]["expected_interval_seconds"] = source["expected_interval_seconds"]
            observations.append(obs)
        except MappingError as exc:
            errors.append(str(exc))

    if observations:
        validate_observation_records(observations)
        validate_observations(observations)

    observations_path = out / f"{source_id}.observations.json"
    appended = append_observations(observations_path, observations)

    raw_archive = out / "raw" / source_id / f"{retrieved_at.replace(':', '')}.json"
    write_json(raw_archive, [raw.__dict__ for raw in raw_records])

    with (ROOT / "rules" / "patterns.yaml").open("r", encoding="utf-8") as handle:
        rules = yaml.safe_load(handle)
    findings = monitor_source_health(observations, rules) if observations else []
    findings_path = out / f"{source_id}.monitor-findings.json"
    write_json(findings_path, findings)

    manifest = {
        "source_id": source_id,
        "retrieved_at": retrieved_at,
        "raw_count": len(raw_records),
        "normalized_count": len(observations),
        "appended_count": len(appended),
        "errors": errors,
        "observations_path": str(observations_path),
        "findings_path": str(findings_path),
        "raw_archive": str(raw_archive),
    }
    write_retrieval_manifest(out / f"{source_id}.manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect and normalize a configured public-data source")
    parser.add_argument("--source", required=True, help="Source id from configs/sources.yaml")
    parser.add_argument("--input-file", help="Optional local CSV/JSON fixture instead of live HTTP")
    parser.add_argument("--station-file", help="Optional station metadata CSV for coordinate join")
    parser.add_argument("--output-dir", default=str(RUNTIME))
    args = parser.parse_args()
    manifest = collect_source(
        args.source,
        input_file=args.input_file,
        station_file=args.station_file,
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
