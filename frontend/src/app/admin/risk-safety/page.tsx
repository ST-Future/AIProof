import { BlockedClaimManager } from "@/components/admin/BlockedClaimManager";
import { RiskRuleManager } from "@/components/admin/RiskRuleManager";

export default function Page() {
  return (
    <div className="flex flex-col gap-10">
      <div>
        <h1 className="text-2xl font-semibold">Risk &amp; Safety</h1>
        <p className="mt-1 text-sm text-neutral-500">
          Detect risky messages and keep the Agent within wellness boundaries.
        </p>
      </div>
      <RiskRuleManager />
      <div className="border-t border-neutral-200 dark:border-neutral-800" />
      <BlockedClaimManager />
    </div>
  );
}
