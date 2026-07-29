"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api";
import {
  type Stage,
  createStage,
  deleteStage,
  listStages,
  updateStage,
} from "@/lib/training";

const inputClass =
  "rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900";

interface FormState {
  key: string;
  name: string;
  description: string;
  order_index: string;
  is_active: boolean;
  entry_conditions: string;
}

const EMPTY: FormState = {
  key: "",
  name: "",
  description: "",
  order_index: "0",
  is_active: true,
  entry_conditions: "",
};

function parseJson(text: string): Record<string, unknown> | null {
  const t = text.trim();
  if (!t) return null;
  return JSON.parse(t) as Record<string, unknown>;
}

export function StageManager() {
  const [stages, setStages] = useState<Stage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setStages(await listStages());
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load stages");
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

  function openEdit(s: Stage) {
    setEditingId(s.id);
    setForm({
      key: s.key,
      name: s.name,
      description: s.description ?? "",
      order_index: String(s.order_index),
      is_active: s.is_active,
      entry_conditions: s.entry_conditions ? JSON.stringify(s.entry_conditions, null, 2) : "",
    });
    setFormOpen(true);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    let entry_conditions: Record<string, unknown> | null;
    try {
      entry_conditions = parseJson(form.entry_conditions);
    } catch {
      setError("Entry conditions must be valid JSON (or empty).");
      setBusy(false);
      return;
    }
    const base = {
      name: form.name,
      description: form.description || null,
      order_index: Number(form.order_index) || 0,
      is_active: form.is_active,
      entry_conditions,
    };
    try {
      if (editingId) await updateStage(editingId, base);
      else await createStage({ key: form.key, ...base });
      setFormOpen(false);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Save failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm("Delete this stage?")) return;
    setError(null);
    try {
      await deleteStage(id);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delete failed");
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Stages</h1>
          <p className="mt-1 text-sm text-neutral-500">
            Journey stages and progression conditions, in order.
          </p>
        </div>
        <button
          type="button"
          onClick={openCreate}
          className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-700"
        >
          New stage
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {formOpen && (
        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-3 rounded-2xl border border-neutral-200 p-5 dark:border-neutral-800"
        >
          <h2 className="text-base font-semibold">{editingId ? "Edit stage" : "New stage"}</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              required
              placeholder="Key (e.g. basic_training)"
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
          </div>
          <input
            placeholder="Description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            className={inputClass}
          />
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
            placeholder='Entry conditions (advanced, JSON) — e.g. {"min_completed_sessions": 3}'
            rows={2}
            value={form.entry_conditions}
            onChange={(e) => setForm({ ...form, entry_conditions: e.target.value })}
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
      ) : stages.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-neutral-300 p-12 text-center dark:border-neutral-700">
          <p className="text-sm text-neutral-500">No stages yet.</p>
        </div>
      ) : (
        <ul className="flex flex-col gap-2">
          {stages.map((s) => (
            <li
              key={s.id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-neutral-200 px-4 py-3 dark:border-neutral-800"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-neutral-400">#{s.order_index}</span>
                  <span className="font-medium">{s.name}</span>
                  {!s.is_active && (
                    <span className="rounded-full bg-neutral-200 px-2 py-0.5 text-xs text-neutral-500 dark:bg-neutral-700">
                      inactive
                    </span>
                  )}
                </div>
                <p className="text-xs text-neutral-500">{s.key}</p>
              </div>
              <div className="flex gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => openEdit(s)}
                  className="rounded-full border border-neutral-300 px-3 py-1 dark:border-neutral-700"
                >
                  Edit
                </button>
                <button
                  type="button"
                  onClick={() => handleDelete(s.id)}
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
