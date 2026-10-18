import pytest
from unittest.mock import AsyncMock, patch
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_test_database():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_health_and_city_catalog():
    assert client.get("/api/health").json()["status"] == "ok"
    catalog = client.get("/api/cities").json()["cities"]
    city = catalog[0]
    assert city["id"] == "chennai"
    assert city["categories"] == ["historical rainfall"]
    assert {entry["name"] for entry in catalog} >= {"Mumbai", "Bengaluru", "Delhi", "Kolkata", "Hyderabad"}


def test_upload_profile_and_analysis_are_dynamic():
    file = ("observations.csv", b"rain_mm,area\n3.5,north\n5.5,south\n", "text/csv")
    profiled = client.post("/api/datasets/profile", files={"file": file})
    assert profiled.status_code == 200
    assert profiled.json()["rows"] == 2
    response = client.post("/api/datasets/analyze", files={"file": file}, data={"missing": "keep", "selected_columns": '["rain_mm", "area"]'})
    assert response.status_code == 200
    assert response.json()["analysis"]["numeric_summary"]["rain_mm"]["mean"] == 4.5


def test_rejects_non_csv_upload():
    response = client.post("/api/datasets/profile", files={"file": ("sample.json", b"{}", "application/json")})
    assert response.status_code == 415


def test_city_rainfall_endpoint_returns_labeled_source_payload():
    payload = {"city": "Chennai", "points": [{"date": "2024-01-01", "precipitation_mm": 1.2}], "source": "Open-Meteo Historical Weather API"}
    with patch("app.main.rainfall", new=AsyncMock(return_value=payload)):
        response = client.get("/api/cities/chennai/rainfall?start_date=2024-01-01&end_date=2024-01-01")
    assert response.status_code == 200
    assert response.json()["points"][0]["precipitation_mm"] == 1.2


def test_rainfall_route_passes_the_selected_city_to_the_data_service():
    payload = {"city": "Mumbai", "points": [{"date": "2024-01-01", "precipitation_mm": 0.0}]}
    with patch("app.main.rainfall", new=AsyncMock(return_value=payload)) as service:
        response = client.get("/api/cities/mumbai/rainfall?start_date=2024-01-01&end_date=2024-01-01")
    assert response.status_code == 200
    assert service.await_args.args[0] == "mumbai"


def test_rainfall_route_rejects_unknown_city():
    response = client.get("/api/cities/unknown/rainfall?start_date=2024-01-01&end_date=2024-01-01")
    assert response.status_code == 404


def test_city_rainfall_uses_bundled_snapshot_when_source_is_offline():
    class OfflineClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return None

        async def get(self, *_args, **_kwargs):
            raise httpx.ConnectError("offline")

    with patch("app.services.city_data.httpx.AsyncClient", return_value=OfflineClient()):
        response = client.get("/api/cities/chennai/rainfall?start_date=2020-01-01&end_date=2020-01-03")
    assert response.status_code == 200
    result = response.json()
    assert len(result["points"]) == 3
    assert result["source_status"].startswith("Bundled snapshot")


def test_export_returns_cleaned_csv():
    response = client.post("/api/datasets/export", files={"file": ("sample.csv", b"x,area\n1,north\n1,north\n", "text/csv")}, data={"drop_duplicates": "true", "missing": "keep"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.text.count("1,north") == 1

