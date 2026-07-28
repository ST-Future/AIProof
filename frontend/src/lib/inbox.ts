/** Knowledge Inbox admin API client. */

import { apiFetch } from "@/lib/api";
import type { AiLevel, KnowledgeEntry } from "@/lib/knowledge";

export type InboxStatus = "new" | "promoted" | "archived";

export interface InboxItem {
  id: string;
  title: string | null;
  content: string;
  category: string | null;
  status: InboxStatus;
  promoted_entry_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface InboxCreateInput {
  content: string;
  title?: string | null;
  category?: string | null;
}

export interface InboxPromoteInput {
  title?: string | null;
  category?: string | null;
  min_ai_level?: AiLevel;
  tags?: string[];
}

const BASE = "/api/admin/inbox";

export function listInbox(status?: InboxStatus): Promise<InboxItem[]> {
  const qs = status ? `?status_filter=${status}` : "";
  return apiFetch<InboxItem[]>(`${BASE}${qs}`, { auth: true });
}

export function createInbox(input: InboxCreateInput): Promise<InboxItem> {
  return apiFetch<InboxItem>(BASE, { method: "POST", body: input, auth: true });
}

export function promoteInbox(id: string, input: InboxPromoteInput): Promise<KnowledgeEntry> {
  return apiFetch<KnowledgeEntry>(`${BASE}/${id}/promote`, {
    method: "POST",
    body: input,
    auth: true,
  });
}

export function archiveInbox(id: string): Promise<InboxItem> {
  return apiFetch<InboxItem>(`${BASE}/${id}/archive`, { method: "POST", auth: true });
}
