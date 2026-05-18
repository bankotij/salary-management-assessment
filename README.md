# Salary Management Tool

Incubyte **Software Craftsperson III** assessment project: a salary management application for HR Managers working with large employee populations (~10,000 records).

The system provides employee CRUD, searchable paginated lists, and SQL-backed salary insights (country and job-title aggregates). It is implemented as a **modular monolith** (FastAPI + SQLite backend, React + Vite frontend) with test-driven development on the server.

## Tech stack

| Layer | Technologies |
|-------|----------------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2, SQLite, Pydantic v2, pytest, httpx |
| Frontend | React 19, TypeScript, Vite 6, native `fetch` API client |
| Data | SQLite file (`backend/salary.db`), bulk seed script |

## Features

- **Employees:** create, read, update, delete via REST API and React UI
- **List & filters:** search by name, filter by `country` and `job_title`, paginated results (default page size 20 in UI)
- **Salary insights:** min / max / average salary by country; same metrics for a job title within a country (SQL aggregates, not in-memory scans)
- **Seed data:** deterministic bulk insert of 10,000 employees from name list files

## Repository layout

```
Assignment/
  backend/     FastAPI app, tests, seed script
  frontend/    React SPA
  README.md, DESIGN_NOTES.md, TRADEOFFS.md, AI_USAGE.md, DEMO_SCRIPT.md
```

## Backend setup

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

The API uses SQLite at `backend/salary.db` by default (`DATABASE_URL=sqlite:///./salary.db`). Tables are created on application startup.

Optional: copy and adjust environment variables (see `app/core/config.py`):

```bash
# Example .env in backend/ (optional)
DATABASE_URL=sqlite:///./salary.db
```

## Run the backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

- API base URL: `http://localhost:8000`
- Health check: `GET http://localhost:8000/health`
- OpenAPI docs: `http://localhost:8000/docs`

CORS allows `http://localhost:5173` (Vite dev server) by default.

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env
```

`.env` (from `.env.example`):

```
VITE_API_BASE_URL=http://localhost:8000
```

## Run the frontend

```bash
cd frontend
npm run dev
```

- UI: `http://localhost:5173`
- Tabs: **Employees** (CRUD + list) and **Salary Insights**

Production build:

```bash
cd frontend
npm run build
```

## Running tests

**Backend** (59 tests, from `backend/` with venv active):

```bash
cd backend
source .venv/bin/activate
pytest -q
```

**Frontend** (typecheck + production bundle):

```bash
cd frontend
npm run build
```

Backend lint (optional): `ruff check .` from `backend/`.

## Seed 10,000 employees

With the backend venv active, from `backend/`:

```bash
python -m scripts.seed_employees --count 10000 --reset --seed 42
```

| Flag | Purpose |
|------|---------|
| `--count` | Number of rows to insert (default `10000`) |
| `--reset` | Delete existing employees before seeding |
| `--seed` | Optional RNG seed for reproducible data |

Seeded values use countries such as `US`, `UK`, `India`, `Canada`, `Germany`, `Australia` and job titles such as `Engineer`, `Manager`, `Analyst` (see `scripts/seed_employees.py`).

## Local demo flow

1. Start API: `uvicorn app.main:app --reload` (in `backend/`)
2. Seed data: `python -m scripts.seed_employees --count 10000 --reset --seed 42`
3. Start UI: `npm run dev` (in `frontend/`)
4. **Employees tab:** browse list; use Search / Country / Job title + **Apply Filters**; paginate
5. **Add employee:** fill form, submit; confirm row appears
6. **Edit / Delete:** row actions; delete asks for confirmation
7. **Salary Insights tab:** try country `US` or `India`; for job title insights use e.g. country `US`, job title `Engineer`
8. Verify tests: `pytest -q` and `npm run build`

See [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) for a video recording checklist.

## API endpoints (summary)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness |
| `POST` | `/employees` | Create employee |
| `GET` | `/employees` | List with `country`, `job_title`, `search`, `page`, `page_size` |
| `GET` | `/employees/{employee_id}` | Get one |
| `PATCH` | `/employees/{employee_id}` | Partial update |
| `DELETE` | `/employees/{employee_id}` | Delete (204) |
| `GET` | `/insights/countries/{country}/salary` | Country salary aggregates |
| `GET` | `/insights/countries/{country}/job-titles/{job_title}/salary` | Job-title aggregates in country |

Interactive details: `http://localhost:8000/docs`.

## Notes for reviewers

- **Scope:** salary management for HR; authentication and multi-tenant access control are intentionally out of scope.
- **Architecture & tradeoffs:** [DESIGN_NOTES.md](./DESIGN_NOTES.md), [TRADEOFFS.md](./TRADEOFFS.md)
- **AI disclosure:** [AI_USAGE.md](./AI_USAGE.md)
- **Demo checklist:** [DEMO_SCRIPT.md](./DEMO_SCRIPT.md)
- **Tests:** backend behavior is specified with pytest (unit + API); frontend relies on TypeScript compile and manual/demo verification.
- **Dependencies:** `react-router-dom` is listed in `frontend/package.json` but the app uses in-page tabs rather than URL routing, to keep the UI simple for this assessment.

## Related documents

- [DESIGN_NOTES.md](./DESIGN_NOTES.md) — architecture and engineering decisions
- [TRADEOFFS.md](./TRADEOFFS.md) — explicit tradeoffs
- [AI_USAGE.md](./AI_USAGE.md) — how AI tools were used
- [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) — short demo script for screen recording
