"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api";
import {
  type AiLevel,
  type KnowledgeEntry,
  type KnowledgeStatus,
  createKnowledge,
  listKnowledge,
  transitionKnowledge,
  updateKnowledge,
} from "@/lib/knowledge";

const AI_LEVELS: { value: AiLevel; label: string }[] = [
  { value: "none", label: "All / free" },
  { value: "basic_chat", label: "Basic ($49)" },
  { value: "energy_guide", label: "Guide ($199)" },
];

const STATUS_STYLES: Record<KnowledgeStatus, string> = {
  draft: "bg-neutral-200 text-neutral-700 dark:bg-neutral-700 dark:text-neutral-200",
  published: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
  unpublished: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  retired: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

interface FormState {
  title: string;
  body: string;
  category: string;
  min_ai_level: AiLevel;
  tags: string;
  safety_notes: string;
}

const EMPTY_FORM: FormState = {
  title: "",
  body: "",
  category: "",
  min_ai_level: "none",
  tags: "",
  safety_notes: "",
};

export function KnowledgeManager() {
  const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setEntries(await listKnowledge());
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load knowledge");
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
    setForm(EMPTY_FORM);
    setFormOpen(true);
  }

  function openEdit(entry: KnowledgeEntry) {
    setEditingId(entry.id);
    setForm({
      title: entry.title,
      body: entry.body,
      category: entry.category ?? "",
      min_ai_level: entry.min_ai_level,
      tags: entry.tags.join(", "),
      safety_notes: entry.safety_notes ?? "",
    });
    setFormOpen(true);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    const payload = {
      title: form.title,
      body: form.body,
      category: form.category || null,
      min_ai_level: form.min_ai_level,
      tags: form.tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean),
      safety_notes: form.safety_notes || null,
    };
    try {
      if (editingId) {
        await updateKnowledge(editingId, payload);
      } else {
        await createKnowledge(payload);
      }
      setFormOpen(false);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Save failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleTransition(id: string, action: "publish" | "unpublish" | "retire") {
    setError(null);
    try {
      await transitionKnowledge(id, action);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Action failed");
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Knowledge</h1>
          <p className="mt-1 text-sm text-neutral-500">
            Founder-approved content: draft, publish, unpublish, retire.
          </p>
        </div>
        <button
          type="button"
          onClick={openCreate}
          className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-700"
        >
          New entry
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {formOpen && (
        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-3 rounded-2xl border border-neutral-200 p-5 dark:border-neutral-800"
        >
          <h2 className="text-base font-semibold">
            {editingId ? "Edit entry" : "New entry"}
          </h2>
          <input
            required
            placeholder="Title"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            className="rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
          />
          <textarea
            required
            placeholder="Body"
            rows={5}
            value={form.body}
            onChange={(e) => setForm({ ...form, body: e.target.value })}
            className="rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
          />
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              placeholder="Category"
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              className="rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
            <select
              value={form.min_ai_level}
              onChange={(e) => setForm({ ...form, min_ai_level: e.target.value as AiLevel })}
              className="rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            >
              {AI_LEVELS.map((l) => (
                <option key={l.value} value={l.value}>
                  Access: {l.label}
                </option>
              ))}
            </select>
          </div>
          <input
            placeholder="Tags (comma-separated)"
            value={form.tags}
            onChange={(e) => setForm({ ...form, tags: e.target.value })}
            className="rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
          />
          <textarea
            placeholder="Safety notes (optional)"
            rows={2}
            value={form.safety_notes}
            onChange={(e) => setForm({ ...form, safety_notes: e.target.value })}
            className="rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
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
      ) : entries.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-neutral-300 p-12 text-center dark:border-neutral-700">
          <p className="text-sm text-neutral-500">No entries yet.</p>
        </div>
      ) : (
        <ul className="flex flex-col gap-2">
          {entries.map((entry) => (
            <li
              key={entry.id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-neutral-200 px-4 py-3 dark:border-neutral-800"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{entry.title}</span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs ${STATUS_STYLES[entry.status]}`}
                  >
                    {entry.status}
                  </span>
                </div>
                <p className="text-xs text-neutral-500">
                  {entry.category || "uncategorized"} · access {entry.min_ai_level}
                </p>
              </div>
              <div className="flex flex-wrap gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => openEdit(entry)}
                  className="rounded-full border border-neutral-300 px-3 py-1 dark:border-neutral-700"
                >
                  Edit
                </button>
                {entry.status !== "published" && (
                  <button
                    type="button"
                    onClick={() => handleTransition(entry.id, "publish")}
                    className="rounded-full border border-emerald-300 px-3 py-1 text-emerald-700 dark:border-emerald-800 dark:text-emerald-300"
                  >
                    Publish
                  </button>
                )}
                {entry.status === "published" && (
                  <button
                    type="button"
                    onClick={() => handleTransition(entry.id, "unpublish")}
                    className="rounded-full border border-amber-300 px-3 py-1 text-amber-700 dark:border-amber-800 dark:text-amber-300"
                  >
                    Unpublish
                  </button>
                )}
                {entry.status !== "retired" && (
                  <button
                    type="button"
                    onClick={() => handleTransition(entry.id, "retire")}
                    className="rounded-full border border-red-300 px-3 py-1 text-red-700 dark:border-red-800 dark:text-red-300"
                  >
                    Retire
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
