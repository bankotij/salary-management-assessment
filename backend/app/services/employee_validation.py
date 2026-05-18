"""Employee input validation rules."""

from typing import Any

REQUIRED_TEXT_FIELDS = ("full_name", "job_title", "country")


class EmployeeValidationError(ValueError):
    """Raised when employee input fails business validation."""


def _require_non_empty_text(data: dict[str, Any], field: str) -> None:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise EmployeeValidationError(f"{field} is required")


def validate_employee_input(data: dict[str, Any]) -> None:
    """Validate required employee fields and positive salary.

    Raises:
        EmployeeValidationError: If any rule is violated.
    """
    for field in REQUIRED_TEXT_FIELDS:
        _require_non_empty_text(data, field)

    salary = data.get("salary")
    if not isinstance(salary, int) or isinstance(salary, bool) or salary <= 0:
        raise EmployeeValidationError("salary must be positive")
