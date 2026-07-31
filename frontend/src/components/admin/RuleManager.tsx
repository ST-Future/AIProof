"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api";
import {
  type Rule,
  type RuleActions,
  type RuleConditions,
  type RuleInput,
  type RuleStatus,
  createRule,
  deleteRule,
  listRules,
  updateRule,
} from "@/lib/rules";

const STATUSES: RuleStatus[] = ["draft", "active", "inactive"];
const ACTION_TYPES = [
  "continue_basics",
  "safety_first",
  "allow_sales",
  "start_cooldown",
  "pause_access",
  "recommend_next",
  "answer",
];

const STATUS_STYLES: Record<RuleStatus, string> = {
  draft: "bg-neutral-200 text-neutral-700 dark:bg-neutral-700 dark:text-neutral-200",
  active: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
  inactive: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
};

const inputClass =
  "rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900";

interface FormState {
  name: string;
  description: string;
  priority: string;
  status: RuleStatus;
  cooldown_seconds: string;
  is_safety_override: boolean;
  // conditions
  stages: string;
  intents: string;
  risks: string;
  min_completed_sessions: string;
  max_completed_sessions: string;
  min_day_count: string;
  // actions
  action_type: string;
  disable_sales: boolean;
  allow_sales: boolean;
  lower_difficulty: boolean;
  message_hint: string;
}

const EMPTY: FormState = {
  name: "",
  description: "",
  priority: "100",
  status: "draft",
  cooldown_seconds: "",
  is_safety_override: false,
  stages: "",
  intents: "",
  risks: "",
  min_completed_sessions: "",
  max_completed_sessions: "",
  min_day_count: "",
  action_type: "answer",
  disable_sales: false,
  allow_sales: false,
  lower_difficulty: false,
  message_hint: "",
};

const csv = (s: string) =>
  s
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);
const num = (s: string) => (s.trim() === "" ? undefined : Number(s));

function summarize(r: Rule): string {
  const c = r.conditions;
  const cond: string[] = [];
  if (c.stages?.length) cond.push(`stage ${c.stages.join("/")}`);
  if (c.intents?.length) cond.push(`intent ${c.intents.join("/")}`);
  if (c.risks?.length) cond.push(`risk ${c.risks.join("/")}`);
  if (c.min_completed_sessions != null) cond.push(`≥${c.min_completed_sessions} sessions`);
  if (c.max_completed_sessions != null) cond.push(`≤${c.max_completed_sessions} sessions`);
  if (c.min_day_count != null) cond.push(`day ≥${c.min_day_count}`);
  const acts: string[] = [];
  if (r.actions.disable_sales) acts.push("no sales");
  if (r.actions.allow_sales) acts.push("allow sales");
  if (r.actions.lower_difficulty) acts.push("ease practice");
  return `if ${cond.join(", ") || "any"} → ${r.actions.type}${acts.length ? ` (${acts.join(", ")})` : ""}`;
}

export function RuleManager() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setRules(await listRules());
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load rules");
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

  function openEdit(r: Rule) {
    setEditingId(r.id);
    const c = r.conditions;
    const a = r.actions;
    setForm({
      name: r.name,
      description: r.description ?? "",
      priority: String(r.priority),
      status: r.status,
      cooldown_seconds: r.cooldown_seconds != null ? String(r.cooldown_seconds) : "",
      is_safety_override: r.is_safety_override,
      stages: (c.stages ?? []).join(", "),
      intents: (c.intents ?? []).join(", "),
      risks: (c.risks ?? []).join(", "),
      min_completed_sessions: c.min_completed_sessions?.toString() ?? "",
      max_completed_sessions: c.max_completed_sessions?.toString() ?? "",
      min_day_count: c.min_day_count?.toString() ?? "",
      action_type: a.type,
      disable_sales: !!a.disable_sales,
      allow_sales: !!a.allow_sales,
      lower_difficulty: !!a.lower_difficulty,
      message_hint: a.message_hint ?? "",
    });
    setFormOpen(true);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);

    const conditions: RuleConditions = {};
    if (csv(form.stages).length) conditions.stages = csv(form.stages);
    if (csv(form.intents).length) conditions.intents = csv(form.intents);
    if (csv(form.risks).length) conditions.risks = csv(form.risks);
    const minC = num(form.min_completed_sessions);
    const maxC = num(form.max_completed_sessions);
    const minD = num(form.min_day_count);
    if (minC != null) conditions.min_completed_sessions = minC;
    if (maxC != null) conditions.max_completed_sessions = maxC;
    if (minD != null) conditions.min_day_count = minD;

    const actions: RuleActions = { type: form.action_type };
    if (form.disable_sales) actions.disable_sales = true;
    if (form.allow_sales) actions.allow_sales = true;
    if (form.lower_difficulty) actions.lower_difficulty = true;
    if (form.message_hint) actions.message_hint = form.message_hint;

    const payload: RuleInput = {
      name: form.name,
      description: form.description || null,
      conditions,
      actions,
      priority: Number(form.priority) || 0,
      status: form.status,
      cooldown_seconds: num(form.cooldown_seconds) ?? null,
      is_safety_override: form.is_safety_override,
    };

    try {
      if (editingId) await updateRule(editingId, payload);
      else await createRule(payload);
      setFormOpen(false);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Save failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm("Delete this rule?")) return;
    setError(null);
    try {
      await deleteRule(id);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delete failed");
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Rules</h1>
          <p className="mt-1 text-sm text-neutral-500">
            IF/THEN decision rules — evaluated by priority; safety overrides sit on top.
          </p>
        </div>
        <button
          type="button"
          onClick={openCreate}
          className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-700"
        >
          New rule
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {formOpen && (
        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-4 rounded-2xl border border-neutral-200 p-5 dark:border-neutral-800"
        >
          <h2 className="text-base font-semibold">{editingId ? "Edit rule" : "New rule"}</h2>
          <input
            required
            placeholder="Rule name"
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

          <fieldset className="rounded-xl border border-neutral-200 p-4 dark:border-neutral-800">
            <legend className="px-1 text-xs font-medium text-neutral-500">
              Conditions (match when all present hold)
            </legend>
            <div className="grid gap-3 sm:grid-cols-3">
              <input
                placeholder="stages (comma)"
                value={form.stages}
                onChange={(e) => setForm({ ...form, stages: e.target.value })}
                className={inputClass}
              />
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
                placeholder="min completed sessions"
                value={form.min_completed_sessions}
                onChange={(e) => setForm({ ...form, min_completed_sessions: e.target.value })}
                className={inputClass}
              />
              <input
                type="number"
                placeholder="max completed sessions"
                value={form.max_completed_sessions}
                onChange={(e) => setForm({ ...form, max_completed_sessions: e.target.value })}
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
          </fieldset>

          <fieldset className="rounded-xl border border-neutral-200 p-4 dark:border-neutral-800">
            <legend className="px-1 text-xs font-medium text-neutral-500">Action</legend>
            <div className="flex flex-col gap-3">
              <select
                value={form.action_type}
                onChange={(e) => setForm({ ...form, action_type: e.target.value })}
                className={inputClass}
              >
                {ACTION_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
              <div className="flex flex-wrap gap-4 text-sm">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={form.disable_sales}
                    onChange={(e) => setForm({ ...form, disable_sales: e.target.checked })}
                  />
                  Disable sales
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={form.allow_sales}
                    onChange={(e) => setForm({ ...form, allow_sales: e.target.checked })}
                  />
                  Allow sales
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={form.lower_difficulty}
                    onChange={(e) => setForm({ ...form, lower_difficulty: e.target.checked })}
                  />
                  Lower difficulty
                </label>
              </div>
              <input
                placeholder="Message hint for the AI (optional)"
                value={form.message_hint}
                onChange={(e) => setForm({ ...form, message_hint: e.target.value })}
                className={inputClass}
              />
            </div>
          </fieldset>

          <div className="flex flex-wrap items-center gap-4">
            <label className="flex items-center gap-2 text-sm">
              Priority
              <input
                type="number"
                value={form.priority}
                onChange={(e) => setForm({ ...form, priority: e.target.value })}
                className={`${inputClass} w-24`}
              />
            </label>
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
              Cooldown (s)
              <input
                type="number"
                value={form.cooldown_seconds}
                onChange={(e) => setForm({ ...form, cooldown_seconds: e.target.value })}
                className={`${inputClass} w-28`}
              />
            </label>
            <label className="flex items-center gap-2 text-sm font-medium text-red-600">
              <input
                type="checkbox"
                checked={form.is_safety_override}
                onChange={(e) => setForm({ ...form, is_safety_override: e.target.checked })}
              />
              Safety override
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
      ) : rules.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-neutral-300 p-12 text-center dark:border-neutral-700">
          <p className="text-sm text-neutral-500">No rules yet.</p>
        </div>
      ) : (
        <ul className="flex flex-col gap-2">
          {rules.map((r) => (
            <li
              key={r.id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-neutral-200 px-4 py-3 dark:border-neutral-800"
            >
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs text-neutral-400">#{r.priority}</span>
                  <span className="font-medium">{r.name}</span>
                  <span className={`rounded-full px-2 py-0.5 text-xs ${STATUS_STYLES[r.status]}`}>
                    {r.status}
                  </span>
                  {r.is_safety_override && (
                    <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900 dark:text-red-200">
                      safety override
                    </span>
                  )}
                </div>
                <p className="text-xs text-neutral-500">{summarize(r)}</p>
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
    </div>
  );
}
