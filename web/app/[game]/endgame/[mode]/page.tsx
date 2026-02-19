import { notFound } from "next/navigation";

import EntityList from "@/components/entity-list";
import SectionGrid from "@/components/section-grid";
import { listDivergentUniverseVersions, loadCollection } from "@/lib/data";
import { ENDGAME_MODES } from "@/lib/sections";

interface EndgameModePageProps {
  params: Promise<{ game: string; mode: string }>;
}

export default async function EndgameModePage({ params }: EndgameModePageProps) {
  const { game, mode } = await params;
  if (game !== "gi" && game !== "sr") {
    notFound();
  }

  const config = ENDGAME_MODES[game][mode];
  if (!config) {
    notFound();
  }

  if (game === "sr" && mode === "divergentuniverse") {
    const versions = await listDivergentUniverseVersions();
    const items = versions.map((version) => ({
      href: `/sr/endgame/divergentuniverse/${version}`,
      title: `Divergent Universe ${version}`,
      description: `Cycle datasets for version ${version}.`,
    }));
    return <SectionGrid heading={config.title} items={items} />;
  }

  const rows = await loadCollection(game, config.dataDir);

  return (
    <EntityList
      title={config.title}
      subtitle={config.description}
      items={rows}
    />
  );
}
