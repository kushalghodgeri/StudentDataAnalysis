"""Verification script: starts uvicorn server, hits key REST API endpoints, and prints responses."""

import os
import sys
import time
import subprocess
from pathlib import Path
import httpx

backend_dir = Path(__file__).resolve().parent.parent

def main():
    print("Starting Uvicorn server on port 8000...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(backend_dir)
    env["APP_ENV"] = "testing"

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(backend_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    time.sleep(3)  # Allow server to bind and start

    base_url = "http://127.0.0.1:8000"
    endpoints_to_test = [
        ("GET", "/health"),
        ("GET", "/api/v1/health"),
        ("GET", "/api/v1/meta/filters"),
        ("GET", "/api/v1/students?page=1&page_size=5"),
        ("GET", "/api/v1/analytics/overview"),
        ("GET", "/api/v1/analytics/performance"),
        ("GET", "/api/v1/analytics/attendance"),
        ("GET", "/api/v1/analytics/demographics"),
        ("GET", "/api/v1/reports"),
        ("GET", "/docs"),
    ]

    try:
        with httpx.Client(base_url=base_url, timeout=5.0) as client:
            all_passed = True
            for method, endpoint in endpoints_to_test:
                try:
                    if method == "GET":
                        r = client.get(endpoint)
                    print(f"[{method}] {endpoint} -> Status: {r.status_code}")
                    if r.status_code not in (200, 404):  # 404 is allowed if data not in empty test db
                        all_passed = False
                except Exception as e:
                    print(f"[{method}] {endpoint} -> Connection Error: {e}")
                    all_passed = False

            # Test report generation endpoint
            try:
                rep_payload = {"semester": 1, "department": "Computer Science", "formats": ["pdf", "csv", "xlsx"]}
                rep_res = client.post("/api/v1/reports/generate", json=rep_payload)
                print(f"[POST] /api/v1/reports/generate -> Status: {rep_res.status_code}")
            except Exception as e:
                print(f"[POST] /api/v1/reports/generate -> Error: {e}")

            if all_passed:
                print("\nALL VERIFICATION ENDPOINTS REACHED SUCCESSFULLY!")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()
        print("Server stopped.")

if __name__ == "__main__":
    main()
