import { notFound } from "next/navigation";

import EntityList from "@/components/entity-list";
import { loadCollection } from "@/lib/data";
import { SECTION_CONFIG } from "@/lib/sections";

interface SectionPageProps {
  params: Promise<{ game: string; section: string }>;
}

export default async function SectionPage({ params }: SectionPageProps) {
  const { game, section } = await params;
  if (game !== "gi" && game !== "sr") {
    notFound();
  }

  const config = SECTION_CONFIG[game][section];
  if (!config) {
    notFound();
  }

  const rows = await loadCollection(game, config.dataDir);

  return (
    <EntityList
      title={config.title}
      subtitle={config.description}
      items={rows}
      facets={config.facets}
    />
  );
}
