# Nuclear Safety Pathology Observatory

A research-oriented, public-data observability platform for longitudinal analysis of radiological environment, nuclear-facility public status, weather, seismic context, radioactive-waste inventory, and open-data quality.

> **Non-operational boundary:** this repository is not a facility control system, official warning system, nuclear safety assessment, emergency notification service, or accident detector. Every generated result is a review candidate derived from public data and requires qualified human review.

## Core questions

- What changed, where, and when?
- Is the change local, regional, or a publication-pipeline artifact?
- Which public records support the finding?
- Which context is missing?
- What alternative explanations remain plausible?
- Did the signal return to baseline after an event or intervention?

## Architecture

```text
Public Open Data
├── Taiwan NUSC adapters
├── Korea KHNP adapters
└── Korea KORAD adapters
        ↓
Normalization + provenance
        ↓
Longitudinal observation store
        ↓
Transparent rule engine
        ↓
Evidence packages
        ↓
Human-review API + dashboard
```

## Repository layout

```text
apps/api/                 Go review API
apps/web/                 Static research dashboard
services/pipeline/        Python collectors, normalizers, analyzer
configs/                  Source registry and application settings
rules/                    Versioned transparent rules
schema/                   JSON Schema contracts
data/synthetic/           Safe synthetic demonstration data
docs/                     Architecture, safety, governance, threat model
db/                       Optional PostgreSQL schema
```

## Quick start

```bash
cp .env.example .env
make demo
make test
make run-api
```

In another terminal:

```bash
make run-web
```

- API: `http://localhost:8080`
- Dashboard: `http://localhost:8081`

Docker:

```bash
docker compose up --build
```

## Demo behavior

The default demo uses only synthetic observations. It produces data-quality and trajectory findings such as:

- stale feed
- constant-value sequence
- local spatial outlier
- multi-station deviation
- schema drift
- post-event recovery delay

Every finding is emitted with:

- `status: requires-expert-review`
- supporting evidence references
- missing evidence
- alternative explanations
- limitations
- uncertainty score

## Safety invariants

The pipeline rejects:

- non-public or secret-marked source definitions
- raw credentials committed to source configuration
- findings labeled as confirmed accidents or releases
- commands that imply facility control
- records without provenance
- records with unsupported units
- results lacking alternative explanations

See [`docs/02-safety-case.md`](docs/02-safety-case.md).
