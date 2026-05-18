# Salary Management Tool

Incubyte Software Craftsperson III assessment — HR salary management for large organizations.

## Status

Work in progress. See [PLAN.md](./PLAN.md) for implementation plan.

## Quick start (coming soon)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Structure

- `backend/` — FastAPI, SQLAlchemy, SQLite, tests, seed script
- `frontend/` — React + Vite + TypeScript
