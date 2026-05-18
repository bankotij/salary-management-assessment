import { FormEvent, useState } from "react";

import { ApiError } from "../api/client";
import {
  getCountrySalaryInsights,
  getJobTitleSalaryInsights,
} from "../api/insights";
import type { CountrySalaryInsights, JobTitleSalaryInsights } from "../types";

const salaryFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function formatSalary(value: number | null): string {
  if (value === null) {
    return "—";
  }
  return salaryFormatter.format(value);
}

function formatCount(count: number): string {
  return count.toLocaleString("en-US");
}

interface MetricItem {
  label: string;
  value: string;
}

function MetricsGrid({ items }: { items: MetricItem[] }) {
  return (
    <div className="insights-metrics" role="group">
      {items.map((item) => (
        <div key={item.label} className="insights-metric-card">
          <span className="insights-metric-card__label">{item.label}</span>
          <span className="insights-metric-card__value">{item.value}</span>
        </div>
      ))}
    </div>
  );
}

export default function SalaryInsights() {
  const [countryInput, setCountryInput] = useState("");
  const [countryLoading, setCountryLoading] = useState(false);
  const [countryError, setCountryError] = useState<string | null>(null);
  const [countryData, setCountryData] = useState<CountrySalaryInsights | null>(null);
  const [countryFetched, setCountryFetched] = useState(false);

  const [jobCountryInput, setJobCountryInput] = useState("");
  const [jobTitleInput, setJobTitleInput] = useState("");
  const [jobLoading, setJobLoading] = useState(false);
  const [jobError, setJobError] = useState<string | null>(null);
  const [jobData, setJobData] = useState<JobTitleSalaryInsights | null>(null);
  const [jobFetched, setJobFetched] = useState(false);

  async function handleCountrySubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const country = countryInput.trim();
    if (!country) {
      setCountryError("Country is required.");
      setCountryData(null);
      setCountryFetched(false);
      return;
    }

    setCountryLoading(true);
    setCountryError(null);
    setCountryData(null);
    setCountryFetched(false);

    try {
      const data = await getCountrySalaryInsights(country);
      setCountryData(data);
      setCountryFetched(true);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Failed to load country salary insights.";
      setCountryError(message);
      setCountryFetched(true);
    } finally {
      setCountryLoading(false);
    }
  }

  async function handleJobTitleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const country = jobCountryInput.trim();
    const jobTitle = jobTitleInput.trim();
    if (!country) {
      setJobError("Country is required.");
      setJobData(null);
      setJobFetched(false);
      return;
    }
    if (!jobTitle) {
      setJobError("Job title is required.");
      setJobData(null);
      setJobFetched(false);
      return;
    }

    setJobLoading(true);
    setJobError(null);
    setJobData(null);
    setJobFetched(false);

    try {
      const data = await getJobTitleSalaryInsights(country, jobTitle);
      setJobData(data);
      setJobFetched(true);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Failed to load job title salary insights.";
      setJobError(message);
      setJobFetched(true);
    } finally {
      setJobLoading(false);
    }
  }

  function countryMetrics(data: CountrySalaryInsights): MetricItem[] {
    return [
      { label: "Employees", value: formatCount(data.employee_count) },
      { label: "Minimum salary", value: formatSalary(data.min_salary) },
      { label: "Maximum salary", value: formatSalary(data.max_salary) },
      { label: "Average salary", value: formatSalary(data.average_salary) },
    ];
  }

  function jobTitleMetrics(data: JobTitleSalaryInsights): MetricItem[] {
    const items: MetricItem[] = [
      { label: "Employees", value: formatCount(data.employee_count) },
      { label: "Average salary", value: formatSalary(data.average_salary) },
      { label: "Minimum salary", value: formatSalary(data.min_salary) },
    ];
    if (data.max_salary !== null) {
      items.push({ label: "Maximum salary", value: formatSalary(data.max_salary) });
    }
    return items;
  }

  return (
    <div className="salary-insights">
      <section className="insights-panel" aria-labelledby="country-insights-heading">
        <h2 id="country-insights-heading">Salary by country</h2>
        <p className="insights-panel__hint">
          Minimum, maximum, and average salary for all employees in a country.
        </p>
        <form className="insights-form" onSubmit={handleCountrySubmit}>
          <label className="insights-form__field">
            <span>Country</span>
            <input
              type="text"
              value={countryInput}
              onChange={(e) => setCountryInput(e.target.value)}
              placeholder="e.g. United States"
              disabled={countryLoading}
            />
          </label>
          <button type="submit" disabled={countryLoading}>
            {countryLoading ? "Fetching…" : "Fetch insights"}
          </button>
        </form>
        {countryLoading && (
          <p className="status-message" role="status">
            Loading country insights…
          </p>
        )}
        {!countryLoading && countryError && (
          <p className="status-message status-message--error" role="alert">
            {countryError}
          </p>
        )}
        {!countryLoading && !countryError && countryFetched && countryData && (
          countryData.employee_count === 0 ? (
            <p className="status-message">No employees found</p>
          ) : (
            <MetricsGrid items={countryMetrics(countryData)} />
          )
        )}
      </section>

      <section className="insights-panel" aria-labelledby="job-title-insights-heading">
        <h2 id="job-title-insights-heading">Salary by job title</h2>
        <p className="insights-panel__hint">
          Salary metrics for employees with a given job title in a country.
        </p>
        <form className="insights-form" onSubmit={handleJobTitleSubmit}>
          <label className="insights-form__field">
            <span>Country</span>
            <input
              type="text"
              value={jobCountryInput}
              onChange={(e) => setJobCountryInput(e.target.value)}
              placeholder="e.g. United States"
              disabled={jobLoading}
            />
          </label>
          <label className="insights-form__field">
            <span>Job title</span>
            <input
              type="text"
              value={jobTitleInput}
              onChange={(e) => setJobTitleInput(e.target.value)}
              placeholder="e.g. Software Engineer"
              disabled={jobLoading}
            />
          </label>
          <button type="submit" disabled={jobLoading}>
            {jobLoading ? "Fetching…" : "Fetch insights"}
          </button>
        </form>
        {jobLoading && (
          <p className="status-message" role="status">
            Loading job title insights…
          </p>
        )}
        {!jobLoading && jobError && (
          <p className="status-message status-message--error" role="alert">
            {jobError}
          </p>
        )}
        {!jobLoading && !jobError && jobFetched && jobData && (
          jobData.employee_count === 0 ? (
            <p className="status-message">No employees found</p>
          ) : (
            <MetricsGrid items={jobTitleMetrics(jobData)} />
          )
        )}
      </section>
    </div>
  );
}
