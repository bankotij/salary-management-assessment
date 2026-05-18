"""Employee service CRUD behavior — RED until service + repository + model exist."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.models import Employee
from app.services.employee_service import EmployeeService
from app.services.employee_validation import EmployeeValidationError


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
def service(db_session: Session) -> EmployeeService:
    return EmployeeService(db_session)


def _employee_payload(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "full_name": "Grace Hopper",
        "job_title": "Engineer",
        "country": "US",
        "salary": 130_000,
        "department": "Platform",
        "employment_type": "full_time",
        "hire_date": date(2019, 6, 1),
    }
    data.update(overrides)
    return data


def test_service_create_employee(service: EmployeeService, db_session: Session) -> None:
    created = service.create_employee(_employee_payload())

    assert isinstance(created, Employee)
    assert created.id is not None
    assert created.full_name == "Grace Hopper"
    db_session.refresh(created)


def test_service_get_employee_by_id(service: EmployeeService) -> None:
    created = service.create_employee(_employee_payload())
    found = service.get_employee(created.id)

    assert found is not None
    assert found.id == created.id


def test_service_list_employees_pagination(service: EmployeeService) -> None:
    for i in range(4):
        service.create_employee(
            _employee_payload(
                full_name=f"Staff {i}",
                salary=60_000 + i,
            )
        )

    page1, total = service.list_employees(page=1, page_size=2)
    page2, _ = service.list_employees(page=2, page_size=2)

    assert total == 4
    assert len(page1) == 2
    assert len(page2) == 2


def test_service_list_filters_by_country(service: EmployeeService) -> None:
    service.create_employee(_employee_payload(full_name="CA One", country="CA"))
    service.create_employee(_employee_payload(full_name="CA Two", country="CA"))
    service.create_employee(_employee_payload(full_name="IN One", country="IN", salary=70_000))

    rows, total = service.list_employees(country="CA")

    assert total == 2
    assert {r.country for r in rows} == {"CA"}


def test_service_list_filters_by_job_title(service: EmployeeService) -> None:
    service.create_employee(_employee_payload(full_name="X", job_title="Analyst"))
    service.create_employee(_employee_payload(full_name="Y", job_title="Analyst"))
    service.create_employee(_employee_payload(full_name="Z", job_title="Manager", salary=110_000))

    rows, total = service.list_employees(job_title="Analyst")

    assert total == 2
    assert {r.job_title for r in rows} == {"Analyst"}


def test_service_list_search_partial_full_name(service: EmployeeService) -> None:
    service.create_employee(_employee_payload(full_name="Maria Rodriguez"))
    service.create_employee(_employee_payload(full_name="Maria Anders", salary=95_000))
    service.create_employee(_employee_payload(full_name="Tom Lee", job_title="Clerk", salary=45_000))

    rows, total = service.list_employees(search="Rod")

    assert total == 1
    assert rows[0].full_name == "Maria Rodriguez"


def test_service_update_employee(service: EmployeeService) -> None:
    created = service.create_employee(_employee_payload())
    updated = service.update_employee(created.id, {"country": "CA", "salary": 140_000})

    assert updated is not None
    assert updated.country == "CA"
    assert updated.salary == 140_000


def test_service_delete_employee(service: EmployeeService) -> None:
    created = service.create_employee(_employee_payload())
    assert service.delete_employee(created.id) is True
    assert service.get_employee(created.id) is None


def test_service_get_employee_returns_none_when_missing(service: EmployeeService) -> None:
    assert service.get_employee(42_424) is None


def test_service_create_validates_input(service: EmployeeService) -> None:
    bad = _employee_payload(salary=0)
    with pytest.raises(EmployeeValidationError, match="salary"):
        service.create_employee(bad)
