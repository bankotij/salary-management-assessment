"""Salary insights HTTP API behavior — RED until insights routes are wired."""

from __future__ import annotations

from collections.abc import Generator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.repositories.employee_repository import EmployeeRepository


@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_engine) -> Generator[TestClient, None, None]:
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def repository(db_session: Session) -> EmployeeRepository:
    return EmployeeRepository(db_session)


def _employee_payload(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "full_name": "Test Employee",
        "job_title": "Engineer",
        "country": "India",
        "salary": 100_000,
        "department": "Engineering",
        "employment_type": "full_time",
        "hire_date": date(2021, 3, 1),
    }
    data.update(overrides)
    return data


def _seed(repository: EmployeeRepository, db_session: Session, **overrides: object) -> None:
    repository.create(_employee_payload(**overrides))
    db_session.commit()


def test_get_country_salary_insights_returns_aggregates(
    client: TestClient,
    repository: EmployeeRepository,
    db_session: Session,
) -> None:
    _seed(repository, db_session, full_name="IN A", country="India", salary=70_000)
    _seed(repository, db_session, full_name="IN B", country="India", salary=90_000)
    _seed(repository, db_session, full_name="IN C", country="India", salary=80_000)

    response = client.get("/insights/countries/India/salary")

    assert response.status_code == 200
    body = response.json()
    assert body["country"] == "India"
    assert body["employee_count"] == 3
    assert body["min_salary"] == 70_000
    assert body["max_salary"] == 90_000
    assert body["average_salary"] == 80_000.0


def test_get_country_salary_insights_only_includes_matching_country(
    client: TestClient,
    repository: EmployeeRepository,
    db_session: Session,
) -> None:
    _seed(repository, db_session, full_name="IN One", country="India", salary=60_000)
    _seed(repository, db_session, full_name="IN Two", country="India", salary=80_000)
    _seed(repository, db_session, full_name="US One", country="US", salary=150_000)

    response = client.get("/insights/countries/India/salary")

    assert response.status_code == 200
    body = response.json()
    assert body["employee_count"] == 2
    assert body["min_salary"] == 60_000
    assert body["max_salary"] == 80_000
    assert body["average_salary"] == 70_000.0


def test_get_job_title_salary_insights_returns_aggregates(
    client: TestClient,
    repository: EmployeeRepository,
    db_session: Session,
) -> None:
    _seed(repository, db_session, full_name="IN Eng 1", country="India", job_title="Engineer", salary=60_000)
    _seed(repository, db_session, full_name="IN Eng 2", country="India", job_title="Engineer", salary=80_000)
    _seed(repository, db_session, full_name="IN Lawyer", country="India", job_title="Lawyer", salary=200_000)

    response = client.get("/insights/countries/India/job-titles/Engineer/salary")

    assert response.status_code == 200
    body = response.json()
    assert body["country"] == "India"
    assert body["job_title"] == "Engineer"
    assert body["employee_count"] == 2
    assert body["average_salary"] == 70_000.0
    assert body["min_salary"] == 60_000
    assert body["max_salary"] == 80_000


def test_get_job_title_salary_insights_only_includes_matching_employees(
    client: TestClient,
    repository: EmployeeRepository,
    db_session: Session,
) -> None:
    _seed(repository, db_session, full_name="IN Eng", country="India", job_title="Engineer", salary=95_000)
    _seed(repository, db_session, full_name="IN Analyst", country="India", job_title="Analyst", salary=75_000)
    _seed(repository, db_session, full_name="US Eng", country="US", job_title="Engineer", salary=110_000)

    response = client.get("/insights/countries/India/job-titles/Engineer/salary")

    assert response.status_code == 200
    body = response.json()
    assert body["employee_count"] == 1
    assert body["average_salary"] == 95_000.0
    assert body["min_salary"] == 95_000
    assert body["max_salary"] == 95_000


def test_get_country_salary_insights_empty_country(
    client: TestClient,
) -> None:
    response = client.get("/insights/countries/Unknown/salary")

    assert response.status_code == 200
    body = response.json()
    assert body["country"] == "Unknown"
    assert body["employee_count"] == 0
    assert body["min_salary"] is None
    assert body["max_salary"] is None
    assert body["average_salary"] is None


def test_get_country_salary_insights_rounds_average(
    client: TestClient,
    repository: EmployeeRepository,
    db_session: Session,
) -> None:
    _seed(repository, db_session, full_name="R1", country="India", salary=100_000)
    _seed(repository, db_session, full_name="R2", country="India", salary=100_001)
    _seed(repository, db_session, full_name="R3", country="India", salary=100_002)

    response = client.get("/insights/countries/India/salary")

    assert response.status_code == 200
    assert response.json()["average_salary"] == 100_001.0
