/** Admin customer directory API client. */

import { apiFetch } from "@/lib/api";

export interface CustomerSummary {
  id: string;
  email: string | null;
  display_name: string | null;
  created_at: string;
  package: "none" | "entry_49" | "coaching_199";
  access_state: "inactive" | "active" | "expired" | "paused";
  has_assessment: boolean;
  energy_summary: string | null;
  stage: string | null;
  day_count: number | null;
  completed_sessions: number | null;
}

export const listCustomers = () =>
  apiFetch<CustomerSummary[]>("/api/admin/customers", { auth: true });
