# Deployment Guide

Practical notes for running the salary management app outside local development. This assessment ships as a **modular monolith** (FastAPI + SQLite) and a **static React SPA** (Vite build). No Docker is required for review or demo.

## Overview

| Component | Default local | Deployed |
|-----------|---------------|----------|
| Backend | `uvicorn` on port 8000 | Same process behind HTTPS reverse proxy |
| Database | SQLite file in `backend/` | SQLite for demo; PostgreSQL recommended for real production |
| Frontend | Vite dev server `:5173` | Static files (`frontend/dist/`) served by CDN or nginx |

## Environment variables

### Backend (`backend/.env`)

Copy from `backend/.env.example`:

```bash
cp .env.example .env
```

| Variable | Example | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `sqlite:///./salary_management.db` | SQLAlchemy connection string |
| `BACKEND_CORS_ORIGINS` | `http://localhost:5173` | Comma-separated browser origins allowed to call the API |

**CORS:** multiple origins are supported:

```env
BACKEND_CORS_ORIGINS=https://app.example.com,https://www.example.com
```

If unset, the app defaults to `http://localhost:5173` for development.

**Database:** SQLite is appropriate for assessment, demos, and single-node deployments. For production at scale, migrate to PostgreSQL (same SQLAlchemy layer; change `DATABASE_URL` only after schema migration tooling is in place).

Default without `.env`: `sqlite:///./salary.db` (see `app/core/config.py`).

### Frontend (build-time)

Copy from `frontend/.env.example`:

```bash
cp .env.example .env.production
```

| Variable | Example | Purpose |
|----------|---------|---------|
| `VITE_API_BASE_URL` | `https://api.example.com` | Base URL for all API requests (no trailing slash) |

Vite embeds this at **build** time. Rebuild after changing:

```bash
cd frontend
npm run build
```

## Backend deployment

### 1. Install

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

For development tooling: `pip install -e ".[dev]"`.

### 2. Configure

Create `backend/.env` with `DATABASE_URL` and `BACKEND_CORS_ORIGINS` (must include the URL where the frontend is hosted).

### 3. Run

Tables are created on startup (`Base.metadata.create_all` in app lifespan).

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Production tips:

- Run behind **nginx** or similar with TLS termination.
- Use a process manager (systemd, supervisord) to restart on failure.
- Persist the SQLite file volume if using SQLite on a single host.

### 4. Seed demo / deployed database

With venv active, from `backend/`:

```bash
python -m scripts.seed_employees --count 10000 --reset --seed 42
```

Use `--reset` only when you intend to wipe existing employee rows.

## Frontend deployment

### 1. Build

```bash
cd frontend
npm ci
# Set API URL for the target environment
echo 'VITE_API_BASE_URL=https://api.example.com' > .env.production
npm run build
```

Output: `frontend/dist/` (HTML, JS, CSS).

### 2. Serve static files

Examples:

- **nginx** — `root` pointing to `frontend/dist/`, `try_files $uri /index.html;` for SPA
- **Any static host** (S3 + CloudFront, Netlify, etc.) — upload `dist/` contents

Ensure `BACKEND_CORS_ORIGINS` on the API includes the exact frontend origin (scheme + host + port).

### 3. Local production preview (optional)

```bash
cd frontend
npm run preview
```

Set `VITE_API_BASE_URL` before `npm run build`, not at preview time.

## Smoke-test checklist (after deploy)

1. **Health:** `GET {API}/health` → `{"status":"ok"}`
2. **OpenAPI:** `{API}/docs` loads
3. **List employees:** `GET {API}/employees?page=1&page_size=5` returns JSON (seed if empty)
4. **Frontend:** open deployed UI; Employees tab loads without CORS errors in browser console
5. **Filters:** apply country filter (e.g. `US` if seeded with default script)
6. **Create:** add a test employee; appears in list
7. **Insights:** Salary Insights tab — country `US`, fetch metrics
8. **Regression:** `cd backend && pytest -q` and `cd frontend && npm run build` in CI or locally before release

## Common issues

| Symptom | Likely cause |
|---------|----------------|
| CORS error in browser | `BACKEND_CORS_ORIGINS` missing frontend URL |
| API calls go to wrong host | Rebuild frontend after changing `VITE_API_BASE_URL` |
| Empty employee list | Run seed script on the same DB file as `DATABASE_URL` |
| 404 on frontend refresh | Static server not configured for SPA fallback to `index.html` |

## What is out of scope

- Authentication / authorization
- Managed Postgres migration scripts
- Container orchestration (add later if your platform requires it)

See also [README.md](./README.md) (local runbook) and [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) (recorded demo steps).
