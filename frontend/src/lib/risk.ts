/** Risk & Safety admin API client (risk rules + blocked claims). */

import { apiFetch } from "@/lib/api";

export type RiskSeverity = "low" | "medium" | "high";

export interface RiskRule {
  id: string;
  category: string;
  keywords: string[];
  severity: RiskSeverity;
  fallback_action: Record<string, unknown> | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RiskRuleInput {
  category?: string;
  keywords?: string[];
  severity?: RiskSeverity;
  fallback_action?: Record<string, unknown> | null;
  is_active?: boolean;
}

export interface BlockedClaim {
  id: string;
  term: string;
  note: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BlockedClaimInput {
  term?: string;
  note?: string | null;
  is_active?: boolean;
}

const RISK = "/api/admin/risk-rules";
const CLAIMS = "/api/admin/blocked-claims";

export const listRiskRules = () => apiFetch<RiskRule[]>(RISK, { auth: true });
export const createRiskRule = (input: RiskRuleInput) =>
  apiFetch<RiskRule>(RISK, { method: "POST", body: input, auth: true });
export const updateRiskRule = (id: string, input: RiskRuleInput) =>
  apiFetch<RiskRule>(`${RISK}/${id}`, { method: "PATCH", body: input, auth: true });
export const deleteRiskRule = (id: string) =>
  apiFetch<void>(`${RISK}/${id}`, { method: "DELETE", auth: true });

export const listBlockedClaims = () => apiFetch<BlockedClaim[]>(CLAIMS, { auth: true });
export const createBlockedClaim = (input: BlockedClaimInput) =>
  apiFetch<BlockedClaim>(CLAIMS, { method: "POST", body: input, auth: true });
export const updateBlockedClaim = (id: string, input: BlockedClaimInput) =>
  apiFetch<BlockedClaim>(`${CLAIMS}/${id}`, { method: "PATCH", body: input, auth: true });
export const deleteBlockedClaim = (id: string) =>
  apiFetch<void>(`${CLAIMS}/${id}`, { method: "DELETE", auth: true });
