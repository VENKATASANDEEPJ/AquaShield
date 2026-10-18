# Evaluation report

## Data quality checks

The bundled Open-Meteo snapshot was retrieved on 2026-10-18 for Chennai (13.0827, 80.2707), 2020-01-01 through 2025-12-31. The ingestion check observed 2,192 rows, no duplicate dates, no missing precipitation values, and no negative precipitation values. The daily precipitation sum over this six-year period is 9,447.5 mm; this is an aggregate over the configured point and period, not a flood-risk score. The artifact and retrieval metadata are in `data/processed/`.

The monthly chart is computed by summing daily precipitation values within each calendar month. “Wet days ≥ 10 mm” is a descriptive user-facing threshold, not a flood threshold or risk classification.

## Predictive models

No model is trained or scored. There is no verified flood occurrence or road-disruption target aligned in time and location to the rainfall series. Accuracy metrics or feature importance would be misleading without those labels. If such a dataset is added, document target construction, missingness, spatial and temporal splits, baseline performance, and leakage checks before enabling a model.

