/** Prompt versioning admin API client. */

import { apiFetch } from "@/lib/api";

export type PromptStatus = "draft" | "published" | "archived";

export interface Prompt {
  id: string;
  key: string;
  version: number;
  content: string;
  status: PromptStatus;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface PromptCreateInput {
  key: string;
  content: string;
  notes?: string | null;
}

export interface PromptUpdateInput {
  content?: string;
  notes?: string | null;
}

const BASE = "/api/admin/prompts";

export const listPrompts = () => apiFetch<Prompt[]>(BASE, { auth: true });
export const createPrompt = (input: PromptCreateInput) =>
  apiFetch<Prompt>(BASE, { method: "POST", body: input, auth: true });
export const updatePrompt = (id: string, input: PromptUpdateInput) =>
  apiFetch<Prompt>(`${BASE}/${id}`, { method: "PATCH", body: input, auth: true });
export const deletePrompt = (id: string) =>
  apiFetch<void>(`${BASE}/${id}`, { method: "DELETE", auth: true });
export const publishPrompt = (versionId: string) =>
  apiFetch<Prompt>(`${BASE}/publish`, { method: "POST", body: { version_id: versionId }, auth: true });
export const rollbackPrompt = (key: string) =>
  apiFetch<Prompt>(`${BASE}/rollback`, { method: "POST", body: { key }, auth: true });
