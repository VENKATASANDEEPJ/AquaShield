import csv
import io
from pathlib import Path
import re

import numpy as np
import pandas as pd
from fastapi import HTTPException, UploadFile

from app.core.config import settings

ALLOWED = {".csv"}


def safe_filename(filename: str | None) -> str:
    basename = (filename or "dataset.csv").replace("\\", "/").rsplit("/", 1)[-1]
    cleaned = re.sub(r"[^A-Za-z0-9._ -]", "_", basename).strip(" .")[:180]
    return cleaned or "dataset.csv"


def read_csv_bytes(raw: bytes, filename: str) -> pd.DataFrame:
    if Path(filename or "").suffix.lower() not in ALLOWED:
        raise HTTPException(415, "Upload a .csv file.")
    if not raw:
        raise HTTPException(400, "The uploaded file is empty.")
    if len(raw) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds the {settings.max_upload_mb} MB limit.")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            text = raw.decode("cp1252")
        except UnicodeDecodeError as exc:
            raise HTTPException(400, "Could not decode this CSV. Save it as UTF-8 and retry.") from exc
    try:
        try:
            delimiter = csv.Sniffer().sniff(text[:8192], delimiters=",;\t|").delimiter
        except csv.Error:
            # Sniffer cannot infer a delimiter for valid one-column CSVs or tiny files.
            delimiter = ","
        try:
            raw_headers = next(csv.reader(io.StringIO(text), delimiter=delimiter))
        except StopIteration as exc:
            raise HTTPException(400, "CSV must contain a header row.") from exc
        normalized_headers = [header.strip()[:200] for header in raw_headers]
        if any(not header for header in normalized_headers) or len(set(normalized_headers)) != len(normalized_headers):
            raise HTTPException(400, "Column names must be non-empty and unique.")
        frame = pd.read_csv(io.StringIO(text), sep=delimiter, on_bad_lines="error", low_memory=False)
    except (ValueError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise HTTPException(400, f"Could not parse CSV: {exc}") from exc
    if frame.empty or len(frame.columns) == 0:
        raise HTTPException(400, "CSV must contain a header and at least one data row.")
    if len(frame) > settings.max_upload_rows:
        raise HTTPException(413, f"File exceeds the {settings.max_upload_rows:,} row limit.")
    if len(frame.columns) > 200:
        raise HTTPException(413, "CSV exceeds the 200-column limit.")
    frame.columns = [str(c).strip()[:200] for c in frame.columns]
    if any(not c for c in frame.columns) or frame.columns.duplicated().any():
        raise HTTPException(400, "Column names must be non-empty and unique.")
    return frame


async def load_upload(file: UploadFile) -> pd.DataFrame:
    raw = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    return read_csv_bytes(raw, file.filename or "upload.csv")


def infer_kind(series: pd.Series) -> str:
    name = str(series.name).strip().lower()
    if name in {"latitude", "lat", "longitude", "lon", "lng", "long", "x", "y"} or any(token in name for token in ("latitude", "longitude")):
        return "geographic candidate"
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if any(token in name for token in ("date", "time", "timestamp")):
        parsed = pd.to_datetime(series, errors="coerce", format="mixed")
        if parsed.notna().mean() >= 0.65:
            return "datetime"
    parsed = pd.to_numeric(series, errors="coerce")
    if len(series.dropna()) and parsed.notna().mean() >= 0.9:
        return "numeric candidate"
    values = series.dropna().astype(str)
    if len(values) and values.str.len().median() >= 8:
        dates = pd.to_datetime(values, errors="coerce", format="mixed")
        if dates.notna().mean() >= 0.85:
            return "datetime candidate"
    return "categorical"


def profile(frame: pd.DataFrame) -> dict:
    missing = frame.isna().sum()
    columns = []
    for name in frame.columns:
        s = frame[name]
        columns.append({"name": name, "dtype": str(s.dtype), "kind": infer_kind(s), "missing": int(missing[name]), "missing_pct": round(float(missing[name] / max(1, len(frame)) * 100), 2), "unique": int(s.nunique(dropna=True) )})
    return {"rows": int(len(frame)), "columns_count": int(len(frame.columns)), "duplicate_rows": int(frame.duplicated().sum()), "columns": columns, "preview": frame.head(10).replace({np.nan: None}).to_dict(orient="records"), "retention": "In-memory processing only; the uploaded file is discarded after the response."}


def clean(frame: pd.DataFrame, drop_duplicates: bool = False, missing: str = "keep", selected_columns: list[str] | None = None) -> pd.DataFrame:
    selected = selected_columns or list(frame.columns)
    unknown = set(selected) - set(frame.columns)
    if unknown:
        raise HTTPException(422, f"Unknown columns: {', '.join(sorted(unknown))}")
    out = frame.loc[:, selected].copy()
    if drop_duplicates:
        out = out.drop_duplicates()
    if missing == "drop_rows":
        out = out.dropna()
    elif missing == "fill_numeric_median":
        for col in out.select_dtypes(include="number"):
            median = out[col].median()
            if pd.notna(median):
                out[col] = out[col].fillna(median)
    elif missing != "keep":
        raise HTTPException(422, "missing must be keep, drop_rows, or fill_numeric_median.")
    return out


def analyze(frame: pd.DataFrame) -> dict:
    numeric = frame.select_dtypes(include="number")
    stats = numeric.describe().replace({np.nan: None}).round(4).to_dict()
    outliers = {}
    for col in numeric:
        values = numeric[col].dropna()
        if values.empty:
            outliers[str(col)] = 0
            continue
        q1, q3 = values.quantile([0.25, 0.75])
        spread = q3 - q1
        outliers[str(col)] = int(((values < q1 - 1.5 * spread) | (values > q3 + 1.5 * spread)).sum())
    categorical = {}
    for col in frame.select_dtypes(exclude="number"):
        counts = frame[col].astype("string").fillna("(missing)").value_counts().head(12)
        categorical[col] = [{"label": str(k), "count": int(v)} for k, v in counts.items()]
    correlations = numeric.corr().replace({np.nan: None}).round(4).to_dict() if len(numeric.columns) > 1 else {}
    return {"rows": int(len(frame)), "columns": int(len(frame.columns)), "numeric_summary": stats, "categorical_frequencies": categorical, "iqr_outlier_counts": outliers, "correlation": correlations, "missing_after_cleaning": {str(k): int(v) for k, v in frame.isna().sum().items()}}

