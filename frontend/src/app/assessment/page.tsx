"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { useAuth } from "@/components/AuthProvider";
import { ApiError } from "@/lib/api";
import {
  type AssessmentAnswers,
  type Goal,
  getAssessment,
  submitAssessment,
} from "@/lib/assessment";
import { type Profile, getProfile } from "@/lib/profile";

type SingleKey = "experience" | "stress_level" | "sleep_quality" | "energy_level";

const SINGLE_QUESTIONS: { key: SingleKey; label: string; options: [string, string][] }[] = [
  {
    key: "experience",
    label: "How much experience do you have with breathing or meditation?",
    options: [
      ["beginner", "New to it"],
      ["some", "Some experience"],
      ["experienced", "Experienced"],
    ],
  },
  {
    key: "stress_level",
    label: "How would you describe your current stress level?",
    options: [
      ["low", "Low"],
      ["moderate", "Moderate"],
      ["high", "High"],
    ],
  },
  {
    key: "sleep_quality",
    label: "How is your sleep lately?",
    options: [
      ["poor", "Poor"],
      ["fair", "Fair"],
      ["good", "Good"],
    ],
  },
  {
    key: "energy_level",
    label: "How are your energy levels day to day?",
    options: [
      ["low", "Low"],
      ["moderate", "Moderate"],
      ["high", "High"],
    ],
  },
];

const GOAL_OPTIONS: [Goal, string][] = [
  ["more_energy", "More energy"],
  ["better_sleep", "Better sleep"],
  ["less_stress", "Less stress"],
  ["emotional_balance", "Emotional balance"],
  ["focus", "Focus"],
  ["general_wellbeing", "General wellbeing"],
];

const MINUTES: number[] = [5, 10, 20];

const DEFAULT_SINGLE: Record<SingleKey, string> = {
  experience: "beginner",
  stress_level: "moderate",
  sleep_quality: "fair",
  energy_level: "moderate",
};

export default function AssessmentPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [single, setSingle] = useState<Record<SingleKey, string>>(DEFAULT_SINGLE);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [minutes, setMinutes] = useState(10);
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);

  // Redirect anonymous visitors to sign in.
  useEffect(() => {
    if (!authLoading && !user) router.replace("/login");
  }, [authLoading, user, router]);

  // Prefill from an existing assessment (so re-visiting edits, not duplicates).
  useEffect(() => {
    if (!user) return;
    let active = true;
    void (async () => {
      try {
        const [existing, existingProfile] = await Promise.all([getAssessment(), getProfile()]);
        if (active && existing) {
          const a = existing.answers;
          setSingle({
            experience: a.experience,
            stress_level: a.stress_level,
            sleep_quality: a.sleep_quality,
            energy_level: a.energy_level,
          });
          setGoals(a.goals ?? []);
          setMinutes(a.minutes_per_day);
          setNotes(a.notes ?? "");
        }
        if (active) setProfile(existingProfile);
      } catch {
        /* first-time users have none; ignore */
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [user]);

  function toggleGoal(g: Goal) {
    setGoals((prev) => (prev.includes(g) ? prev.filter((x) => x !== g) : [...prev, g]));
    setSaved(false);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    const payload = {
      ...single,
      goals,
      minutes_per_day: minutes,
      notes: notes.trim() || null,
    } as unknown as AssessmentAnswers;
    try {
      await submitAssessment(payload);
      setProfile(await getProfile());
      setSaved(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save your answers");
    } finally {
      setBusy(false);
    }
  }

  if (authLoading || (user && loading)) {
    return <p className="mx-auto max-w-2xl px-6 py-16 text-sm text-neutral-500">Loading…</p>;
  }
  if (!user) return null;

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-col gap-8 px-6 py-16">
      <div>
        <h1 className="text-3xl font-semibold">Your assessment</h1>
        <p className="mt-2 text-neutral-600 dark:text-neutral-300">
          A few quick questions so your guide can personalize your practice. This is for wellness
          and growth — not medical advice.
        </p>
      </div>

      {profile?.summary && (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5 dark:border-emerald-900 dark:bg-emerald-950">
          <h2 className="text-sm font-semibold text-emerald-800 dark:text-emerald-200">
            Your Energy Profile
          </h2>
          <p className="mt-1 text-sm text-emerald-900 dark:text-emerald-100">{profile.summary}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-8">
        {SINGLE_QUESTIONS.map((q) => (
          <fieldset key={q.key} className="flex flex-col gap-3">
            <legend className="text-sm font-medium">{q.label}</legend>
            <div className="flex flex-wrap gap-2">
              {q.options.map(([value, label]) => {
                const active = single[q.key] === value;
                return (
                  <button
                    key={value}
                    type="button"
                    onClick={() => {
                      setSingle((s) => ({ ...s, [q.key]: value }));
                      setSaved(false);
                    }}
                    className={
                      "rounded-full border px-4 py-2 text-sm transition " +
                      (active
                        ? "border-emerald-600 bg-emerald-600 text-white"
                        : "border-neutral-300 hover:bg-neutral-100 dark:border-neutral-700 dark:hover:bg-neutral-800")
                    }
                  >
                    {label}
                  </button>
                );
              })}
            </div>
          </fieldset>
        ))}

        <fieldset className="flex flex-col gap-3">
          <legend className="text-sm font-medium">What would you like to focus on?</legend>
          <div className="flex flex-wrap gap-2">
            {GOAL_OPTIONS.map(([value, label]) => {
              const active = goals.includes(value);
              return (
                <button
                  key={value}
                  type="button"
                  onClick={() => toggleGoal(value)}
                  className={
                    "rounded-full border px-4 py-2 text-sm transition " +
                    (active
                      ? "border-emerald-600 bg-emerald-600 text-white"
                      : "border-neutral-300 hover:bg-neutral-100 dark:border-neutral-700 dark:hover:bg-neutral-800")
                  }
                >
                  {label}
                </button>
              );
            })}
          </div>
        </fieldset>

        <fieldset className="flex flex-col gap-3">
          <legend className="text-sm font-medium">How much time can you practice each day?</legend>
          <div className="flex flex-wrap gap-2">
            {MINUTES.map((m) => {
              const active = minutes === m;
              return (
                <button
                  key={m}
                  type="button"
                  onClick={() => {
                    setMinutes(m);
                    setSaved(false);
                  }}
                  className={
                    "rounded-full border px-4 py-2 text-sm transition " +
                    (active
                      ? "border-emerald-600 bg-emerald-600 text-white"
                      : "border-neutral-300 hover:bg-neutral-100 dark:border-neutral-700 dark:hover:bg-neutral-800")
                  }
                >
                  {m} min
                </button>
              );
            })}
          </div>
        </fieldset>

        <label className="flex flex-col gap-2 text-sm">
          <span className="font-medium">Anything you&apos;d like your guide to keep in mind?</span>
          <textarea
            rows={3}
            value={notes}
            onChange={(e) => {
              setNotes(e.target.value);
              setSaved(false);
            }}
            placeholder="Optional"
            className="rounded-lg border border-neutral-300 px-3 py-2 dark:border-neutral-700 dark:bg-neutral-900"
          />
        </label>

        {error && <p className="text-sm text-red-600">{error}</p>}
        {saved && (
          <p className="text-sm text-emerald-600">
            Saved — your guide will use this to personalize your practice.
          </p>
        )}

        <button
          type="submit"
          disabled={busy}
          className="w-fit rounded-full bg-emerald-600 px-6 py-3 text-sm font-medium text-white transition hover:bg-emerald-700 disabled:opacity-60"
        >
          {busy ? "Saving…" : saved ? "Update answers" : "Save my answers"}
        </button>
      </form>
    </main>
  );
}
