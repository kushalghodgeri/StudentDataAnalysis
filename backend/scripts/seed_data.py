"""Seed database with 500 students, 20 courses, ~3000 enrollments, and generate dirty data sample."""

import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from faker import Faker
import numpy as np
import pandas as pd
from app.config.settings import get_settings
from app.db.connection import DatabaseConnection
from app.utils.logger import logger

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

DEPARTMENTS = [
    "Computer Science",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Information Technology",
    "Biotechnology",
]

COURSES_DATA = [
    ("CS101", "Introduction to Computer Science", 4),
    ("CS102", "Data Structures & Algorithms", 4),
    ("CS201", "Database Management Systems", 3),
    ("CS202", "Operating Systems", 4),
    ("CS301", "Computer Networks", 3),
    ("CS302", "Software Engineering", 3),
    ("CS401", "Artificial Intelligence & ML", 4),
    ("EE101", "Circuit Analysis", 3),
    ("EE201", "Digital Electronics", 4),
    ("EE301", "Signals and Systems", 3),
    ("ME101", "Engineering Mechanics", 3),
    ("ME201", "Thermodynamics", 4),
    ("ME301", "Fluid Mechanics", 3),
    ("CE101", "Structural Mechanics", 3),
    ("CE201", "Surveying & Geomatics", 3),
    ("IT101", "Web Development Fundamentals", 3),
    ("IT201", "Cloud Computing Architectures", 3),
    ("IT301", "Information Security & Cyber Defense", 3),
    ("BT101", "Molecular Biology", 3),
    ("BT201", "Bioprocess Engineering", 4),
]


def apply_schema(db: DatabaseConnection) -> None:
    """Read schema.sql and apply to MySQL database."""
    schema_path = backend_dir / "app" / "db" / "schema.sql"
    if not schema_path.exists():
        logger.error(f"Schema file not found at {schema_path}")
        return

    with open(schema_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split into individual statements
    statements = sql_content.split(";")
    logger.info("Applying database schema...")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for statement in statements:
            stmt = statement.strip()
            if stmt and not stmt.startswith("--"):
                try:
                    cursor.execute(stmt)
                except Exception as e:
                    logger.warning(f"Error executing statement [{stmt[:40]}...]: {e}")
        cursor.close()
    logger.info("Schema application complete.")


def seed_database(db: DatabaseConnection):
    """Seed MySQL with clean, realistic data matching user specification."""
    logger.info("Starting database seeding...")

    with db.get_connection() as conn:
        cursor = conn.cursor()

        # 1. Clear existing records safely
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE enrollments;")
        cursor.execute("TRUNCATE TABLE students;")
        cursor.execute("TRUNCATE TABLE courses;")
        cursor.execute("TRUNCATE TABLE stg_student_raw;")
        cursor.execute("TRUNCATE TABLE import_logs;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        # 2. Insert 20 Courses
        cursor.executemany(
            "INSERT INTO courses (course_code, course_name, credits) VALUES (%s, %s, %s);",
            COURSES_DATA,
        )
        logger.info(f"Seeded {len(COURSES_DATA)} courses.")

        # Fetch inserted course ids
        cursor.execute("SELECT course_id, course_code FROM courses;")
        course_map = {row[1]: row[0] for row in cursor.fetchall()}
        course_ids = list(course_map.values())

        # 3. Insert 500 Students
        students_records = []
        emails_seen = set()
        for i in range(1, 501):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}{i}@university.edu"
            if email in emails_seen:
                email = f"student_{i}_{fake.unique.email()}"
            emails_seen.add(email)

            gender = random.choice(["M", "F", "O"])
            dob = fake.date_of_birth(minimum_age=18, maximum_age=25)
            dept = random.choice(DEPARTMENTS)
            adm_year = random.choice([2021, 2022, 2023, 2024])

            students_records.append((
                first_name, last_name, email, gender, dob, dept, adm_year
            ))

        cursor.executemany(
            """
            INSERT INTO students (first_name, last_name, email, gender, dob, department, admission_year)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """,
            students_records,
        )
        logger.info(f"Seeded {len(students_records)} students.")

        # Fetch student IDs
        cursor.execute("SELECT student_id, admission_year FROM students;")
        student_rows = cursor.fetchall()

        # 4. Insert ~3000 Enrollments
        enrollments_records = []
        for s_id, adm_year in student_rows:
            # Assign courses across semesters 1 to 8
            # Each student takes 5 to 7 courses across semesters
            num_courses = random.randint(5, 7)
            chosen_courses = random.sample(course_ids, num_courses)

            for c_id in chosen_courses:
                sem = random.randint(1, 8)
                # Realistic bimodal marks distribution (passing vs struggling)
                is_struggling = random.random() < 0.12
                if is_struggling:
                    marks = round(random.uniform(20.0, 39.5), 2)
                    att = round(random.uniform(45.0, 74.0), 2)
                else:
                    marks = round(np.clip(random.gauss(68, 14), 40.0, 98.0), 2)
                    att = round(np.clip(random.gauss(84, 8), 65.0, 100.0), 2)

                enrollments_records.append((s_id, c_id, sem, marks, att))

        cursor.executemany(
            """
            INSERT INTO enrollments (student_id, course_id, semester, marks, attendance_pct)
            VALUES (%s, %s, %s, %s, %s);
            """,
            enrollments_records,
        )
        logger.info(f"Seeded {len(enrollments_records)} enrollments.")

        # 5. Confirm Row Counts
        cursor.execute("SELECT COUNT(*) FROM courses;")
        c_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM students;")
        s_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM enrollments;")
        e_count = cursor.fetchone()[0]

        print("\n========================================================")
        print(" DATABASE SEEDING VERIFICATION SUMMARY")
        print("========================================================")
        print(f"Courses Table Rows    : {c_count} (Expected: 20)")
        print(f"Students Table Rows   : {s_count} (Expected: 500)")
        print(f"Enrollments Table Rows: {e_count} (Expected: ~3000)")
        print("========================================================\n")


def generate_dirty_raw_csv():
    """Create a sample dataset with deliberate dirty data to test cleaner rules."""
    raw_dir = backend_dir / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    csv_path = raw_dir / "dirty_student_data.csv"

    records = []
    # 200 regular records
    for i in range(1, 201):
        first = fake.first_name()
        last = fake.last_name()
        records.append({
            "student_id": i,
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}{i}@example.com",
            "gender": random.choice(["M", "F", "O"]),
            "dob": fake.date_of_birth(minimum_age=18, maximum_age=25).strftime("%Y-%m-%d"),
            "department": random.choice(DEPARTMENTS),
            "admission_year": random.choice([2021, 2022, 2023, 2024]),
            "course_code": random.choice(COURSES_DATA)[0],
            "course_name": "Sample Course",
            "credits": 3,
            "semester": random.randint(1, 8),
            "marks": round(random.uniform(45, 95), 2),
            "attendance_pct": round(random.uniform(70, 98), 2),
        })

    # Deliberate dirty records:
    # 1. Duplicate rows
    for _ in range(10):
        records.append(dict(records[random.randint(0, 50)]))

    # 2. Messy casing and extra whitespace
    records.append({
        "student_id": 901,
        "first_name": "   jOHn  ",
        "last_name": "  dOE   ",
        "email": "  JOHNDOE901@EXAMPLE.COM   ",
        "gender": "m",
        "dob": "2002-05-14",
        "department": "Computer Science",
        "admission_year": 2022,
        "course_code": "CS101",
        "course_name": "Intro CS",
        "credits": 4,
        "semester": 1,
        "marks": 78.5,
        "attendance_pct": 88.0,
    })

    # 3. Invalid emails (should be dropped)
    records.append({
        "student_id": 902,
        "first_name": "Broken",
        "last_name": "Email",
        "email": "invalid-email-format-without-at",
        "gender": "F",
        "dob": "2001-08-20",
        "department": "Electrical Engineering",
        "admission_year": 2022,
        "course_code": "EE101",
        "credits": 3,
        "semester": 1,
        "marks": 65.0,
        "attendance_pct": 80.0,
    })

    # 4. Out of bounds marks and attendance
    records.append({
        "student_id": 903,
        "first_name": "Extreme",
        "last_name": "Scores",
        "email": "extreme.scores903@example.com",
        "gender": "M",
        "dob": "2003-01-10",
        "department": "Civil Engineering",
        "admission_year": 2023,
        "course_code": "CE101",
        "credits": 3,
        "semester": 2,
        "marks": 105.0,  # >100, should be clipped to 100
        "attendance_pct": -5.0,  # <0, should be clipped to 0
    })

    # 5. Missing student_id (should be dropped)
    records.append({
        "student_id": None,
        "first_name": "No",
        "last_name": "StudentId",
        "email": "no.id@example.com",
        "gender": "O",
        "dob": "2002-11-11",
        "department": "Biotechnology",
        "admission_year": 2022,
        "course_code": "BT101",
        "credits": 3,
        "semester": 1,
        "marks": 55.0,
        "attendance_pct": 75.0,
    })

    # 6. Missing marks (should be imputed with course median)
    records.append({
        "student_id": 904,
        "first_name": "Missing",
        "last_name": "Marks",
        "email": "missing.marks904@example.com",
        "gender": "F",
        "dob": "2002-09-15",
        "department": "Computer Science",
        "admission_year": 2022,
        "course_code": "CS101",
        "credits": 4,
        "semester": 1,
        "marks": None,  # Should be imputed
        "attendance_pct": 85.0,
    })

    # 7. Low outlier for IQR
    records.append({
        "student_id": 905,
        "first_name": "Outlier",
        "last_name": "Student",
        "email": "outlier905@example.com",
        "gender": "M",
        "dob": "2001-04-12",
        "department": "Mechanical Engineering",
        "admission_year": 2021,
        "course_code": "ME101",
        "credits": 3,
        "semester": 3,
        "marks": 5.0,  # Outlier
        "attendance_pct": 40.0,
    })

    df = pd.DataFrame(records)
    df.to_csv(csv_path, index=False)
    logger.info(f"Generated dirty data sample with {len(df)} rows at {csv_path}")


if __name__ == "__main__":
    generate_dirty_raw_csv()
    try:
        db = DatabaseConnection()
        if db.ping():
            apply_schema(db)
            seed_database(db)
        else:
            print("Notice: MySQL database is currently offline or unreachable. Generated dirty sample data successfully.")
    except Exception as e:
        print(f"Notice: Database seeding encountered: {e}. Raw CSV sample created successfully.")
