import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "joblink.db"

app = FastAPI(
    title="JobLink UG API",
    description="SQLite-backed API for JobLink UG jobs, employers, applications, and admin dashboards.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


JobStatus = Literal["Live", "Pending", "Closed"]


class JobBase(BaseModel):
    title: str = Field(..., min_length=2)
    company: str = Field(..., min_length=2)
    location: str = Field(..., min_length=2)
    category: str = "General"
    type: str = "Full-time"
    experience: str = "Entry"
    work_mode: str = "On-site"
    salary: str = ""
    salary_min: int = 0
    salary_max: int = 0
    posted_at: date = Field(default_factory=date.today)
    skills: list[str] = Field(default_factory=list)
    description: str = "No description added yet."


class JobCreate(JobBase):
    pass


class Job(JobBase):
    id: str
    status: JobStatus = "Pending"
    applicants: int = 0


class ApplicationCreate(BaseModel):
    applicant_name: str = Field(..., min_length=2)
    email: str = Field(..., min_length=5)
    cv_url: str | None = None
    note: str | None = None


class Application(ApplicationCreate):
    id: str
    job_id: str
    status: Literal["pending", "reviewed", "accepted", "rejected"] = "pending"


SEED_JOBS = [
    {
        "title": "Frontend Developer",
        "company": "Kampala Digital Studio",
        "location": "Kampala",
        "category": "IT & Software",
        "type": "Full-time",
        "experience": "Mid-Level",
        "work_mode": "Hybrid",
        "salary": "UGX 2.5M - 4M",
        "salary_min": 2500000,
        "salary_max": 4000000,
        "posted_at": "2026-06-10",
        "skills": ["JavaScript", "React", "CSS"],
        "status": "Live",
        "applicants": 18,
        "description": "Build mobile-first web products for local businesses and support React interfaces.",
    },
    {
        "title": "Customer Support Associate",
        "company": "Pearl Logistics",
        "location": "Entebbe",
        "category": "Customer Service",
        "type": "Part-time",
        "experience": "Entry",
        "work_mode": "On-site",
        "salary": "UGX 900K - 1.4M",
        "salary_min": 900000,
        "salary_max": 1400000,
        "posted_at": "2026-06-08",
        "skills": ["Communication", "CRM", "Problem solving"],
        "status": "Pending",
        "applicants": 7,
        "description": "Handle customer calls, track deliveries, and resolve client issues.",
    },
    {
        "title": "Solar Installation Technician",
        "company": "Nile Energy",
        "location": "Mbarara",
        "category": "Construction",
        "type": "Contract",
        "experience": "Mid-Level",
        "work_mode": "On-site",
        "salary": "UGX 120K / day",
        "salary_min": 2400000,
        "salary_max": 3200000,
        "posted_at": "2026-06-06",
        "skills": ["Electrical wiring", "Solar panels", "Field service"],
        "status": "Live",
        "applicants": 24,
        "description": "Install and maintain solar home systems for residential and SME customers.",
    },
]

REPORTS = [
    "Employer verification request: Pearl Logistics",
    "Duplicate listing flagged: Sales Agent",
    "Applicant complaint awaiting review",
]


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "JobLink UG API", "database": str(DB_PATH.name)}


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "JobLink UG API is running",
        "docs": "/docs",
        "health": "/health",
        "jobs": "/jobs",
    }


@app.get("/jobs", response_model=list[Job])
def list_jobs(
    search: str | None = None,
    location: str | None = None,
    category: str | None = None,
    job_type: str | None = Query(default=None, alias="job_type"),
    experience: str | None = None,
    work_mode: str | None = None,
    status: JobStatus | Literal["all"] = "Live",
    salary_min: int | None = None,
    salary_max: int | None = None,
    sort: Literal["newest", "salary_high", "salary_low"] = "newest",
) -> list[Job]:
    clauses = []
    params: list[str | int] = []

    if status != "all":
        clauses.append("status = ?")
        params.append(status)

    if search:
        clauses.append(
            "(lower(title || ' ' || company || ' ' || location || ' ' || category || ' ' || type || ' ' || experience || ' ' || work_mode || ' ' || skills) LIKE ?)"
        )
        params.append(f"%{search.lower()}%")

    if location:
        clauses.append("lower(location) = ?")
        params.append(location.lower())

    if category:
        clauses.append("lower(category) = ?")
        params.append(category.lower())

    if job_type:
        clauses.append("lower(type) = ?")
        params.append(job_type.lower())

    if experience:
        clauses.append("lower(experience) = ?")
        params.append(experience.lower())

    if work_mode:
        clauses.append("lower(work_mode) = ?")
        params.append(work_mode.lower())

    if salary_min is not None:
        clauses.append("salary_max >= ?")
        params.append(salary_min)

    if salary_max is not None:
        clauses.append("salary_min <= ?")
        params.append(salary_max)

    order_by = {
        "newest": "posted_at DESC",
        "salary_high": "salary_max DESC",
        "salary_low": "salary_min ASC",
    }[sort]

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with connect() as db:
        rows = db.execute(f"SELECT * FROM jobs {where} ORDER BY {order_by}", params).fetchall()
    return [job_from_row(row) for row in rows]


@app.get("/jobs/{job_id}", response_model=Job)
def get_job(job_id: str) -> Job:
    return find_job(job_id)


@app.post("/jobs", response_model=Job, status_code=201)
def create_job(payload: JobCreate) -> Job:
    with connect() as db:
        cursor = db.execute(
            """
            INSERT INTO jobs (
                title, company, location, category, type, experience, work_mode,
                salary, salary_min, salary_max, posted_at, skills, description, status, applicants
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', 0)
            """,
            job_values(payload),
        )
        db.commit()
        return find_job(str(cursor.lastrowid))


@app.patch("/jobs/{job_id}/status", response_model=Job)
def update_job_status(job_id: str, status: JobStatus) -> Job:
    find_job(job_id)
    with connect() as db:
        db.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
        db.commit()
    return find_job(job_id)


@app.patch("/jobs/{job_id}/approve", response_model=Job)
def approve_job(job_id: str) -> Job:
    return update_job_status(job_id, "Live")


@app.delete("/jobs/{job_id}", status_code=204)
def delete_job(job_id: str) -> None:
    find_job(job_id)
    with connect() as db:
        db.execute("DELETE FROM applications WHERE job_id = ?", (job_id,))
        db.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        db.commit()


@app.post("/jobs/{job_id}/applications", response_model=Application, status_code=201)
def apply_for_job(job_id: str, payload: ApplicationCreate) -> Application:
    find_job(job_id)
    with connect() as db:
        cursor = db.execute(
            """
            INSERT INTO applications (job_id, applicant_name, email, cv_url, note, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
            """,
            (job_id, payload.applicant_name, payload.email, payload.cv_url, payload.note),
        )
        db.execute("UPDATE jobs SET applicants = applicants + 1 WHERE id = ?", (job_id,))
        db.commit()
        return find_application(str(cursor.lastrowid))


@app.get("/applications", response_model=list[Application])
def list_applications(status: str | None = None) -> list[Application]:
    with connect() as db:
        if status:
            rows = db.execute("SELECT * FROM applications WHERE status = ?", (status,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM applications ORDER BY id DESC").fetchall()
    return [application_from_row(row) for row in rows]


@app.patch("/applications/{application_id}/status", response_model=Application)
def update_application_status(
    application_id: str,
    status: Literal["pending", "reviewed", "accepted", "rejected"],
) -> Application:
    find_application(application_id)
    with connect() as db:
        db.execute("UPDATE applications SET status = ? WHERE id = ?", (status, application_id))
        db.commit()
    return find_application(application_id)


@app.get("/employers/listings", response_model=list[Job])
def employer_listings(company: str | None = None) -> list[Job]:
    with connect() as db:
        if company:
            rows = db.execute(
                "SELECT * FROM jobs WHERE lower(company) = ? ORDER BY posted_at DESC",
                (company.lower(),),
            ).fetchall()
        else:
            rows = db.execute("SELECT * FROM jobs ORDER BY posted_at DESC").fetchall()
    return [job_from_row(row) for row in rows]


@app.get("/admin/summary")
def admin_summary() -> dict[str, int]:
    with connect() as db:
        total_jobs = db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        active_jobs = db.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Live'").fetchone()[0]
        pending_jobs = db.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Pending'").fetchone()[0]
        total_applications = db.execute("SELECT COALESCE(SUM(applicants), 0) FROM jobs").fetchone()[0]
    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "pending_jobs": pending_jobs,
        "total_users": 1248,
        "total_applications": total_applications,
    }


@app.get("/admin/reports")
def admin_reports() -> list[dict[str, str]]:
    return [{"status": "Needs review", "message": report} for report in REPORTS]


@app.get("/categories")
def categories() -> list[str]:
    with connect() as db:
        rows = db.execute("SELECT DISTINCT category FROM jobs WHERE category != ''").fetchall()
    defaults = {"Driver", "Builder", "Cleaner", "Nurse", "Teacher"}
    return sorted({row["category"] for row in rows} | defaults)


@app.get("/locations")
def locations() -> list[str]:
    with connect() as db:
        rows = db.execute("SELECT DISTINCT location FROM jobs WHERE location != ''").fetchall()
    defaults = {"Kampala", "Wakiso", "Mpigi", "Entebbe", "Mbarara"}
    return sorted({row["location"] for row in rows} | defaults)


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                category TEXT NOT NULL,
                type TEXT NOT NULL,
                experience TEXT NOT NULL,
                work_mode TEXT NOT NULL,
                salary TEXT NOT NULL,
                salary_min INTEGER NOT NULL DEFAULT 0,
                salary_max INTEGER NOT NULL DEFAULT 0,
                posted_at TEXT NOT NULL,
                skills TEXT NOT NULL DEFAULT '[]',
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                applicants INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                applicant_name TEXT NOT NULL,
                email TEXT NOT NULL,
                cv_url TEXT,
                note TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
            """
        )
        count = db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        if count == 0:
            for job in SEED_JOBS:
                db.execute(
                    """
                    INSERT INTO jobs (
                        title, company, location, category, type, experience, work_mode,
                        salary, salary_min, salary_max, posted_at, skills, description, status, applicants
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job["title"],
                        job["company"],
                        job["location"],
                        job["category"],
                        job["type"],
                        job["experience"],
                        job["work_mode"],
                        job["salary"],
                        job["salary_min"],
                        job["salary_max"],
                        job["posted_at"],
                        json.dumps(job["skills"]),
                        job["description"],
                        job["status"],
                        job["applicants"],
                    ),
                )
        db.commit()


def find_job(job_id: str) -> Job:
    with connect() as db:
        row = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_from_row(row)


def find_application(application_id: str) -> Application:
    with connect() as db:
        row = db.execute("SELECT * FROM applications WHERE id = ?", (application_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")
    return application_from_row(row)


def job_values(job: JobBase) -> tuple:
    return (
        job.title,
        job.company,
        job.location,
        job.category,
        job.type,
        job.experience,
        job.work_mode,
        job.salary,
        job.salary_min,
        job.salary_max,
        job.posted_at.isoformat(),
        json.dumps(job.skills),
        job.description,
    )


def job_from_row(row: sqlite3.Row) -> Job:
    return Job(
        id=str(row["id"]),
        title=row["title"],
        company=row["company"],
        location=row["location"],
        category=row["category"],
        type=row["type"],
        experience=row["experience"],
        work_mode=row["work_mode"],
        salary=row["salary"],
        salary_min=row["salary_min"],
        salary_max=row["salary_max"],
        posted_at=date.fromisoformat(row["posted_at"]),
        skills=json.loads(row["skills"] or "[]"),
        description=row["description"],
        status=row["status"],
        applicants=row["applicants"],
    )


def application_from_row(row: sqlite3.Row) -> Application:
    return Application(
        id=str(row["id"]),
        job_id=str(row["job_id"]),
        applicant_name=row["applicant_name"],
        email=row["email"],
        cv_url=row["cv_url"],
        note=row["note"],
        status=row["status"],
    )
