"use client";

import { useEffect, useState } from "react";

import { API_BASE_URL, getHealth, type HealthResponse } from "@/lib/api";

type State =
  | { kind: "loading" }
  | { kind: "ok"; data: HealthResponse }
  | { kind: "error"; message: string };

export function BackendStatus() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    let active = true;
    getHealth()
      .then((data) => active && setState({ kind: "ok", data }))
      .catch(
        (err: unknown) =>
          active &&
          setState({
            kind: "error",
            message: err instanceof Error ? err.message : "Unknown error",
          }),
      );
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="rounded-2xl border border-neutral-200 p-6 dark:border-neutral-800">
      <div className="mb-2 flex items-center gap-2">
        <span
          className={
            "inline-block h-2.5 w-2.5 rounded-full " +
            (state.kind === "ok"
              ? "bg-emerald-500"
              : state.kind === "error"
                ? "bg-red-500"
                : "bg-amber-400")
          }
        />
        <h2 className="text-base font-semibold">Backend connection</h2>
      </div>
      <p className="text-sm text-neutral-500">
        FastAPI at <code>{API_BASE_URL}</code>
      </p>
      {state.kind === "loading" && (
        <p className="mt-2 text-sm text-neutral-500">Checking /health…</p>
      )}
      {state.kind === "ok" && (
        <dl className="mt-3 grid grid-cols-2 gap-1 text-sm">
          <dt className="text-neutral-500">Status</dt>
          <dd>{state.data.status}</dd>
          <dt className="text-neutral-500">Env</dt>
          <dd>{state.data.env}</dd>
          <dt className="text-neutral-500">Database</dt>
          <dd>{state.data.database}</dd>
        </dl>
      )}
      {state.kind === "error" && (
        <p className="mt-2 text-sm text-red-600">
          Cannot reach backend: {state.message}
        </p>
      )}
    </div>
  );
}
