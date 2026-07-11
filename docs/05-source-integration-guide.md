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
2. Configure the current endpoint and service key through environment variables (`NSPO_KOREA_SERVICE_KEY`, `NSPO_KHNP_*_URL`).
3. Confirm whether the current service returns XML or JSON — the connector accepts both.
4. Respect published quotas (`NSPO_RATE_LIMIT_SECONDS`, `configs/app.yaml` rate limits).
5. Preserve official result codes and raw record identifiers.

Registered Korea sources (all disabled by default):

| Source ID | Env var | Mapping |
| --- | --- | --- |
| `kr-khnp-weather` | `NSPO_KHNP_WEATHER_URL` | `configs/mappings/kr-khnp-weather.yaml` |
| `kr-khnp-operation-status` | `NSPO_KHNP_OPERATION_STATUS_URL` | `configs/mappings/kr-khnp-operation-status.yaml` |
| `kr-korad-radiation` | `NSPO_KORAD_RADIATION_URL` | `configs/mappings/kr-korad-radiation.yaml` |
| `kr-korad-weather` | `NSPO_KORAD_WEATHER_URL` | `configs/mappings/kr-korad-weather.yaml` |
| `kr-korad-seismic` | `NSPO_KORAD_SEISMIC_URL` | `configs/mappings/kr-korad-seismic.yaml` |
| `kr-korad-waste` | `NSPO_KORAD_WASTE_URL` | `configs/mappings/kr-korad-waste.yaml` |
| `kr-korad-silo` | `NSPO_KORAD_SILO_URL` | `configs/mappings/kr-korad-silo.yaml` |

CI uses checked-in XML/JSON fixtures only and never calls live Korea APIs.

## KORAD

Treat each service as a separate source contract. Radiation, meteorological, seismic, waste-inventory, and silo-status datasets require different normalizers.
