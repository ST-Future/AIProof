/** Agent rules admin API client. */

import { apiFetch } from "@/lib/api";

export type RuleStatus = "draft" | "active" | "inactive";

export interface RuleConditions {
  stages?: string[];
  intents?: string[];
  risks?: string[];
  min_completed_sessions?: number;
  max_completed_sessions?: number;
  min_day_count?: number;
}

export interface RuleActions {
  type: string;
  disable_sales?: boolean;
  allow_sales?: boolean;
  lower_difficulty?: boolean;
  cooldown_seconds?: number;
  message_hint?: string;
}

export interface Rule {
  id: string;
  name: string;
  description: string | null;
  conditions: RuleConditions & Record<string, unknown>;
  actions: RuleActions & Record<string, unknown>;
  priority: number;
  status: RuleStatus;
  cooldown_seconds: number | null;
  is_safety_override: boolean;
  created_at: string;
  updated_at: string;
}

export interface RuleInput {
  name?: string;
  description?: string | null;
  conditions?: RuleConditions;
  actions?: RuleActions;
  priority?: number;
  status?: RuleStatus;
  cooldown_seconds?: number | null;
  is_safety_override?: boolean;
}

const BASE = "/api/admin/rules";

export const listRules = () => apiFetch<Rule[]>(BASE, { auth: true });
export const createRule = (input: RuleInput) =>
  apiFetch<Rule>(BASE, { method: "POST", body: input, auth: true });
export const updateRule = (id: string, input: RuleInput) =>
  apiFetch<Rule>(`${BASE}/${id}`, { method: "PATCH", body: input, auth: true });
export const deleteRule = (id: string) =>
  apiFetch<void>(`${BASE}/${id}`, { method: "DELETE", auth: true });
