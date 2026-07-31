"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api";
import {
  type RiskRule,
  type RiskRuleInput,
  type RiskSeverity,
  createRiskRule,
  deleteRiskRule,
  listRiskRules,
  updateRiskRule,
} from "@/lib/risk";

const SEVERITIES: RiskSeverity[] = ["low", "medium", "high"];
const SEVERITY_STYLES: Record<RiskSeverity, string> = {
  low: "bg-neutral-200 text-neutral-700 dark:bg-neutral-700 dark:text-neutral-200",
  medium: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  high: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

const inputClass =
  "rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900";

const csv = (s: string) =>
  s
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);

interface FormState {
  category: string;
  keywords: string;
  severity: RiskSeverity;
  is_active: boolean;
  fallback_message: string;
}

const EMPTY: FormState = {
  category: "",
  keywords: "",
  severity: "medium",
  is_active: true,
  fallback_message: "",
};

export function RiskRuleManager() {
  const [rules, setRules] = useState<RiskRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setRules(await listRiskRules());
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load risk rules");
    }
  }, []);

  useEffect(() => {
    let active = true;
    void (async () => {
      await refresh();
      if (active) setLoading(false);
    })();
    return () => {
      active = false;
    };
  }, [refresh]);

  function openCreate() {
    setEditingId(null);
    setForm(EMPTY);
    setFormOpen(true);
  }

  function openEdit(r: RiskRule) {
    setEditingId(r.id);
    setForm({
      category: r.category,
      keywords: r.keywords.join(", "),
      severity: r.severity,
      is_active: r.is_active,
      fallback_message: typeof r.fallback_action?.message === "string" ? r.fallback_action.message : "",
    });
    setFormOpen(true);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    const payload: RiskRuleInput = {
      category: form.category,
      keywords: csv(form.keywords),
      severity: form.severity,
      is_active: form.is_active,
      fallback_action: form.fallback_message
        ? { type: "safety_first", message: form.fallback_message, disable_sales: true }
        : null,
    };
    try {
      if (editingId) await updateRiskRule(editingId, payload);
      else await createRiskRule(payload);
      setFormOpen(false);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Save failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm("Delete this risk rule?")) return;
    try {
      await deleteRiskRule(id);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delete failed");
    }
  }

  return (
    <section className="flex flex-col gap-4">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">Risk rules</h2>
          <p className="text-sm text-neutral-500">
            Keywords + severity that trigger a safety-first response.
          </p>
        </div>
        <button
          type="button"
          onClick={openCreate}
          className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-700"
        >
          New risk rule
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {formOpen && (
        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-3 rounded-2xl border border-neutral-200 p-5 dark:border-neutral-800"
        >
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              required
              placeholder="Category (e.g. cardiac)"
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              className={inputClass}
            />
            <select
              value={form.severity}
              onChange={(e) => setForm({ ...form, severity: e.target.value as RiskSeverity })}
              className={inputClass}
            >
              {SEVERITIES.map((s) => (
                <option key={s} value={s}>
                  Severity: {s}
                </option>
              ))}
            </select>
          </div>
          <input
            placeholder="Keywords (comma-separated)"
            value={form.keywords}
            onChange={(e) => setForm({ ...form, keywords: e.target.value })}
            className={inputClass}
          />
          <input
            placeholder="Safe fallback message (optional)"
            value={form.fallback_message}
            onChange={(e) => setForm({ ...form, fallback_message: e.target.value })}
            className={inputClass}
          />
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
              />
              Active
            </label>
            <button
              type="submit"
              disabled={busy}
              className="rounded-full bg-emerald-600 px-5 py-2 text-sm font-medium text-white transition hover:bg-emerald-700 disabled:opacity-60"
            >
              {busy ? "Saving…" : "Save"}
            </button>
            <button
              type="button"
              onClick={() => setFormOpen(false)}
              className="rounded-full border border-neutral-300 px-5 py-2 text-sm dark:border-neutral-700"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <p className="text-sm text-neutral-500">Loading…</p>
      ) : rules.length === 0 ? (
        <p className="text-sm text-neutral-500">No risk rules yet.</p>
      ) : (
        <ul className="flex flex-col gap-2">
          {rules.map((r) => (
            <li
              key={r.id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-neutral-200 px-4 py-3 dark:border-neutral-800"
            >
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium">{r.category}</span>
                  <span className={`rounded-full px-2 py-0.5 text-xs ${SEVERITY_STYLES[r.severity]}`}>
                    {r.severity}
                  </span>
                  {!r.is_active && (
                    <span className="rounded-full bg-neutral-200 px-2 py-0.5 text-xs text-neutral-500 dark:bg-neutral-700">
                      inactive
                    </span>
                  )}
                </div>
                <p className="text-xs text-neutral-500">{r.keywords.join(", ") || "no keywords"}</p>
              </div>
              <div className="flex gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => openEdit(r)}
                  className="rounded-full border border-neutral-300 px-3 py-1 dark:border-neutral-700"
                >
                  Edit
                </button>
                <button
                  type="button"
                  onClick={() => handleDelete(r.id)}
                  className="rounded-full border border-red-300 px-3 py-1 text-red-700 dark:border-red-800 dark:text-red-300"
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
