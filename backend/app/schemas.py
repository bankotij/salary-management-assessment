"""Pydantic request and response schemas."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class EmployeeCreate(BaseModel):
    full_name: str
    job_title: str
    country: str
    salary: int
    department: str | None = None
    employment_type: str | None = None
    hire_date: date | None = None


class EmployeeUpdate(BaseModel):
    full_name: str | None = None
    job_title: str | None = None
    country: str | None = None
    salary: int | None = None
    department: str | None = None
    employment_type: str | None = None
    hire_date: date | None = None


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    job_title: str
    country: str
    salary: int
    department: str | None
    employment_type: str | None
    hire_date: date | None
    created_at: datetime
    updated_at: datetime


class EmployeeListResponse(BaseModel):
    items: list[EmployeeResponse]
    total: int
    page: int
    page_size: int

class CountrySalaryInsightsResponse(BaseModel):
    country: str
    employee_count: int
    min_salary: int | None
    max_salary: int | None
    average_salary: float | None


class JobTitleSalaryInsightsResponse(BaseModel):
    country: str
    job_title: str
    employee_count: int
    min_salary: int | None
    max_salary: int | None
    average_salary: float | None

