"""Integration tests for all FastAPI REST endpoints using TestClient."""

import io
import pytest


def test_health_endpoint(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "db_connected" in data

    # Base path /api/v1 test
    v1_res = test_client.get("/api/v1/health")
    assert v1_res.status_code == 200


def test_meta_filters(test_client):
    response = test_client.get("/api/v1/meta/filters")
    assert response.status_code == 200
    data = response.json()
    assert "departments" in data
    assert "semesters" in data
    assert "courses" in data


def test_students_pagination_and_query(test_client):
    response = test_client.get("/api/v1/students?page=1&page_size=10&department=Computer+Science")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data


def test_student_detail_found_and_not_found(test_client, mock_db):
    # Found
    response = test_client.get("/api/v1/students/101")
    assert response.status_code == 200
    data = response.json()
    assert "student_id" in data
    assert "enrollments" in data
    assert "stats" in data

    # Not found - mock get_student_detail returning None
    original_fetchone = mock_db.cursor_mock.fetchone.return_value
    mock_db.cursor_mock.fetchone.return_value = None

    nf_response = test_client.get("/api/v1/students/99999")
    assert nf_response.status_code == 404
    err = nf_response.json()
    assert "error" in err
    assert err["error"]["code"] == "RESOURCE_NOT_FOUND"

    mock_db.cursor_mock.fetchone.return_value = original_fetchone


def test_analytics_overview(test_client):
    response = test_client.get("/api/v1/analytics/overview?semester=1")
    assert response.status_code == 200
    data = response.json()
    assert "total_students" in data
    assert "total_courses" in data
    assert "avg_marks" in data
    assert "pass_rate" in data
    assert "avg_attendance" in data
    assert "at_risk_count" in data


def test_analytics_performance(test_client):
    response = test_client.get("/api/v1/analytics/performance?semester=1")
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "grade_distribution" in data
    assert "dept_averages" in data
    assert "semester_trend" in data
    assert "top10" in data
    assert "bottom10" in data


def test_analytics_attendance(test_client):
    response = test_client.get("/api/v1/analytics/attendance")
    assert response.status_code == 200
    data = response.json()
    assert "by_department" in data
    assert "correlation" in data
    assert "at_risk" in data


def test_analytics_demographics(test_client):
    response = test_client.get("/api/v1/analytics/demographics")
    assert response.status_code == 200
    data = response.json()
    assert "gender" in data
    assert "department_counts" in data
    assert "cohorts" in data


def test_imports_upload_csv(test_client):
    csv_content = b"student_id,first_name,last_name,email,gender,dob,department,admission_year,course_code,semester,marks,attendance_pct\n1,Alice,Smith,alice@example.com,F,2002-01-01,CS,2022,CS101,1,85,90\n"
    files = {"file": ("test_students.csv", io.BytesIO(csv_content), "text/csv")}

    response = test_client.post("/api/v1/imports", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "import_id" in data
    assert "cleaning_summary" in data
    assert data["cleaning_summary"]["rows_in"] == 1


def test_imports_upload_invalid_format(test_client):
    txt_content = b"Not a csv or excel"
    files = {"file": ("test.txt", io.BytesIO(txt_content), "text/plain")}

    response = test_client.post("/api/v1/imports", files=files)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "IMPORT_ERROR"


def test_reports_generate_and_list(test_client):
    payload = {
        "semester": 1,
        "department": "Computer Science",
        "formats": ["pdf", "csv", "xlsx"],
    }
    response = test_client.post("/api/v1/reports/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert "files" in data
    assert "charts" in data
    assert len(data["files"]) == 3
    assert len(data["charts"]) == 7

    list_res = test_client.get("/api/v1/reports")
    assert list_res.status_code == 200
    reports = list_res.json()
    assert isinstance(reports, list)


def test_standardized_error_format(test_client):
    # Trigger 422 validation error
    res = test_client.get("/api/v1/students?page=-5")
    assert res.status_code == 422
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in data["error"]
