-- =====================================================================
-- Database Schema for Student Data Analysis and Reporting Tool
-- Tables: courses, students, enrollments, stg_student_raw, import_logs
-- Views: vw_enrollment_detail, vw_student_summary
-- =====================================================================

CREATE DATABASE IF NOT EXISTS student_analytics;
USE student_analytics;

-- 1. Courses Table
CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_name VARCHAR(150) NOT NULL,
    credits INT NOT NULL DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_course_code (course_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Students Table
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    gender ENUM('M', 'F', 'O') NOT NULL,
    dob DATE NOT NULL,
    department VARCHAR(80) NOT NULL,
    admission_year INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_department (department),
    INDEX idx_admission_year (admission_year),
    INDEX idx_dept_adm_year (department, admission_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Enrollments Table
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    semester INT NOT NULL,
    marks DECIMAL(5,2) NULL,
    attendance_pct DECIMAL(5,2) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_enrollments_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    CONSTRAINT fk_enrollments_course FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    CONSTRAINT uq_student_course_semester UNIQUE (student_id, course_id, semester),
    INDEX idx_student_semester (student_id, semester),
    INDEX idx_course_id (course_id),
    INDEX idx_semester (semester)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Staging Table for Raw Student Import
CREATE TABLE IF NOT EXISTS stg_student_raw (
    staging_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id VARCHAR(64) NOT NULL,
    student_id VARCHAR(50) NULL,
    first_name VARCHAR(100) NULL,
    last_name VARCHAR(100) NULL,
    email VARCHAR(150) NULL,
    gender VARCHAR(20) NULL,
    dob VARCHAR(50) NULL,
    department VARCHAR(100) NULL,
    admission_year VARCHAR(20) NULL,
    course_code VARCHAR(50) NULL,
    course_name VARCHAR(150) NULL,
    credits VARCHAR(20) NULL,
    semester VARCHAR(20) NULL,
    marks VARCHAR(30) NULL,
    attendance_pct VARCHAR(30) NULL,
    import_status ENUM('PENDING', 'VALIDATED', 'PROCESSED', 'REJECTED') DEFAULT 'PENDING',
    error_message TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stg_batch (batch_id),
    INDEX idx_stg_status (import_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Import Logs Table
CREATE TABLE IF NOT EXISTS import_logs (
    import_id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    total_rows INT NOT NULL DEFAULT 0,
    valid_rows INT NOT NULL DEFAULT 0,
    rejected_rows INT NOT NULL DEFAULT 0,
    duplicates_removed INT NOT NULL DEFAULT 0,
    nulls_filled INT NOT NULL DEFAULT 0,
    outliers_flagged INT NOT NULL DEFAULT 0,
    status ENUM('SUCCESS', 'FAILED', 'PARTIAL') NOT NULL,
    error_summary TEXT NULL,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. SQL Views for Common Joins
CREATE OR REPLACE VIEW vw_enrollment_detail AS
SELECT 
    e.enrollment_id,
    e.semester,
    e.marks,
    e.attendance_pct,
    s.student_id,
    s.first_name,
    s.last_name,
    CONCAT(s.first_name, ' ', s.last_name) AS full_name,
    s.email,
    s.gender,
    s.dob,
    s.department,
    s.admission_year,
    c.course_id,
    c.course_code,
    c.course_name,
    c.credits,
    CASE 
        WHEN e.marks >= 85 THEN 'A'
        WHEN e.marks >= 70 THEN 'B'
        WHEN e.marks >= 55 THEN 'C'
        WHEN e.marks >= 40 THEN 'D'
        ELSE 'F'
    END AS grade,
    CASE WHEN e.marks >= 40 THEN 1 ELSE 0 END AS is_passed,
    CASE WHEN e.attendance_pct < 75.0 AND e.marks < 40.0 THEN 1 ELSE 0 END AS is_at_risk
FROM enrollments e
JOIN students s ON e.student_id = s.student_id
JOIN courses c ON e.course_id = c.course_id;

CREATE OR REPLACE VIEW vw_student_summary AS
SELECT
    s.student_id,
    s.first_name,
    s.last_name,
    CONCAT(s.first_name, ' ', s.last_name) AS full_name,
    s.email,
    s.gender,
    s.department,
    s.admission_year,
    COUNT(e.enrollment_id) AS total_enrolled_courses,
    ROUND(AVG(e.marks), 2) AS gpa_marks_avg,
    ROUND(AVG(e.attendance_pct), 2) AS overall_attendance_pct,
    SUM(CASE WHEN e.marks >= 40 THEN 1 ELSE 0 END) AS total_courses_passed
FROM students s
LEFT JOIN enrollments e ON s.student_id = e.student_id
GROUP BY s.student_id, s.first_name, s.last_name, s.email, s.gender, s.department, s.admission_year;
