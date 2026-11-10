"""Pytest test configuration and shared data fixtures."""

import os
os.environ["APP_ENV"] = "testing"

from datetime import date
import asyncio
import io
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock
from urllib.parse import parse_qs, urlencode, urlparse
import numpy as np
import pandas as pd
import pytest

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.connection import DatabaseConnection, get_db
from app.main import create_app


class InMemoryASGIResponse:
    """Wrapper matching HTTP response interface."""

    def __init__(self, status_code: int, headers: list, content: bytes):
        self.status_code = status_code
        self.headers = {
            k.decode("latin1").lower(): v.decode("latin1") for k, v in headers
        }
        self.content = content

    def json(self):
        return json.loads(self.content.decode("utf-8"))

    @property
    def text(self):
        return self.content.decode("utf-8")


class InMemoryTestClient:
    """Fast, in-process ASGI test client requiring zero network loopback sockets."""

    def __init__(self, app):
        self.app = app

    def _request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
        files: Optional[dict] = None,
    ) -> InMemoryASGIResponse:
        parsed = urlparse(url)
        path = parsed.path
        query_dict = parse_qs(parsed.query)
        if params:
            for k, v in params.items():
                query_dict[k] = [str(v)]
        query_string = urlencode(query_dict, doseq=True).encode("utf-8")

        headers = [(b"host", b"testserver")]
        body = b""

        if json_data is not None:
            headers.append((b"content-type", b"application/json"))
            body = json.dumps(json_data).encode("utf-8")
        elif files:
            boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
            headers.append(
                (b"content-type", f"multipart/form-data; boundary={boundary}".encode("utf-8"))
            )
            body_parts = []
            for field_name, file_tuple in files.items():
                fname, fobj, fcontent_type = file_tuple
                f_data = fobj.read() if hasattr(fobj, "read") else fobj
                body_parts.append(
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="{field_name}"; filename="{fname}"\r\n'
                    f"Content-Type: {fcontent_type}\r\n\r\n".encode("utf-8")
                    + f_data
                    + b"\r\n"
                )
            body_parts.append(f"--{boundary}--\r\n".encode("utf-8"))
            body = b"".join(body_parts)

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method.upper(),
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("utf-8"),
            "query_string": query_string,
            "headers": headers,
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "app": self.app,
        }

        response_body = []
        response_headers = []
        status_code = [200]

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            if message["type"] == "http.response.start":
                status_code[0] = message["status"]
                response_headers.extend(message.get("headers", []))
            elif message["type"] == "http.response.body":
                response_body.append(message.get("body", b""))

        asyncio.run(self.app(scope, receive, send))
        return InMemoryASGIResponse(status_code[0], response_headers, b"".join(response_body))

    def get(self, url: str, **kwargs):
        return self._request("GET", url, params=kwargs.get("params"))

    def post(self, url: str, **kwargs):
        return self._request(
            "POST", url, json_data=kwargs.get("json"), files=kwargs.get("files")
        )


@pytest.fixture
def sample_clean_df() -> pd.DataFrame:
    """Fixture providing clean, valid enrollment and student DataFrame."""
    data = [
        {
            "enrollment_id": 1,
            "student_id": 101,
            "first_name": "Alice",
            "last_name": "Smith",
            "full_name": "Alice Smith",
            "email": "alice.smith@university.edu",
            "gender": "F",
            "dob": date(2002, 4, 15),
            "department": "Computer Science",
            "admission_year": 2022,
            "course_id": 1,
            "course_code": "CS101",
            "course_name": "Intro to CS",
            "credits": 4,
            "semester": 1,
            "marks": 88.0,
            "attendance_pct": 92.0,
            "grade": "A",
            "is_passed": True,
            "is_at_risk": False,
        },
        {
            "enrollment_id": 2,
            "student_id": 101,
            "first_name": "Alice",
            "last_name": "Smith",
            "full_name": "Alice Smith",
            "email": "alice.smith@university.edu",
            "gender": "F",
            "dob": date(2002, 4, 15),
            "department": "Computer Science",
            "admission_year": 2022,
            "course_id": 2,
            "course_code": "CS102",
            "course_name": "Data Structures",
            "credits": 4,
            "semester": 1,
            "marks": 76.0,
            "attendance_pct": 85.0,
            "grade": "B",
            "is_passed": True,
            "is_at_risk": False,
        },
        {
            "enrollment_id": 3,
            "student_id": 102,
            "first_name": "Bob",
            "last_name": "Jones",
            "full_name": "Bob Jones",
            "email": "bob.jones@university.edu",
            "gender": "M",
            "dob": date(2001, 8, 20),
            "department": "Electrical Engineering",
            "admission_year": 2021,
            "course_id": 3,
            "course_code": "EE101",
            "course_name": "Circuit Analysis",
            "credits": 3,
            "semester": 2,
            "marks": 35.0,
            "attendance_pct": 60.0,
            "grade": "F",
            "is_passed": False,
            "is_at_risk": True,
        },
        {
            "enrollment_id": 4,
            "student_id": 103,
            "first_name": "Charlie",
            "last_name": "Brown",
            "full_name": "Charlie Brown",
            "email": "charlie.brown@university.edu",
            "gender": "O",
            "dob": date(2003, 1, 10),
            "department": "Mechanical Engineering",
            "admission_year": 2023,
            "course_id": 4,
            "course_code": "ME101",
            "course_name": "Engineering Mechanics",
            "credits": 3,
            "semester": 1,
            "marks": 62.0,
            "attendance_pct": 78.0,
            "grade": "C",
            "is_passed": True,
            "is_at_risk": False,
        },
        {
            "enrollment_id": 5,
            "student_id": 104,
            "first_name": "Diana",
            "last_name": "Prince",
            "full_name": "Diana Prince",
            "email": "diana.prince@university.edu",
            "gender": "F",
            "dob": date(2002, 11, 25),
            "department": "Computer Science",
            "admission_year": 2022,
            "course_id": 1,
            "course_code": "CS101",
            "course_name": "Intro to CS",
            "credits": 4,
            "semester": 1,
            "marks": 94.0,
            "attendance_pct": 98.0,
            "grade": "A",
            "is_passed": True,
            "is_at_risk": False,
        },
        {
            "enrollment_id": 6,
            "student_id": 105,
            "first_name": "Evan",
            "last_name": "Wright",
            "full_name": "Evan Wright",
            "email": "evan.wright@university.edu",
            "gender": "M",
            "dob": date(2002, 2, 14),
            "department": "Civil Engineering",
            "admission_year": 2022,
            "course_id": 5,
            "course_code": "CE101",
            "course_name": "Structural Mechanics",
            "credits": 3,
            "semester": 2,
            "marks": 48.0,
            "attendance_pct": 72.0,
            "grade": "D",
            "is_passed": True,
            "is_at_risk": False,
        },
    ]
    return pd.DataFrame(data)


@pytest.fixture
def sample_dirty_df() -> pd.DataFrame:
    """Fixture providing intentionally dirty data for cleaner test cases."""
    records = [
        {
            "student_id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "gender": "M",
            "dob": "2002-05-14",
            "department": "Computer Science",
            "admission_year": "2022",
            "course_code": "CS101",
            "semester": "1",
            "marks": "75.0",
            "attendance_pct": "85.0",
        },
        {
            "student_id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "gender": "M",
            "dob": "2002-05-14",
            "department": "Computer Science",
            "admission_year": "2022",
            "course_code": "CS101",
            "semester": "1",
            "marks": "75.0",
            "attendance_pct": "85.0",
        },
        {
            "student_id": 2,
            "first_name": "   aLiCe  ",
            "last_name": "  wOnDeR   ",
            "email": "  ALICE.WONDER@EXAMPLE.COM   ",
            "gender": "f",
            "dob": "15-04-2003",
            "department": "Computer Science",
            "admission_year": 2023,
            "course_code": "CS101",
            "semester": 1,
            "marks": 85.0,
            "attendance_pct": 90.0,
        },
        {
            "student_id": 3,
            "first_name": "Bad",
            "last_name": "Email",
            "email": "not_an_email_address",
            "gender": "O",
            "dob": "2002-01-01",
            "department": "Electrical Engineering",
            "admission_year": 2022,
            "course_code": "EE101",
            "semester": 1,
            "marks": 50.0,
            "attendance_pct": 80.0,
        },
        {
            "student_id": None,
            "first_name": "Missing",
            "last_name": "ID",
            "email": "missing.id@example.com",
            "gender": "M",
            "dob": "2002-02-02",
            "department": "Civil Engineering",
            "admission_year": 2022,
            "course_code": "CE101",
            "semester": 1,
            "marks": 60.0,
            "attendance_pct": 75.0,
        },
        {
            "student_id": 4,
            "first_name": "Score",
            "last_name": "Extreme",
            "email": "score.extreme@example.com",
            "gender": "M",
            "dob": "2002-03-03",
            "department": "Computer Science",
            "admission_year": 2022,
            "course_code": "CS101",
            "semester": 1,
            "marks": 110.0,
            "attendance_pct": -10.0,
        },
        {
            "student_id": 5,
            "first_name": "Needs",
            "last_name": "Imputation",
            "email": "needs.imputation@example.com",
            "gender": "F",
            "dob": "2002-06-06",
            "department": "Computer Science",
            "admission_year": 2022,
            "course_code": "CS101",
            "semester": 1,
            "marks": np.nan,
            "attendance_pct": 80.0,
        },
        {
            "student_id": 6,
            "first_name": "Outlier",
            "last_name": "Low",
            "email": "outlier.low@example.com",
            "gender": "M",
            "dob": "2001-07-07",
            "department": "Computer Science",
            "admission_year": 2021,
            "course_code": "CS101",
            "semester": 1,
            "marks": 5.0,
            "attendance_pct": 50.0,
        },
    ]
    return pd.DataFrame(records)


@pytest.fixture
def mock_db(sample_clean_df) -> MagicMock:
    """Fixture providing a mocked DatabaseConnection satisfying all repository calls."""
    db = MagicMock(spec=DatabaseConnection)
    db.ping.return_value = True

    cursor_mock = MagicMock()
    cursor_mock.fetchall.return_value = sample_clean_df.to_dict(orient="records")
    cursor_mock.fetchone.return_value = {
        "alive": 1,
        "total_count": len(sample_clean_df),
        "total_students": 5,
        "total_courses": 5,
        "avg_marks": 67.17,
        "avg_attendance": 81.83,
        "pass_rate": 83.33,
        "at_risk_count": 1,
        "total_enrolled_courses": 2,
        "gpa_marks_avg": 82.0,
        "overall_attendance_pct": 88.5,
        "total_courses_passed": 2,
        "student_id": 101,
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@university.edu",
        "gender": "F",
        "dob": date(2002, 4, 15),
        "department": "Computer Science",
        "admission_year": 2022,
        "cnt": 5,
    }
    cursor_mock.lastrowid = 1
    cursor_mock.rowcount = 1

    class MockCursorContext:
        def __enter__(self):
            return cursor_mock
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    class MockConnContext:
        def __enter__(self):
            conn = MagicMock()
            conn.cursor.return_value = cursor_mock
            return conn
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    db.get_cursor.return_value = MockCursorContext()
    db.get_connection.return_value = MockConnContext()
    db.cursor_mock = cursor_mock
    return db


@pytest.fixture
def test_client(mock_db) -> InMemoryTestClient:
    """FastAPI test client with overridden database dependency."""
    old_instance = DatabaseConnection._instance
    DatabaseConnection._instance = mock_db
    app = create_app()
    app.dependency_overrides[get_db] = lambda: mock_db
    client = InMemoryTestClient(app)
    yield client
    app.dependency_overrides.clear()
    DatabaseConnection._instance = old_instance
