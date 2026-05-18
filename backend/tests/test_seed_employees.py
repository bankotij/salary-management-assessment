"""Employee seed script behavior — RED until scripts/seed_employees.py exists."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.models import Employee
from scripts.seed_employees import (
    BULK_INSERT_BATCH_SIZE,
    generate_employee_payloads,
    insert_employees_in_batches,
    load_names,
    seed_employees,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FIRST_NAMES_FILE = DATA_DIR / "first_names.txt"
LAST_NAMES_FILE = DATA_DIR / "last_names.txt"

REQUIRED_PAYLOAD_FIELDS = {
    "full_name",
    "job_title",
    "country",
    "salary",
    "department",
    "employment_type",
    "hire_date",
}


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_load_names_reads_non_empty_lines() -> None:
    first_names = load_names(FIRST_NAMES_FILE)
    last_names = load_names(LAST_NAMES_FILE)

    assert len(first_names) >= 2
    assert len(last_names) >= 2
    assert all(name.strip() for name in first_names)
    assert all(name.strip() for name in last_names)


def test_generate_employee_payloads_builds_full_name() -> None:
    first_names = ["Ada", "Grace"]
    last_names = ["Lovelace", "Hopper"]

    payloads = generate_employee_payloads(4, first_names, last_names, random_seed=7)

    assert all(" " in payload["full_name"] for payload in payloads)
    for payload in payloads:
        first, last = payload["full_name"].split(" ", 1)
        assert first in first_names
        assert last in last_names


def test_generate_employee_payloads_returns_requested_count() -> None:
    first_names = load_names(FIRST_NAMES_FILE)
    last_names = load_names(LAST_NAMES_FILE)

    payloads = generate_employee_payloads(25, first_names, last_names, random_seed=1)

    assert len(payloads) == 25


def test_generate_employee_payloads_include_required_fields() -> None:
    payloads = generate_employee_payloads(3, ["A"], ["B"], random_seed=99)

    for payload in payloads:
        assert REQUIRED_PAYLOAD_FIELDS.issubset(payload.keys())
        assert isinstance(payload["hire_date"], date)


def test_generate_employee_payloads_salary_is_positive() -> None:
    payloads = generate_employee_payloads(10, ["A", "B"], ["C", "D"], random_seed=5)

    assert all(payload["salary"] > 0 for payload in payloads)


def test_insert_employees_in_batches_uses_add_all_not_per_row_add() -> None:
    session = MagicMock()
    payloads = [{"full_name": f"Employee {i}", "salary": 50_000 + i} for i in range(12)]

    insert_employees_in_batches(session, payloads, batch_size=5)

    assert session.add.call_count == 0
    assert session.add_all.call_count == 3
    session.add_all.assert_any_call(payloads[0:5])
    session.add_all.assert_any_call(payloads[5:10])
    session.add_all.assert_any_call(payloads[10:12])


def test_generate_employee_payloads_is_deterministic_with_seed() -> None:
    first_names = load_names(FIRST_NAMES_FILE)
    last_names = load_names(LAST_NAMES_FILE)

    first_run = generate_employee_payloads(20, first_names, last_names, random_seed=42)
    second_run = generate_employee_payloads(20, first_names, last_names, random_seed=42)

    assert first_run == second_run


def test_seed_employees_inserts_requested_count(db_session: Session) -> None:
    seed_employees(db_session, count=15, random_seed=3)
    db_session.commit()

    total = db_session.scalar(select(func.count()).select_from(Employee))
    assert total == 15


def test_seed_employees_reset_clears_existing_before_insert(db_session: Session) -> None:
    seed_employees(db_session, count=5, random_seed=1)
    db_session.commit()
    seed_employees(db_session, count=7, random_seed=2, reset=True)
    db_session.commit()

    total = db_session.scalar(select(func.count()).select_from(Employee))
    assert total == 7


def test_bulk_insert_batch_size_is_reasonable() -> None:
    assert BULK_INSERT_BATCH_SIZE >= 100
