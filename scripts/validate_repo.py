from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from nspo.config import load_app_config
from nspo.safety import validate_findings, validate_observations

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    observations = json.loads((ROOT / "data/synthetic/observations.json").read_text(encoding="utf-8"))
    observation_schema = json.loads((ROOT / "schema/observation.schema.json").read_text(encoding="utf-8"))
    finding_schema = json.loads((ROOT / "schema/finding.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(observation_schema)
    Draft202012Validator.check_schema(finding_schema)
    validator = Draft202012Validator(observation_schema)
    for item in observations:
        validator.validate(item)

    app_config = load_app_config(ROOT / "configs" / "app.yaml")
    validate_observations(observations, app_config)

    findings_path = ROOT / "data/derived/findings.json"
    if findings_path.exists():
        findings = json.loads(findings_path.read_text(encoding="utf-8"))
        finding_validator = Draft202012Validator(finding_schema)
        for item in findings:
            finding_validator.validate(item)
        validate_findings(findings, app_config)

    yaml.safe_load((ROOT / "configs/sources.yaml").read_text(encoding="utf-8"))
    yaml.safe_load((ROOT / "configs/app.yaml").read_text(encoding="utf-8"))
    yaml.safe_load((ROOT / "rules/patterns.yaml").read_text(encoding="utf-8"))
    yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))

    dockerfiles = list(ROOT.rglob("Dockerfile"))
    assert len(dockerfiles) <= 3, f"expected at most 3 Dockerfiles, got {len(dockerfiles)}"
    print(f"validated {len(observations)} observations, {len(dockerfiles)} Dockerfiles")


if __name__ == "__main__":
    main()