"use client";

import { useState } from "react";

import { KnowledgeInbox } from "@/components/admin/knowledge/KnowledgeInbox";
import { KnowledgeManager } from "@/components/admin/knowledge/KnowledgeManager";

type Tab = "entries" | "inbox";

export function KnowledgeWorkspace() {
  const [tab, setTab] = useState<Tab>("entries");

  return (
    <div className="flex flex-col gap-6">
      <div className="flex gap-1 border-b border-neutral-200 dark:border-neutral-800">
        {(["entries", "inbox"] as const).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={
              "-mb-px border-b-2 px-4 py-2 text-sm font-medium transition " +
              (tab === t
                ? "border-emerald-600 text-emerald-600"
                : "border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200")
            }
          >
            {t === "entries" ? "Entries" : "Inbox"}
          </button>
        ))}
      </div>

      {tab === "entries" ? <KnowledgeManager /> : <KnowledgeInbox />}
    </div>
  );
}
