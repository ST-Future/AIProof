/** Knowledge base admin API client. */

import { apiFetch } from "@/lib/api";

export type KnowledgeStatus = "draft" | "published" | "unpublished" | "retired";
export type AiLevel = "none" | "basic_chat" | "energy_guide";

export interface KnowledgeEntry {
  id: string;
  title: string;
  body: string;
  category: string | null;
  min_ai_level: AiLevel;
  status: KnowledgeStatus;
  tags: string[];
  safety_notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeInput {
  title: string;
  body: string;
  category?: string | null;
  min_ai_level?: AiLevel;
  tags?: string[];
  safety_notes?: string | null;
}

const BASE = "/api/admin/knowledge";

export interface KnowledgeFilters {
  status?: KnowledgeStatus;
  category?: string;
  q?: string;
  tag?: string;
}

export function listKnowledge(filters: KnowledgeFilters = {}): Promise<KnowledgeEntry[]> {
  const params = new URLSearchParams();
  if (filters.status) params.set("status_filter", filters.status);
  if (filters.category) params.set("category", filters.category);
  if (filters.q) params.set("q", filters.q);
  if (filters.tag) params.set("tag", filters.tag);
  const qs = params.toString();
  return apiFetch<KnowledgeEntry[]>(qs ? `${BASE}?${qs}` : BASE, { auth: true });
}

export function createKnowledge(input: KnowledgeInput): Promise<KnowledgeEntry> {
  return apiFetch<KnowledgeEntry>(BASE, { method: "POST", body: input, auth: true });
}

export function updateKnowledge(
  id: string,
  input: Partial<KnowledgeInput>,
): Promise<KnowledgeEntry> {
  return apiFetch<KnowledgeEntry>(`${BASE}/${id}`, { method: "PATCH", body: input, auth: true });
}

export type StatusAction = "publish" | "unpublish" | "retire";

export function transitionKnowledge(id: string, action: StatusAction): Promise<KnowledgeEntry> {
  return apiFetch<KnowledgeEntry>(`${BASE}/${id}/${action}`, { method: "POST", auth: true });
}
