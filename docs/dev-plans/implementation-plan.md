# Implementation Plan

Status: implemented (Phases 1–4 landed on main)  
Aligned with: [`docs/08-roadmap.md`](../08-roadmap.md), [`docs/01-architecture.md`](../01-architecture.md), [`docs/02-safety-case.md`](../02-safety-case.md)  
Last updated: 2026-07-11

## 1. Purpose

Turn the current synthetic-demo scaffold into a reproducible public-data observability platform that answers the core research questions without crossing the non-operational boundary:

- What changed, where, and when?
- Is the change local, regional, or a publication-pipeline artifact?
- Which public records support the finding?
- Which context is missing?
- What alternative explanations remain plausible?
- Did the signal return to baseline after an event or intervention?

Every deliverable below must preserve safety invariants: public/synthetic data only, provenance required, findings always `requires-expert-review`, no facility-control or emergency labels.

## 2. Current baseline (Phase 1 — largely complete)

| Area | Present today | Gap |
| --- | --- | --- |
| Transparent rules | `rules/patterns.yaml` (5 rules) | Missing `schema-drift` rule called out in README demo behavior |
| Synthetic demo | `scripts/generate_demo.py`, `data/synthetic/` | No labeled fault corpus for precision/recall eval |
| Analyzer | `services/pipeline/nspo/engine/analyzer.py` | File-only I/O; no unit validation from `configs/app.yaml` |
| Connectors | TW CSV + KR XML stubs | Disabled by default; no normalizers → observation schema |
| Review API | Go `/healthz`, `/api/findings`, `/api/reviews` | JSON file store; no GET reviews; no auth |
| Dashboard | Static `apps/web` | Findings list only; no review UI or evidence drill-down |
| Schemas | `schema/*.schema.json`, `db/schema.sql` | Postgres unused; no migration tooling |
| Governance | Docs + `configs/sources.yaml` | No runtime source-health / freshness report artifact |
| CI | `.github/workflows/ci.yml` | Covers demo path; no live-adapter integration tests |

Phase 1 exit criteria are met for a local synthetic demo (`make demo`, `make test`, `make run-api` / `make run-web`). Remaining Phase 1 polish is listed in §4.1.

## 3. Architecture targets

```text
Public Open Data
├── Taiwan NUSC adapters
├── Korea KHNP adapters
└── Korea KORAD adapters
        ↓
Normalization + provenance + unit checks
        ↓
Longitudinal observation store (JSON → optional PostgreSQL)
        ↓
Versioned transparent rule engine
        ↓
Evidence packages (findings)
        ↓
Human-review API + dashboard
```

Trust boundaries and constraints remain as in [`docs/01-architecture.md`](../01-architecture.md) and ADRs 0001 / 0002.

### Non-goals (all phases)

- Facility control, scanning, or non-public acquisition
- Confirmed accident / release / emergency conclusions
- ML-first detection that removes inspectable rule provenance
- Operational decision support for plant personnel

## 4. Phased work

### 4.1 Phase 1 polish — Synthetic validation (close-out)

**Goal:** Demo path is complete, schema-enforced, and evaluable under [`docs/06-research-protocol.md`](../06-research-protocol.md).

| ID | Work item | Owner area | Acceptance |
| --- | --- | --- | --- |
| P1-1 | Add `schema-drift` rule + analyzer handler; emit finding when observed headers/fields diverge from registered mapping hash | `rules/`, `analyzer` | Synthetic fixture triggers finding; status + alternatives + limitations present |
| P1-2 | Enforce `configs/app.yaml` accepted units and forbidden finding labels in analyzer / validate script | `pipeline`, `scripts/` | Unsupported unit or forbidden label fails validation |
| P1-3 | Validate observations and findings against JSON Schema in `make test` / `validate_repo.py` | `schema/`, `scripts/` | Invalid records fail CI |
| P1-4 | Build a small labeled synthetic fault set (stale, constant, spatial, multi-station, recovery, schema-drift) with expected rule IDs | `data/synthetic/` | Pytest asserts precision of rule firing on labeled faults |
| P1-5 | Dashboard: show evidence IDs, missing evidence, uncertainty, and explicit research disclaimer; optional POST review form against API | `apps/web` | Reviewer can submit `acknowledged` / `needs-more-data` / `rejected` / `corrected` |
| P1-6 | API: `GET /api/reviews` (append-only list) to match review workflow completeness | `apps/api` | Contract documented in `docs/07-api-contract.md` |

**Exit:** `make demo && make test` green; README demo behaviors all produced from synthetic data; research protocol evaluation metrics computable on labeled faults.

---

### 4.2 Phase 2 — Taiwan public-data adapter

**Goal:** Ingest real NUSC public CSV feeds into normalized observations with provenance, without enabling by default until field mappings are verified.

Reference: [`docs/05-source-integration-guide.md`](../05-source-integration-guide.md).

| ID | Work item | Acceptance |
| --- | --- | --- |
| P2-1 | Document official dataset pages and env vars for realtime radiation, station metadata, historical monthly (extend `sources.yaml` + `.env.example`) | Source registry complete; no hard-coded transient URLs |
| P2-2 | Configurable field-mapping YAML per source (Chinese/English headers → observation fields); refuse to normalize without mapping | Unit tests with sample CSV fixtures (redacted/public samples only) |
| P2-3 | Normalizer: `RawRecord` → observation schema (`public_data=true`, provenance, timezone, units) | Schema validation passes; unknown units rejected |
| P2-4 | Station metadata join (lat/lon, station_id stability) | Spatial rules can run on real station geometry |
| P2-5 | Historical monthly ingest path (batch file or URL) with retrieval versioning | Corrections stored as new retrieval versions; no silent overwrite |
| P2-6 | Freshness + schema monitoring jobs: compare `expected_interval_seconds` and schema hash | Emits data-quality findings only |
| P2-7 | CLI: `nspo collect --source tw-nusc-...` writing under `data/runtime/` (gitignored) | Manual run succeeds with env-configured URL; default CI remains synthetic |

**Exit:** Optional live collect documented; synthetic remains default; TW adapter produces review candidates that never claim facility events.

---

### 4.3 Phase 3 — Korea public-data adapter

**Goal:** KHNP + KORAD public API ingestion with XML/JSON normalization and quota-safe clients.

| ID | Work item | Acceptance |
| --- | --- | --- |
| P3-1 | Split connectors: KHNP weather / public operation-status; KORAD radiation, weather, seismic, waste-inventory, silo-status as separate source contracts | One normalizer per `sources.yaml` id |
| P3-2 | Support XML and JSON responses; preserve official result codes and raw record ids | Provenance includes source_record_id + content_hash |
| P3-3 | Service key only via `NSPO_KOREA_SERVICE_KEY`; never log credentials | `validate_repo` / tests reject secrets in configs |
| P3-4 | Rate limit + timeout from `configs/app.yaml` / env | Quotas respected; connector errors are typed and non-fatal to other sources |
| P3-5 | Metric mapping into observation enum (`gamma-dose-rate`, weather metrics, `seismic-intensity`, `waste-inventory`) | Schema-valid observations |
| P3-6 | Fixture-based tests (checked-in anonymized XML/JSON samples) | CI does not call live Korea APIs |

**Exit:** KR adapters enabled only when env configured; findings remain expert-review candidates with multilingual-ready metadata fields (keys English; values may retain source language with translation notes).

---

### 4.4 Phase 4 — Cross-border research

**Goal:** Comparative observability research artifacts, not safety conclusions.

| ID | Work item | Acceptance |
| --- | --- | --- |
| P4-1 | Open-data observability maturity index (freshness compliance, schema stability, provenance completeness, endpoint availability) | Reproducible report from archived public records |
| P4-2 | Source reliability reports per authority / source_id | Dashboard or static HTML/Markdown export |
| P4-3 | Event/recovery trajectory views using documented public events only | Recovery rule outputs linked to evidence packages |
| P4-4 | Multilingual metadata (EN/ZH/KO labels for metrics, rule titles, disclaimers) | UI language switch; findings payload remains machine-stable English ids |
| P4-5 | Optional PostgreSQL backend behind store interface (`db/schema.sql` + migrations) | File store still works for demo; PG optional via compose |

**Exit:** Cross-border research protocol questions in `docs/06-research-protocol.md` can be answered with exported evidence packages; no generalization to facility safety.

## 5. Cross-cutting engineering work

### 5.1 Pipeline

1. Introduce explicit stages: `collect` → `normalize` → `analyze` → `publish-findings`.
2. Reject records that violate safety claims S1–S4 ([`docs/02-safety-case.md`](../02-safety-case.md)).
3. Keep rules deterministic and versioned; bump `rules/patterns.yaml` `version` on parameter changes and record version on each finding.
4. Append-only raw retrieval archives where license allows ([`docs/03-data-governance.md`](../03-data-governance.md)).

### 5.2 API & storage

1. Keep Go stdlib HTTP API thin: findings + reviews + health.
2. Abstract `store.Store` for JSON today / Postgres later.
3. Reviews remain append-oriented (threat model control).
4. Update [`docs/07-api-contract.md`](../07-api-contract.md) whenever endpoints change; generate or hand-sync frontend types if API grows.

### 5.3 Dashboard

1. Descriptive language only; retain non-operational banner.
2. Surface alternatives, limitations, missing evidence, uncertainty before any visual emphasis on magnitude.
3. No cards or chrome that imply alert/emergency severity colors for “confirmed” states (forbidden by schema).

### 5.4 Security & ops

1. Env-only secrets; read-only GET connectors ([`docs/04-threat-model.md`](../04-threat-model.md)).
2. Timeouts, rate limits, User-Agent identification.
3. Least-privilege Docker Compose; no credential volume mounts into git.
4. SECURITY.md scope: repo + synthetic + authorized public APIs only.

### 5.5 Testing & CI

| Layer | Coverage |
| --- | --- |
| Unit | Analyzer rules, normalizers, unit/provenance guards |
| Contract | JSON Schema validation of observations/findings |
| API | Go handler tests for decisions and validation errors |
| Integration | Synthetic end-to-end `make demo` in CI |
| Live adapters | Manual / optional nightly with secrets; never required for merge |

## 6. Suggested implementation order

```text
Week focus (indicative)
1. P1-1 … P1-4   schema-drift + validation + labeled faults
2. P1-5, P1-6    review UX + GET reviews + API doc sync
3. P2-1 … P2-3   TW mapping + normalizer + fixtures
4. P2-4 … P2-7   metadata, history, freshness job, collect CLI
5. P3-1 … P3-3   KR source split + XML/JSON + secret hygiene
6. P3-4 … P3-6   quotas, metrics, fixture CI
7. P4-1 … P4-3   maturity index, reliability, trajectories
8. P4-4, P4-5    i18n + optional Postgres
```

Reorder only if a research partner needs a specific live source earlier; keep synthetic as the merge-gate path.

## 7. Definition of done (per feature)

A feature is done when:

1. Safety invariants still hold (public_data, provenance, review status, alternatives, limitations).
2. Schemas / source registry / docs updated in the same change set.
3. Unit or fixture tests cover the happy path and at least one rejection path.
4. Dashboard or API consumers do not require undocumented fields.
5. No credentials, transient download URLs, or non-public endpoints are committed.

## 8. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Upstream schema / URL churn (esp. NUSC CSV headers) | Explicit mapping files; schema-drift findings; no guessed headers |
| Over-interpretation of findings by users | Fixed disclaimer copy; forbidden labels; uncertainty + alternatives mandatory |
| API key leakage | Env-only; CI secret scan via `validate_repo`; never log query strings with keys |
| Live API flakiness blocking development | Synthetic default; fixture tests; optional live collect |
| Silent historical corrections | Retrieval versioning; append observations rather than overwrite |

## 9. Doc sync checklist

When implementing phases, update in the same PR as needed:

- [ ] `README.md` — quick start / demo behavior
- [ ] `docs/05-source-integration-guide.md` — new sources
- [ ] `docs/07-api-contract.md` — endpoint changes
- [ ] `docs/08-roadmap.md` — mark completed bullets
- [ ] `configs/sources.yaml` / `.env.example`
- [ ] `INVENTORY.md` if file layout changes
- [ ] ADR only when architecture decision changes

## 10. Immediate next actions

1. Implement **P1-1** (`schema-drift`) so README demo claims match the rule engine.
2. Wire **P1-2 / P1-3** so unit and schema guards are enforced in CI, not only documented.
3. Add **P1-4** labeled synthetic faults before enabling any live TW/KR collect by default.
4. Only then proceed to Phase 2 field-mapping work against current official dataset pages.
