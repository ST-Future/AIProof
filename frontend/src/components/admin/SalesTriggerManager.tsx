"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api";
import type { RuleConditions, RuleStatus } from "@/lib/rules";
import {
  type Package,
  type SalesMode,
  type SalesTrigger,
  type SalesTriggerInput,
  createSalesTrigger,
  deleteSalesTrigger,
  listSalesTriggers,
  updateSalesTrigger,
} from "@/lib/sales";

const STATUSES: RuleStatus[] = ["draft", "active", "inactive"];
const PACKAGES: { value: Package; label: string }[] = [
  { value: "none", label: "— none —" },
  { value: "entry_49", label: "Entry ($49)" },
  { value: "coaching_199", label: "Coaching ($199)" },
];

const inputClass =
  "rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900";

interface FormState {
  name: string;
  description: string;
  mode: SalesMode;
  target_package: Package;
  priority: string;
  status: RuleStatus;
  cooldown_seconds: string;
  intents: string;
  risks: string;
  min_day_count: string;
}

const EMPTY: FormState = {
  name: "",
  description: "",
  mode: "allow",
  target_package: "none",
  priority: "100",
  status: "draft",
  cooldown_seconds: "",
  intents: "",
  risks: "",
  min_day_count: "",
};

const csv = (s: string) =>
  s
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);
const num = (s: string) => (s.trim() === "" ? undefined : Number(s));

function summarize(t: SalesTrigger): string {
  const c = t.conditions;
  const parts: string[] = [];
  if (c.intents?.length) parts.push(`intent ${c.intents.join("/")}`);
  if (c.risks?.length) parts.push(`risk ${c.risks.join("/")}`);
  if (c.min_day_count != null) parts.push(`day ≥${c.min_day_count}`);
  return `when ${parts.join(", ") || "any"}`;
}

export function SalesTriggerManager() {
  const [rows, setRows] = useState<SalesTrigger[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setRows(await listSalesTriggers());
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load sales triggers");
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

  function openEdit(t: SalesTrigger) {
    setEditingId(t.id);
    setForm({
      name: t.name,
      description: t.description ?? "",
      mode: t.mode,
      target_package: t.target_package ?? "none",
      priority: String(t.priority),
      status: t.status,
      cooldown_seconds: t.cooldown_seconds != null ? String(t.cooldown_seconds) : "",
      intents: (t.conditions.intents ?? []).join(", "),
      risks: (t.conditions.risks ?? []).join(", "),
      min_day_count: t.conditions.min_day_count?.toString() ?? "",
    });
    setFormOpen(true);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    const conditions: RuleConditions = {};
    if (csv(form.intents).length) conditions.intents = csv(form.intents);
    if (csv(form.risks).length) conditions.risks = csv(form.risks);
    const minD = num(form.min_day_count);
    if (minD != null) conditions.min_day_count = minD;

    const payload: SalesTriggerInput = {
      name: form.name,
      description: form.description || null,
      conditions,
      mode: form.mode,
      target_package: form.target_package === "none" ? null : form.target_package,
      priority: Number(form.priority) || 0,
      status: form.status,
      cooldown_seconds: num(form.cooldown_seconds) ?? null,
    };
    try {
      if (editingId) await updateSalesTrigger(editingId, payload);
      else await createSalesTrigger(payload);
      setFormOpen(false);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Save failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm("Delete this sales trigger?")) return;
    try {
      await deleteSalesTrigger(id);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delete failed");
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Sales Triggers</h1>
          <p className="mt-1 text-sm text-neutral-500">
            When package explanation / upsell is allowed or blocked (with refusal cooldown).
          </p>
        </div>
        <button
          type="button"
          onClick={openCreate}
          className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-700"
        >
          New trigger
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {formOpen && (
        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-3 rounded-2xl border border-neutral-200 p-5 dark:border-neutral-800"
        >
          <h2 className="text-base font-semibold">{editingId ? "Edit trigger" : "New trigger"}</h2>
          <input
            required
            placeholder="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className={inputClass}
          />
          <input
            placeholder="Description (optional)"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            className={inputClass}
          />
          <div className="grid gap-3 sm:grid-cols-3">
            <input
              placeholder="intents (comma)"
              value={form.intents}
              onChange={(e) => setForm({ ...form, intents: e.target.value })}
              className={inputClass}
            />
            <input
              placeholder="risks (comma)"
              value={form.risks}
              onChange={(e) => setForm({ ...form, risks: e.target.value })}
              className={inputClass}
            />
            <input
              type="number"
              placeholder="min day count"
              value={form.min_day_count}
              onChange={(e) => setForm({ ...form, min_day_count: e.target.value })}
              className={inputClass}
            />
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <select
              value={form.mode}
              onChange={(e) => setForm({ ...form, mode: e.target.value as SalesMode })}
              className={inputClass}
            >
              <option value="allow">Mode: allow</option>
              <option value="block">Mode: block</option>
            </select>
            <select
              value={form.target_package}
              onChange={(e) => setForm({ ...form, target_package: e.target.value as Package })}
              className={inputClass}
            >
              {PACKAGES.map((p) => (
                <option key={p.value} value={p.value}>
                  Package: {p.label}
                </option>
              ))}
            </select>
            <select
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value as RuleStatus })}
              className={inputClass}
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            <label className="flex items-center gap-2 text-sm">
              Priority
              <input
                type="number"
                value={form.priority}
                onChange={(e) => setForm({ ...form, priority: e.target.value })}
                className={`${inputClass} w-20`}
              />
            </label>
            <label className="flex items-center gap-2 text-sm">
              Cooldown (s)
              <input
                type="number"
                value={form.cooldown_seconds}
                onChange={(e) => setForm({ ...form, cooldown_seconds: e.target.value })}
                className={`${inputClass} w-28`}
              />
            </label>
          </div>
          <div className="flex gap-3">
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
      ) : rows.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-neutral-300 p-12 text-center dark:border-neutral-700">
          <p className="text-sm text-neutral-500">No sales triggers yet.</p>
        </div>
      ) : (
        <ul className="flex flex-col gap-2">
          {rows.map((t) => (
            <li
              key={t.id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-neutral-200 px-4 py-3 dark:border-neutral-800"
            >
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs text-neutral-400">#{t.priority}</span>
                  <span className="font-medium">{t.name}</span>
                  <span
                    className={
                      "rounded-full px-2 py-0.5 text-xs " +
                      (t.mode === "block"
                        ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                        : "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200")
                    }
                  >
                    {t.mode}
                  </span>
                  {t.status !== "active" && (
                    <span className="rounded-full bg-neutral-200 px-2 py-0.5 text-xs text-neutral-500 dark:bg-neutral-700">
                      {t.status}
                    </span>
                  )}
                </div>
                <p className="text-xs text-neutral-500">
                  {summarize(t)}
                  {t.cooldown_seconds ? ` · cooldown ${t.cooldown_seconds}s` : ""}
                </p>
              </div>
              <div className="flex gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => openEdit(t)}
                  className="rounded-full border border-neutral-300 px-3 py-1 dark:border-neutral-700"
                >
                  Edit
                </button>
                <button
                  type="button"
                  onClick={() => handleDelete(t.id)}
                  className="rounded-full border border-red-300 px-3 py-1 text-red-700 dark:border-red-800 dark:text-red-300"
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
