import type { AdminSection } from "@/components/admin/sections";

/**
 * Empty stateful shell for an admin section: title, description, an optional
 * "New" action (placeholder), and an empty-state list. The real CRUD lands in
 * Milestone 1 (Week 2 onward).
 */
export function SectionPlaceholder({ section }: { section: AdminSection }) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{section.label}</h1>
          <p className="mt-1 text-sm text-neutral-500">{section.description}</p>
        </div>
        {section.newLabel && (
          <button
            type="button"
            disabled
            title="Available in Milestone 1"
            className="cursor-not-allowed rounded-full bg-emerald-600 px-4 py-2 text-sm font-medium text-white opacity-50"
          >
            {section.newLabel}
          </button>
        )}
      </div>

      <div className="rounded-2xl border border-dashed border-neutral-300 p-12 text-center dark:border-neutral-700">
        <p className="text-sm text-neutral-500">No items yet.</p>
        <p className="mt-1 text-xs text-neutral-400">This section is wired up in Milestone 1.</p>
      </div>
    </div>
  );
}
