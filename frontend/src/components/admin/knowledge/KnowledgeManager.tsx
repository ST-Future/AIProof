"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

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

const AI_LEVEL_LABELS: Record<AiLevel, string> = {
  none: "All / free",
  basic_chat: "Basic ($49)",
  energy_guide: "Guide ($199)",
};

const STATUSES: KnowledgeStatus[] = ["draft", "published", "unpublished", "retired"];

const STATUS_STYLES: Record<KnowledgeStatus, string> = {
  draft: "bg-neutral-200 text-neutral-700 dark:bg-neutral-700 dark:text-neutral-200",
  published: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
  unpublished: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  retired: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

type GroupBy = "none" | "category" | "min_ai_level";

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

const inputClass =
  "rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900";

export function KnowledgeManager() {
  const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters (applied client-side) + grouped "Training Panel" view.
  const [q, setQ] = useState("");
  const [statusFilter, setStatusFilter] = useState<KnowledgeStatus | "">("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [groupBy, setGroupBy] = useState<GroupBy>("none");

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

  const categories = useMemo(
    () => [...new Set(entries.map((e) => e.category).filter((c): c is string => !!c))].sort(),
    [entries],
  );

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return entries.filter((e) => {
      if (statusFilter && e.status !== statusFilter) return false;
      if (categoryFilter && e.category !== categoryFilter) return false;
      if (needle && !`${e.title} ${e.body}`.toLowerCase().includes(needle)) return false;
      return true;
    });
  }, [entries, q, statusFilter, categoryFilter]);

  const groups = useMemo(() => {
    if (groupBy === "none") return null;
    const map = new Map<string, KnowledgeEntry[]>();
    for (const e of filtered) {
      const key =
        groupBy === "category"
          ? e.category || "Uncategorized"
          : AI_LEVEL_LABELS[e.min_ai_level];
      const arr = map.get(key);
      if (arr) arr.push(e);
      else map.set(key, [e]);
    }
    return [...map.entries()].sort(([a], [b]) => a.localeCompare(b));
  }, [filtered, groupBy]);

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
      if (editingId) await updateKnowledge(editingId, payload);
      else await createKnowledge(payload);
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

  function renderRow(entry: KnowledgeEntry) {
    return (
      <li
        key={entry.id}
        className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-neutral-200 px-4 py-3 dark:border-neutral-800"
      >
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-medium">{entry.title}</span>
            <span className={`rounded-full px-2 py-0.5 text-xs ${STATUS_STYLES[entry.status]}`}>
              {entry.status}
            </span>
          </div>
          <p className="text-xs text-neutral-500">
            {entry.category || "uncategorized"} · access {AI_LEVEL_LABELS[entry.min_ai_level]}
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
    );
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

      {/* Filters + grouping (Founder Training Panel) */}
      <div className="flex flex-wrap items-center gap-2">
        <input
          placeholder="Search title or body…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className={`${inputClass} grow`}
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as KnowledgeStatus | "")}
          className={inputClass}
        >
          <option value="">All statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className={inputClass}
        >
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <select
          value={groupBy}
          onChange={(e) => setGroupBy(e.target.value as GroupBy)}
          className={inputClass}
          title="Group the list (Founder Training Panel)"
        >
          <option value="none">No grouping</option>
          <option value="category">Group by category</option>
          <option value="min_ai_level">Group by access level</option>
        </select>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {formOpen && (
        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-3 rounded-2xl border border-neutral-200 p-5 dark:border-neutral-800"
        >
          <h2 className="text-base font-semibold">{editingId ? "Edit entry" : "New entry"}</h2>
          <input
            required
            placeholder="Title"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            className={inputClass}
          />
          <textarea
            required
            placeholder="Body"
            rows={5}
            value={form.body}
            onChange={(e) => setForm({ ...form, body: e.target.value })}
            className={inputClass}
          />
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              placeholder="Category"
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              className={inputClass}
            />
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
          </div>
          <input
            placeholder="Tags (comma-separated)"
            value={form.tags}
            onChange={(e) => setForm({ ...form, tags: e.target.value })}
            className={inputClass}
          />
          <textarea
            placeholder="Safety notes (optional)"
            rows={2}
            value={form.safety_notes}
            onChange={(e) => setForm({ ...form, safety_notes: e.target.value })}
            className={inputClass}
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
      ) : filtered.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-neutral-300 p-12 text-center dark:border-neutral-700">
          <p className="text-sm text-neutral-500">No entries match.</p>
        </div>
      ) : groups ? (
        <div className="flex flex-col gap-6">
          {groups.map(([name, items]) => (
            <div key={name}>
              <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold">
                {name}
                <span className="rounded-full bg-neutral-100 px-2 py-0.5 text-xs font-normal text-neutral-500 dark:bg-neutral-800">
                  {items.length}
                </span>
              </h3>
              <ul className="flex flex-col gap-2">{items.map(renderRow)}</ul>
            </div>
          ))}
        </div>
      ) : (
        <ul className="flex flex-col gap-2">{filtered.map(renderRow)}</ul>
      )}
    </div>
  );
}
