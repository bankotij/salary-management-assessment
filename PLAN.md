# Salary Management Tool — Implementation Plan

## Goal

Minimal, usable salary management for ~10,000 employees. Modular monolith: FastAPI + SQLite + SQLAlchemy, React + Vite + TypeScript. TDD throughout; incremental commits per assessment commit plan.

## Persona & scope

- **Persona:** HR Manager
- **In scope:** Employee CRUD (UI + API), salary insights by country/job title, performant seeding, pagination/search, tests, docs, local run + deployment readiness
- **Out of scope:** Microservices, auth/multi-tenancy, median (unless trivial), overbuilt analytics

## Architecture (modular monolith)

```
backend/app/
  main.py          # FastAPI app, routers, lifespan
  database.py      # Engine, session, Base
  models.py        # SQLAlchemy Employee
  schemas.py       # Pydantic request/response DTOs
  core/config.py   # Settings (DB URL, CORS)
  api/             # Thin route handlers
  repositories/    # DB queries only
  services/        # Business rules, validation, insights math
frontend/src/
  api/             # Typed fetch clients
  components/      # Form, table, insights, layout
  pages/           # Employees, Insights
```

**Layers:** API -> Service -> Repository -> DB. Validation in service/domain (tested without HTTP).

## Employee domain

| Field | Notes |
|-------|--------|
| id | Auto |
| full_name, job_title, country | Required |
| salary | Positive integer (whole USD) |
| department, employment_type, hire_date | Optional product fields |
| created_at, updated_at | Audit |

**Indexes:** `country`, `job_title`.

## API (target)

| Method | Path |
|--------|------|
| GET | `/health` |
| GET | `/employees?country&job_title&search&page&page_size` |
| POST | `/employees` |
| GET | `/employees/{id}` |
| PATCH | `/employees/{id}` |
| DELETE | `/employees/{id}` |
| GET | `/insights/countries/{country}/salary` |
| GET | `/insights/countries/{country}/job-titles/{job_title}/salary` |

Insights responses include **count**, min, max, avg.

## TDD commit sequence

| # | Focus |
|---|--------|
| 1 | Project structure, tooling, skeleton |
| 2 | Failing tests: employee validation |
| 3 | Green: domain model + validation |
| 4 | Failing tests: repository/service CRUD |
| 5 | Green: employee CRUD API |
| 6 | Failing tests: salary insights calculations |
| 7 | Green: insights API |
| 8 | Failing tests: seed generation |
| 9 | Green: 10k bulk seed script |
| 10 | React employee UI |
| 11 | React insights UI |
| 12 | Integration/API tests, edge cases |
| 13 | DESIGN_NOTES, AI_USAGE, TRADEOFFS, README |
| 14 | Deployment config, demo checklist |

## Seeding strategy

- Combine `data/first_names.txt` + `data/last_names.txt` for full names
- Bulk insert in batches
- Idempotent: `--reset` flag or documented truncate + reseed

## Testing strategy

- **Unit:** validation, insights math, seed name combinator, filters
- **API:** httpx + TestClient, in-memory SQLite per test session
- Fast, deterministic, readable test names

## Performance notes (10k)

- Pagination on list endpoint (default page_size 50)
- DB indexes on filter columns
- Insights: aggregate SQL — never load all rows into Python
- Seed: batch commits (500-1000 rows per flush)

## Current status

- [x] Commit 1: structure + tooling
- [ ] Commit 2: failing validation tests

## Next TDD step

**Red:** `tests/test_employee_validation.py` — validation rules for required fields and positive salary.
**Green (commit 3):** `app/services/employee_validation.py`.
