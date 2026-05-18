"""Employee repository CRUD behavior — RED until repository + model exist."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.models import Employee
from app.repositories.employee_repository import EmployeeRepository


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


@pytest.fixture
def repository(db_session: Session) -> EmployeeRepository:
    return EmployeeRepository(db_session)


def _employee_payload(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "full_name": "Ada Lovelace",
        "job_title": "Engineer",
        "country": "UK",
        "salary": 120_000,
        "department": "R&D",
        "employment_type": "full_time",
        "hire_date": date(2020, 1, 15),
    }
    data.update(overrides)
    return data


def test_create_employee(repository: EmployeeRepository, db_session: Session) -> None:
    payload = _employee_payload()
    created = repository.create(payload)

    assert created.id is not None
    assert created.full_name == payload["full_name"]
    assert created.job_title == payload["job_title"]
    assert created.country == payload["country"]
    assert created.salary == payload["salary"]
    db_session.refresh(created)


def test_get_employee_by_id(repository: EmployeeRepository) -> None:
    created = repository.create(_employee_payload())
    found = repository.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id
    assert found.full_name == "Ada Lovelace"


def test_list_employees_with_pagination(repository: EmployeeRepository) -> None:
    for i in range(5):
        repository.create(
            _employee_payload(
                full_name=f"Employee {i}",
                salary=50_000 + i,
            )
        )

    page1, total = repository.list_employees(page=1, page_size=2)
    page3, total_again = repository.list_employees(page=3, page_size=2)

    assert total == 5
    assert total_again == 5
    assert len(page1) == 2
    assert len(page3) == 1


def test_list_filters_by_country(repository: EmployeeRepository) -> None:
    repository.create(_employee_payload(full_name="UK One", country="UK"))
    repository.create(_employee_payload(full_name="UK Two", country="UK"))
    repository.create(_employee_payload(full_name="US One", country="US", salary=90_000))

    rows, total = repository.list_employees(country="UK")

    assert total == 2
    assert {r.country for r in rows} == {"UK"}


def test_list_filters_by_job_title(repository: EmployeeRepository) -> None:
    repository.create(_employee_payload(full_name="A", job_title="Engineer"))
    repository.create(_employee_payload(full_name="B", job_title="Engineer"))
    repository.create(_employee_payload(full_name="C", job_title="Lawyer", salary=200_000))

    rows, total = repository.list_employees(job_title="Engineer")

    assert total == 2
    assert {r.job_title for r in rows} == {"Engineer"}


def test_list_search_matches_partial_full_name(repository: EmployeeRepository) -> None:
    repository.create(_employee_payload(full_name="Jonathan Smith"))
    repository.create(_employee_payload(full_name="Anne Smythe", salary=80_000))
    repository.create(_employee_payload(full_name="Other Person", job_title="Clerk", salary=40_000))

    rows, total = repository.list_employees(search="smith")

    assert total == 1
    assert rows[0].full_name == "Jonathan Smith"


def test_update_employee(repository: EmployeeRepository, db_session: Session) -> None:
    created = repository.create(_employee_payload())
    updated = repository.update(created.id, {"job_title": "Principal Engineer", "salary": 150_000})

    assert updated is not None
    assert updated.id == created.id
    assert updated.job_title == "Principal Engineer"
    assert updated.salary == 150_000
    db_session.refresh(created)
    assert created.job_title == "Principal Engineer"


def test_delete_employee(repository: EmployeeRepository) -> None:
    created = repository.create(_employee_payload())
    deleted = repository.delete(created.id)

    assert deleted is True
    assert repository.get_by_id(created.id) is None


def test_get_by_id_returns_none_when_missing(repository: EmployeeRepository) -> None:
    assert repository.get_by_id(999_999) is None
