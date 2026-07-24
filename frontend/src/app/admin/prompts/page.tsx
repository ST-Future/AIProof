import { SectionPlaceholder } from "@/components/admin/SectionPlaceholder";
import { getSection } from "@/components/admin/sections";

export default function Page() {
  return <SectionPlaceholder section={getSection("prompts")} />;
}
