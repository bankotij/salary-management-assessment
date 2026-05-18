# Design Notes

## Problem framing

HR Managers need to maintain accurate salary records for large organizations and answer common compensation questions: salary spread and averages by geography, and averages for specific roles within a country. The assessment targets ~10,000 employees, so list and insight operations must remain practical on a single machine without distributed infrastructure.

## Persona: HR Manager

Primary workflows:

1. Find and update employee records (search, filter, paginate, edit, delete)
2. Add new hires
3. Review salary statistics by country and by job title within a country

The UI is a single-page application with two sections (Employees, Salary Insights) rather than a multi-module enterprise portal.

## Architecture: modular monolith

One deployable backend process and one frontend SPA. Internal boundaries are **layers and modules**, not network services:

```
HTTP (FastAPI routers)
    → services (business rules, validation orchestration)
        → repositories (SQLAlchemy queries)
            → SQLite
```

### Why not microservices

For this scope, microservices would add operational cost (deployment, tracing, versioning) without solving a demonstrated scaling bottleneck. Employee CRUD and insights share the same database and transactional context; keeping them in one codebase preserves consistency and speeds iteration.

## Backend layers

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **API** | `app/api/employees.py`, `app/api/insights.py` | HTTP mapping, status codes, dependency injection (`get_db`) |
| **Service** | `app/services/employee_service.py`, `employee_validation.py`, `salary_insights_service.py` | Business rules, validation, orchestration |
| **Repository** | `app/repositories/employee_repository.py` | Query construction, pagination, filters |
| **Model** | `app/models.py` | SQLAlchemy `Employee` table + indexes on `country`, `job_title`, `full_name` |

**Schemas** (`app/schemas.py`): Pydantic request/response DTOs separate from ORM models.

**Configuration** (`app/core/config.py`): `database_url`, CORS origins via `pydantic-settings`.

## Frontend structure

```
frontend/src/
├── api/           # client.ts, employees.ts, insights.ts
├── components/    # Layout, EmployeeTable, EmployeeForm, SalaryInsights
├── pages/         # EmployeesPage
├── types.ts       # shared TypeScript interfaces
└── App.tsx        # tab shell: Employees | Salary Insights
```

State is local React state (`useState` / `useEffect` / `useCallback`); no Redux or React Query. Mutations refresh the current employee list while preserving applied filters and page when possible.

## Data model

`Employee` fields:

| Field | Notes |
|-------|-------|
| `id` | Auto-increment PK |
| `full_name`, `job_title`, `country` | Required; indexed for filter/search |
| `salary` | Positive integer (USD-style whole numbers in seed/UI) |
| `department`, `employment_type`, `hire_date` | Optional |
| `created_at`, `updated_at` | Audit timestamps |

## Validation approach

- **Server:** `employee_validation.py` enforces required fields, positive salary, and consistent rules for create/update. Failures raise `EmployeeValidationError` → HTTP 400 with structured `detail`.
- **Client:** `EmployeeForm.tsx` mirrors key rules (required name/title/country, salary > 0) before calling the API.
- **Insights:** empty populations return `employee_count: 0` with null aggregates rather than errors.

## Testing approach

Backend tests (~59) follow TDD-style layering:

| Area | Example files |
|------|----------------|
| Validation | `tests/test_employee_validation.py` |
| Repository | `tests/test_employee_repository.py` |
| Service | `tests/test_employee_service.py` |
| Employee API | `tests/test_employee_api.py` (httpx + in-memory SQLite, `StaticPool`) |
| Insights service/API | `tests/test_salary_insights_service.py`, `tests/test_salary_insights_api.py` |
| Seed | `tests/test_seed_employees.py` |

API tests override `get_db` with a per-test session so routes do not depend on route-level table creation.

Frontend: `npm run build` (TypeScript + Vite); no separate E2E suite in this submission.

## Performance considerations

- **Pagination** on `GET /employees` avoids loading 10k rows into memory.
- **Indexes** on filter/search columns.
- **Insights** computed with SQL `COUNT`, `MIN`, `MAX`, `AVG` in `SalaryInsightsService` — not by fetching all employees into Python.
- **Seed script** inserts in batches of 500 (`BULK_INSERT_BATCH_SIZE`) to reduce ORM overhead.
- **SQLite** is sufficient for local assessment/demo; production would likely move to PostgreSQL with connection pooling.

## Known limitations / future improvements

- No authentication or role-based access control
- No audit log of who changed salaries
- No CSV import/export
- No charting library (metrics shown as cards)
- Single-region currency formatting (USD `Intl.NumberFormat` in UI)
- `react-router-dom` dependency unused; could add deep links or remove dependency
- Deployment, observability, and backup strategy not included (see planned deployment step)
