import Link from "next/link";

import SectionGrid from "@/components/section-grid";

export default function HomePage() {
  return (
    <>
      <section className="section-block">
        <header className="section-head">
          <h1>Combat-Only Wiki</h1>
          <p>
            Lightweight GI/SR wiki generated from normalized one-entity-per-file JSON data.
            Lore, story, quests, and admin-only content are removed from the main site output.
          </p>
        </header>
      </section>

      <SectionGrid
        heading="Choose Game"
        items={[
          {
            href: "/gi",
            title: "Genshin Impact",
            description: "Monsters, characters, weapons, artifacts, endgame, wishes, tutorials, formulas, and credits.",
          },
          {
            href: "/sr",
            title: "Honkai: Star Rail",
            description: "Monsters, characters, light cones, relics, endgame, warp banners, glossary, and combat stats.",
          },
        ]}
      />

      <section className="section-block">
        <header className="section-head">
          <h1>Data Maintenance</h1>
          <p>
            Use <code>tools/extract_from_site.py</code> to regenerate datasets from a local raw
            <code> site/</code> mirror.
          </p>
          <p>
            <Link href="/gi">Browse GI</Link> | <Link href="/sr">Browse SR</Link>
          </p>
        </header>
      </section>
    </>
  );
}
