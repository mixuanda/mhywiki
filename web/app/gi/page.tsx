import SectionGrid from "@/components/section-grid";

export default function GIPage() {
  return (
    <>
      <SectionGrid
        heading="GI Core Data"
        items={[
          { href: "/gi/characters", title: "Characters", description: "Character combat sheets." },
          { href: "/gi/weapons", title: "Weapons", description: "Weapon stats and passives." },
          { href: "/gi/artifacts", title: "Artifacts", description: "Artifact set bonuses." },
          { href: "/gi/enemies", title: "Monsters + Analysis", description: "Enemy stats and analysis." },
          { href: "/gi/banners", title: "Wish Banners", description: "Wish banner history by phase." },
          { href: "/gi/achievements", title: "Achievements", description: "Achievement data entries." },
          { href: "/gi/tutorials", title: "Tutorials", description: "Combat tutorial records." },
          { href: "/gi/change-summary", title: "Change Summary", description: "Version-diff notes." },
          { href: "/gi/formulae", title: "Formula Compendium", description: "Damage/mechanics formulas." },
          { href: "/gi/donor-credits", title: "Donor Credits", description: "Legacy donor credits page." }
        ]}
      />

      <SectionGrid
        heading="GI Endgame Modes"
        items={[
          { href: "/gi/endgame/abyss", title: "Spiral Abyss", description: "Cycle-by-cycle abyss data." },
          {
            href: "/gi/endgame/theater",
            title: "Imaginarium Theater",
            description: "Fantasy True Realm season datasets."
          },
          { href: "/gi/endgame/youjing", title: "Youjing Weizhan", description: "Boss season datasets." }
        ]}
      />
    </>
  );
}
