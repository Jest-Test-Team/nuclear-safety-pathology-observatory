from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from nspo.engine.analyzer import analyze
from nspo.io.jsonio import load_json
from nspo.research import compute_maturity_index, recovery_trajectories, source_reliability_report

ROOT = Path(__file__).resolve().parents[3]


def _rules():
    with (ROOT / "rules/patterns.yaml").open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_maturity_and_reliability_reports():
    observations = load_json(ROOT / "data/synthetic/observations.json")
    now = datetime(2026, 7, 11, 1, 0, tzinfo=timezone.utc)
    maturity = compute_maturity_index(observations, now=now)
    assert 0.0 <= maturity["score"] <= 1.0
    assert "freshness_compliance" in maturity["components"]
    assert "not a facility safety assessment" in maturity["disclaimer"].lower()
    reliability = source_reliability_report(observations, now=now)
    assert reliability
    assert reliability[0]["source_id"]


def test_recovery_trajectories_link_evidence():
    observations = load_json(ROOT / "data/synthetic/observations.json")
    findings = analyze(observations, _rules())
    trajectories = recovery_trajectories(observations, findings)
    assert trajectories
    assert trajectories[0]["evidence_observation_ids"]
    assert trajectories[0]["values"]
