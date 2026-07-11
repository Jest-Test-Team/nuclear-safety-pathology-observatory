from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from nspo.engine.analyzer import analyze
from nspo.io.jsonio import load_json, write_json
from nspo.research import compute_maturity_index, recovery_trajectories, source_reliability_report

ROOT = Path(__file__).resolve().parents[4]


def main() -> None:
    parser = argparse.ArgumentParser(description="Export cross-border research reports from archived observations")
    parser.add_argument("--input", default=str(ROOT / "data/synthetic/observations.json"))
    parser.add_argument("--rules", default=str(ROOT / "rules/patterns.yaml"))
    parser.add_argument("--output-dir", default=str(ROOT / "data/derived/research"))
    args = parser.parse_args()

    observations = load_json(args.input)
    with Path(args.rules).open("r", encoding="utf-8") as handle:
        rules = yaml.safe_load(handle)
    findings = analyze(observations, rules)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    maturity = compute_maturity_index(observations)
    reliability = source_reliability_report(observations)
    trajectories = recovery_trajectories(observations, findings)

    write_json(out / "maturity_index.json", maturity)
    write_json(out / "source_reliability.json", reliability)
    write_json(out / "recovery_trajectories.json", trajectories)

    markdown = [
        "# Source reliability report",
        "",
        maturity["disclaimer"],
        "",
        f"Overall maturity score: **{maturity['score']}**",
        "",
        "| source_id | country | observations | fresh | schema_drift_count |",
        "| --- | --- | ---: | --- | ---: |",
    ]
    for row in reliability:
        markdown.append(
            f"| {row['source_id']} | {row['authority_country']} | {row['observation_count']} | {row['fresh']} | {row['schema_drift_count']} |"
        )
    (out / "source_reliability.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    print(json.dumps({"output_dir": str(out), "maturity_score": maturity["score"], "trajectories": len(trajectories)}, indent=2))


if __name__ == "__main__":
    main()
