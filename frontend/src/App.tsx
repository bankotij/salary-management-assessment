import { useState } from "react";

import Layout from "./components/Layout";
import SalaryInsights from "./components/SalaryInsights";
import EmployeesPage from "./pages/EmployeesPage";

type AppTab = "employees" | "insights";

export default function App() {
  const [tab, setTab] = useState<AppTab>("employees");

  return (
    <Layout>
      <nav className="app-tabs" aria-label="Application sections">
        <button
          type="button"
          className={
            tab === "employees" ? "app-tabs__tab app-tabs__tab--active" : "app-tabs__tab"
          }
          onClick={() => setTab("employees")}
        >
          Employees
        </button>
        <button
          type="button"
          className={
            tab === "insights" ? "app-tabs__tab app-tabs__tab--active" : "app-tabs__tab"
          }
          onClick={() => setTab("insights")}
        >
          Salary Insights
        </button>
      </nav>
      {tab === "employees" ? <EmployeesPage /> : <SalaryInsights />}
    </Layout>
  );
}
