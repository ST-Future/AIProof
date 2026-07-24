/** Central definition of the Founder/Admin sections (nav + section pages). */

export interface AdminSection {
  slug: string;
  href: string;
  label: string;
  description: string;
  /** Label for the "New" action; omitted for read-only/log sections. */
  newLabel?: string;
}

export const ADMIN_SECTIONS: AdminSection[] = [
  {
    slug: "knowledge",
    href: "/admin/knowledge",
    label: "Knowledge",
    description: "Founder-approved content: draft, publish, unpublish, retire.",
    newLabel: "New entry",
  },
  {
    slug: "training-plans",
    href: "/admin/training-plans",
    label: "Training Plans",
    description: "Practice modules: steps, duration, goals, stop conditions, next stage.",
    newLabel: "New module",
  },
  {
    slug: "stages",
    href: "/admin/stages",
    label: "Stages",
    description: "Journey stages and progression conditions.",
    newLabel: "New stage",
  },
  {
    slug: "rules",
    href: "/admin/rules",
    label: "Rules",
    description: "IF/THEN decision rules: conditions, actions, priority, safety override.",
    newLabel: "New rule",
  },
  {
    slug: "prompts",
    href: "/admin/prompts",
    label: "Prompts",
    description: "Versioned prompts with publish and rollback.",
    newLabel: "New prompt",
  },
  {
    slug: "risk-safety",
    href: "/admin/risk-safety",
    label: "Risk & Safety",
    description: "Risk categories, keywords, severity, and safe fallbacks.",
    newLabel: "New risk rule",
  },
  {
    slug: "sales-triggers",
    href: "/admin/sales-triggers",
    label: "Sales Triggers",
    description: "When package explanation or upsell is allowed or blocked.",
    newLabel: "New trigger",
  },
  {
    slug: "agent-runs",
    href: "/admin/agent-runs",
    label: "Agent Runs",
    description: "Execution logs: intent, risk, rules, knowledge, prompt, tokens, latency.",
  },
  {
    slug: "customers",
    href: "/admin/customers",
    label: "Customers",
    description: "Customer accounts, training state, and manual overrides.",
  },
  {
    slug: "quality-feedback",
    href: "/admin/quality-feedback",
    label: "Quality Feedback",
    description: "Flag answers: too general, inaccurate, too strong/weak, unsafe.",
  },
];

export function getSection(slug: string): AdminSection {
  const section = ADMIN_SECTIONS.find((s) => s.slug === slug);
  if (!section) throw new Error(`Unknown admin section: ${slug}`);
  return section;
}
