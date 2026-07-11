from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from nspo.engine.analyzer import analyze
from nspo.io.jsonio import load_json, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze normalized public observations with transparent rules")
    parser.add_argument("--input", required=True)
    parser.add_argument("--rules", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    observations = load_json(args.input)
    with Path(args.rules).open("r", encoding="utf-8") as handle:
        rules = yaml.safe_load(handle)
    findings = analyze(observations, rules)
    write_json(args.output, findings)
    print(f"wrote {len(findings)} findings to {args.output}")


if __name__ == "__main__":
    main()
