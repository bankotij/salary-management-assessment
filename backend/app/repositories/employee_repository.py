"""Employee persistence."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import Employee


class EmployeeRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, data: dict[str, Any]) -> Employee:
        hire = data.get("hire_date")
        if hire is not None and not isinstance(hire, date):
            raise TypeError("hire_date must be a date or None")

        employee = Employee(
            full_name=str(data["full_name"]),
            job_title=str(data["job_title"]),
            country=str(data["country"]),
            salary=int(data["salary"]),
            department=self._optional_str(data.get("department")),
            employment_type=self._optional_str(data.get("employment_type")),
            hire_date=hire if isinstance(hire, date) else None,
        )
        self._db.add(employee)
        self._db.flush()
        self._db.refresh(employee)
        return employee

    def get_by_id(self, employee_id: int) -> Employee | None:
        return self._db.get(Employee, employee_id)

    def list_employees(
        self,
        *,
        country: str | None = None,
        job_title: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Employee], int]:
        stmt: Select[tuple[Employee]] = select(Employee)
        stmt = self._apply_filters(stmt, country=country, job_title=job_title, search=search)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int(self._db.scalar(count_stmt) or 0)

        safe_page = max(page, 1)
        safe_size = max(page_size, 1)
        offset = (safe_page - 1) * safe_size
        page_stmt = stmt.order_by(Employee.id).offset(offset).limit(safe_size)
        rows = list(self._db.scalars(page_stmt).all())
        return rows, total

    def update(self, employee_id: int, data: dict[str, Any]) -> Employee | None:
        employee = self.get_by_id(employee_id)
        if employee is None:
            return None

        for key, value in data.items():
            if not hasattr(Employee, key):
                continue
            if key in {"id", "created_at"}:
                continue
            if key == "hire_date" and value is not None and not isinstance(value, date):
                raise TypeError("hire_date must be a date or None")
            setattr(employee, key, value)

        employee.updated_at = datetime.now()
        self._db.flush()
        self._db.refresh(employee)
        return employee

    def delete(self, employee_id: int) -> bool:
        employee = self.get_by_id(employee_id)
        if employee is None:
            return False
        self._db.delete(employee)
        self._db.flush()
        return True

    @staticmethod
    def _optional_str(value: object) -> str | None:
        if value is None:
            return None
        return str(value)

    @staticmethod
    def _apply_filters(
        stmt: Select[tuple[Employee]],
        *,
        country: str | None,
        job_title: str | None,
        search: str | None,
    ) -> Select[tuple[Employee]]:
        if country is not None:
            stmt = stmt.where(Employee.country == country)
        if job_title is not None:
            stmt = stmt.where(Employee.job_title == job_title)
        if search is not None and search.strip():
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(Employee.full_name.ilike(pattern))
        return stmt
