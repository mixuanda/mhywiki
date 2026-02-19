import SectionGrid from "@/components/section-grid";

export default function SRPage() {
  return (
    <>
      <SectionGrid
        heading="SR Core Data"
        items={[
          { href: "/sr/characters", title: "Characters", description: "Character combat sheets." },
          { href: "/sr/lightcones", title: "Light Cones", description: "Light cone records." },
          { href: "/sr/relics", title: "Relics", description: "Relic set data." },
          { href: "/sr/enemies", title: "Monsters + Analysis", description: "Enemy stats and analysis." },
          { href: "/sr/stages", title: "Combat Stages", description: "Stage wave compositions." },
          { href: "/sr/banners", title: "Warp Banners", description: "Warp banner history." },
          { href: "/sr/achievements", title: "Achievements", description: "Achievement entries." },
          { href: "/sr/change-summary", title: "Change Summary", description: "Version diff snapshots." },
          { href: "/sr/future-intel", title: "Future Intel", description: "Future version tracking." },
          { href: "/sr/formulae", title: "Formula Compendium", description: "Mechanics formula entries." },
          {
            href: "/sr/dialogue-line-stats",
            title: "Dialogue Line Stats",
            description: "Line-count tools/stat pages."
          }
        ]}
      />

      <SectionGrid
        heading="SR Endgame Modes"
        items={[
          { href: "/sr/endgame/moc", title: "Memory of Chaos", description: "Cycle datasets." },
          { href: "/sr/endgame/purefiction", title: "Pure Fiction", description: "Cycle datasets." },
          {
            href: "/sr/endgame/apocalypticshadow",
            title: "Apocalyptic Shadow",
            description: "Cycle datasets."
          },
          {
            href: "/sr/endgame/yixiangzhongcai",
            title: "Yixiang Zhongcai",
            description: "Cycle datasets."
          },
          {
            href: "/sr/endgame/divergentuniverse",
            title: "Divergent Universe",
            description: "Version-separated datasets (2.7, 3.8, ...)."
          }
        ]}
      />

      <SectionGrid
        heading="SR Glossary"
        items={[
          {
            href: "/sr/glossary/effects",
            title: "Effects",
            description: "Buff/debuff/status records."
          },
          { href: "/sr/glossary/terms", title: "Terms", description: "Keywords and mechanic nouns." }
        ]}
      />
    </>
  );
}
