.PHONY: install-backend install-frontend test-backend dev-backend dev-frontend

install-backend:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"

install-frontend:
	cd frontend && npm install

test-backend:
	cd backend && . .venv/bin/activate && pytest

dev-backend:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload

dev-frontend:
	cd frontend && npm run dev
