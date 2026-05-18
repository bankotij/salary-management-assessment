"""Salary insights calculations using SQL aggregates."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Employee


class SalaryInsightsService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_country_salary_insights(self, country: str) -> dict[str, Any]:
        count, min_salary, max_salary, average_salary = self._aggregate_salaries(
            Employee.country == country
        )
        return {
            "country": country,
            "employee_count": count,
            "min_salary": min_salary,
            "max_salary": max_salary,
            "average_salary": average_salary,
        }

    def get_job_title_salary_insights(self, country: str, job_title: str) -> dict[str, Any]:
        count, min_salary, max_salary, average_salary = self._aggregate_salaries(
            Employee.country == country,
            Employee.job_title == job_title,
        )
        return {
            "country": country,
            "job_title": job_title,
            "employee_count": count,
            "min_salary": min_salary,
            "max_salary": max_salary,
            "average_salary": average_salary,
        }

    def _aggregate_salaries(self, *filters: Any) -> tuple[int, int | None, int | None, float | None]:
        stmt = select(
            func.count(Employee.id),
            func.min(Employee.salary),
            func.max(Employee.salary),
            func.avg(Employee.salary),
        ).where(*filters)
        row = self._db.execute(stmt).one()
        count = int(row[0] or 0)
        if count == 0:
            return 0, None, None, None
        return (
            count,
            int(row[1]),
            int(row[2]),
            round(float(row[3]), 2),
        )
