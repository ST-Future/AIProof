/** Training stages + modules admin API client. */

import { apiFetch } from "@/lib/api";
import type { AiLevel } from "@/lib/knowledge";

type Json = Record<string, unknown>;

export interface Stage {
  id: string;
  key: string;
  name: string;
  description: string | null;
  order_index: number;
  entry_conditions: Json | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface StageInput {
  key?: string;
  name?: string;
  description?: string | null;
  order_index?: number;
  entry_conditions?: Json | null;
  is_active?: boolean;
}

export interface Module {
  id: string;
  key: string;
  name: string;
  target_user: string | null;
  stage_id: string | null;
  goal: string | null;
  steps: string[];
  duration_minutes: number | null;
  stop_conditions: Json | null;
  next_module_id: string | null;
  next_stage_id: string | null;
  min_ai_level: AiLevel;
  order_index: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ModuleInput {
  key?: string;
  name?: string;
  target_user?: string | null;
  stage_id?: string | null;
  goal?: string | null;
  steps?: string[];
  duration_minutes?: number | null;
  stop_conditions?: Json | null;
  next_module_id?: string | null;
  next_stage_id?: string | null;
  min_ai_level?: AiLevel;
  order_index?: number;
  is_active?: boolean;
}

const STAGES = "/api/admin/stages";
const MODULES = "/api/admin/training-modules";

export const listStages = () => apiFetch<Stage[]>(STAGES, { auth: true });
export const createStage = (input: StageInput) =>
  apiFetch<Stage>(STAGES, { method: "POST", body: input, auth: true });
export const updateStage = (id: string, input: StageInput) =>
  apiFetch<Stage>(`${STAGES}/${id}`, { method: "PATCH", body: input, auth: true });
export const deleteStage = (id: string) =>
  apiFetch<void>(`${STAGES}/${id}`, { method: "DELETE", auth: true });

export const listModules = () => apiFetch<Module[]>(MODULES, { auth: true });
export const createModule = (input: ModuleInput) =>
  apiFetch<Module>(MODULES, { method: "POST", body: input, auth: true });
export const updateModule = (id: string, input: ModuleInput) =>
  apiFetch<Module>(`${MODULES}/${id}`, { method: "PATCH", body: input, auth: true });
export const deleteModule = (id: string) =>
  apiFetch<void>(`${MODULES}/${id}`, { method: "DELETE", auth: true });
