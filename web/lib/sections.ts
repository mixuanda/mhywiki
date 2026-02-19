export type Game = "gi" | "sr";

export interface FacetConfig {
  key: string;
  label: string;
}

export interface SectionConfig {
  title: string;
  description: string;
  dataDir: string;
  facets?: FacetConfig[];
}

export const SECTION_CONFIG: Record<Game, Record<string, SectionConfig>> = {
  gi: {
    "characters": {
      title: "GI Characters",
      description: "One-file-per-character combat sheets.",
      dataDir: "characters",
      facets: [
        { key: "rarity", label: "Rarity" },
        { key: "element", label: "Element" },
        { key: "weaponType", label: "Weapon" }
      ]
    },
    "weapons": {
      title: "GI Weapons",
      description: "Weapon stats and passive data.",
      dataDir: "weapons",
      facets: [
        { key: "rarity", label: "Rarity" },
        { key: "weaponType", label: "Weapon Type" }
      ]
    },
    "artifacts": {
      title: "GI Artifacts",
      description: "Artifact set bonuses and part names.",
      dataDir: "artifacts"
    },
    "enemies": {
      title: "GI Monsters + Analysis",
      description: "Enemy base stats and analysis attachments.",
      dataDir: "enemies"
    },
    "banners": {
      title: "GI Wish Banners",
      description: "One file per banner phase.",
      dataDir: "banners"
    },
    "achievements": {
      title: "GI Achievements",
      description: "Achievement entries by ID.",
      dataDir: "achievements"
    },
    "tutorials": {
      title: "GI Tutorials",
      description: "Combat-relevant tutorial entries.",
      dataDir: "tutorials"
    },
    "change-summary": {
      title: "GI Change Summary",
      description: "Version diff snapshots and changelog files.",
      dataDir: "change_summary"
    },
    "formulae": {
      title: "GI Formula Compendium",
      description: "Extracted formula notes.",
      dataDir: "formulae"
    },
    "donor-credits": {
      title: "GI Donor Credits",
      description: "Legacy donor/credits page payload preserved as-is.",
      dataDir: "donor_credits"
    }
  },
  sr: {
    "characters": {
      title: "SR Characters",
      description: "One-file-per-character combat sheets.",
      dataDir: "characters",
      facets: [
        { key: "rarity", label: "Rarity" },
        { key: "element", label: "Element" },
        { key: "path", label: "Path" }
      ]
    },
    "lightcones": {
      title: "SR Light Cones",
      description: "One-file-per-light-cone records.",
      dataDir: "lightcones",
      facets: [
        { key: "rarity", label: "Rarity" },
        { key: "path", label: "Path" }
      ]
    },
    "relics": {
      title: "SR Relics",
      description: "Relic set bonuses and detail payload.",
      dataDir: "relics"
    },
    "enemies": {
      title: "SR Monsters + Analysis",
      description: "Enemy sheets with grouped camp and boss analysis.",
      dataDir: "enemies"
    },
    "banners": {
      title: "SR Warp Banners",
      description: "One file per banner phase.",
      dataDir: "banners"
    },
    "achievements": {
      title: "SR Achievements",
      description: "Achievement entries by ID.",
      dataDir: "achievements"
    },
    "stages": {
      title: "SR Combat Stages",
      description: "Stage waves and enemy references.",
      dataDir: "stages"
    },
    "change-summary": {
      title: "SR Change Summary",
      description: "Character/relic change snapshots.",
      dataDir: "change_summary"
    },
    "future-intel": {
      title: "SR Future Intel",
      description: "Future version tracking entries.",
      dataDir: "future_intel"
    },
    "formulae": {
      title: "SR Formula Compendium",
      description: "Formula references and mechanics notes.",
      dataDir: "formulae"
    },
    "dialogue-line-stats": {
      title: "SR Dialogue Line Stats",
      description: "Tools/statistics datasets by version.",
      dataDir: "dialogue_line_stats"
    }
  }
};

export const ENDGAME_MODES: Record<Game, Record<string, SectionConfig>> = {
  gi: {
    "abyss": {
      title: "Spiral Abyss",
      description: "One file per abyss cycle.",
      dataDir: "endgame/abyss"
    },
    "theater": {
      title: "Imaginarium Theater",
      description: "One file per theater season.",
      dataDir: "endgame/theater"
    },
    "youjing": {
      title: "Youjing Weizhan",
      description: "One file per Youjing season.",
      dataDir: "endgame/youjing"
    }
  },
  sr: {
    "moc": {
      title: "Memory of Chaos",
      description: "One file per MoC cycle.",
      dataDir: "endgame/moc"
    },
    "purefiction": {
      title: "Pure Fiction",
      description: "One file per Pure Fiction cycle.",
      dataDir: "endgame/purefiction"
    },
    "apocalypticshadow": {
      title: "Apocalyptic Shadow",
      description: "One file per Apocalyptic Shadow cycle.",
      dataDir: "endgame/apocalypticshadow"
    },
    "yixiangzhongcai": {
      title: "Yixiang Zhongcai",
      description: "One file per Yixiang Zhongcai cycle.",
      dataDir: "endgame/yixiangzhongcai"
    },
    "divergentuniverse": {
      title: "Divergent Universe",
      description: "Version-separated datasets (2.7, 3.8, ...).",
      dataDir: "endgame/divergentuniverse"
    }
  }
};

export const GLOSSARY_CONFIG: Record<string, SectionConfig> = {
  "effects": {
    title: "Effects",
    description: "Buff/debuff/status glossary entries.",
    dataDir: "glossary/effects"
  },
  "terms": {
    title: "Terms",
    description: "Keyword and mechanic definitions.",
    dataDir: "glossary/terms"
  }
};
