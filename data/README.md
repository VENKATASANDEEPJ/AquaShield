# Data directory

`processed/chennai_daily_rainfall.csv` is a verified 2020-01-01 through 2025-12-31 Open-Meteo ERA5 daily precipitation snapshot. Its `.metadata.json` sidecar records source, request coordinates, date coverage, row/missing counts, retrieval time, and SHA-256. The API uses it only as a labeled fallback for covered dates when the upstream is unavailable. `raw/` remains reserved; no flood-event or road-access dataset is bundled. Use the ingestion script to refresh the snapshot. Values are reanalysis estimates, not direct rain-gauge readings. Observe source terms and do not commit sensitive user datasets.

