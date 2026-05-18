# Demo Script (video checklist)

Short recording (~5–8 minutes) showing end-to-end behavior. Commands assume repo root `/path/to/Assignment`.

## 1. Start backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Show: `GET http://localhost:8000/health` → `{"status":"ok"}` (browser or curl).

## 2. Seed 10,000 employees

New terminal:

```bash
cd backend
source .venv/bin/activate
python -m scripts.seed_employees --count 10000 --reset --seed 42
```

Show terminal output: `Seeded 10000 employees`.

## 3. Start frontend

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`.

## 4. Employee list

- **Employees** tab (default)
- Show table with many rows
- Set **Country** filter to `US` (or `India`) → **Apply Filters**
- Use **Search** with part of a name → **Apply Filters**
- Click **Next** / **Previous** to show pagination

## 5. Add employee

- **Add employee**
- Fill required fields (name, title, country, salary > 0)
- Submit → success message and new row visible

## 6. Edit employee

- **Edit** on a row → change salary or title → save
- Confirm updated values in table

## 7. Delete employee

- **Delete** on a row → confirm dialog → row removed

## 8. Country salary insights

- Switch to **Salary Insights** tab
- Country insights: enter `US` → **Fetch insights**
- Show cards: employee count, min, max, average salary

## 9. Job title salary insights

- Country: `US`, Job title: `Engineer` → **Fetch insights**
- Show employee count and salary metrics
- Optional: country with no matches → **No employees found**

## 10. Tests passing

```bash
cd backend && source .venv/bin/activate && pytest -q
cd frontend && npm run build
```

Show both complete successfully (59 backend tests; frontend build OK).

## Optional closing

- Briefly open `http://localhost:8000/docs` to show OpenAPI
- Mention docs: `README.md`, `DESIGN_NOTES.md`, `TRADEOFFS.md`, `AI_USAGE.md`
