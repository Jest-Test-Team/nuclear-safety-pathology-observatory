# Data Governance

## Source governance

For every source, record:

- authority and country
- official dataset page
- machine endpoint
- retrieval timestamp
- source record identifier
- content hash
- license or reuse terms
- expected update interval
- schema version or observed schema hash

## Corrections

Public authorities may revise historical measurements. Store retrieval versions and correction records rather than silently overwriting evidence.

## Retention

Raw payload retention should be limited to what licensing and research protocols allow. Normalized observations should preserve provenance but not credentials or internal request headers.
