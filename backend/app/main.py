import json
from datetime import date
from fastapi import Depends, FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd

from app import models
from app.core.config import settings
from app.database import Base, engine, get_db
from app.services.csv_analysis import analyze, clean, load_upload, profile, safe_filename
from app.services.city_data import city_catalog, rainfall

Base.metadata.create_all(bind=engine)
app = FastAPI(title="AquaShield AI API", version="0.1.0", description="Historical rainfall exploration and temporary custom CSV analysis.")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AquaShield AI", "version": "0.1.0"}


@app.get("/api/cities")
def cities():
    return {"cities": city_catalog()}


@app.get("/api/cities/{city_id}/rainfall")
async def city_rainfall(city_id: str, start_date: date = date(2020, 1, 1), end_date: date = date(2025, 12, 31)):
    return await rainfall(city_id, start_date, end_date)


@app.post("/api/datasets/profile")
async def dataset_profile(file: UploadFile = File(...)):
    frame = await load_upload(file)
    result = profile(frame)
    result["filename"] = safe_filename(file.filename)
    return result


@app.post("/api/datasets/analyze")
async def dataset_analyze(file: UploadFile = File(...), drop_duplicates: bool = Form(False), missing: str = Form("keep"), selected_columns: str = Form(""), db: Session = Depends(get_db)):
    frame = await load_upload(file)
    selected = None
    if selected_columns:
        try:
            selected = json.loads(selected_columns)
            if not isinstance(selected, list) or not all(isinstance(c, str) for c in selected):
                raise ValueError
        except (json.JSONDecodeError, ValueError) as exc:
            from fastapi import HTTPException
            raise HTTPException(422, "selected_columns must be a JSON array of column names.") from exc
    transformed = clean(frame, drop_duplicates, missing, selected)
    result = {"profile_before": profile(frame), "analysis": analyze(transformed), "transformations": {"selected_columns": selected or list(frame.columns), "drop_duplicates": drop_duplicates, "missing": missing, "rows_before": len(frame), "rows_after": len(transformed), "rows_removed": len(frame) - len(transformed)}}
    db.add(models.Experiment(filename=safe_filename(file.filename), rows=len(transformed), columns=len(transformed.columns), summary=json.dumps({"removed": result["transformations"]["rows_removed"], "missing": missing})))
    db.commit()
    return result


@app.post("/api/datasets/export")
async def dataset_export(file: UploadFile = File(...), drop_duplicates: bool = Form(False), missing: str = Form("keep"), selected_columns: str = Form("")):
    frame = await load_upload(file)
    selected = None
    if selected_columns:
        try:
            selected = json.loads(selected_columns)
        except json.JSONDecodeError as exc:
            from fastapi import HTTPException
            raise HTTPException(422, "selected_columns must be a JSON array.") from exc
    transformed = clean(frame, drop_duplicates, missing, selected)
    content = transformed.to_csv(index=False).encode("utf-8")
    return StreamingResponse(iter([content]), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": "attachment; filename=aquashield-cleaned.csv"})


@app.get("/api/experiments")
def experiments(db: Session = Depends(get_db)):
    rows = db.query(models.Experiment).order_by(models.Experiment.created_at.desc()).limit(50).all()
    return {"experiments": [{"id": row.id, "filename": row.filename, "rows": row.rows, "columns": row.columns, "summary": json.loads(row.summary), "created_at": row.created_at.isoformat()} for row in rows]}

