/** Customer background-assessment API client. */

import { apiFetch } from "@/lib/api";

export type Experience = "beginner" | "some" | "experienced";
export type Level = "low" | "moderate" | "high";
export type SleepQuality = "poor" | "fair" | "good";
export type Goal =
  | "more_energy"
  | "better_sleep"
  | "less_stress"
  | "emotional_balance"
  | "focus"
  | "general_wellbeing";
export type MinutesPerDay = 5 | 10 | 20;

export interface AssessmentAnswers {
  experience: Experience;
  stress_level: Level;
  sleep_quality: SleepQuality;
  energy_level: Level;
  goals: Goal[];
  minutes_per_day: MinutesPerDay;
  notes: string | null;
}

export interface Assessment {
  id: string;
  answers: AssessmentAnswers;
  version: number;
  submitted_at: string | null;
  created_at: string;
  updated_at: string;
}

export const getAssessment = () =>
  apiFetch<Assessment | null>("/api/assessment", { auth: true });

export const submitAssessment = (answers: AssessmentAnswers) =>
  apiFetch<Assessment>("/api/assessment/submit", { method: "POST", body: answers, auth: true });
