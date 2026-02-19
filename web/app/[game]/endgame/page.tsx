import { notFound } from "next/navigation";

import SectionGrid from "@/components/section-grid";
import { ENDGAME_MODES } from "@/lib/sections";

interface EndgameIndexPageProps {
  params: Promise<{ game: string }>;
}

export default async function EndgameIndexPage({ params }: EndgameIndexPageProps) {
  const { game } = await params;
  if (game !== "gi" && game !== "sr") {
    notFound();
  }

  const modes = ENDGAME_MODES[game];
  const items = Object.entries(modes).map(([slug, config]) => ({
    href: `/${game}/endgame/${slug}`,
    title: config.title,
    description: config.description,
  }));

  return <SectionGrid heading={`${game.toUpperCase()} Endgame Modes`} items={items} />;
}
