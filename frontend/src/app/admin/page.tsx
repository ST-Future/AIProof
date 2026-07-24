import type { Metadata } from "next";

import { AdminGuard } from "./AdminGuard";
import { BackendStatus } from "./BackendStatus";

export const metadata: Metadata = {
  title: "Admin — Great Energy Field",
};

// Founder/Admin backend sections (built out across Weeks 1–3 & Milestone 2).
const adminSections = [
  "Knowledge",
  "Training Plans",
  "Stages",
  "Rules",
  "Prompts",
  "Risk & Safety",
  "Sales Triggers",
  "Agent Runs",
  "Customers",
  "Quality Feedback",
];

export default function AdminHome() {
  return (
    <AdminGuard>
      <main className="mx-auto flex min-h-screen max-w-5xl flex-col gap-10 px-6 py-16">
        <header className="flex flex-col gap-2">
          <h1 className="text-3xl font-semibold">Founder / Admin dashboard</h1>
          <p className="text-neutral-600 dark:text-neutral-400">
            Agent management shell. Sections are wired up during Milestone 1.
          </p>
        </header>

        <BackendStatus />

        <section>
          <h2 className="mb-4 text-lg font-semibold">Sections</h2>
          <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {adminSections.map((name) => (
              <li
                key={name}
                className="rounded-xl border border-dashed border-neutral-300 p-4 text-sm text-neutral-500 dark:border-neutral-700"
              >
                {name}
                <span className="ml-2 rounded-full bg-neutral-100 px-2 py-0.5 text-xs text-neutral-500 dark:bg-neutral-800">
                  soon
                </span>
              </li>
            ))}
          </ul>
        </section>
      </main>
    </AdminGuard>
  );
}
