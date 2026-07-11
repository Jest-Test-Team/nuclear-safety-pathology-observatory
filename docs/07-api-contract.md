# API Contract

## GET `/healthz`

Returns service health and research mode.

## GET `/api/findings`

Returns generated expert-review findings.

## POST `/api/reviews`

Example:

```json
{
  "finding_id": "finding-...",
  "decision": "needs-more-data",
  "reviewer": "analyst@example.invalid",
  "comment": "Request station maintenance context."
}
```

Allowed decisions: `acknowledged`, `needs-more-data`, `rejected`, `corrected`.
