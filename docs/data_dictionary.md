# Data dictionary

## Bundled Chennai rainfall snapshot

File: `data/processed/chennai_daily_rainfall.csv`  
Source: Open-Meteo Historical Weather API, ERA5 reanalysis  
Period: 2020-01-01 through 2025-12-31  
Coordinate: 13.0827, 80.2707 (Chennai point; not ward geometry)  
Rows: 2,192 daily records; missing precipitation values: 0 at retrieval.

| Field | Type | Meaning | Unit / caveat |
|---|---|---|---|
| `date` | ISO date | Local calendar day in Asia/Kolkata for the source coordinate | Daily temporal resolution |
| `precipitation_mm` | Decimal number | ERA5 reanalysis daily precipitation sum | Millimetres; estimated gridded weather value, not a direct rain-gauge observation |

The adjacent metadata JSON records the request, retrieval time, missingness, license terms, and SHA-256 of the CSV content. Re-ingesting the same period can produce a different hash if upstream values or processing are revised.

## Uploaded CSVs

Column names and values are user-defined. The application records only the safe basename, row/column counts, and a compact transformation summary for a completed run. It does not persist uploaded row contents.

