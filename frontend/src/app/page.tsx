import Link from "next/link";

const differentiators = [
  {
    title: "Founder knowledge",
    body: "Answers are grounded in the founder's approved training method, not generic AI text.",
  },
  {
    title: "Knows where you are",
    body: "The Agent tracks your training stage, day count, and progress — not just the last message.",
  },
  {
    title: "Rules & safety first",
    body: "Structured rules control what happens next; safety always overrides sales.",
  },
];

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-4xl flex-col justify-center gap-16 px-6 py-20">
      <section className="flex flex-col gap-6">
        <p className="text-sm font-medium uppercase tracking-widest text-emerald-600">
          Great Energy Field
        </p>
        <h1 className="text-4xl font-semibold leading-tight sm:text-5xl">
          AI-guided energy practice and personal growth
        </h1>
        <p className="max-w-2xl text-lg text-neutral-600 dark:text-neutral-300">
          A training-type AI Agent that delivers the founder&apos;s method to each
          person — breathing, meditation, energy practice, journaling, and steady
          personal growth.
        </p>
        <div className="flex gap-4">
          <Link
            href="/admin"
            className="rounded-full bg-emerald-600 px-6 py-3 text-sm font-medium text-white transition hover:bg-emerald-700"
          >
            Admin dashboard
          </Link>
        </div>
      </section>

      <section className="grid gap-6 sm:grid-cols-3">
        <h2 className="sr-only">Why this AI is different</h2>
        {differentiators.map((d) => (
          <div
            key={d.title}
            className="rounded-2xl border border-neutral-200 p-6 dark:border-neutral-800"
          >
            <h3 className="mb-2 text-base font-semibold">{d.title}</h3>
            <p className="text-sm text-neutral-600 dark:text-neutral-400">{d.body}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
