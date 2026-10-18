import pytest
from fastapi import HTTPException
from app.services.csv_analysis import analyze, clean, profile, read_csv_bytes


def test_parse_profile_and_summary():
    frame = read_csv_bytes(b"rain,area\n2.0,north\n4.0,south\n", "rain.csv")
    result = profile(frame)
    assert result["rows"] == 2
    assert result["columns"][0]["kind"] == "numeric"
    assert analyze(frame)["numeric_summary"]["rain"]["mean"] == 3.0


def test_rejects_wrong_extension_and_bad_csv():
    with pytest.raises(HTTPException) as extension:
        read_csv_bytes(b"a\n1", "dataset.txt")
    assert extension.value.status_code == 415
    with pytest.raises(HTTPException):
        read_csv_bytes(b"", "dataset.csv")
    with pytest.raises(HTTPException) as duplicate_header:
        read_csv_bytes(b"value,value\n1,2\n", "dataset.csv")
    assert duplicate_header.value.status_code == 400


def test_cleaning_is_explicit_and_reports_expected_rows():
    frame = read_csv_bytes(b"x,y\n1,4\n1,4\n3,\n", "data.csv")
    assert profile(frame)["duplicate_rows"] == 1
    transformed = clean(frame, drop_duplicates=True, missing="drop_rows")
    assert len(transformed) == 1
    assert transformed.iloc[0]["x"] == 1


def test_invalid_selected_columns_rejected():
    frame = read_csv_bytes(b"x\n1\n", "data.csv")
    with pytest.raises(HTTPException) as error:
        clean(frame, selected_columns=["not_a_column"])
    assert error.value.status_code == 422


def test_geographic_fields_and_outlier_profile():
    frame = read_csv_bytes(b"latitude,value\n13.0,1\n13.1,2\n13.2,3\n13.3,100\n", "data.csv")
    assert profile(frame)["columns"][0]["kind"] == "geographic candidate"
    assert analyze(frame)["iqr_outlier_counts"]["value"] == 1

