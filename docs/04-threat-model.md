# Threat Model

## Assets

- source credentials
- data provenance
- normalized observations
- findings and review decisions
- public trust

## Primary threats

- poisoned or malformed upstream data
- schema drift causing silent misinterpretation
- credential leakage
- forged provenance
- dashboard language overstating findings
- denial of service against ingestion
- unauthorized review modification
- accidental publication of sensitive inferred detail

## Controls

- strict schemas and accepted units
- content hashes
- environment-only secrets
- read-only connectors
- append-oriented review records
- explicit forbidden finding labels
- least-privilege deployment
- source-specific rate limits and timeouts
