import { notFound } from "next/navigation";

import EntityList from "@/components/entity-list";
import { loadDivergentUniverseVersion } from "@/lib/data";

interface DUVersionPageProps {
  params: Promise<{ version: string }>;
}

export default async function DUVersionPage({ params }: DUVersionPageProps) {
  const { version } = await params;
  const rows = await loadDivergentUniverseVersion(version);

  if (!rows.length) {
    notFound();
  }

  return (
    <EntityList
      title={`Divergent Universe ${version}`}
      subtitle="One file per cycle/season in this DU version bucket."
      items={rows}
    />
  );
}
