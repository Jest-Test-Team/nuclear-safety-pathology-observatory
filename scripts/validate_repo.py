from __future__ import annotations

import json
from pathlib import Path

import yaml

from nspo.config import load_app_config
from nspo.safety import validate_findings, validate_observations
from nspo.schema_validate import validate_finding_records, validate_observation_records

ROOT = Path(__file__).resolve().parents[1]


def _assert_no_committed_secrets() -> None:
    tracked_files = list((ROOT / "configs").rglob("*"))
    tracked_files += list((ROOT / "data" / "synthetic").rglob("*"))
    tracked_files.append(ROOT / ".env.example")
    for file_path in tracked_files:
        if not file_path.is_file():
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            lower = stripped.lower()
            if "servicekey=" in lower or "api_key=" in lower or "apikey=" in lower:
                _, _, value = stripped.partition("=")
                if value.strip() and value.strip() not in {'""', "''"}:
                    raise AssertionError(f"possible committed credential in {file_path}: {stripped}")
            if stripped.startswith("NSPO_KOREA_SERVICE_KEY="):
                assert stripped == "NSPO_KOREA_SERVICE_KEY=", "service key must be empty in committed env examples"
            if "BEGIN PRIVATE KEY" in stripped:
                raise AssertionError(f"private key material in {file_path}")


def main() -> None:
    observations = json.loads((ROOT / "data/synthetic/observations.json").read_text(encoding="utf-8"))
    validate_observation_records(observations)

    app_config = load_app_config(ROOT / "configs" / "app.yaml")
    validate_observations(observations, app_config)

    findings_path = ROOT / "data/derived/findings.json"
    if findings_path.exists():
        findings = json.loads(findings_path.read_text(encoding="utf-8"))
        validate_finding_records(findings)
        validate_findings(findings, app_config)

    yaml.safe_load((ROOT / "configs/sources.yaml").read_text(encoding="utf-8"))
    yaml.safe_load((ROOT / "configs/app.yaml").read_text(encoding="utf-8"))
    yaml.safe_load((ROOT / "rules/patterns.yaml").read_text(encoding="utf-8"))
    yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    _assert_no_committed_secrets()

    dockerfiles = list(ROOT.rglob("Dockerfile"))
    assert len(dockerfiles) <= 3, f"expected at most 3 Dockerfiles, got {len(dockerfiles)}"
    print(f"validated {len(observations)} observations, {len(dockerfiles)} Dockerfiles")


if __name__ == "__main__":
    main()
