"""Salary insights HTTP API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CountrySalaryInsightsResponse, JobTitleSalaryInsightsResponse
from app.services.salary_insights_service import SalaryInsightsService

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/countries/{country}/salary", response_model=CountrySalaryInsightsResponse)
def get_country_salary_insights(
    country: str,
    db: Session = Depends(get_db),
) -> CountrySalaryInsightsResponse:
    result = SalaryInsightsService(db).get_country_salary_insights(country)
    return CountrySalaryInsightsResponse(**result)


@router.get(
    "/countries/{country}/job-titles/{job_title}/salary",
    response_model=JobTitleSalaryInsightsResponse,
)
def get_job_title_salary_insights(
    country: str,
    job_title: str,
    db: Session = Depends(get_db),
) -> JobTitleSalaryInsightsResponse:
    result = SalaryInsightsService(db).get_job_title_salary_insights(country, job_title)
    return JobTitleSalaryInsightsResponse(**result)
