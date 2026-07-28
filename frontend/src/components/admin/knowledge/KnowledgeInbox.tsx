"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api";
import {
  type InboxItem,
  archiveInbox,
  createInbox,
  listInbox,
  promoteInbox,
} from "@/lib/inbox";
import type { AiLevel } from "@/lib/knowledge";

const AI_LEVELS: { value: AiLevel; label: string }[] = [
  { value: "none", label: "All / free" },
  { value: "basic_chat", label: "Basic ($49)" },
  { value: "energy_guide", label: "Guide ($199)" },
];

const STATUS_STYLES: Record<InboxItem["status"], string> = {
  new: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
  promoted: "bg-neutral-200 text-neutral-600 dark:bg-neutral-700 dark:text-neutral-300",
  archived: "bg-neutral-200 text-neutral-500 dark:bg-neutral-800 dark:text-neutral-400",
};

const inputClass =
  "rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900";

interface PromoteState {
  title: string;
  category: string;
  min_ai_level: AiLevel;
  tags: string;
}

export function KnowledgeInbox() {
  const [items, setItems] = useState<InboxItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);

  const [promotingId, setPromotingId] = useState<string | null>(null);
  const [promote, setPromote] = useState<PromoteState>({
    title: "",
    category: "",
    min_ai_level: "none",
    tags: "",
  });

  const refresh = useCallback(async () => {
    try {
      setItems(await listInbox());
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load inbox");
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

  async function handleCapture(e: React.FormEvent) {
    e.preventDefault();
    if (!note.trim()) return;
    setBusy(true);
    setError(null);
    try {
      await createInbox({ content: note.trim() });
      setNote("");
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Capture failed");
    } finally {
      setBusy(false);
    }
  }

  function openPromote(item: InboxItem) {
    setPromotingId(item.id);
    setPromote({
      title: item.title ?? "",
      category: item.category ?? "",
      min_ai_level: "none",
      tags: "",
    });
  }

  async function handlePromote(e: React.FormEvent) {
    e.preventDefault();
    if (!promotingId) return;
    setBusy(true);
    setError(null);
    try {
      await promoteInbox(promotingId, {
        title: promote.title || null,
        category: promote.category || null,
        min_ai_level: promote.min_ai_level,
        tags: promote.tags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
      });
      setPromotingId(null);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Promote failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleArchive(id: string) {
    setError(null);
    try {
      await archiveInbox(id);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Archive failed");
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Knowledge Inbox</h1>
        <p className="mt-1 text-sm text-neutral-500">
          Jot raw notes fast, then promote them into categorized knowledge entries.
        </p>
      </div>

      <form
        onSubmit={handleCapture}
        className="flex flex-col gap-3 rounded-2xl border border-neutral-200 p-5 dark:border-neutral-800"
      >
        <textarea
          placeholder="Capture a quick note…"
          rows={3}
          value={note}
          onChange={(e) => setNote(e.target.value)}
          className={inputClass}
        />
        <button
          type="submit"
          disabled={busy || !note.trim()}
          className="w-fit rounded-full bg-emerald-600 px-5 py-2 text-sm font-medium text-white transition hover:bg-emerald-700 disabled:opacity-60"
        >
          Capture
        </button>
      </form>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {loading ? (
        <p className="text-sm text-neutral-500">Loading…</p>
      ) : items.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-neutral-300 p-12 text-center dark:border-neutral-700">
          <p className="text-sm text-neutral-500">Inbox is empty.</p>
        </div>
      ) : (
        <ul className="flex flex-col gap-2">
          {items.map((item) => (
            <li
              key={item.id}
              className="rounded-xl border border-neutral-200 px-4 py-3 dark:border-neutral-800"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="mb-1 flex items-center gap-2">
                    <span className={`rounded-full px-2 py-0.5 text-xs ${STATUS_STYLES[item.status]}`}>
                      {item.status}
                    </span>
                    {item.title && <span className="text-sm font-medium">{item.title}</span>}
                  </div>
                  <p className="whitespace-pre-wrap text-sm text-neutral-600 dark:text-neutral-300">
                    {item.content}
                  </p>
                </div>
                {item.status === "new" && (
                  <div className="flex gap-2 text-xs">
                    <button
                      type="button"
                      onClick={() => openPromote(item)}
                      className="rounded-full border border-emerald-300 px-3 py-1 text-emerald-700 dark:border-emerald-800 dark:text-emerald-300"
                    >
                      Promote
                    </button>
                    <button
                      type="button"
                      onClick={() => handleArchive(item.id)}
                      className="rounded-full border border-neutral-300 px-3 py-1 dark:border-neutral-700"
                    >
                      Archive
                    </button>
                  </div>
                )}
              </div>

              {promotingId === item.id && (
                <form
                  onSubmit={handlePromote}
                  className="mt-3 flex flex-col gap-2 rounded-lg bg-neutral-50 p-3 dark:bg-neutral-900"
                >
                  <div className="grid gap-2 sm:grid-cols-2">
                    <input
                      placeholder="Entry title"
                      value={promote.title}
                      onChange={(e) => setPromote({ ...promote, title: e.target.value })}
                      className={inputClass}
                    />
                    <input
                      placeholder="Category"
                      value={promote.category}
                      onChange={(e) => setPromote({ ...promote, category: e.target.value })}
                      className={inputClass}
                    />
                    <select
                      value={promote.min_ai_level}
                      onChange={(e) =>
                        setPromote({ ...promote, min_ai_level: e.target.value as AiLevel })
                      }
                      className={inputClass}
                    >
                      {AI_LEVELS.map((l) => (
                        <option key={l.value} value={l.value}>
                          Access: {l.label}
                        </option>
                      ))}
                    </select>
                    <input
                      placeholder="Tags (comma-separated)"
                      value={promote.tags}
                      onChange={(e) => setPromote({ ...promote, tags: e.target.value })}
                      className={inputClass}
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="submit"
                      disabled={busy}
                      className="rounded-full bg-emerald-600 px-4 py-1.5 text-sm font-medium text-white transition hover:bg-emerald-700 disabled:opacity-60"
                    >
                      Create draft entry
                    </button>
                    <button
                      type="button"
                      onClick={() => setPromotingId(null)}
                      className="rounded-full border border-neutral-300 px-4 py-1.5 text-sm dark:border-neutral-700"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
