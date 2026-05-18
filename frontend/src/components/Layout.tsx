import type { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="layout">
      <header className="layout__header">
        <h1>Salary Management</h1>
        <p className="layout__subtitle">
          Manage employee records and salary information for your organization.
        </p>
      </header>
      <main className="layout__main">{children}</main>
    </div>
  );
}
