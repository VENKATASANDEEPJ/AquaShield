# Limitations

- Chennai rainfall is queried at one coordinate from reanalysis. Spatial and temporal resolution cannot support road-segment or ward-level conclusions.
- Precipitation is a weather variable, not proof of flood occurrence, drainage failure, or road disruption.
- No verified, aligned flood occurrence labels exist; the app does not train or serve flood prediction models.
- No road network or flood hotspot map is active. The initial hotspot file listing did not provide enough verifiable detail to safely use it.
- State water monitoring does not measure floodwater exposure. The application makes no claims about contamination or health.
- Open-Meteo free API terms are non-commercial; service limits and availability are outside this app's control.
- CSV processing is temporary and single-process. Metadata may identify the supplied filename; do not upload sensitive or identifying filenames. Authentication and multi-user isolation are not implemented.
- The UI has not been deployed. Host persistence, CORS, uptime, and production PostgreSQL behavior must be configured and verified separately.

