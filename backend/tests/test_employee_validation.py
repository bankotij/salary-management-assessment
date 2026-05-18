"""Tests for employee input validation (commit 2 - RED phase)."""

import pytest

from app.services.employee_validation import (
    EmployeeValidationError,
    validate_employee_input,
)


def test_valid_employee_input_passes() -> None:
    validate_employee_input(
        {
            "full_name": "Ada Lovelace",
            "job_title": "Engineer",
            "country": "UK",
            "salary": 120_000,
        }
    )


def test_rejects_empty_full_name() -> None:
    with pytest.raises(EmployeeValidationError, match="full_name"):
        validate_employee_input(
            {
                "full_name": "   ",
                "job_title": "Engineer",
                "country": "UK",
                "salary": 50_000,
            }
        )


def test_rejects_empty_job_title() -> None:
    with pytest.raises(EmployeeValidationError, match="job_title"):
        validate_employee_input(
            {
                "full_name": "Ada Lovelace",
                "job_title": "",
                "country": "UK",
                "salary": 50_000,
            }
        )


def test_rejects_empty_country() -> None:
    with pytest.raises(EmployeeValidationError, match="country"):
        validate_employee_input(
            {
                "full_name": "Ada Lovelace",
                "job_title": "Engineer",
                "country": "  ",
                "salary": 50_000,
            }
        )


@pytest.mark.parametrize("salary", [0, -1])
def test_rejects_non_positive_salary(salary: int) -> None:
    with pytest.raises(EmployeeValidationError, match="salary"):
        validate_employee_input(
            {
                "full_name": "Ada Lovelace",
                "job_title": "Engineer",
                "country": "UK",
                "salary": salary,
            }
        )
