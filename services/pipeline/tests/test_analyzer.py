from __future__ import annotations

from pathlib import Path

import yaml

from nspo.engine.analyzer import analyze
from nspo.io.jsonio import load_json

ROOT = Path(__file__).resolve().parents[3]


def _rules():
    with (ROOT / "rules/patterns.yaml").open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_demo_produces_review_only_findings():
    observations = load_json(ROOT / "data/synthetic/observations.json")
    findings = analyze(observations, _rules())
    assert findings
    assert all(item["status"] == "requires-expert-review" for item in findings)
    assert all(item["alternative_explanations"] for item in findings)
    assert all(item["limitations"] for item in findings)
    rule_ids = {item["rule_id"] for item in findings}
    assert {"stale-feed", "constant-value", "multi-station-deviation", "post-event-recovery-delay"}.issubset(rule_ids)


def test_rejects_non_public_observations():
    observations = load_json(ROOT / "data/synthetic/observations.json")
    observations[0]["public_data"] = False
    try:
        analyze(observations, _rules())
    except ValueError as exc:
        assert "public_data" in str(exc)
    else:
        raise AssertionError("expected ValueError")
