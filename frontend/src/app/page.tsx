import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";

import { Reveal } from "@/components/Reveal";

export const metadata: Metadata = {
  title: "Great Energy Field — AI-guided energy practice & personal growth",
  description:
    "A training-type AI that learns where you are, guides your breathing, meditation, and energy practice step by step, and keeps you safe — built on a founder's method.",
};

/* ---------------------------------- icons --------------------------------- */

type IconName =
  | "spark"
  | "compass"
  | "shield"
  | "trend"
  | "chat"
  | "rings"
  | "journal"
  | "calendar"
  | "stairs"
  | "lock";

const ICON_PATHS: Record<IconName, ReactNode> = {
  spark: <path d="M12 2.5l1.9 5.6L19.5 10l-5.6 1.9L12 17.5l-1.9-5.6L4.5 10l5.6-1.9z" />,
  compass: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M15.5 8.5l-2 5-5 2 2-5z" />
    </>
  ),
  shield: (
    <>
      <path d="M12 3l7 3v5c0 4.5-3 7.6-7 9-4-1.4-7-4.5-7-9V6z" />
      <path d="M9 12l2 2 4-4" />
    </>
  ),
  trend: (
    <>
      <polyline points="3 17 9 11 13 15 21 7" />
      <polyline points="16 7 21 7 21 12" />
    </>
  ),
  chat: (
    <>
      <rect x="3" y="4" width="18" height="12" rx="3" />
      <path d="M8 16v3l4-3" />
    </>
  ),
  rings: (
    <>
      <circle cx="12" cy="12" r="3" />
      <circle cx="12" cy="12" r="7.5" />
    </>
  ),
  journal: (
    <>
      <rect x="5" y="3" width="14" height="18" rx="2" />
      <path d="M9 8h6M9 12h6M9 16h4" />
    </>
  ),
  calendar: (
    <>
      <rect x="4" y="5" width="16" height="15" rx="2" />
      <path d="M4 9h16M8 3v4M16 3v4" />
    </>
  ),
  stairs: <path d="M4 19h4v-5h4v-5h4V4" />,
  lock: (
    <>
      <rect x="5" y="11" width="14" height="9" rx="2" />
      <path d="M8 11V8a4 4 0 018 0v3" />
    </>
  ),
};

function Icon({ name, className = "h-6 w-6" }: { name: IconName; className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.6}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {ICON_PATHS[name]}
    </svg>
  );
}

const CARD_HOVER =
  "transition duration-300 hover:-translate-y-1 hover:border-emerald-300 hover:shadow-md dark:hover:border-emerald-800";

/* --------------------------------- content -------------------------------- */

const DIFFERENTIATORS: { icon: IconName; title: string; body: string }[] = [
  {
    icon: "spark",
    title: "Founder knowledge, not generic AI",
    body: "Answers are grounded in the founder's approved training method and safety boundaries — not open-web guesses.",
  },
  {
    icon: "compass",
    title: "It knows where you are",
    body: "The Agent tracks your stage, day count, and progress, so guidance fits your journey — not just your last message.",
  },
  {
    icon: "shield",
    title: "Rules & safety first",
    body: "Structured rules decide what happens next, and safety always overrides sales when you mention discomfort.",
  },
  {
    icon: "trend",
    title: "Grows with you",
    body: "Practice sessions, a journal, and weekly summaries turn small daily steps into visible, lasting change.",
  },
];

const STEPS: { title: string; body: string }[] = [
  { title: "Welcome", body: "Understand the promise: calm, energy, and steady personal growth." },
  { title: "We get to know you", body: "A short, wellness-framed assessment — no medical questions." },
  { title: "Set your goals", body: "Pick what matters: more energy, better sleep, less stress." },
  { title: "Your personalized plan", body: "We generate your Energy Profile and a starting plan." },
  { title: "Guided first practice", body: "Begin with simple breathing, gently guided step by step." },
  { title: "Begin your journey", body: "Practice, reflect, and watch your progress build over time." },
];

const FEATURES: { icon: IconName; title: string; body: string }[] = [
  { icon: "chat", title: "Basic AI Chat", body: "Ask questions and get grounded, on-method guidance any time." },
  { icon: "rings", title: "Energy Field AI Guide", body: "Deeper, personalized coaching that adapts to your practice." },
  { icon: "journal", title: "Practice journal", body: "Capture how each session felt and track your sensations." },
  { icon: "calendar", title: "Weekly summary", body: "A gentle recap of your week and what to focus on next." },
  { icon: "stairs", title: "Training stages", body: "Move from beginner to advanced as your practice deepens." },
  { icon: "lock", title: "Safety-first guardrails", body: "The Agent slows down and prioritizes your wellbeing when needed." },
];

const ENTRY_PERKS = [
  "Basic AI Chat",
  "Beginner assessment & Energy Profile",
  "Guided starter practices",
  "Limited personalization",
];

const COACHING_PERKS = [
  "Everything in Entry",
  "Energy Field AI Guide (deeper coaching)",
  "Personalized practice support",
  "Practice journal & weekly summary",
  "Priority guidance as you advance",
];

const FAQ: { q: string; a: string }[] = [
  {
    q: "Is this medical or therapy advice?",
    a: "No. Great Energy Field is a wellness and personal-growth practice — breathing, meditation, energy practice, and journaling. It does not diagnose, treat, or cure any condition, and it will encourage you to seek professional support if something feels serious.",
  },
  {
    q: "How is this different from a normal AI chatbot?",
    a: "A regular chatbot answers each message in isolation. Our Agent knows your training stage and history, follows the founder's structured method and safety rules, and guides an actual practice plan — so the guidance is consistent, personal, and safe.",
  },
  {
    q: "How do payments work?",
    a: "You can pay by card or PayPal. Crypto is also supported (USDT/USDC on BNB Smart Chain) as a 30-day access unlock. Your data is always saved, and you can renew whenever you like.",
  },
  {
    q: "Is my data private?",
    a: "Your account, assessment, and practice history are stored securely and used only to personalize your guidance. You stay in control of your journey.",
  },
];

/* --------------------------------- pieces --------------------------------- */

function SectionHeading({ eyebrow, title, sub }: { eyebrow: string; title: string; sub?: string }) {
  return (
    <div className="mx-auto max-w-2xl text-center">
      <p className="text-sm font-medium uppercase tracking-widest text-emerald-600">{eyebrow}</p>
      <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">{title}</h2>
      {sub && <p className="mt-4 text-neutral-600 dark:text-neutral-300">{sub}</p>}
    </div>
  );
}

function Check() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600"
      aria-hidden="true"
    >
      <path d="M5 12l4 4 10-11" />
    </svg>
  );
}

/* ----------------------------------- page --------------------------------- */

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div
          className="pointer-events-none absolute inset-x-0 top-0 h-[520px]"
          style={{ background: "radial-gradient(60% 60% at 50% 0%, rgba(16,185,129,0.14), transparent)" }}
        />
        <div className="relative mx-auto grid max-w-6xl items-center gap-12 px-6 py-20 lg:grid-cols-2 lg:py-28">
          <Reveal className="flex flex-col gap-6">
            <span className="inline-flex w-fit items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-300">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 motion-safe:animate-pulse" />
              AI-guided wellness & energy practice
            </span>
            <h1 className="text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl lg:text-6xl">
              Your personal guide to energy, calm, and steady growth
            </h1>
            <p className="max-w-xl text-lg text-neutral-600 dark:text-neutral-300">
              A training-type AI that learns where you are, guides your breathing, meditation, and
              energy practice step by step, and keeps you safe — built on a founder&apos;s method,
              not generic chatbot answers.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link
                href="/login"
                className="rounded-full bg-emerald-600 px-6 py-3 text-sm font-medium text-white shadow-sm transition hover:-translate-y-0.5 hover:bg-emerald-700 hover:shadow-md"
              >
                Start your journey
              </Link>
              <Link
                href="#how-it-works"
                className="rounded-full border border-neutral-300 px-6 py-3 text-sm font-medium transition hover:-translate-y-0.5 hover:bg-neutral-100 dark:border-neutral-700 dark:hover:bg-neutral-900"
              >
                See how it works
              </Link>
            </div>
            <div className="flex flex-wrap gap-2 pt-2">
              {["Breathing", "Meditation", "Energy practice", "Journaling"].map((t) => (
                <span
                  key={t}
                  className="rounded-full bg-neutral-100 px-3 py-1 text-xs text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300"
                >
                  {t}
                </span>
              ))}
            </div>
          </Reveal>
          <Reveal delay={150} className="flex justify-center lg:justify-end">
            <div className="relative w-full max-w-md">
              <div
                className="pointer-events-none absolute -inset-6 rounded-[2.5rem] blur-2xl"
                style={{ background: "radial-gradient(50% 50% at 50% 50%, rgba(16,185,129,0.25), transparent)" }}
              />
              <Image
                src="/logo.png"
                alt="Great Energy Field"
                width={768}
                height={512}
                priority
                sizes="(max-width: 1024px) 100vw, 448px"
                className="relative h-auto w-full rounded-3xl shadow-xl ring-1 ring-emerald-200/50 dark:ring-emerald-900/40"
              />
              <div className="absolute left-0 top-8 rounded-2xl border border-neutral-200 bg-white/90 px-3 py-2 text-xs shadow-sm backdrop-blur motion-safe:animate-bounce [animation-duration:3s] dark:border-neutral-800 dark:bg-neutral-900/90">
                <span className="mr-1 inline-block h-2 w-2 rounded-full bg-emerald-500" />
                Breathing · 5 min
              </div>
              <div className="absolute bottom-8 right-0 rounded-2xl border border-neutral-200 bg-white/90 px-3 py-2 text-xs shadow-sm backdrop-blur motion-safe:animate-bounce [animation-delay:1.5s] [animation-duration:3s] dark:border-neutral-800 dark:bg-neutral-900/90">
                <span className="mr-1 inline-block h-2 w-2 rounded-full bg-emerald-500" />
                Day 7 · stable
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* Differentiators */}
      <section className="border-t border-neutral-200 py-20 dark:border-neutral-800">
        <div className="mx-auto max-w-6xl px-6">
          <Reveal>
            <SectionHeading
              eyebrow="Why it's different"
              title="Not a chatbot — a guide that knows you"
              sub="Great Energy Field is a Knowledge Base, a User-State system, a Rules engine, and an AI guide working together."
            />
          </Reveal>
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {DIFFERENTIATORS.map((d, i) => (
              <Reveal key={d.title} delay={i * 80}>
                <div className={`h-full rounded-2xl border border-neutral-200 p-6 dark:border-neutral-800 ${CARD_HOVER}`}>
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-950">
                    <Icon name={d.icon} />
                  </div>
                  <h3 className="mt-4 text-base font-semibold">{d.title}</h3>
                  <p className="mt-2 text-sm text-neutral-600 dark:text-neutral-400">{d.body}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="scroll-mt-24 bg-emerald-50/50 py-20 dark:bg-neutral-900/50">
        <div className="mx-auto max-w-6xl px-6">
          <Reveal>
            <SectionHeading
              eyebrow="How it works"
              title="From first hello to daily practice"
              sub="A gentle onboarding that helps you feel understood, supported, and guided — one step at a time."
            />
          </Reveal>
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {STEPS.map((s, i) => (
              <Reveal key={s.title} delay={i * 80}>
                <div className={`h-full rounded-2xl border border-neutral-200 bg-white p-6 dark:border-neutral-800 dark:bg-neutral-950 ${CARD_HOVER}`}>
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-600 text-sm font-semibold text-white">
                    {i + 1}
                  </div>
                  <h3 className="mt-4 text-base font-semibold">{s.title}</h3>
                  <p className="mt-2 text-sm text-neutral-600 dark:text-neutral-400">{s.body}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20">
        <div className="mx-auto max-w-6xl px-6">
          <Reveal>
            <SectionHeading eyebrow="What you get" title="Everything to build a lasting practice" />
          </Reveal>
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((f, i) => (
              <Reveal key={f.title} delay={i * 70}>
                <div className={`flex h-full gap-4 rounded-2xl border border-neutral-200 p-6 dark:border-neutral-800 ${CARD_HOVER}`}>
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-950">
                    <Icon name={f.icon} />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold">{f.title}</h3>
                    <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">{f.body}</p>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="scroll-mt-24 bg-emerald-50/50 py-20 dark:bg-neutral-900/50">
        <div className="mx-auto max-w-5xl px-6">
          <Reveal>
            <SectionHeading
              eyebrow="Membership"
              title="Choose how you want to grow"
              sub="Pay by card, PayPal, or crypto (USDT/USDC on BNB Smart Chain)."
            />
          </Reveal>
          <div className="mt-14 grid items-start gap-6 md:grid-cols-2">
            <Reveal>
              <div className={`rounded-3xl border border-neutral-200 bg-white p-8 dark:border-neutral-800 dark:bg-neutral-950 ${CARD_HOVER}`}>
                <h3 className="text-lg font-semibold">Entry</h3>
                <p className="mt-1 text-sm text-neutral-500">Start exploring your practice.</p>
                <div className="mt-6 flex items-baseline gap-1">
                  <span className="text-4xl font-semibold">$49</span>
                  <span className="text-sm text-neutral-500">one-time</span>
                </div>
                <ul className="mt-6 flex flex-col gap-3 text-sm">
                  {ENTRY_PERKS.map((p) => (
                    <li key={p} className="flex gap-2">
                      <Check />
                      <span className="text-neutral-700 dark:text-neutral-300">{p}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  href="/login"
                  className="mt-8 block rounded-full border border-emerald-600 px-6 py-3 text-center text-sm font-medium text-emerald-700 transition hover:bg-emerald-50 dark:text-emerald-400 dark:hover:bg-emerald-950"
                >
                  Get started
                </Link>
              </div>
            </Reveal>

            <Reveal delay={120}>
              <div className="relative rounded-3xl border-2 border-emerald-500 bg-white p-8 shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-lg dark:bg-neutral-950">
                <span className="absolute -top-3 right-6 rounded-full bg-emerald-600 px-3 py-1 text-xs font-medium text-white">
                  Most guidance
                </span>
                <h3 className="text-lg font-semibold">Monthly AI Coaching</h3>
                <p className="mt-1 text-sm text-neutral-500">Personalized, deeper guidance.</p>
                <div className="mt-6 flex items-baseline gap-1">
                  <span className="text-4xl font-semibold">$199</span>
                  <span className="text-sm text-neutral-500">/ month</span>
                </div>
                <ul className="mt-6 flex flex-col gap-3 text-sm">
                  {COACHING_PERKS.map((p) => (
                    <li key={p} className="flex gap-2">
                      <Check />
                      <span className="text-neutral-700 dark:text-neutral-300">{p}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  href="/login"
                  className="mt-8 block rounded-full bg-emerald-600 px-6 py-3 text-center text-sm font-medium text-white transition hover:bg-emerald-700"
                >
                  Start coaching
                </Link>
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      {/* Safety / positioning */}
      <section className="py-20">
        <div className="mx-auto max-w-4xl px-6">
          <Reveal>
            <div className="flex flex-col items-center gap-4 rounded-3xl border border-neutral-200 p-10 text-center dark:border-neutral-800">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 dark:bg-emerald-950">
                <Icon name="shield" />
              </div>
              <h2 className="text-2xl font-semibold">Wellness, not medical</h2>
              <p className="max-w-2xl text-neutral-600 dark:text-neutral-300">
                Great Energy Field supports breathing, meditation, energy practice, and personal
                growth. It is not medical diagnosis or treatment and makes no promises of healing or
                cures. If you ever mention discomfort or distress, the guide pauses, prioritizes your
                safety, and never pushes an upgrade.
              </p>
            </div>
          </Reveal>
        </div>
      </section>

      {/* FAQ */}
      <section className="bg-emerald-50/50 py-20 dark:bg-neutral-900/50">
        <div className="mx-auto max-w-3xl px-6">
          <Reveal>
            <SectionHeading eyebrow="FAQ" title="Good questions, clear answers" />
          </Reveal>
          <div className="mt-12 flex flex-col gap-3">
            {FAQ.map((item, i) => (
              <Reveal key={item.q} delay={i * 60}>
                <details
                  name="faq"
                  className="group rounded-2xl border border-neutral-200 bg-white p-5 transition hover:border-emerald-300 dark:border-neutral-800 dark:bg-neutral-950 dark:hover:border-emerald-800"
                >
                  <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-base font-medium">
                    {item.q}
                    <span className="text-lg text-emerald-600 transition-transform duration-300 group-open:rotate-45">
                      +
                    </span>
                  </summary>
                  <p className="mt-3 text-sm text-neutral-600 dark:text-neutral-400">{item.a}</p>
                </details>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20">
        <div className="mx-auto max-w-6xl px-6">
          <Reveal>
            <div className="relative overflow-hidden rounded-3xl bg-emerald-600 px-8 py-16 text-center text-white">
              <div
                className="pointer-events-none absolute inset-0"
                style={{ background: "radial-gradient(60% 80% at 50% 0%, rgba(255,255,255,0.18), transparent)" }}
              />
              <div className="relative flex flex-col items-center gap-6">
                <h2 className="max-w-2xl text-3xl font-semibold tracking-tight sm:text-4xl">
                  Begin your energy practice today
                </h2>
                <p className="max-w-xl text-emerald-50">
                  Create your account, complete a short assessment, and take your first guided
                  breath. Your journey starts in minutes.
                </p>
                <Link
                  href="/login"
                  className="rounded-full bg-white px-7 py-3 text-sm font-semibold text-emerald-700 transition hover:-translate-y-0.5 hover:bg-emerald-50 hover:shadow-md"
                >
                  Start your journey
                </Link>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-neutral-200 py-10 dark:border-neutral-800">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 text-sm text-neutral-500 sm:flex-row">
          <Link href="/" className="flex items-center gap-2">
          <Image
            src="/logo-mark.png"
            alt=""
            width={40}
            height={40}
            unoptimized
            priority
            className="h-9 w-9 object-contain"
          />
          <span className="text-lg font-semibold leading-none tracking-tight text-emerald-600">
            Great Energy Field
          </span>
        </Link>
          <div className="flex gap-6">
            <Link href="#how-it-works" className="transition hover:text-emerald-600">
              How it works
            </Link>
            <Link href="#pricing" className="transition hover:text-emerald-600">
              Pricing
            </Link>
            <Link href="/login" className="transition hover:text-emerald-600">
              Sign in
            </Link>
          </div>
          <span>© 2026 Great Energy Field</span>
        </div>
      </footer>
    </div>
  );
}
