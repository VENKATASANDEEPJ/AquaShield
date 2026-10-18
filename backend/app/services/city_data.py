from datetime import date
from time import monotonic
import json
from pathlib import Path

import httpx
import pandas as pd
from fastapi import HTTPException

SOURCE = "Open-Meteo Historical Weather API (ERA5 reanalysis)"
_cache: dict[str, tuple[float, dict]] = {}
SNAPSHOT_CSV = Path(__file__).resolve().parents[3] / "data" / "processed" / "chennai_daily_rainfall.csv"
SNAPSHOT_METADATA = SNAPSHOT_CSV.with_suffix(".metadata.json")
CITIES = [
    {"id": "chennai", "name": "Chennai", "region": "Tamil Nadu, India", "latitude": 13.0827, "longitude": 80.2707},
    {"id": "mumbai", "name": "Mumbai", "region": "Maharashtra, India", "latitude": 19.0760, "longitude": 72.8777},
    {"id": "bengaluru", "name": "Bengaluru", "region": "Karnataka, India", "latitude": 12.9716, "longitude": 77.5946},
    {"id": "delhi", "name": "Delhi", "region": "Delhi, India", "latitude": 28.6139, "longitude": 77.2090},
    {"id": "kolkata", "name": "Kolkata", "region": "West Bengal, India", "latitude": 22.5726, "longitude": 88.3639},
    {"id": "hyderabad", "name": "Hyderabad", "region": "Telangana, India", "latitude": 17.3850, "longitude": 78.4867},
]
CITY_BY_ID = {city["id"]: city for city in CITIES}
LAT, LON = CITY_BY_ID["chennai"]["latitude"], CITY_BY_ID["chennai"]["longitude"]


def city_catalog() -> list[dict]:
    return [{
        "id": city["id"], "name": city["name"], "region": city["region"],
        "sources": [{"name": SOURCE, "url": "https://open-meteo.com/en/docs/historical-weather-api"}],
        "coverage": f"Point location at {city['latitude']}, {city['longitude']}; not ward-level",
        "date_range": "2010 onward; source availability dependent",
        "categories": ["historical rainfall"],
        "last_refresh": "Retrieved on demand; one-hour in-memory cache",
        "limitations": ["ERA5 reanalysis estimate, not a rain-gauge observation", "Point estimate does not describe city-wide variation", "No verified flood incident, road disruption, or water-quality data configured"],
        "capabilities": ["Historical rainfall trend"],
    } for city in CITIES]


def _snapshot_fallback(start_date: date, end_date: date) -> dict | None:
    if not SNAPSHOT_CSV.is_file() or not SNAPSHOT_METADATA.is_file():
        return None
    try:
        metadata = json.loads(SNAPSHOT_METADATA.read_text(encoding="utf-8"))
        if start_date.isoformat() < metadata["start_date"] or end_date.isoformat() > metadata["end_date"]:
            return None
        frame = pd.read_csv(SNAPSHOT_CSV, parse_dates=["date"])
        frame = frame[(frame["date"].dt.date >= start_date) & (frame["date"].dt.date <= end_date)]
        points = [{"date": row.date.strftime("%Y-%m-%d"), "precipitation_mm": None if pd.isna(row.precipitation_mm) else float(row.precipitation_mm)} for row in frame.itertuples(index=False)]
        if not points:
            return None
        return {"city": "Chennai", "coordinates": {"latitude": LAT, "longitude": LON}, "start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "points": points, "source": SOURCE, "data_type": "Bundled ERA5 reanalysis snapshot; not a direct city rain-gauge observation.", "attribution": "Open-Meteo; ERA5 data, CC BY 4.0. Non-commercial API terms apply.", "retrieved_at": metadata.get("retrieved_at_utc", "unknown")[:10], "source_status": "Bundled snapshot; the live source was unavailable."}
    except (OSError, ValueError, KeyError, pd.errors.ParserError):
        return None


async def rainfall(city_id: str, start_date: date, end_date: date) -> dict:
    city = CITY_BY_ID.get(city_id)
    if not city:
        raise HTTPException(404, "This city is not in the configured city catalog.")
    if start_date > end_date:
        raise HTTPException(422, "start_date must be on or before end_date.")
    if start_date < date(2010, 1, 1):
        raise HTTPException(422, "This explorer currently supports dates from 2010 onward.")
    if (end_date - start_date).days > 365 * 10:
        raise HTTPException(422, "Select a period of at most 10 years.")
    key = f"{city_id}:{start_date}:{end_date}"
    if key in _cache and monotonic() - _cache[key][0] < 3600:
        return _cache[key][1]
    params = {"latitude": city["latitude"], "longitude": city["longitude"], "start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "daily": "precipitation_sum", "timezone": "Asia/Kolkata"}
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get("https://archive-api.open-meteo.com/v1/archive", params=params)
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        fallback = _snapshot_fallback(start_date, end_date) if city_id == "chennai" else None
        if fallback:
            return fallback
        raise HTTPException(503, "Historical rainfall source is temporarily unavailable. Try again later.") from exc
    daily = payload.get("daily", {})
    dates, values = daily.get("time", []), daily.get("precipitation_sum", [])
    if len(dates) != len(values):
        raise HTTPException(502, "Rainfall source returned an incomplete response.")
    points = [{"date": d, "precipitation_mm": v} for d, v in zip(dates, values)]
    result = {"city": city["name"], "coordinates": {"latitude": city["latitude"], "longitude": city["longitude"]}, "start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "points": points, "source": SOURCE, "data_type": "Historical gridded reanalysis estimate at the city point; not a direct city rain-gauge observation.", "attribution": "Open-Meteo; ERA5 data, CC BY 4.0. Non-commercial API terms apply.", "retrieved_at": date.today().isoformat()}
    _cache[key] = (monotonic(), result)
    return result

