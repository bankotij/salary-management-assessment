import { request } from "./client";
import type { CountrySalaryInsights, JobTitleSalaryInsights } from "../types";

export function getCountrySalaryInsights(country: string): Promise<CountrySalaryInsights> {
  return request<CountrySalaryInsights>(
    `/insights/countries/${encodeURIComponent(country)}/salary`,
  );
}

export function getJobTitleSalaryInsights(
  country: string,
  jobTitle: string,
): Promise<JobTitleSalaryInsights> {
  return request<JobTitleSalaryInsights>(
    `/insights/countries/${encodeURIComponent(country)}/job-titles/${encodeURIComponent(jobTitle)}/salary`,
  );
}
