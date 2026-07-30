/** Customer Energy Profile API client. */

import { apiFetch } from "@/lib/api";

export interface Profile {
  id: string;
  summary: string | null;
  traits: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export const getProfile = () => apiFetch<Profile | null>("/api/profile", { auth: true });
