# Architecture

## Design intent

The platform separates acquisition, normalization, analysis, and review so that no connector can directly publish a high-consequence conclusion.

```text
Connector → Raw record → Normalized observation → Rule engine → Finding → Expert review
```

## Trust boundaries

1. External public-data publishers
2. Connector runtime
3. Normalized observation store
4. Analyzer
5. Human-review API
6. Public dashboard

## Architectural constraints

- Connectors are read-only.
- Credentials are environment variables only.
- Source definitions must be marked public or synthetic.
- Rules are versioned and human-readable.
- Findings cannot use emergency or confirmed-incident labels.
- Dashboard language remains descriptive rather than causal.
