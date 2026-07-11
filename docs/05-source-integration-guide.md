# Source Integration Guide

## Taiwan NUSC CSV

1. Locate the current official dataset page (start from the Nuclear Safety Commission open-data portal).
2. Copy the current CSV/API access URL into an environment variable — never commit transient download URLs.
3. Inspect headers and create or update an explicit field mapping under `configs/mappings/`.
4. Verify units and timestamp timezone (`Asia/Taipei` unless the dataset declares otherwise).
5. Record the dataset license and expected update frequency in `configs/sources.yaml`.

Registered Taiwan sources:

| Source ID | Env var | Mapping file | Default |
| --- | --- | --- | --- |
| `tw-nusc-radiation-realtime` | `NSPO_TW_NUSC_RADIATION_URL` | `configs/mappings/tw-nusc-radiation-realtime.yaml` | disabled |
| `tw-nusc-station-metadata` | `NSPO_TW_NUSC_STATIONS_URL` | `configs/mappings/tw-nusc-station-metadata.yaml` | disabled |
| `tw-nusc-radiation-monthly` | `NSPO_TW_NUSC_MONTHLY_URL` | `configs/mappings/tw-nusc-radiation-monthly.yaml` | disabled |

Collect (after configuring env + verifying mappings):

```bash
PYTHONPATH=services/pipeline python3 -m nspo.engine.collect --source tw-nusc-radiation-realtime
```

Never assume that all NUSC CSV datasets share the same headers.

## Korea data.go.kr / KHNP

1. Register for an API key.
2. Configure the current endpoint and service key through environment variables.
3. Confirm whether the current service returns XML or JSON.
4. Respect published quotas.
5. Preserve official result codes and raw record identifiers.

## KORAD

Treat each service as a separate source contract. Radiation, meteorological, seismic, waste-inventory, and silo-status datasets require different normalizers.
