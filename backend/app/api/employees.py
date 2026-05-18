"""Employee HTTP API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import ensure_tables, get_db
from app.schemas import (
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.services.employee_service import EmployeeService
from app.services.employee_validation import EmployeeValidationError

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=EmployeeResponse)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)) -> EmployeeResponse:
    ensure_tables(db)
    service = EmployeeService(db)
    try:
        employee = service.create_employee(payload.model_dump())
        db.commit()
    except EmployeeValidationError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return EmployeeResponse.model_validate(employee)


@router.get("", response_model=EmployeeListResponse)
def list_employees(
    country: str | None = None,
    job_title: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1),
    db: Session = Depends(get_db),
) -> EmployeeListResponse:
    ensure_tables(db)
    service = EmployeeService(db)
    rows, total = service.list_employees(
        country=country,
        job_title=job_title,
        search=search,
        page=page,
        page_size=page_size,
    )
    return EmployeeListResponse(
        items=[EmployeeResponse.model_validate(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)) -> EmployeeResponse:
    ensure_tables(db)
    employee = EmployeeService(db).get_employee(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return EmployeeResponse.model_validate(employee)


@router.patch("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
) -> EmployeeResponse:
    ensure_tables(db)
    service = EmployeeService(db)
    try:
        employee = service.update_employee(
            employee_id,
            payload.model_dump(exclude_unset=True),
        )
        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")
        db.commit()
    except EmployeeValidationError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return EmployeeResponse.model_validate(employee)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)) -> Response:
    ensure_tables(db)
    service = EmployeeService(db)
    deleted = service.delete_employee(employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
