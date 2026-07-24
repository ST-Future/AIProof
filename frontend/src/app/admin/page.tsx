import { BackendStatus } from "./BackendStatus";

export default function AdminHome() {
  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold">Founder / Admin dashboard</h1>
        <p className="text-neutral-600 dark:text-neutral-400">
          Manage the Agent: knowledge, training, rules, prompts, safety, and logs.
          Pick a section from the left. CRUD is wired up during Milestone 1.
        </p>
      </header>

      <BackendStatus />
    </div>
  );
}
