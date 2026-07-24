/** Auth types and API calls (signup, login, current user). */

import { apiFetch, clearToken, setToken } from "@/lib/api";

export type UserRole = "customer" | "admin";

export interface AuthUser {
  id: string;
  role: UserRole;
  status: string;
  display_name: string | null;
  created_at: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export async function login(email: string, password: string): Promise<AuthUser> {
  const res = await apiFetch<TokenResponse>("/api/auth/login", {
    method: "POST",
    body: { email, password },
  });
  setToken(res.access_token);
  return res.user;
}

export async function signup(
  email: string,
  password: string,
  displayName?: string,
): Promise<AuthUser> {
  const res = await apiFetch<TokenResponse>("/api/auth/signup", {
    method: "POST",
    body: { email, password, display_name: displayName || null },
  });
  setToken(res.access_token);
  return res.user;
}

export function fetchMe(): Promise<AuthUser> {
  return apiFetch<AuthUser>("/api/auth/me", { auth: true });
}

export function logout(): void {
  clearToken();
}
