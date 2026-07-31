"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api";
import {
  type BlockedClaim,
  createBlockedClaim,
  deleteBlockedClaim,
  listBlockedClaims,
  updateBlockedClaim,
} from "@/lib/risk";

export function BlockedClaimManager() {
  const [claims, setClaims] = useState<BlockedClaim[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [term, setTerm] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setClaims(await listBlockedClaims());
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load blocked claims");
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

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!term.trim()) return;
    setBusy(true);
    setError(null);
    try {
      await createBlockedClaim({ term: term.trim() });
      setTerm("");
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Add failed");
    } finally {
      setBusy(false);
    }
  }

  async function toggle(c: BlockedClaim) {
    try {
      await updateBlockedClaim(c.id, { is_active: !c.is_active });
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Update failed");
    }
  }

  async function remove(id: string) {
    try {
      await deleteBlockedClaim(id);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delete failed");
    }
  }

  return (
    <section className="flex flex-col gap-4">
      <div>
        <h2 className="text-lg font-semibold">Blocked claims</h2>
        <p className="text-sm text-neutral-500">
          Medical-claim terms the Agent must never use.
        </p>
      </div>

      <form onSubmit={handleAdd} className="flex gap-2">
        <input
          placeholder="Add a term (e.g. cure)"
          value={term}
          onChange={(e) => setTerm(e.target.value)}
          className="grow rounded-lg border border-neutral-300 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
        />
        <button
          type="submit"
          disabled={busy || !term.trim()}
          className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-700 disabled:opacity-60"
        >
          Add
        </button>
      </form>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {loading ? (
        <p className="text-sm text-neutral-500">Loading…</p>
      ) : claims.length === 0 ? (
        <p className="text-sm text-neutral-500">No blocked terms yet.</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {claims.map((c) => (
            <span
              key={c.id}
              className={
                "flex items-center gap-2 rounded-full border px-3 py-1 text-sm " +
                (c.is_active
                  ? "border-red-300 text-red-700 dark:border-red-800 dark:text-red-300"
                  : "border-neutral-300 text-neutral-400 line-through dark:border-neutral-700")
              }
            >
              {c.term}
              <button
                type="button"
                title={c.is_active ? "Disable" : "Enable"}
                onClick={() => toggle(c)}
                className="text-xs text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200"
              >
                {c.is_active ? "off" : "on"}
              </button>
              <button
                type="button"
                title="Delete"
                onClick={() => remove(c.id)}
                className="text-xs text-neutral-400 hover:text-red-600"
              >
                ✕
              </button>
            </span>
          ))}
        </div>
      )}
    </section>
  );
}
