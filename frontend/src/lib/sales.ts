/** Sales trigger admin API client. */

import { apiFetch } from "@/lib/api";
import type { RuleConditions, RuleStatus } from "@/lib/rules";

export type SalesMode = "allow" | "block";
export type Package = "none" | "entry_49" | "coaching_199";

export interface SalesTrigger {
  id: string;
  name: string;
  description: string | null;
  conditions: RuleConditions & Record<string, unknown>;
  target_package: Package | null;
  mode: SalesMode;
  priority: number;
  status: RuleStatus;
  cooldown_seconds: number | null;
  created_at: string;
  updated_at: string;
}

export interface SalesTriggerInput {
  name?: string;
  description?: string | null;
  conditions?: RuleConditions;
  target_package?: Package | null;
  mode?: SalesMode;
  priority?: number;
  status?: RuleStatus;
  cooldown_seconds?: number | null;
}

const BASE = "/api/admin/sales-triggers";

export const listSalesTriggers = () => apiFetch<SalesTrigger[]>(BASE, { auth: true });
export const createSalesTrigger = (input: SalesTriggerInput) =>
  apiFetch<SalesTrigger>(BASE, { method: "POST", body: input, auth: true });
export const updateSalesTrigger = (id: string, input: SalesTriggerInput) =>
  apiFetch<SalesTrigger>(`${BASE}/${id}`, { method: "PATCH", body: input, auth: true });
export const deleteSalesTrigger = (id: string) =>
  apiFetch<void>(`${BASE}/${id}`, { method: "DELETE", auth: true });
