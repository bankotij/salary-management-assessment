"""Employee business logic."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.services.employee_validation import validate_employee_input


class EmployeeService:
    def __init__(self, db: Session) -> None:
        self._repo = EmployeeRepository(db)

    def create_employee(self, data: dict[str, Any]) -> Employee:
        validate_employee_input(data)
        return self._repo.create(data)

    def get_employee(self, employee_id: int) -> Employee | None:
        return self._repo.get_by_id(employee_id)

    def list_employees(
        self,
        *,
        country: str | None = None,
        job_title: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Employee], int]:
        return self._repo.list_employees(
            country=country,
            job_title=job_title,
            search=search,
            page=page,
            page_size=page_size,
        )

    def update_employee(self, employee_id: int, data: dict[str, Any]) -> Employee | None:
        existing = self._repo.get_by_id(employee_id)
        if existing is None:
            return None

        merged: dict[str, Any] = {
            "full_name": data.get("full_name", existing.full_name),
            "job_title": data.get("job_title", existing.job_title),
            "country": data.get("country", existing.country),
            "salary": data.get("salary", existing.salary),
        }
        if self._touches_validated_fields(data):
            validate_employee_input(merged)

        return self._repo.update(employee_id, data)

    def delete_employee(self, employee_id: int) -> bool:
        return self._repo.delete(employee_id)

    @staticmethod
    def _touches_validated_fields(data: dict[str, Any]) -> bool:
        return bool(
            set(data.keys()) & {"full_name", "job_title", "country", "salary"}
        )
