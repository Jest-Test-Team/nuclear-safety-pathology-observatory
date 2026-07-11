from __future__ import annotations

from pathlib import Path

import yaml

from nspo.engine.analyzer import analyze
from nspo.io.jsonio import load_json

ROOT = Path(__file__).resolve().parents[3]
FAULT_ROOT = ROOT / "data/synthetic"


def _rules():
    with (ROOT / "rules/patterns.yaml").open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_labeled_fault_precision():
    catalog = load_json(FAULT_ROOT / "fault_labels.json")
    rules = _rules()
    for case in catalog["cases"]:
        observations = load_json(FAULT_ROOT / case["observations_file"])
        findings = analyze(observations, rules)
        fired = {item["rule_id"] for item in findings}
        expected = set(case["expected_rule_ids"])
        forbidden = set(case.get("forbidden_rule_ids", []))
        missing = expected - fired
        assert not missing, f"{case['id']}: missing expected rules {missing}; fired={fired}"
        overlap = fired & forbidden
        assert not overlap, f"{case['id']}: unexpected rules {overlap}; fired={fired}"
        for finding in findings:
            if finding["rule_id"] in expected:
                assert finding["status"] == "requires-expert-review"
                assert finding["alternative_explanations"]
                assert finding["limitations"]
