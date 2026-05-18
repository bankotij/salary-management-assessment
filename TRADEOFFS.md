# Tradeoffs

Explicit decisions made for speed, clarity, and assessment fit.

## SQLite for persistence

**Chosen:** file-based SQLite (`sqlite:///./salary.db`).

**Why:** zero external services for reviewers; fast local setup; adequate for 10k rows and demo queries.

**Cost:** limited concurrent write scalability; not ideal for multi-instance production without migration to PostgreSQL/MySQL.

## Modular monolith over microservices

**Chosen:** one FastAPI application with internal layers.

**Why:** shared transactions, simpler deployment, faster TDD loop, matches team-size and problem scale.

**Cost:** cannot scale API and insights independently without later extraction.

## FastAPI + React

**Chosen:** FastAPI (Python) backend, React + Vite frontend.

**Why:** strong typing (Pydantic + TypeScript), automatic OpenAPI docs, familiar HR-facing SPA patterns, fast dev feedback (`--reload`, Vite HMR).

**Cost:** two runtimes in local dev; no server-side rendering.

## SQL aggregates for salary insights

**Chosen:** `SalaryInsightsService` runs `COUNT` / `MIN` / `MAX` / `AVG` in the database.

**Why:** correct and efficient for 10k+ rows; avoids loading entire table into application memory.

**Cost:** insight logic is SQL-centric; complex analytics would need more queries or a warehouse.

## Bulk batched seed inserts

**Chosen:** `BULK_INSERT_BATCH_SIZE = 500` in `scripts/seed_employees.py`.

**Why:** seeds 10,000 employees in seconds on a laptop.

**Cost:** less granular error reporting per row; acceptable for synthetic data.

## Simple React state (no React Query / Redux)

**Chosen:** `useState` / `useEffect` in page components.

**Why:** few screens, straightforward refresh-after-mutation pattern, less boilerplate for assessors to read.

**Cost:** no automatic cache invalidation, deduplication, or optimistic updates — acceptable for this UI size.

## No authentication

**Chosen:** open API and UI on localhost.

**Why:** assessment scope is salary management functionality, not an identity platform.

**Cost:** not production-ready without authn/authz, HTTPS, and tenant isolation.

## In-page tabs instead of React Router

**Chosen:** `App.tsx` toggles Employees vs Salary Insights.

**Why:** single assessment page, simpler demo path.

**Cost:** no shareable URLs per section (`react-router-dom` is in `package.json` but unused).

## Test-heavy backend, build-only frontend

**Chosen:** comprehensive pytest; frontend verified via `tsc` + Vite build and manual demo.

**Why:** time budget and highest risk in business rules and SQL.

**Cost:** UI regressions rely on manual checks unless E2E tests are added later.
