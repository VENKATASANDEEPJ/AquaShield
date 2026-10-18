# Dataset sources and status

| Source | Status | Coverage and use | Terms / caveats |
|---|---|---|---|
| Open-Meteo Historical Weather API (ERA5) | Implemented as on-demand city-point query; 2020–2025 CSV snapshot included | Daily precipitation for Chennai at 13.0827, 80.2707; API range 2010 onward; packaged fallback covers 2020-01-01 through 2025-12-31 | Reanalysis estimate, not station observation. Free service is non-commercial, attribution required, rate limited, no uptime guarantee. [Docs](https://open-meteo.com/en/docs/historical-weather-api), [terms](https://open-meteo.com/en/terms). |
| NASA GPM IMERG | Candidate only | Gridded satellite precipitation; potentially useful for another rainfall resolution/time step | Coarse grid for street analysis; registration/access workflow may apply. [NASA documentation](https://gpm.nasa.gov/data/imerg). |
| Geofabrik OpenStreetMap | Candidate only | Regional road and geographic context | ODbL attribution and share-alike requirements for derived databases. Coverage varies. [Download/license](https://www.geofabrik.de/en/data/download.html). |
| Chennai Floods 2005 (OpenCity listing) | Unverified candidate; not loaded | Listing names a GCC flood hotspot KML | File, schema, license, positional precision and completeness require validation. [Listing](https://data.opencity.in/dataset/chennai-floods-2005-data). |
| NWDP/CPCB surface-water quality | Catalogue candidate; not loaded | Manual biological parameters by state and period, CSV/API listed | Monitoring points do not represent floodwater contamination. Inspect station locations, units, dates and license before use. [Catalogue](https://nwdp.nwic.gov.in/en/dataset/surface-water-quality-manual-biological-parameters-cpcb). |

Only the first source is currently used by the application. No event, access, waterlogging, health, drainage, or floodwater-quality observations are bundled.

