"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { ApiError } from "@/lib/api";
import {
  type Prompt,
  type PromptStatus,
  createPrompt,
  deletePrompt,
  listPrompts,
  publishPrompt,
  rollbackPrompt,
  updatePrompt,
} from "@/lib/prompts";

const STATUS_STYLES: Record<PromptStatus, string> = {
  draft: "bg-neutral-200 text-neutral-700 dark:bg-neutral-700 dark:text-neutral-200",
  published: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
  archived: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
};

const inputClass =
  "rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900";

type Mode = { kind: "closed" } | { kind: "create"; key?: string } | { kind: "edit"; prompt: Prompt };

export function PromptManager() {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>({ kind: "closed" });
  const [busy, setBusy] = useState(false);

  const [keyField, setKeyField] = useState("");
  const [content, setContent] = useState("");
  const [notes, setNotes] = useState("");

  const refresh = useCallback(async () => {
    try {
      setPrompts(await listPrompts());
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load prompts");
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

  // Group by key, preserving the backend order (key asc, version desc).
  const groups = useMemo(() => {
    const map = new Map<string, Prompt[]>();
    for (const p of prompts) {
      const arr = map.get(p.key);
      if (arr) arr.push(p);
      else map.set(p.key, [p]);
    }
    return [...map.entries()];
  }, [prompts]);

  function openCreate(key?: string) {
    setKeyField(key ?? "");
    setContent("");
    setNotes("");
    setMode({ kind: "create", key });
  }

  function openEdit(prompt: Prompt) {
    setKeyField(prompt.key);
    setContent(prompt.content);
    setNotes(prompt.notes ?? "");
    setMode({ kind: "edit", prompt });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (mode.kind === "edit") {
        await updatePrompt(mode.prompt.id, { content, notes: notes || null });
      } else {
        await createPrompt({ key: keyField, content, notes: notes || null });
      }
      setMode({ kind: "closed" });
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Save failed");
    } finally {
      setBusy(false);
    }
  }

  async function run(fn: () => Promise<unknown>) {
    setError(null);
    try {
      await fn();
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Action failed");
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Prompts</h1>
          <p className="mt-1 text-sm text-neutral-500">
            Versioned prompts per key (stage / AI level). Publish a version live, or roll back.
          </p>
        </div>
        <button
          type="button"
          onClick={() => openCreate()}
          className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-700"
        >
          New prompt
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {mode.kind !== "closed" && (
        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-3 rounded-2xl border border-neutral-200 p-5 dark:border-neutral-800"
        >
          <h2 className="text-base font-semibold">
            {mode.kind === "edit"
              ? `Edit ${mode.prompt.key} v${mode.prompt.version}`
              : "New prompt version"}
          </h2>
          <input
            required
            placeholder="Key (e.g. system.base, stage.beginner)"
            value={keyField}
            disabled={mode.kind === "edit" || (mode.kind === "create" && !!mode.key)}
            onChange={(e) => setKeyField(e.target.value)}
            className={`${inputClass} disabled:opacity-60`}
          />
          <textarea
            required
            placeholder="Prompt content"
            rows={6}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className={`${inputClass} font-mono`}
          />
          <input
            placeholder="Notes (optional)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className={inputClass}
          />
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={busy}
              className="rounded-full bg-emerald-600 px-5 py-2 text-sm font-medium text-white transition hover:bg-emerald-700 disabled:opacity-60"
            >
              {busy ? "Saving…" : mode.kind === "edit" ? "Save" : "Create version"}
            </button>
            <button
              type="button"
              onClick={() => setMode({ kind: "closed" })}
              className="rounded-full border border-neutral-300 px-5 py-2 text-sm dark:border-neutral-700"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <p className="text-sm text-neutral-500">Loading…</p>
      ) : groups.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-neutral-300 p-12 text-center dark:border-neutral-700">
          <p className="text-sm text-neutral-500">No prompts yet.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-6">
          {groups.map(([key, versions]) => (
            <div key={key} className="rounded-2xl border border-neutral-200 p-4 dark:border-neutral-800">
              <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                <span className="font-mono text-sm font-semibold">{key}</span>
                <div className="flex gap-2 text-xs">
                  <button
                    type="button"
                    onClick={() => openCreate(key)}
                    className="rounded-full border border-neutral-300 px-3 py-1 dark:border-neutral-700"
                  >
                    New version
                  </button>
                  <button
                    type="button"
                    onClick={() => run(() => rollbackPrompt(key))}
                    className="rounded-full border border-amber-300 px-3 py-1 text-amber-700 dark:border-amber-800 dark:text-amber-300"
                  >
                    Rollback
                  </button>
                </div>
              </div>
              <ul className="flex flex-col gap-2">
                {versions.map((p) => (
                  <li
                    key={p.id}
                    className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-neutral-200 px-3 py-2 dark:border-neutral-800"
                  >
                    <div className="flex min-w-0 items-center gap-2">
                      <span className="text-xs text-neutral-400">v{p.version}</span>
                      <span className={`rounded-full px-2 py-0.5 text-xs ${STATUS_STYLES[p.status]}`}>
                        {p.status}
                      </span>
                      {p.is_active && (
                        <span className="rounded-full bg-emerald-600 px-2 py-0.5 text-xs font-medium text-white">
                          active
                        </span>
                      )}
                      <span className="truncate text-xs text-neutral-500">
                        {p.content.slice(0, 60)}
                        {p.content.length > 60 ? "…" : ""}
                      </span>
                    </div>
                    <div className="flex gap-2 text-xs">
                      {!p.is_active && (
                        <button
                          type="button"
                          onClick={() => run(() => publishPrompt(p.id))}
                          className="rounded-full border border-emerald-300 px-3 py-1 text-emerald-700 dark:border-emerald-800 dark:text-emerald-300"
                        >
                          Publish
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => openEdit(p)}
                        className="rounded-full border border-neutral-300 px-3 py-1 dark:border-neutral-700"
                      >
                        Edit
                      </button>
                      {!p.is_active && (
                        <button
                          type="button"
                          onClick={() => run(() => deletePrompt(p.id))}
                          className="rounded-full border border-red-300 px-3 py-1 text-red-700 dark:border-red-800 dark:text-red-300"
                        >
                          Delete
                        </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
