# Architecture

The Vite React client calls a small FastAPI service. City rainfall is fetched by the backend from Open-Meteo and cached in process for one hour. CSVs are parsed and analyzed in memory with Pandas. SQLite stores only high-level run metadata; PostgreSQL can be configured through `DATABASE_URL`.

```text
React/Vite ──HTTP──> FastAPI ──> Open-Meteo Historical API
                         ├────> Pandas CSV profiling/analysis (memory only)
                         └────> SQLAlchemy metadata (SQLite local / PostgreSQL configured)
```

This is an academic single-user MVP. It does not include accounts, tenant separation, durable private uploads, spatial flood modeling, or a production cache. The web map and unsupported hazard layers are intentionally absent until verified geographic incident data is available.

