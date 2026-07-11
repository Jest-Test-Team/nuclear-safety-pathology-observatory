# Source Integration Guide

## Taiwan NUSC CSV

1. Locate the current official dataset page.
2. Copy the current CSV/API access URL into an environment variable.
3. Inspect headers and create an explicit field mapping.
4. Verify units and timestamp timezone.
5. Record the dataset license and expected update frequency.

Never assume that all NUSC CSV datasets share the same headers.

## Korea data.go.kr / KHNP

1. Register for an API key.
2. Configure the current endpoint and service key through environment variables.
3. Confirm whether the current service returns XML or JSON.
4. Respect published quotas.
5. Preserve official result codes and raw record identifiers.

## KORAD

Treat each service as a separate source contract. Radiation, meteorological, seismic, waste-inventory, and silo-status datasets require different normalizers.
