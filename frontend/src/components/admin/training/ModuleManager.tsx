"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api";
import type { AiLevel } from "@/lib/knowledge";
import {
  type Module,
  type Stage,
  createModule,
  deleteModule,
  listModules,
  listStages,
  updateModule,
} from "@/lib/training";

const AI_LEVELS: { value: AiLevel; label: string }[] = [
  { value: "none", label: "All / free" },
  { value: "basic_chat", label: "Basic ($49)" },
  { value: "energy_guide", label: "Guide ($199)" },
];

const inputClass =
  "rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900";

interface FormState {
  key: string;
  name: string;
  target_user: string;
  stage_id: string;
  goal: string;
  steps: string;
  duration_minutes: string;
  next_module_id: string;
  next_stage_id: string;
  min_ai_level: AiLevel;
  order_index: string;
  is_active: boolean;
  stop_conditions: string;
}

const EMPTY: FormState = {
  key: "",
  name: "",
  target_user: "",
  stage_id: "",
  goal: "",
  steps: "",
  duration_minutes: "",
  next_module_id: "",
  next_stage_id: "",
  min_ai_level: "none",
  order_index: "0",
  is_active: true,
  stop_conditions: "",
};

function parseJson(text: string): Record<string, unknown> | null {
  const t = text.trim();
  if (!t) return null;
  return JSON.parse(t) as Record<string, unknown>;
}

export function ModuleManager() {
  const [modules, setModules] = useState<Module[]>([]);
  const [stages, setStages] = useState<Stage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [m, s] = await Promise.all([listModules(), listStages()]);
      setModules(m);
      setStages(s);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load training plans");
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

  const stageName = (id: string | null) => stages.find((s) => s.id === id)?.name ?? "—";
  const moduleName = (id: string | null) => modules.find((m) => m.id === id)?.name ?? "—";

  function openCreate() {
    setEditingId(null);
    setForm(EMPTY);
    setFormOpen(true);
  }

  function openEdit(m: Module) {
    setEditingId(m.id);
    setForm({
      key: m.key,
      name: m.name,
      target_user: m.target_user ?? "",
      stage_id: m.stage_id ?? "",
      goal: m.goal ?? "",
      steps: m.steps.join("\n"),
      duration_minutes: m.duration_minutes != null ? String(m.duration_minutes) : "",
      next_module_id: m.next_module_id ?? "",
      next_stage_id: m.next_stage_id ?? "",
      min_ai_level: m.min_ai_level,
      order_index: String(m.order_index),
      is_active: m.is_active,
      stop_conditions: m.stop_conditions ? JSON.stringify(m.stop_conditions, null, 2) : "",
    });
    setFormOpen(true);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    let stop_conditions: Record<string, unknown> | null;
    try {
      stop_conditions = parseJson(form.stop_conditions);
    } catch {
      setError("Stop conditions must be valid JSON (or empty).");
      setBusy(false);
      return;
    }
    const base = {
      name: form.name,
      target_user: form.target_user || null,
      stage_id: form.stage_id || null,
      goal: form.goal || null,
      steps: form.steps
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean),
      duration_minutes: form.duration_minutes ? Number(form.duration_minutes) : null,
      next_module_id: form.next_module_id || null,
      next_stage_id: form.next_stage_id || null,
      min_ai_level: form.min_ai_level,
      order_index: Number(form.order_index) || 0,
      is_active: form.is_active,
      stop_conditions,
    };
    try {
      if (editingId) await updateModule(editingId, base);
      else await createModule({ key: form.key, ...base });
      setFormOpen(false);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Save failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm("Delete this module?")) return;
    setError(null);
    try {
      await deleteModule(id);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delete failed");
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Training Plans</h1>
          <p className="mt-1 text-sm text-neutral-500">
            Practice modules: steps, duration, goals, stop conditions, next stage.
          </p>
        </div>
        <button
          type="button"
          onClick={openCreate}
          className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-700"
        >
          New module
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {formOpen && (
        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-3 rounded-2xl border border-neutral-200 p-5 dark:border-neutral-800"
        >
          <h2 className="text-base font-semibold">{editingId ? "Edit module" : "New module"}</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              required
              placeholder="Key (e.g. box_breathing)"
              value={form.key}
              disabled={!!editingId}
              onChange={(e) => setForm({ ...form, key: e.target.value })}
              className={`${inputClass} disabled:opacity-60`}
            />
            <input
              required
              placeholder="Name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className={inputClass}
            />
            <input
              placeholder="Target user (e.g. beginners)"
              value={form.target_user}
              onChange={(e) => setForm({ ...form, target_user: e.target.value })}
              className={inputClass}
            />
            <select
              value={form.stage_id}
              onChange={(e) => setForm({ ...form, stage_id: e.target.value })}
              className={inputClass}
            >
              <option value="">Stage: none</option>
              {stages.map((s) => (
                <option key={s.id} value={s.id}>
                  Stage: {s.name}
                </option>
              ))}
            </select>
          </div>
          <input
            placeholder="Goal"
            value={form.goal}
            onChange={(e) => setForm({ ...form, goal: e.target.value })}
            className={inputClass}
          />
          <textarea
            placeholder="Steps — one per line"
            rows={4}
            value={form.steps}
            onChange={(e) => setForm({ ...form, steps: e.target.value })}
            className={inputClass}
          />
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="flex items-center gap-2 text-sm">
              Duration (min)
              <input
                type="number"
                value={form.duration_minutes}
                onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })}
                className={`${inputClass} w-24`}
              />
            </label>
            <select
              value={form.min_ai_level}
              onChange={(e) => setForm({ ...form, min_ai_level: e.target.value as AiLevel })}
              className={inputClass}
            >
              {AI_LEVELS.map((l) => (
                <option key={l.value} value={l.value}>
                  Access: {l.label}
                </option>
              ))}
            </select>
            <select
              value={form.next_module_id}
              onChange={(e) => setForm({ ...form, next_module_id: e.target.value })}
              className={inputClass}
            >
              <option value="">Next module: none</option>
              {modules
                .filter((m) => m.id !== editingId)
                .map((m) => (
                  <option key={m.id} value={m.id}>
                    Next module: {m.name}
                  </option>
                ))}
            </select>
            <select
              value={form.next_stage_id}
              onChange={(e) => setForm({ ...form, next_stage_id: e.target.value })}
              className={inputClass}
            >
              <option value="">Next stage: none</option>
              {stages.map((s) => (
                <option key={s.id} value={s.id}>
                  Next stage: {s.name}
                </option>
              ))}
            </select>
          </div>
          <div className="grid items-center gap-3 sm:grid-cols-2">
            <label className="flex items-center gap-2 text-sm">
              Order
              <input
                type="number"
                value={form.order_index}
                onChange={(e) => setForm({ ...form, order_index: e.target.value })}
                className={`${inputClass} w-24`}
              />
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
              />
              Active
            </label>
          </div>
          <textarea
            placeholder='Stop conditions (advanced, JSON) — e.g. {"max_sessions": 5}'
            rows={2}
            value={form.stop_conditions}
            onChange={(e) => setForm({ ...form, stop_conditions: e.target.value })}
            className={`${inputClass} font-mono`}
          />
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
      ) : modules.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-neutral-300 p-12 text-center dark:border-neutral-700">
          <p className="text-sm text-neutral-500">No modules yet.</p>
        </div>
      ) : (
        <ul className="flex flex-col gap-2">
          {modules.map((m) => (
            <li
              key={m.id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-neutral-200 px-4 py-3 dark:border-neutral-800"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{m.name}</span>
                  {m.duration_minutes != null && (
                    <span className="text-xs text-neutral-400">{m.duration_minutes} min</span>
                  )}
                  {!m.is_active && (
                    <span className="rounded-full bg-neutral-200 px-2 py-0.5 text-xs text-neutral-500 dark:bg-neutral-700">
                      inactive
                    </span>
                  )}
                </div>
                <p className="text-xs text-neutral-500">
                  stage {stageName(m.stage_id)} · next module {moduleName(m.next_module_id)} · next
                  stage {stageName(m.next_stage_id)} · access {m.min_ai_level}
                </p>
              </div>
              <div className="flex gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => openEdit(m)}
                  className="rounded-full border border-neutral-300 px-3 py-1 dark:border-neutral-700"
                >
                  Edit
                </button>
                <button
                  type="button"
                  onClick={() => handleDelete(m.id)}
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
