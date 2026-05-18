import { FormEvent, useState } from "react";

import { ApiError } from "../api/client";
import type { Employee, EmployeeCreate } from "../types";

export interface EmployeeFormValues {
  full_name: string;
  job_title: string;
  country: string;
  salary: string;
  department: string;
  employment_type: string;
  hire_date: string;
}

interface EmployeeFormProps {
  mode: "create" | "edit";
  initialEmployee?: Employee;
  onSubmit: (payload: EmployeeCreate) => Promise<void>;
  onCancel?: () => void;
  submitting?: boolean;
}

const emptyValues: EmployeeFormValues = {
  full_name: "",
  job_title: "",
  country: "",
  salary: "",
  department: "",
  employment_type: "",
  hire_date: "",
};

function valuesFromEmployee(employee: Employee): EmployeeFormValues {
  return {
    full_name: employee.full_name,
    job_title: employee.job_title,
    country: employee.country,
    salary: String(employee.salary),
    department: employee.department ?? "",
    employment_type: employee.employment_type ?? "",
    hire_date: employee.hire_date ?? "",
  };
}

function optionalText(value: string): string | null {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function validate(values: EmployeeFormValues): Record<string, string> {
  const errors: Record<string, string> = {};
  if (!values.full_name.trim()) {
    errors.full_name = "Full name is required.";
  }
  if (!values.job_title.trim()) {
    errors.job_title = "Job title is required.";
  }
  if (!values.country.trim()) {
    errors.country = "Country is required.";
  }
  const salary = Number(values.salary);
  if (!values.salary.trim() || Number.isNaN(salary) || salary <= 0) {
    errors.salary = "Salary must be greater than zero.";
  }
  return errors;
}

function toPayload(values: EmployeeFormValues): EmployeeCreate {
  return {
    full_name: values.full_name.trim(),
    job_title: values.job_title.trim(),
    country: values.country.trim(),
    salary: Number(values.salary),
    department: optionalText(values.department),
    employment_type: optionalText(values.employment_type),
    hire_date: optionalText(values.hire_date),
  };
}

function FieldError({ message }: { message?: string }) {
  if (!message) {
    return null;
  }
  return <span className="field-error">{message}</span>;
}

export default function EmployeeForm({
  mode,
  initialEmployee,
  onSubmit,
  onCancel,
  submitting = false,
}: EmployeeFormProps) {
  const [values, setValues] = useState<EmployeeFormValues>(
    initialEmployee ? valuesFromEmployee(initialEmployee) : emptyValues,
  );
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState<string | null>(null);

  function updateField<K extends keyof EmployeeFormValues>(
    field: K,
    value: EmployeeFormValues[K],
  ) {
    setValues((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setApiError(null);
    const errors = validate(values);
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) {
      return;
    }
    try {
      await onSubmit(toPayload(values));
    } catch (err) {
      if (err instanceof ApiError) {
        setApiError(err.message);
      } else if (err instanceof Error) {
        setApiError(err.message);
      } else {
        setApiError("Failed to save employee.");
      }
    }
  }

  const title = mode === "create" ? "Add employee" : "Edit employee";
  const submitLabel = mode === "create" ? "Create employee" : "Save changes";

  return (
    <section className="employee-form-panel">
      <h3>{title}</h3>
      <form className="employee-form" onSubmit={handleSubmit} noValidate>
        <div className="employee-form__grid">
          <div className="employee-form__field">
            <label htmlFor="full_name">Full name</label>
            <input
              id="full_name"
              type="text"
              value={values.full_name}
              onChange={(event) => updateField("full_name", event.target.value)}
              disabled={submitting}
              aria-invalid={Boolean(fieldErrors.full_name)}
            />
            <FieldError message={fieldErrors.full_name} />
          </div>
          <div className="employee-form__field">
            <label htmlFor="job_title">Job title</label>
            <input
              id="job_title"
              type="text"
              value={values.job_title}
              onChange={(event) => updateField("job_title", event.target.value)}
              disabled={submitting}
              aria-invalid={Boolean(fieldErrors.job_title)}
            />
            <FieldError message={fieldErrors.job_title} />
          </div>
          <div className="employee-form__field">
            <label htmlFor="country">Country</label>
            <input
              id="country"
              type="text"
              value={values.country}
              onChange={(event) => updateField("country", event.target.value)}
              disabled={submitting}
              aria-invalid={Boolean(fieldErrors.country)}
            />
            <FieldError message={fieldErrors.country} />
          </div>
          <div className="employee-form__field">
            <label htmlFor="salary">Salary</label>
            <input
              id="salary"
              type="number"
              value={values.salary}
              onChange={(event) => updateField("salary", event.target.value)}
              disabled={submitting}
              aria-invalid={Boolean(fieldErrors.salary)}
            />
              min={1}
              step={1}
            <FieldError message={fieldErrors.salary} />
          </div>
          <div className="employee-form__field">
            <label htmlFor="department">Department</label>
            <input
              id="department"
              type="text"
              value={values.department}
              onChange={(event) => updateField("department", event.target.value)}
              disabled={submitting}
              
            />
            <FieldError message={fieldErrors.department} />
          </div>
          <div className="employee-form__field">
            <label htmlFor="employment_type">Employment type</label>
            <input
              id="employment_type"
              type="text"
              value={values.employment_type}
              onChange={(event) => updateField("employment_type", event.target.value)}
              disabled={submitting}
              
            />
            <FieldError message={fieldErrors.employment_type} />
          </div>
          <div className="employee-form__field">
            <label htmlFor="hire_date">Hire date</label>
            <input
              id="hire_date"
              type="date"
              value={values.hire_date}
              onChange={(event) => updateField("hire_date", event.target.value)}
              disabled={submitting}
              
            />
            <FieldError message={fieldErrors.hire_date} />
          </div>
        </div>

        {apiError && (
          <p className="status-message status-message--error" role="alert">
            {apiError}
          </p>
        )}

        <div className="employee-form__actions">
          <button type="submit" disabled={submitting}>
            {submitLabel}
          </button>
          {mode === "edit" && onCancel && (
            <button
              type="button"
              className="button--secondary"
              onClick={onCancel}
              disabled={submitting}
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </section>
  );
}
