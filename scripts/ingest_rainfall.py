"""Download reproducible daily Chennai rainfall estimates from Open-Meteo."""
import argparse
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import httpx
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
URL = "https://archive-api.open-meteo.com/v1/archive"


def fetch(start: date, end: date) -> tuple[pd.DataFrame, dict]:
    if start > end:
        raise ValueError("Start date must not be after end date.")
    params = {"latitude": 13.0827, "longitude": 80.2707, "start_date": start.isoformat(), "end_date": end.isoformat(), "daily": "precipitation_sum", "timezone": "Asia/Kolkata"}
    response = httpx.get(URL, params=params, timeout=45)
    response.raise_for_status()
    payload = response.json()
    daily = payload.get("daily", {})
    dates, rain = daily.get("time", []), daily.get("precipitation_sum", [])
    if not dates or len(dates) != len(rain):
        raise ValueError("Source returned no daily values or inconsistent dates and precipitation.")
    frame = pd.DataFrame({"date": pd.to_datetime(dates), "precipitation_mm": rain})
    if frame["date"].duplicated().any() or (frame["precipitation_mm"].dropna() < 0).any():
        raise ValueError("Source data failed duplicate-date or non-negative rainfall validation.")
    metadata = {"source": "Open-Meteo Historical Weather API", "dataset": "ERA5 reanalysis daily precipitation_sum", "source_url": URL, "retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "latitude": 13.0827, "longitude": 80.2707, "timezone": "Asia/Kolkata", "start_date": start.isoformat(), "end_date": end.isoformat(), "rows": len(frame), "missing_precipitation": int(frame["precipitation_mm"].isna().sum()), "data_type": "Reanalysis estimate; not a direct rain-gauge reading", "license_and_terms": "CC BY 4.0 attribution; free API for non-commercial use subject to rate limits and availability terms"}
    metadata["csv_sha256"] = hashlib.sha256(frame.to_csv(index=False).encode("utf-8")).hexdigest()
    return frame, metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat, required=True, help="YYYY-MM-DD")
    parser.add_argument("--end", type=date.fromisoformat, required=True, help="YYYY-MM-DD")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/chennai_daily_rainfall.csv")
    args = parser.parse_args()
    try:
        frame, metadata = fetch(args.start, args.end)
    except (httpx.HTTPError, ValueError) as exc:
        print(f"Ingestion failed: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)
    metadata_path = args.output.with_suffix(".metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved {metadata['rows']} verified daily records to {args.output}")
    print(f"Source metadata: {metadata_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

