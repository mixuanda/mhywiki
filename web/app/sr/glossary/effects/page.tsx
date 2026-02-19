import EntityList from "@/components/entity-list";
import { loadCollection } from "@/lib/data";

export default async function SREffectsPage() {
  const rows = await loadCollection("sr", "glossary/effects");
  return (
    <EntityList
      title="SR Effects"
      subtitle="Buff/debuff/status glossary entries."
      items={rows}
      facets={[{ key: "effectType", label: "Category" }]}
    />
  );
}
