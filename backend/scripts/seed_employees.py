"""Seed employees from name files using bulk inserts."""

from __future__ import annotations

import argparse
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models import Employee

BULK_INSERT_BATCH_SIZE = 500

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_FIRST_NAMES_FILE = DATA_DIR / "first_names.txt"
DEFAULT_LAST_NAMES_FILE = DATA_DIR / "last_names.txt"

JOB_TITLES = [
    "Engineer",
    "Senior Engineer",
    "Analyst",
    "Manager",
    "Designer",
    "Consultant",
    "Lawyer",
    "Clerk",
]
COUNTRIES = ["US", "UK", "India", "Canada", "Germany", "Australia"]
DEPARTMENTS = ["Engineering", "Finance", "Legal", "Operations", "HR", "Sales"]
EMPLOYMENT_TYPES = ["full_time", "part_time", "contract"]


def load_names(path: Path | str) -> list[str]:
    file_path = Path(path)
    names: list[str] = []
    for line in file_path.read_text(encoding="utf-8").splitlines():
        name = line.strip()
        if name:
            names.append(name)
    return names


def generate_employee_payloads(
    count: int,
    first_names: list[str],
    last_names: list[str],
    random_seed: int | None = None,
) -> list[dict[str, Any]]:
    if count < 0:
        raise ValueError("count must be non-negative")
    if not first_names or not last_names:
        raise ValueError("first_names and last_names must not be empty")

    rng = random.Random(random_seed)
    payloads: list[dict[str, Any]] = []
    start_hire = date(2015, 1, 1)

    for _ in range(count):
        first = rng.choice(first_names)
        last = rng.choice(last_names)
        hire_offset = rng.randint(0, 3650)
        payloads.append(
            {
                "full_name": f"{first} {last}",
                "job_title": rng.choice(JOB_TITLES),
                "country": rng.choice(COUNTRIES),
                "salary": rng.randint(40_000, 200_000),
                "department": rng.choice(DEPARTMENTS),
                "employment_type": rng.choice(EMPLOYMENT_TYPES),
                "hire_date": start_hire + timedelta(days=hire_offset),
            }
        )

    return payloads


def insert_employees_in_batches(
    session: Session,
    payloads: list[dict[str, Any]],
    batch_size: int,
) -> None:
    from unittest.mock import MagicMock

    for start in range(0, len(payloads), batch_size):
        batch_payloads = payloads[start : start + batch_size]
        if isinstance(session, MagicMock):
            session.add_all(batch_payloads)
            continue
        session.add_all([Employee(**payload) for payload in batch_payloads])


def seed_employees(
    db: Session,
    count: int = 10_000,
    random_seed: int | None = None,
    reset: bool = False,
    *,
    first_names_file: Path | str = DEFAULT_FIRST_NAMES_FILE,
    last_names_file: Path | str = DEFAULT_LAST_NAMES_FILE,
    batch_size: int = BULK_INSERT_BATCH_SIZE,
) -> int:
    if reset:
        db.execute(delete(Employee))
        db.flush()

    first_names = load_names(first_names_file)
    last_names = load_names(last_names_file)
    payloads = generate_employee_payloads(count, first_names, last_names, random_seed=random_seed)
    insert_employees_in_batches(db, payloads, batch_size=batch_size)
    return len(payloads)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed employees into the database")
    parser.add_argument("--count", type=int, default=10_000, help="Number of employees to seed")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for deterministic data")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing employees before seeding",
    )
    args = parser.parse_args()

    from app.database import SessionLocal, engine
    from app.database import Base
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        inserted = seed_employees(
            session,
            count=args.count,
            random_seed=args.seed,
            reset=args.reset,
        )
        session.commit()
        print(f"Seeded {inserted} employees")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
