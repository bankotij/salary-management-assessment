import type { Employee } from "../types";

interface EmployeeTableProps {
  employees: Employee[];
  onEdit: (employee: Employee) => void;
  onDelete: (employee: Employee) => void;
  actionsDisabled?: boolean;
}

const salaryFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function formatHireDate(value: string | null): string {
  if (!value) {
    return "—";
  }
  return new Date(value).toLocaleDateString();
}

function formatText(value: string | null): string {
  return value?.trim() ? value : "—";
}

export default function EmployeeTable({
  employees,
  onEdit,
  onDelete,
  actionsDisabled = false,
}: EmployeeTableProps) {
  return (
    <div className="table-wrap">
      <table className="employee-table">
        <thead>
          <tr>
            <th scope="col">Full name</th>
            <th scope="col">Job title</th>
            <th scope="col">Country</th>
            <th scope="col">Salary</th>
            <th scope="col">Department</th>
            <th scope="col">Employment type</th>
            <th scope="col">Hire date</th>
            <th scope="col">Actions</th>
          </tr>
        </thead>
        <tbody>
          {employees.map((employee) => (
            <tr key={employee.id}>
              <td>{employee.full_name}</td>
              <td>{employee.job_title}</td>
              <td>{employee.country}</td>
              <td>{salaryFormatter.format(employee.salary)}</td>
              <td>{formatText(employee.department)}</td>
              <td>{formatText(employee.employment_type)}</td>
              <td>{formatHireDate(employee.hire_date)}</td>
              <td className="employee-table__actions">
                <button
                  type="button"
                  className="button--secondary button--small"
                  onClick={() => onEdit(employee)}
                  disabled={actionsDisabled}
                >
                  Edit
                </button>
                <button
                  type="button"
                  className="button--danger button--small"
                  onClick={() => onDelete(employee)}
                  disabled={actionsDisabled}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
