# Methodology

## City analysis

The API retrieves daily `precipitation_sum` from the Open-Meteo Historical Weather API for the Chennai coordinate. The frontend groups available daily values into calendar months and sums them. The “wet day” count is a descriptive count of days with at least 10 mm; it is not a flood threshold. The chart only renders returned source values and labels the series as a reanalysis estimate.

## Custom CSV analysis

The backend checks extension, byte size, row and column limits, decoding, delimiter, parsing, and unique non-empty headers. It profiles inferred types, nulls, unique values, and exact duplicate rows. Users select columns and choose to retain missing values, drop rows containing missing values, or fill numeric missing values with the column median. Duplicate removal is separately opt-in. Results include numeric descriptive statistics and top category frequencies. The workflow reports row counts before and after cleaning. It does not silently transform the uploaded file.

## Modeling

No supervised model is included. A model should be added only when a target is independently observed, time and location are aligned, leakage can be controlled, and a baseline plus meaningful holdout evaluation can be reported.

