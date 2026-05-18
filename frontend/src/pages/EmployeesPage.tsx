import { FormEvent, useCallback, useEffect, useState } from "react";

import {
  createEmployee,
  deleteEmployee,
  listEmployees,
  updateEmployee,
} from "../api/employees";
import { ApiError } from "../api/client";
import EmployeeForm from "../components/EmployeeForm";
import EmployeeTable from "../components/EmployeeTable";
import type { Employee, EmployeeCreate } from "../types";

const PAGE_SIZE = 20;

interface AppliedFilters {
  search: string;
  country: string;
  job_title: string;
}

const emptyFilters: AppliedFilters = {
  search: "",
  country: "",
  job_title: "",
};

type FormMode = "none" | "create" | "edit";

export default function EmployeesPage() {
  const [search, setSearch] = useState("");
  const [country, setCountry] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [appliedFilters, setAppliedFilters] = useState<AppliedFilters>(emptyFilters);
  const [page, setPage] = useState(1);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formMode, setFormMode] = useState<FormMode>("none");
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);
  const [mutating, setMutating] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [mutationError, setMutationError] = useState<string | null>(null);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const busy = loading || mutating;

  const loadEmployees = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listEmployees({
        page,
        page_size: PAGE_SIZE,
        search: appliedFilters.search || undefined,
        country: appliedFilters.country || undefined,
        job_title: appliedFilters.job_title || undefined,
      });
      setEmployees(response.items);
      setTotal(response.total);
    } catch (err) {
      setEmployees([]);
      setTotal(0);
      setError(err instanceof Error ? err.message : "Failed to load employees.");
    } finally {
      setLoading(false);
    }
  }, [appliedFilters, page]);

  useEffect(() => {
    void loadEmployees();
  }, [loadEmployees]);

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  function handleApplyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAppliedFilters({
      search: search.trim(),
      country: country.trim(),
      job_title: jobTitle.trim(),
    });
    setPage(1);
  }

  function handleClearFilters() {
    setSearch("");
    setCountry("");
    setJobTitle("");
    setAppliedFilters(emptyFilters);
    setPage(1);
  }

  function openCreateForm() {
    setEditingEmployee(null);
    setFormMode("create");
    setMutationError(null);
  }

  function openEditForm(employee: Employee) {
    setEditingEmployee(employee);
    setFormMode("edit");
    setMutationError(null);
  }

  function closeForm() {
    setFormMode("none");
    setEditingEmployee(null);
    setMutationError(null);
  }

  async function handleCreate(payload: EmployeeCreate) {
    setMutating(true);
    setMutationError(null);
    try {
      await createEmployee(payload);
      setFeedback("Employee created successfully.");
      closeForm();
      await loadEmployees();
    } catch (err) {
      const message =
        err instanceof ApiError || err instanceof Error
          ? err.message
          : "Failed to create employee.";
      setMutationError(message);
      throw err;
    } finally {
      setMutating(false);
    }
  }

  async function handleUpdate(payload: EmployeeCreate) {
    if (!editingEmployee) {
      return;
    }
    setMutating(true);
    setMutationError(null);
    try {
      await updateEmployee(editingEmployee.id, payload);
      setFeedback("Employee updated successfully.");
      closeForm();
      await loadEmployees();
    } catch (err) {
      const message =
        err instanceof ApiError || err instanceof Error
          ? err.message
          : "Failed to update employee.";
      setMutationError(message);
      throw err;
    } finally {
      setMutating(false);
    }
  }

  async function handleDelete(employee: Employee) {
    const confirmed = window.confirm(
      `Delete ${employee.full_name}? This action cannot be undone.`,
    );
    if (!confirmed) {
      return;
    }
    setMutating(true);
    setMutationError(null);
    try {
      await deleteEmployee(employee.id);
      setFeedback("Employee deleted successfully.");
      if (formMode === "edit" && editingEmployee?.id === employee.id) {
        closeForm();
      }
      await loadEmployees();
    } catch (err) {
      setMutationError(
        err instanceof ApiError || err instanceof Error
          ? err.message
          : "Failed to delete employee.",
      );
    } finally {
      setMutating(false);
    }
  }

  const canGoPrevious = page > 1;
  const canGoNext = page < totalPages;

  return (
    <section className="employees-page">
      <div className="employees-page__header">
        <div>
          <h2>Employees</h2>
          <p>Browse and filter employee records.</p>
        </div>
        <button type="button" onClick={openCreateForm} disabled={busy}>
          Add employee
        </button>
      </div>

      {feedback && (
        <p className="status-message status-message--success" role="status">
          {feedback}
        </p>
      )}
      {mutationError && !loading && (
        <p className="status-message status-message--error" role="alert">
          {mutationError}
        </p>
      )}

      {formMode === "create" && (
        <EmployeeForm mode="create" onSubmit={handleCreate} submitting={mutating} />
      )}
      {formMode === "edit" && editingEmployee && (
        <EmployeeForm
          key={editingEmployee.id}
          mode="edit"
          initialEmployee={editingEmployee}
          onSubmit={handleUpdate}
          onCancel={closeForm}
          submitting={mutating}
        />
      )}

      <form className="filters" onSubmit={handleApplyFilters}>
        <div className="filters__field">
          <label htmlFor="search">Search by name</label>
          <input
            id="search"
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Partial full name"
            disabled={busy}
          />
        </div>
        <div className="filters__field">
          <label htmlFor="country">Country</label>
          <input
            id="country"
            type="text"
            value={country}
            onChange={(event) => setCountry(event.target.value)}
            placeholder="e.g. India"
            disabled={busy}
          />
        </div>
        <div className="filters__field">
          <label htmlFor="job_title">Job title</label>
          <input
            id="job_title"
            type="text"
            value={jobTitle}
            onChange={(event) => setJobTitle(event.target.value)}
            placeholder="e.g. Engineer"
            disabled={busy}
          />
        </div>
        <div className="filters__actions">
          <button type="submit" disabled={busy}>
            Apply filters
          </button>
          <button type="button" className="button--secondary" onClick={handleClearFilters} disabled={busy}>
            Clear
          </button>
        </div>
      </form>

      {loading && <p className="status-message" role="status">Loading employees…</p>}
      {error && !loading && (
        <p className="status-message status-message--error" role="alert">
          {error}
        </p>
      )}
      {!loading && !error && employees.length === 0 && (
        <p className="status-message">No employees match your filters.</p>
      )}
      {!loading && !error && employees.length > 0 && (
        <EmployeeTable
          employees={employees}
          onEdit={openEditForm}
          onDelete={handleDelete}
          actionsDisabled={busy}
        />
      )}

      <div className="pagination">
        <button type="button" onClick={() => setPage((p) => p - 1)} disabled={busy || !canGoPrevious}>
          Previous
        </button>
        <span className="pagination__info">
          Page {page} of {totalPages} ({total} employees)
        </span>
        <button type="button" onClick={() => setPage((p) => p + 1)} disabled={busy || !canGoNext}>
          Next
        </button>
      </div>
    </section>
  );
}
