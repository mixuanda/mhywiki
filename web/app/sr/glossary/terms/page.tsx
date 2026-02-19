import EntityList from "@/components/entity-list";
import { loadCollection } from "@/lib/data";

export default async function SRTermsPage() {
  const rows = await loadCollection("sr", "glossary/terms");
  return (
    <EntityList
      title="SR Terms"
      subtitle="Keywords and mechanic definitions."
      items={rows}
    />
  );
}
