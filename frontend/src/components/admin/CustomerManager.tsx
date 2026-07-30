"use client";

import { useEffect, useState } from "react";

import { ApiError } from "@/lib/api";
import { type CustomerSummary, listCustomers } from "@/lib/customers";

const PACKAGE_LABELS: Record<CustomerSummary["package"], string> = {
  none: "Free",
  entry_49: "Entry ($49)",
  coaching_199: "Coaching ($199)",
};

const ACCESS_STYLES: Record<CustomerSummary["access_state"], string> = {
  inactive: "bg-neutral-200 text-neutral-600 dark:bg-neutral-700 dark:text-neutral-300",
  active: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
  expired: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  paused: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
};

export function CustomerManager() {
  const [rows, setRows] = useState<CustomerSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    void (async () => {
      try {
        const data = await listCustomers();
        if (active) setRows(data);
      } catch (err) {
        if (active) setError(err instanceof ApiError ? err.message : "Failed to load customers");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Customers</h1>
        <p className="mt-1 text-sm text-neutral-500">
          Each customer&apos;s membership, assessment, Energy Profile, and training state.
        </p>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {loading ? (
        <p className="text-sm text-neutral-500">Loading…</p>
      ) : rows.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-neutral-300 p-12 text-center dark:border-neutral-700">
          <p className="text-sm text-neutral-500">No customers yet.</p>
        </div>
      ) : (
        <ul className="flex flex-col gap-2">
          {rows.map((c) => (
            <li
              key={c.id}
              className="flex flex-col gap-2 rounded-xl border border-neutral-200 px-4 py-3 dark:border-neutral-800"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="min-w-0">
                  <span className="font-medium">{c.display_name || c.email || "—"}</span>
                  {c.display_name && c.email && (
                    <span className="ml-2 text-xs text-neutral-500">{c.email}</span>
                  )}
                </div>
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className="rounded-full bg-neutral-100 px-2 py-0.5 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300">
                    {PACKAGE_LABELS[c.package]}
                  </span>
                  <span className={`rounded-full px-2 py-0.5 ${ACCESS_STYLES[c.access_state]}`}>
                    {c.access_state}
                  </span>
                  <span className="text-neutral-500">
                    {c.stage ?? "no stage"} · day {c.day_count ?? 0} · {c.completed_sessions ?? 0}{" "}
                    sessions
                  </span>
                  <span
                    className={
                      "rounded-full px-2 py-0.5 " +
                      (c.has_assessment
                        ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200"
                        : "bg-neutral-100 text-neutral-500 dark:bg-neutral-800")
                    }
                  >
                    {c.has_assessment ? "assessed" : "no assessment"}
                  </span>
                </div>
              </div>
              {c.energy_summary && (
                <p className="text-xs text-neutral-500">{c.energy_summary}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
