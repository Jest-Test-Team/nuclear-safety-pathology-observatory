# Safety Case

## Intended use

Research, public-data quality assessment, educational visualization, longitudinal trend analysis, and expert-review workflow prototyping.

## Explicitly excluded use

- reactor or facility control
- operational decision support for plant personnel
- emergency alerting
- accident, release, or facility-safety confirmation
- inference of non-public facility configuration
- vulnerability discovery against nuclear infrastructure

## Safety claims

### S1 — No autonomous high-consequence conclusion

All findings use `requires-expert-review`. The schema does not permit a confirmed accident or release state.

### S2 — Evidence and uncertainty are mandatory

Each finding includes evidence references, alternative explanations, limitations, and uncertainty.

### S3 — Public-data boundary

The pipeline rejects observations not marked `public_data=true` and requires provenance.

### S4 — Read-only acquisition

Connectors only perform HTTP GET requests against operator-configured public endpoints.
