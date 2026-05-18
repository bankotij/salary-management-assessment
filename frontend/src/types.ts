export interface Employee {
  id: number;
  full_name: string;
  job_title: string;
  country: string;
  salary: number;
  department: string | null;
  employment_type: string | null;
  hire_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface EmployeeCreate {
  full_name: string;
  job_title: string;
  country: string;
  salary: number;
  department?: string | null;
  employment_type?: string | null;
  hire_date?: string | null;
}

export interface EmployeeUpdate {
  full_name?: string;
  job_title?: string;
  country?: string;
  salary?: number;
  department?: string | null;
  employment_type?: string | null;
  hire_date?: string | null;
}

export interface EmployeeListResponse {
  items: Employee[];
  total: number;
  page: number;
  page_size: number;
}

export interface CountrySalaryInsights {
  country: string;
  employee_count: number;
  min_salary: number | null;
  max_salary: number | null;
  average_salary: number | null;
}

export interface JobTitleSalaryInsights {
  country: string;
  job_title: string;
  employee_count: number;
  min_salary: number | null;
  max_salary: number | null;
  average_salary: number | null;
}
