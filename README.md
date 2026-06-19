# JobLink UG

A static website prototype for a Uganda-focused job board serving job seekers, employers, and admins.

## Open

Double-click `index.html` or open it in your browser.

No Node.js or npm is required for the website.

## API

The project now includes a FastAPI backend prototype.

Install the API dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the API:

```powershell
uvicorn api.main:app --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

When the API is running, `script.js` automatically loads jobs from:

```text
http://127.0.0.1:8000/jobs?status=all
```

Job posting, admin approval, and job applications will also use the API. If the API is not running, the website falls back to the browser demo data so the prototype still works.

## Database

The API uses SQLite for local persistence. When the API starts, it creates:

```text
api/joblink.db
```

The database stores:

- jobs
- applications
- job statuses
- applicant counts

The API seeds starter jobs only when the jobs table is empty, so new jobs and applications stay saved after the server restarts.

## Features

- Job seekers can search jobs, filter listings, save jobs, and apply.
- Listings support keyword search, location, category, job type, experience, salary, date posted, remote/on-site, and newest sorting.
- Employers can submit new jobs and review listing status.
- Admins can view platform stats, approve pending jobs, and review reports.
- Demo data is saved in the browser with `localStorage`.

## Frontend API URL

The frontend reads the API base URL from `config.js`.

For local development:

```js
window.JOBLINK_API_URL = "http://127.0.0.1:8000";
```

After deploying the backend on Render, change `config.js` to your Render URL:

```js
window.JOBLINK_API_URL = "https://your-render-backend-url.onrender.com";
```

## Deploy

### 1. Push to GitHub

```powershell
git init
git add .
git commit -m "Prepare JobLink UG for deployment"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/joblink-ug.git
git push -u origin main
```

### 2. Deploy Backend on Render

Render can use `render.yaml`, or you can configure the service manually:

```text
Build command: pip install -r requirements.txt
Start command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

SQLite is fine for testing on Render. Before real users, move to PostgreSQL because Render free disks are not meant for reliable production database storage.

### 3. Deploy Frontend on Netlify

Netlify can use `netlify.toml`.

```text
Publish directory: .
Build command: leave empty
```

After the backend is live, update `config.js` with the Render API URL, commit, and push again.

## Before Real Users

- Move SQLite to PostgreSQL.
- Add job seeker, employer, and admin login.
- Protect admin endpoints.
- Ensure employer jobs require approval before public listing.
- Add database backups.
- Add CV upload storage.

## API Endpoints

```http
GET /health
GET /jobs
GET /jobs?search=python
GET /jobs?location=kampala
GET /jobs?category=IT%20%26%20Software
GET /jobs?job_type=full-time
GET /jobs?sort=newest
GET /jobs/{job_id}
POST /jobs
PATCH /jobs/{job_id}/approve
PATCH /jobs/{job_id}/status?status=Closed
DELETE /jobs/{job_id}
POST /jobs/{job_id}/applications
GET /applications
PATCH /applications/{application_id}/status?status=reviewed
GET /employers/listings
GET /admin/summary
GET /admin/reports
GET /categories
GET /locations
```
