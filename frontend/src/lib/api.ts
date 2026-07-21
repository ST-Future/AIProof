/**
 * Thin client for the Great Energy Field FastAPI backend.
 *
 * The backend base URL comes from NEXT_PUBLIC_API_BASE_URL and defaults to the
 * local FastAPI dev server. All future endpoints (/api/chat, /api/training/*,
 * /api/admin/*) are called through here with the Supabase JWT as a bearer token.
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export interface HealthResponse {
  status: string;
  service: string;
  env: string;
  database: string;
}

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { Accept: "application/json", ...(init?.headers ?? {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

export function getHealth(): Promise<HealthResponse> {
  return apiGet<HealthResponse>("/health");
}
