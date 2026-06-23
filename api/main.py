import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Literal

import jwt
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "joblink.db"
JWT_SECRET = os.getenv("JWT_SECRET", "local-development-secret-change-before-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_HOURS = 12

Role = Literal["seeker", "employer", "admin"]
JobStatus = Literal["Live", "Pending", "Closed"]
ApplicationStatus = Literal["pending", "reviewed", "accepted", "rejected"]

app = FastAPI(
    title="JobLink UG API",
    description="SQLite-backed API for JobLink UG jobs, employers, applications, and admin dashboards.",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://joblink-ug.netlify.app",
        "https://wondrous-pony-c710e4.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


class UserPublic(BaseModel):
    id: str
    email: str
    role: Role


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)
    role: Literal["seeker", "employer"]


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserPublic


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
    note: str | None = None
    cv_url: str | None = None


class Application(BaseModel):
    id: str
    job_id: str
    applicant_name: str
    email: str
    cv_url: str | None = None
    note: str | None = None
    status: ApplicationStatus = "pending"


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


def optional_user(token: Annotated[str | None, Depends(oauth2_scheme)]) -> UserPublic | None:
    if not token:
        return None
    return user_from_token(token)


def require_user(token: Annotated[str | None, Depends(oauth2_scheme)]) -> UserPublic:
    if not token:
        raise HTTPException(status_code=401, detail="Sign in is required")
    return user_from_token(token)


def require_roles(*allowed_roles: Role):
    def dependency(current_user: Annotated[UserPublic, Depends(require_user)]) -> UserPublic:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="You do not have permission for this action")
        return current_user

    return dependency


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "JobLink UG API is running",
        "docs": "/docs",
        "health": "/health",
        "jobs": "/jobs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "JobLink UG API", "database": DB_PATH.name}


@app.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest) -> TokenResponse:
    email = normalise_email(payload.email)
    validate_email(email)

    with connect() as db:
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="An account with this email already exists")

        cursor = db.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
            (email, hash_password(payload.password), payload.role),
        )
        db.commit()
        user = UserPublic(id=str(cursor.lastrowid), email=email, role=payload.role)
    return token_response(user)


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    email = normalise_email(payload.email)
    with connect() as db:
        row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if not row or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return token_response(user_from_row(row))


@app.get("/auth/me", response_model=UserPublic)
def auth_me(current_user: Annotated[UserPublic, Depends(require_user)]) -> UserPublic:
    return current_user


@app.get("/jobs", response_model=list[Job])
def list_jobs(
    search: str | None = None,
    location: str | None = None,
    category: str | None = None,
    job_type: str | None = Query(default=None, alias="job_type"),
    experience: str | None = None,
    work_mode: str | None = None,
    status_filter: JobStatus | Literal["all"] = Query(default="Live", alias="status"),
    salary_min: int | None = None,
    salary_max: int | None = None,
    sort: Literal["newest", "salary_high", "salary_low"] = "newest",
    current_user: Annotated[UserPublic | None, Depends(optional_user)] = None,
) -> list[Job]:
    if status_filter != "Live" and (not current_user or current_user.role != "admin"):
        raise HTTPException(status_code=403, detail="Only admins can view non-public jobs")

    clauses = []
    params: list[str | int] = []

    if status_filter != "all":
        clauses.append("status = ?")
        params.append(status_filter)

    if search:
        clauses.append(
            "lower(title || ' ' || company || ' ' || location || ' ' || category || ' ' || type || ' ' || experience || ' ' || work_mode || ' ' || skills) LIKE ?"
        )
        params.append(f"%{search.lower()}%")

    for column, value in {
        "location": location,
        "category": category,
        "type": job_type,
        "experience": experience,
        "work_mode": work_mode,
    }.items():
        if value:
            clauses.append(f"lower({column}) = ?")
            params.append(value.lower())

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
def get_job(
    job_id: str,
    current_user: Annotated[UserPublic | None, Depends(optional_user)] = None,
) -> Job:
    job = find_job(job_id)
    if job.status != "Live" and (not current_user or current_user.role != "admin"):
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/jobs", response_model=Job, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    current_user: Annotated[UserPublic, Depends(require_roles("employer", "admin"))],
) -> Job:
    with connect() as db:
        cursor = db.execute(
            """
            INSERT INTO jobs (
                title, company, location, category, type, experience, work_mode,
                salary, salary_min, salary_max, posted_at, skills, description,
                status, applicants, employer_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', 0, ?)
            """,
            (*job_values(payload), current_user.id),
        )
        db.commit()
    return find_job(str(cursor.lastrowid))


@app.patch("/jobs/{job_id}/status", response_model=Job)
def update_job_status(
    job_id: str,
    current_user: Annotated[UserPublic, Depends(require_roles("admin"))],
    status_value: JobStatus = Query(alias="status"),
) -> Job:
    find_job(job_id)
    with connect() as db:
        db.execute("UPDATE jobs SET status = ? WHERE id = ?", (status_value, job_id))
        db.commit()
    return find_job(job_id)


@app.patch("/jobs/{job_id}/approve", response_model=Job)
def approve_job(
    job_id: str,
    current_user: Annotated[UserPublic, Depends(require_roles("admin"))],
) -> Job:
    with connect() as db:
        result = db.execute("UPDATE jobs SET status = 'Live' WHERE id = ?", (job_id,))
        db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return find_job(job_id)


@app.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: str,
    current_user: Annotated[UserPublic, Depends(require_roles("employer", "admin"))],
) -> None:
    job = find_job_row(job_id)
    if current_user.role != "admin" and job["employer_id"] != int(current_user.id):
        raise HTTPException(status_code=403, detail="You can only delete your own jobs")
    with connect() as db:
        db.execute("DELETE FROM applications WHERE job_id = ?", (job_id,))
        db.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        db.commit()


@app.post("/jobs/{job_id}/applications", response_model=Application, status_code=status.HTTP_201_CREATED)
def apply_for_job(
    job_id: str,
    payload: ApplicationCreate,
    current_user: Annotated[UserPublic, Depends(require_roles("seeker"))],
) -> Application:
    job = find_job(job_id)
    if job.status != "Live":
        raise HTTPException(status_code=400, detail="Applications are only open for live jobs")

    with connect() as db:
        existing = db.execute(
            "SELECT id FROM applications WHERE job_id = ? AND seeker_id = ?",
            (job_id, current_user.id),
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="You already applied for this job")

        cursor = db.execute(
            """
            INSERT INTO applications (job_id, seeker_id, applicant_name, email, cv_url, note, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
            """,
            (job_id, current_user.id, current_user.email, current_user.email, payload.cv_url, payload.note),
        )
        db.execute("UPDATE jobs SET applicants = applicants + 1 WHERE id = ?", (job_id,))
        db.commit()
    return find_application(str(cursor.lastrowid))


@app.get("/applications", response_model=list[Application])
def list_applications(
    current_user: Annotated[UserPublic, Depends(require_roles("employer", "admin", "seeker"))],
) -> list[Application]:
    with connect() as db:
        if current_user.role == "admin":
            rows = db.execute("SELECT * FROM applications ORDER BY id DESC").fetchall()
        elif current_user.role == "employer":
            rows = db.execute(
                """
                SELECT applications.* FROM applications
                JOIN jobs ON jobs.id = applications.job_id
                WHERE jobs.employer_id = ? ORDER BY applications.id DESC
                """,
                (current_user.id,),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM applications WHERE seeker_id = ? ORDER BY id DESC",
                (current_user.id,),
            ).fetchall()
    return [application_from_row(row) for row in rows]


@app.patch("/applications/{application_id}/status", response_model=Application)
def update_application_status(
    application_id: str,
    current_user: Annotated[UserPublic, Depends(require_roles("employer", "admin"))],
    status_value: ApplicationStatus = Query(alias="status"),
) -> Application:
    application = find_application_row(application_id)
    if current_user.role != "admin":
        job = find_job_row(str(application["job_id"]))
        if job["employer_id"] != int(current_user.id):
            raise HTTPException(status_code=403, detail="You can only manage applications for your jobs")

    with connect() as db:
        db.execute("UPDATE applications SET status = ? WHERE id = ?", (status_value, application_id))
        db.commit()
    return find_application(application_id)


@app.get("/employers/listings", response_model=list[Job])
def employer_listings(
    current_user: Annotated[UserPublic, Depends(require_roles("employer", "admin"))],
) -> list[Job]:
    with connect() as db:
        if current_user.role == "admin":
            rows = db.execute("SELECT * FROM jobs ORDER BY posted_at DESC").fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM jobs WHERE employer_id = ? ORDER BY posted_at DESC",
                (current_user.id,),
            ).fetchall()
    return [job_from_row(row) for row in rows]


@app.get("/admin/summary")
def admin_summary(
    current_user: Annotated[UserPublic, Depends(require_roles("admin"))],
) -> dict[str, int]:
    with connect() as db:
        total_jobs = db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        active_jobs = db.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Live'").fetchone()[0]
        pending_jobs = db.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Pending'").fetchone()[0]
        total_applications = db.execute("SELECT COALESCE(SUM(applicants), 0) FROM jobs").fetchone()[0]
        total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "pending_jobs": pending_jobs,
        "total_users": total_users,
        "total_applications": total_applications,
    }


@app.get("/admin/reports")
def admin_reports(
    current_user: Annotated[UserPublic, Depends(require_roles("admin"))],
) -> list[dict[str, str]]:
    return [{"status": "Needs review", "message": report} for report in REPORTS]


@app.get("/categories")
def categories() -> list[str]:
    with connect() as db:
        rows = db.execute("SELECT DISTINCT category FROM jobs WHERE category != ''").fetchall()
    return sorted({row["category"] for row in rows} | {"Driver", "Builder", "Cleaner", "Nurse", "Teacher"})


@app.get("/locations")
def locations() -> list[str]:
    with connect() as db:
        rows = db.execute("SELECT DISTINCT location FROM jobs WHERE location != ''").fetchall()
    return sorted({row["location"] for row in rows} | {"Kampala", "Wakiso", "Mpigi", "Entebbe", "Mbarara"})


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db() -> None:
    with connect() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('seeker', 'employer', 'admin')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
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
                applicants INTEGER NOT NULL DEFAULT 0,
                employer_id INTEGER
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                seeker_id INTEGER,
                applicant_name TEXT NOT NULL,
                email TEXT NOT NULL,
                cv_url TEXT,
                note TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id),
                FOREIGN KEY (seeker_id) REFERENCES users(id)
            )
            """
        )
        ensure_column(db, "jobs", "employer_id", "INTEGER")
        ensure_column(db, "applications", "seeker_id", "INTEGER")

        count = db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        if count == 0:
            for job in SEED_JOBS:
                db.execute(
                    """
                    INSERT INTO jobs (
                        title, company, location, category, type, experience, work_mode,
                        salary, salary_min, salary_max, posted_at, skills, description, status, applicants
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job["title"], job["company"], job["location"], job["category"], job["type"],
                        job["experience"], job["work_mode"], job["salary"], job["salary_min"],
                        job["salary_max"], job["posted_at"], json.dumps(job["skills"]),
                        job["description"], job["status"], job["applicants"],
                    ),
                )
        seed_admin_from_env(db)
        db.commit()


def ensure_column(db: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row["name"] for row in db.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in columns:
        db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def seed_admin_from_env(db: sqlite3.Connection) -> None:
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    if not email or not password:
        return

    email = normalise_email(email)
    existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if not existing:
        db.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, 'admin')",
            (email, hash_password(password)),
        )


def user_from_token(token: str) -> UserPublic:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = str(payload.get("sub", ""))
    except jwt.PyJWTError as error:
        raise HTTPException(status_code=401, detail="Invalid or expired sign-in token") from error

    with connect() as db:
        row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Account not found")
    return user_from_row(row)


def token_response(user: UserPublic) -> TokenResponse:
    expires_at = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRES_HOURS)
    token = jwt.encode(
        {"sub": user.id, "role": user.role, "exp": expires_at},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    return TokenResponse(access_token=token, user=user)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310000)
    return f"{base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_password(password: str, stored_value: str) -> bool:
    try:
        salt_text, digest_text = stored_value.split("$", maxsplit=1)
        salt = base64.b64decode(salt_text)
        expected = base64.b64decode(digest_text)
    except (ValueError, base64.binascii.Error):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310000)
    return hmac.compare_digest(actual, expected)


def normalise_email(value: str) -> str:
    return value.strip().lower()


def validate_email(email: str) -> None:
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise HTTPException(status_code=422, detail="Enter a valid email address")


def find_job(job_id: str) -> Job:
    return job_from_row(find_job_row(job_id))


def find_job_row(job_id: str) -> sqlite3.Row:
    with connect() as db:
        row = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return row


def find_application(application_id: str) -> Application:
    return application_from_row(find_application_row(application_id))


def find_application_row(application_id: str) -> sqlite3.Row:
    with connect() as db:
        row = db.execute("SELECT * FROM applications WHERE id = ?", (application_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")
    return row


def job_values(job: JobBase) -> tuple:
    return (
        job.title, job.company, job.location, job.category, job.type, job.experience,
        job.work_mode, job.salary, job.salary_min, job.salary_max, job.posted_at.isoformat(),
        json.dumps(job.skills), job.description,
    )


def user_from_row(row: sqlite3.Row) -> UserPublic:
    return UserPublic(id=str(row["id"]), email=row["email"], role=row["role"])


def job_from_row(row: sqlite3.Row) -> Job:
    return Job(
        id=str(row["id"]), title=row["title"], company=row["company"],
        location=row["location"], category=row["category"], type=row["type"],
        experience=row["experience"], work_mode=row["work_mode"], salary=row["salary"],
        salary_min=row["salary_min"], salary_max=row["salary_max"],
        posted_at=date.fromisoformat(row["posted_at"]), skills=json.loads(row["skills"] or "[]"),
        description=row["description"], status=row["status"], applicants=row["applicants"],
    )


def application_from_row(row: sqlite3.Row) -> Application:
    return Application(
        id=str(row["id"]), job_id=str(row["job_id"]), applicant_name=row["applicant_name"],
        email=row["email"], cv_url=row["cv_url"], note=row["note"], status=row["status"],
    )
