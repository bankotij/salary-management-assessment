"""Salary insights behavior — RED until SalaryInsightsService is implemented."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.repositories.employee_repository import EmployeeRepository
from app.services.salary_insights_service import SalaryInsightsService


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


@pytest.fixture
def insights_service(db_session: Session) -> SalaryInsightsService:
    return SalaryInsightsService(db_session)


def _employee_payload(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "full_name": "Test Employee",
        "job_title": "Engineer",
        "country": "UK",
        "salary": 100_000,
        "department": "Engineering",
        "employment_type": "full_time",
        "hire_date": date(2021, 3, 1),
    }
    data.update(overrides)
    return data


def test_country_salary_insights_returns_aggregate_fields(
    repository: EmployeeRepository,
    insights_service: SalaryInsightsService,
) -> None:
    repository.create(_employee_payload(full_name="UK A", country="UK", salary=80_000))
    repository.create(_employee_payload(full_name="UK B", country="UK", salary=120_000))
    repository.create(_employee_payload(full_name="UK C", country="UK", salary=100_000))

    result = insights_service.get_country_salary_insights("UK")

    assert result["employee_count"] == 3
    assert result["min_salary"] == 80_000
    assert result["max_salary"] == 120_000
    assert result["average_salary"] == 100_000.0


def test_country_insights_only_include_matching_country(
    repository: EmployeeRepository,
    insights_service: SalaryInsightsService,
) -> None:
    repository.create(_employee_payload(full_name="India A", country="India", salary=70_000))
    repository.create(_employee_payload(full_name="India B", country="India", salary=90_000))
    repository.create(_employee_payload(full_name="US A", country="US", salary=150_000))

    result = insights_service.get_country_salary_insights("India")

    assert result["employee_count"] == 2
    assert result["min_salary"] == 70_000
    assert result["max_salary"] == 90_000
    assert result["average_salary"] == 80_000.0


def test_job_title_salary_insights_returns_average_and_count(
    repository: EmployeeRepository,
    insights_service: SalaryInsightsService,
) -> None:
    repository.create(
        _employee_payload(full_name="IN Eng 1", country="India", job_title="Engineer", salary=60_000)
    )
    repository.create(
        _employee_payload(full_name="IN Eng 2", country="India", job_title="Engineer", salary=80_000)
    )
    repository.create(
        _employee_payload(full_name="IN Lawyer", country="India", job_title="Lawyer", salary=200_000)
    )

    result = insights_service.get_job_title_salary_insights("India", "Engineer")

    assert result["employee_count"] == 2
    assert result["average_salary"] == 70_000.0


def test_job_title_insights_only_include_matching_country_and_title(
    repository: EmployeeRepository,
    insights_service: SalaryInsightsService,
) -> None:
    repository.create(
        _employee_payload(full_name="CA Eng", country="Canada", job_title="Engineer", salary=95_000)
    )
    repository.create(
        _employee_payload(full_name="CA Analyst", country="Canada", job_title="Analyst", salary=75_000)
    )
    repository.create(
        _employee_payload(full_name="US Eng", country="US", job_title="Engineer", salary=110_000)
    )

    result = insights_service.get_job_title_salary_insights("Canada", "Engineer")

    assert result["employee_count"] == 1
    assert result["average_salary"] == 95_000.0
    assert result["min_salary"] == 95_000
    assert result["max_salary"] == 95_000


def test_country_insights_empty_when_no_employees(
    insights_service: SalaryInsightsService,
) -> None:
    result = insights_service.get_country_salary_insights("Antarctica")

    assert result["employee_count"] == 0
    assert result["min_salary"] is None
    assert result["max_salary"] is None
    assert result["average_salary"] is None


def test_average_salary_rounded_to_two_decimal_places(
    repository: EmployeeRepository,
    insights_service: SalaryInsightsService,
) -> None:
    repository.create(_employee_payload(full_name="R1", country="UK", salary=100_000))
    repository.create(_employee_payload(full_name="R2", country="UK", salary=100_001))
    repository.create(_employee_payload(full_name="R3", country="UK", salary=100_002))

    result = insights_service.get_country_salary_insights("UK")

    assert result["average_salary"] == 100_001.0
