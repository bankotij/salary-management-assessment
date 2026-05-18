"""Employee HTTP API behavior — RED until routes and schemas are wired."""

from __future__ import annotations

from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    Base.metadata.drop_all(bind=engine)


def _employee_json(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "full_name": "Ada Lovelace",
        "job_title": "Engineer",
        "country": "UK",
        "salary": 120_000,
        "department": "R&D",
        "employment_type": "full_time",
        "hire_date": "2020-01-15",
    }
    payload.update(overrides)
    return payload


def test_post_employees_creates_employee(client: TestClient) -> None:
    response = client.post("/employees", json=_employee_json())

    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["full_name"] == "Ada Lovelace"
    assert body["job_title"] == "Engineer"
    assert body["country"] == "UK"
    assert body["salary"] == 120_000


def test_post_employees_rejects_invalid_salary(client: TestClient) -> None:
    response = client.post("/employees", json=_employee_json(salary=0))

    assert response.status_code in (400, 422)


def test_get_employee_by_id(client: TestClient) -> None:
    created = client.post("/employees", json=_employee_json()).json()
    response = client.get(f"/employees/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["full_name"] == "Ada Lovelace"


def test_get_employee_by_id_returns_404_when_missing(client: TestClient) -> None:
    response = client.get("/employees/999999")

    assert response.status_code == 404


def test_get_employees_paginated(client: TestClient) -> None:
    for i in range(5):
        client.post(
            "/employees",
            json=_employee_json(full_name=f"Employee {i}", salary=50_000 + i),
        )

    response = client.get("/employees", params={"page": 1, "page_size": 2})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2
    assert body["page"] == 1
    assert body["page_size"] == 2


def test_get_employees_filters_by_country(client: TestClient) -> None:
    client.post("/employees", json=_employee_json(full_name="India One", country="India"))
    client.post("/employees", json=_employee_json(full_name="India Two", country="India"))
    client.post(
        "/employees",
        json=_employee_json(full_name="UK One", country="UK", salary=90_000),
    )

    response = client.get("/employees", params={"country": "India"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert {item["country"] for item in body["items"]} == {"India"}


def test_get_employees_filters_by_job_title(client: TestClient) -> None:
    client.post("/employees", json=_employee_json(full_name="A", job_title="Engineer"))
    client.post("/employees", json=_employee_json(full_name="B", job_title="Engineer"))
    client.post(
        "/employees",
        json=_employee_json(full_name="C", job_title="Lawyer", salary=200_000),
    )

    response = client.get("/employees", params={"job_title": "Engineer"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert {item["job_title"] for item in body["items"]} == {"Engineer"}


def test_get_employees_search_partial_full_name(client: TestClient) -> None:
    client.post("/employees", json=_employee_json(full_name="Jonathan Smith"))
    client.post(
        "/employees",
        json=_employee_json(full_name="Anne Smythe", salary=80_000),
    )
    client.post(
        "/employees",
        json=_employee_json(full_name="Other Person", job_title="Clerk", salary=40_000),
    )

    response = client.get("/employees", params={"search": "smith"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["full_name"] == "Jonathan Smith"


def test_patch_employee_updates_fields(client: TestClient) -> None:
    created = client.post("/employees", json=_employee_json()).json()
    response = client.patch(
        f"/employees/{created['id']}",
        json={"job_title": "Principal Engineer", "salary": 150_000},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["job_title"] == "Principal Engineer"
    assert body["salary"] == 150_000


def test_delete_employee(client: TestClient) -> None:
    created = client.post("/employees", json=_employee_json()).json()
    response = client.delete(f"/employees/{created['id']}")

    assert response.status_code in (200, 204)


def test_get_deleted_employee_returns_404(client: TestClient) -> None:
    created = client.post("/employees", json=_employee_json()).json()
    client.delete(f"/employees/{created['id']}")
    response = client.get(f"/employees/{created['id']}")

    assert response.status_code == 404
