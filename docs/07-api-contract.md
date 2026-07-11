# API Contract

## GET `/healthz`

Returns service health and research mode.

## GET `/api/findings`

Returns generated expert-review findings.

## GET `/api/reviews`

Returns the append-only expert-review log. When no reviews have been recorded yet, the response is an empty JSON array.

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
