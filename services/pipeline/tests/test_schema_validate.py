from __future__ import annotations

import copy
from pathlib import Path

import pytest
from jsonschema.exceptions import ValidationError

from nspo.io.jsonio import load_json
from nspo.schema_validate import validate_finding_records, validate_observation_records

ROOT = Path(__file__).resolve().parents[3]


def test_synthetic_observations_match_schema():
    observations = load_json(ROOT / "data/synthetic/observations.json")
    validate_observation_records(observations)


def test_invalid_observation_fails_schema():
    observations = load_json(ROOT / "data/synthetic/observations.json")
    bad = copy.deepcopy(observations[0])
    bad["metric"] = "not-a-metric"
    with pytest.raises(ValidationError):
        validate_observation_records([bad])


def test_invalid_finding_status_fails_schema():
    findings = load_json(ROOT / "data/derived/findings.json")
    assert findings, "run make demo before this test"
    bad = copy.deepcopy(findings[0])
    bad["status"] = "confirmed-accident"
    with pytest.raises(ValidationError):
        validate_finding_records([bad])
