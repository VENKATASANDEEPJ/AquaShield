# AquaShield AI

A research-minded urban water and rainfall analysis platform. The current pilot is Chennai. It separates source observations, gridded/reanalysis estimates, and user-provided data; it does not claim to provide live flood alerts, street-safety guarantees, contaminant detection, or validated flood predictions.

## Current scope

- **City Explorer:** Chennai historical daily precipitation from Open-Meteo's Historical Weather API, queried and cached by the backend. A verified 2020–2025 snapshot is bundled as an offline fallback for that date range. This is reanalysis-derived city-point data, not a rain gauge or street-level measurement.
- **Custom Data Lab:** temporary CSV upload, preview, type and quality profile, configurable missing/duplicate cleanup, descriptive analysis, charts, and CSV export. Uploads stay in memory and are discarded after the process/request; they are not saved to the database or disk.
- **Persistence:** SQLite stores dataset metadata and analysis experiment summaries; uploaded row data is not persisted.
- **Modeling:** no flood model is enabled because the repository has no verified flood-event labels aligned to rainfall and road observations.

## Problem and objectives

Urban rainfall and waterlogging information often comes from separate sources and does not share the same spatial or temporal coverage. AquaShield demonstrates an evidence-first workflow for describing rainfall, tracing source limitations, and helping users analyze their own environmental CSVs. Its objective is decision support and reusable analysis, not real-time alerts or civic complaint tracking.

## Data lifecycle and analysis method

The ingestion script requests Open-Meteo daily precipitation, validates date uniqueness and non-negative values, and saves a CSV with a provenance sidecar and SHA-256. The EDA notebook checks row/date coverage, duplicates, missingness, negative values, descriptive statistics, and monthly totals. The feature shown in the city view is monthly precipitation aggregated from daily source values; the ≥10 mm wet-day count is descriptive only.

The Custom Data Lab infers column types and geographic/date candidates, reports missingness and duplicates, and offers opt-in duplicate removal, row deletion for missing values, or median filling of numeric columns. It returns descriptive statistics, category frequencies, correlations, and IQR outlier counts. Transformations and row counts are shown to the user.

## Data dictionary and evaluation

The bundled dataset has 2,192 daily rows for 2020-01-01 through 2025-12-31 and no missing precipitation values at retrieval. See [data dictionary](docs/data_dictionary.md), [dataset source notes](docs/dataset_sources.md), and [evaluation report](docs/evaluation_report.md). No supervised model is included: no verified event labels align to this rainfall series, so no accuracy or forecast claim is reported.

<img width="1910" height="907" alt="image" src="https://github.com/user-attachments/assets/24b03137-3dcd-4a99-908e-98f373dd85cb" />


## Persistence and privacy

SQLAlchemy stores completed analysis run summaries in SQLite by default. Set `DATABASE_URL` to PostgreSQL for deployment; a psycopg driver is included. Upload contents are processed in memory and never persisted by the backend; the selected browser file remains in browser memory during that tab's workflow. Experiment metadata includes a sanitized filename, row/column counts, and cleaning summary. Authentication and multi-user data isolation are not implemented.

## Requirements

Python 3.10+ and Node.js 20.19+ (or 22.12+). Python dependencies are in `backend/requirements.txt`; frontend dependencies are pinned in `frontend/package.json` and `frontend/package-lock.json`.

## Run locally

1. Create a Python virtual environment and install `backend/requirements.txt`.
2. From `backend`, run `uvicorn app.main:app --reload`.
3. In a second terminal, from `frontend`, run `npm install` then `npm run dev`.
4. Open the Vite address (normally `http://localhost:5173`). API docs are at `http://127.0.0.1:8000/docs`.

Copy `.env.example` to `backend/.env` for local settings. Optional variables: `DATABASE_URL` (defaults to `sqlite:///./aquashield.db`), `CORS_ORIGINS` (comma-separated origins; localhost defaults are included), `MAX_UPLOAD_MB` (20), and `MAX_UPLOAD_ROWS` (200000). Set `VITE_API_BASE_URL` for a separately hosted API.

## Data and provenance

The backend fetches daily precipitation on request for Chennai (13.0827, 80.2707), over a selected period from 2010 onward, and caches responses in memory for one hour. The bundled offline snapshot covers 2020-01-01 to 2025-12-31 and includes a provenance sidecar. Source: [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), using ERA5 reanalysis. Data is subject to Open-Meteo terms: free access is for non-commercial use, attribution is required (CC BY 4.0), quotas apply, and the free service has no uptime guarantee. When the upstream is unavailable, the app labels a matching bundled snapshot as stale; it reports an error for dates outside the snapshot rather than showing unsupported values.

The Chennai flood-hotspot KML surfaced in the initial source review could not be independently retrieved and validated. It is not included or represented in this version. No road-disruption, drainage-overflow, health, or floodwater quality records are currently configured. The surface-water quality datasets catalogued by NWDP/CPCB concern monitoring stations and must not be described as floodwater measurements.

## API

- `GET /api/health`
- `GET /api/cities`
- `GET /api/cities/chennai/rainfall?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `POST /api/datasets/profile` (multipart `file`)
- `POST /api/datasets/analyze` (multipart CSV + cleaning options; temporary)
- `GET /api/datasets/export` (multipart CSV + options; returns cleaned CSV)
- `GET /api/experiments` (persisted aggregate metadata only)

CSV routes reject non-CSV uploads, enforce size and row limits, constrain parsing, and never execute uploaded content. This is a single-user academic MVP; it does not yet provide authentication, tenant isolation, or persistent private file storage.

## Checks

Run backend tests from `backend` with `python -m pytest -q`. Build the frontend from `frontend` with `npm run build`. The EDA notebook expects the bundled CSV or a refreshed CSV produced by the ingestion script.

## Deployment status

Deployment has not been performed or verified. `render.yaml` and `frontend/vercel.json` provide starting configuration only. For Render, install `backend/requirements.txt` and run `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. For Vercel, set the root to `frontend` and set `VITE_API_BASE_URL`. Configure CORS for the actual deployed frontend origin. SQLite on an ephemeral host is not durable; use PostgreSQL and set `DATABASE_URL` before claiming persistent production storage. Open-Meteo free access is non-commercial and not an SLA-backed production dependency.

## Project layout

See `docs/architecture.md`, `docs/data_dictionary.md`, `docs/dataset_sources.md`, `docs/evaluation_report.md`, `docs/limitations.md`, `docs/methodology.md`, and `docs/interview_guide.md` for implementation details and presentation guidance.

