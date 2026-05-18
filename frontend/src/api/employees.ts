import { request } from "./client";
import type {
  Employee,
  EmployeeCreate,
  EmployeeListResponse,
  EmployeeUpdate,
} from "../types";

export interface ListEmployeesParams {
  country?: string;
  job_title?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

function toQueryString(params: ListEmployeesParams): string {
  const searchParams = new URLSearchParams();
  if (params.country) {
    searchParams.set("country", params.country);
  }
  if (params.job_title) {
    searchParams.set("job_title", params.job_title);
  }
  if (params.search) {
    searchParams.set("search", params.search);
  }
  if (params.page !== undefined) {
    searchParams.set("page", String(params.page));
  }
  if (params.page_size !== undefined) {
    searchParams.set("page_size", String(params.page_size));
  }
  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

export function listEmployees(params: ListEmployeesParams = {}): Promise<EmployeeListResponse> {
  return request<EmployeeListResponse>(`/employees${toQueryString(params)}`);
}

export function createEmployee(payload: EmployeeCreate): Promise<Employee> {
  return request<Employee>("/employees", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getEmployee(id: number): Promise<Employee> {
  return request<Employee>(`/employees/${id}`);
}

export function updateEmployee(id: number, payload: EmployeeUpdate): Promise<Employee> {
  return request<Employee>(`/employees/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteEmployee(id: number): Promise<void> {
  return request<void>(`/employees/${id}`, {
    method: "DELETE",
  });
}
