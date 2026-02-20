(function () {
  var GAME_KIND_MAP = {
    gi: ["character", "weapon", "artifact", "enemy", "banner"],
    sr: ["character", "lightcone", "relic", "enemy", "banner"]
  };

  var I18N_DICT = {
    en: {
      heroTitle: "Combat Wiki Admin",
      heroSubtitle: "Edit and create GI / SR combat entities with canonical JSON + legacy sync.",
      langLabel: "Language",
      sessionSignedIn: "Signed in",
      sessionSignedOut: "Signed out",
      loginTitle: "Sign In",
      loginPasswordLabel: "Admin Password",
      loginPasswordPlaceholder: "Enter password and press Enter",
      loginBtn: "Login",
      navigatorTitle: "Entity Navigator",
      editorTitle: "Editor",
      gameLabel: "Game",
      kindLabel: "Entity Type",
      gameGi: "Genshin Impact",
      gameSr: "Honkai: Star Rail",
      kindCharacter: "Character",
      kindWeapon: "Weapon (GI)",
      kindArtifact: "Artifact (GI)",
      kindEnemy: "Enemy",
      kindBanner: "Banner",
      kindLightcone: "Light Cone (SR)",
      kindRelic: "Relic (SR)",
      entityIdLabel: "Entity ID",
      entityIdPlaceholder: "e.g. 115, 1209, Keqing",
      entityNameLabel: "Display Name",
      entityNamePlaceholder: "Optional for new entity",
      entitySearchLabel: "Search IDs / names",
      entitySearchPlaceholder: "Type to filter current index",
      refreshListBtn: "Refresh List",
      loadBtn: "Load Existing",
      newBtn: "New Template",
      noIndexLoaded: "No index loaded.",
      tabWizard: "New Entity Wizard",
      tabHuman: "Human Categories",
      tabDraft: "Draft Input",
      tabJson: "JSON Editor",
      tabPreview: "Preview",
      wizardHint: "Create new entities with a guided form, then generate canonical JSON.",
      wizardStep1: "Step 1: Select game + type on the left and set Entity ID.",
      wizardStep2: "Step 2: Fill basic combat fields below.",
      wizardStep3: "Step 3: Click \"Generate JSON From Wizard\", then save.",
      wizardTemplateBtn: "Load Wizard Template",
      wizardLoadJsonBtn: "Load Wizard From JSON",
      wizardGenerateBtn: "Generate JSON From Wizard",
      humanHint: "Edit old JSON as grouped fields. Use \"Apply Categories To JSON\" before saving JSON.",
      loadHumanBtn: "Load From JSON",
      applyHumanBtn: "Apply Categories To JSON",
      humanCharacterBlocksLegend: "Character Combat Blocks",
      humanCharacterBlocksHint: "Character fields are split into separate JSON blocks for skills, talents, constellations/traces and combat mechanics.",
      humanAdvancedLegend: "Advanced Blocks (JSON)",
      humanCombatLabel: "Combat JSON (non-character blocks)",
      humanGiAttackConfigLabel: "GI: Normal/Charged/Plunge Skills (`_AvatarAttackConfig_`)",
      humanGiSkillPConfigLabel: "GI: Talents + Constellations (`_AvatarSkillPConfig_`)",
      humanGiDataConfigLabel: "GI: Combat Mechanics (`_AvatarDataConfig_`)",
      humanGiMatsLabel: "GI: Level-Up Materials (`_AvatarMats_`)",
      humanGiCostumeConfigLabel: "GI: Costume/Avatar Config (`_AvatarCostumeConfig_`)",
      humanGiAcsCacheLabel: "GI: Extra Cache (`acs_cache_`)",
      humanSrAvatarSkillLabel: "SR: Skill Definitions (`_avatarskill_`)",
      humanSrSkillTreeLabel: "SR: Trace Tree (`_avatarskilltree_`)",
      humanSrRankLabel: "SR: Eidolon Rank (`_avatarrank_`)",
      humanSrMtcLabel: "SR: Combat Metadata (`_mtc_`)",
      humanSrAdiffLabel: "SR: Additional Diff (`_adiff_`)",
      humanSrNotesLabel: "SR: Notes (`_notes_`)",
      draftTextLabel: "Human-readable source text",
      jsonLabel: "Canonical entity JSON",
      formatJsonBtn: "Format JSON",
      validateJsonBtn: "Validate JSON",
      parseDraftBtn: "Parse Draft",
      saveDraftBtn: "Save Draft + Sync",
      saveJsonBtn: "Save JSON + Sync",
      logoutBtn: "Logout",
      githubTitle: "GitHub PR (Optional)",
      ghRepoLabel: "Repo (owner/name)",
      ghBaseLabel: "Base branch",
      ghTokenLabel: "GitHub Token",
      ghTitleLabel: "PR Title",
      ghBodyLabel: "PR Body",
      ghPathsLabel: "Changed file paths (one per line)",
      ghPrBtn: "Create PR from Local Files",
      wizardHintCharacterGi: "Character wizard: fill element / weapon type / talents / base-max stats and material refs.",
      wizardHintCharacterSr: "Character wizard: fill path / element / traces / base stats and material refs.",
      wizardHintWeapon: "Weapon wizard (GI): use base ATK, sub stat type/value, and material refs.",
      wizardHintLightcone: "Light Cone wizard (SR): use path, skill ID, base stats, and materials.",
      wizardHintRelic: "Artifact/Relic wizard: fill name/version and put set effects in Extra Fields JSON.",
      wizardHintEnemy: "Enemy wizard: use stats/resistance/weakness and optional analysis/detail blocks.",
      wizardHintBanner: "Banner wizard: set version + phase and featured five/four star JSON arrays.",
      wizardHintDefault: "Fill applicable fields and generate JSON.",
      errorApiNotRunning: "Admin API is not running. Start `npm run dev:admin` and open http://127.0.0.1:8899/admin/",
      errorApiNonJson: "Admin API returned non-JSON response (HTTP {code}).",
      errorEntityJsonRequired: "Entity JSON is required.",
      errorEntityJsonParse: "Entity JSON parse failed.",
      errorEntityJsonObject: "Entity JSON must be an object.",
      errorIdRequired: "ID is required.",
      errorEntityIdRequired: "Entity ID is required.",
      errorDraftEmpty: "Draft text is empty.",
      errorPasswordRequired: "Password is required.",
      errorJsonNoId: "JSON has no id.",
      errorJsonNeedId: "ID is required in Entity ID or JSON id.",
      errorRepoTokenTitlePaths: "repo/token/title/paths are required.",
      errorGithubRequired: "repo/token/title/paths are required.",
      statusLoadedEntity: "Loaded entity {id}.",
      statusCreatedTemplate: "New wizard template created. Fill fields and generate JSON.",
      statusDraftParsed: "Draft parsed successfully.",
      statusDraftSaved: "Saved draft and synced legacy web.",
      statusJsonSaved: "Saved JSON and synced legacy web.",
      statusJsonFormatted: "JSON formatted.",
      statusJsonValid: "JSON is valid for save.",
      statusHumanLoaded: "Loaded category editor from JSON.",
      statusHumanApplied: "Applied category edits to JSON.",
      statusWizardLoaded: "Wizard template loaded for {game} {kind}.",
      statusWizardFromJson: "Loaded wizard fields from JSON.",
      statusWizardGenerated: "Generated JSON from wizard.",
      statusLoginOk: "Login successful.",
      statusLoggedOut: "Logged out.",
      statusPrCreated: "PR created: {url}",
      listShownTotal: "{shown} shown / {total} total",
      listNoEntities: "No entities found.",
      listNoId: "(no-id)",
      listNoName: "(no-name)"
    },
    zh: {
      heroTitle: "战斗向 Wiki 管理后台",
      heroSubtitle: "用于编辑与新建 GI / SR 战斗实体，生成规范 JSON 并同步旧版页面。",
      langLabel: "语言",
      sessionSignedIn: "已登录",
      sessionSignedOut: "未登录",
      loginTitle: "登录",
      loginPasswordLabel: "管理员密码",
      loginPasswordPlaceholder: "输入密码后回车或点击登录",
      loginBtn: "登录",
      navigatorTitle: "实体导航",
      editorTitle: "编辑器",
      gameLabel: "游戏",
      kindLabel: "实体类型",
      gameGi: "原神",
      gameSr: "崩坏：星穹铁道",
      kindCharacter: "角色",
      kindWeapon: "武器（GI）",
      kindArtifact: "圣遗物（GI）",
      kindEnemy: "敌人",
      kindBanner: "卡池",
      kindLightcone: "光锥（SR）",
      kindRelic: "遗器（SR）",
      entityIdLabel: "实体 ID",
      entityIdPlaceholder: "例如：115、1209、Keqing",
      entityNameLabel: "显示名称",
      entityNamePlaceholder: "新建实体可选填写",
      entitySearchLabel: "搜索 ID / 名称",
      entitySearchPlaceholder: "输入关键字过滤当前索引",
      refreshListBtn: "刷新列表",
      loadBtn: "加载已有",
      newBtn: "新建模板",
      noIndexLoaded: "尚未加载索引。",
      tabWizard: "新建向导",
      tabHuman: "人工分类编辑",
      tabDraft: "草稿输入",
      tabJson: "JSON 编辑",
      tabPreview: "预览",
      wizardHint: "使用引导表单创建实体，再生成规范 JSON。",
      wizardStep1: "步骤 1：先在左侧选择游戏和类型，并设置实体 ID。",
      wizardStep2: "步骤 2：填写下方基础战斗字段。",
      wizardStep3: "步骤 3：点击“由向导生成 JSON”，再保存。",
      wizardTemplateBtn: "加载向导模板",
      wizardLoadJsonBtn: "从 JSON 回填向导",
      wizardGenerateBtn: "由向导生成 JSON",
      humanHint: "将旧 JSON 按分类字段编辑。保存前先执行“应用分类到 JSON”。",
      loadHumanBtn: "从 JSON 载入",
      applyHumanBtn: "应用分类到 JSON",
      humanCharacterBlocksLegend: "角色战斗分块",
      humanCharacterBlocksHint: "角色字段已拆成可读 JSON 分块：技能、天赋、命座/行迹与机制信息。",
      humanAdvancedLegend: "高级分块（JSON）",
      humanCombatLabel: "战斗 JSON（非角色分块）",
      humanGiAttackConfigLabel: "GI：普攻/重击/下落技能（`_AvatarAttackConfig_`）",
      humanGiSkillPConfigLabel: "GI：天赋 + 命座（`_AvatarSkillPConfig_`）",
      humanGiDataConfigLabel: "GI：战斗机制（`_AvatarDataConfig_`）",
      humanGiMatsLabel: "GI：角色培养材料（`_AvatarMats_`）",
      humanGiCostumeConfigLabel: "GI：时装/角色配置（`_AvatarCostumeConfig_`）",
      humanGiAcsCacheLabel: "GI：额外缓存（`acs_cache_`）",
      humanSrAvatarSkillLabel: "SR：技能定义（`_avatarskill_`）",
      humanSrSkillTreeLabel: "SR：行迹树（`_avatarskilltree_`）",
      humanSrRankLabel: "SR：星魂（`_avatarrank_`）",
      humanSrMtcLabel: "SR：战斗元信息（`_mtc_`）",
      humanSrAdiffLabel: "SR：附加差异（`_adiff_`）",
      humanSrNotesLabel: "SR：备注（`_notes_`）",
      draftTextLabel: "可读草稿文本",
      jsonLabel: "规范实体 JSON",
      formatJsonBtn: "格式化 JSON",
      validateJsonBtn: "校验 JSON",
      parseDraftBtn: "解析草稿",
      saveDraftBtn: "保存草稿并同步",
      saveJsonBtn: "保存 JSON 并同步",
      logoutBtn: "退出登录",
      githubTitle: "GitHub PR（可选）",
      ghRepoLabel: "仓库（owner/name）",
      ghBaseLabel: "目标分支",
      ghTokenLabel: "GitHub Token",
      ghTitleLabel: "PR 标题",
      ghBodyLabel: "PR 描述",
      ghPathsLabel: "变更文件路径（每行一个）",
      ghPrBtn: "从本地文件创建 PR",
      wizardHintCharacterGi: "角色向导：填写元素/武器类型/天赋命座/基础-满级属性和材料。",
      wizardHintCharacterSr: "角色向导：填写命途/属性/行迹/基础属性和材料。",
      wizardHintWeapon: "武器向导（GI）：填写基础攻击、副词条类型/数值和材料。",
      wizardHintLightcone: "光锥向导（SR）：填写命途、技能 ID、基础属性和材料。",
      wizardHintRelic: "圣遗物/遗器向导：填写名称版本，并在“额外字段 JSON”写套装效果。",
      wizardHintEnemy: "敌人向导：填写属性/抗性/弱点，可选 analysis/detail 分块。",
      wizardHintBanner: "卡池向导：填写版本与期数，以及五星/四星角色数组。",
      wizardHintDefault: "填写适用字段后生成 JSON。",
      errorApiNotRunning: "管理 API 未运行。请执行 `npm run dev:admin` 并打开 http://127.0.0.1:8899/admin/",
      errorApiNonJson: "管理 API 返回了非 JSON 响应（HTTP {code}）。",
      errorEntityJsonRequired: "必须提供实体 JSON。",
      errorEntityJsonParse: "实体 JSON 解析失败。",
      errorEntityJsonObject: "实体 JSON 必须是对象。",
      errorIdRequired: "必须填写 ID。",
      errorEntityIdRequired: "必须填写实体 ID。",
      errorDraftEmpty: "草稿为空。",
      errorPasswordRequired: "必须输入密码。",
      errorJsonNoId: "JSON 中没有 id。",
      errorJsonNeedId: "需要在实体 ID 或 JSON id 中提供 ID。",
      errorRepoTokenTitlePaths: "repo/token/title/paths 为必填。",
      errorGithubRequired: "repo/token/title/paths 为必填。",
      statusLoadedEntity: "已加载实体 {id}。",
      statusCreatedTemplate: "已创建新向导模板，请填写字段并生成 JSON。",
      statusDraftParsed: "草稿解析成功。",
      statusDraftSaved: "草稿已保存并同步到旧版网页。",
      statusJsonSaved: "JSON 已保存并同步到旧版网页。",
      statusJsonFormatted: "JSON 已格式化。",
      statusJsonValid: "JSON 可用于保存。",
      statusHumanLoaded: "已从 JSON 载入分类编辑器。",
      statusHumanApplied: "已将分类编辑应用到 JSON。",
      statusWizardLoaded: "已加载向导模板：{game} {kind}。",
      statusWizardFromJson: "已从 JSON 回填向导字段。",
      statusWizardGenerated: "已由向导生成 JSON。",
      statusLoginOk: "登录成功。",
      statusLoggedOut: "已退出登录。",
      statusPrCreated: "PR 已创建：{url}",
      listShownTotal: "显示 {shown} / 共 {total}",
      listNoEntities: "未找到实体。",
      listNoId: "（无 ID）",
      listNoName: "（无名称）"
    }
  };

  var HUMAN_KNOWN_TOP_LEVEL_KEYS = {
    id: true,
    game: true,
    kind: true,
    entityType: true,
    name: true,
    title: true,
    description: true,
    version: true,
    rarity: true,
    element: true,
    path: true,
    weaponType: true,
    nation: true,
    affiliation: true,
    materialRefs: true,
    weakness: true,
    baseStats: true,
    maxStats: true,
    stats: true,
    resistance: true,
    manualSections: true,
    rawText: true,
    combat: true,
    analysis: true,
    detail: true,
    source: true,
    featuredFiveStar: true,
    featuredFourStar: true,
    phase: true,
    baseAtk: true,
    subStatType: true,
    subStatValue: true,
    skillId: true
  };

  function preferredLang() {
    var saved = localStorage.getItem("admin_lang");
    if (saved === "en" || saved === "zh") return saved;
    var browserLang = String((navigator.language || navigator.userLanguage || "")).toLowerCase();
    if (browserLang.indexOf("zh") === 0) return "zh";
    return "en";
  }

  var state = {
    token: localStorage.getItem("admin_token") || "",
    listRows: [],
    activeListId: "",
    searchTimer: 0,
    currentTab: "tab-human",
    lang: preferredLang()
  };

  var dom = {
    loginCard: document.getElementById("login-card"),
    loginStatus: document.getElementById("login-status"),
    workspace: document.getElementById("workspace"),
    editorStatus: document.getElementById("editor-status"),
    githubCard: document.getElementById("github-card"),
    ghStatus: document.getElementById("gh-status"),
    sessionBadge: document.getElementById("session-badge"),
    langSelect: document.getElementById("admin-lang"),
    previewJson: document.getElementById("preview-json"),

    game: document.getElementById("game"),
    kind: document.getElementById("kind"),
    entityId: document.getElementById("entity-id"),
    entityName: document.getElementById("entity-name"),
    entitySearch: document.getElementById("entity-search"),
    entityList: document.getElementById("entity-list"),
    entityListMeta: document.getElementById("entity-list-meta"),

    entityText: document.getElementById("entity-text"),
    skillsText: document.getElementById("skills-text"),
    materialsText: document.getElementById("materials-text"),
    talentsText: document.getElementById("talents-text"),
    notesText: document.getElementById("notes-text"),
    entityJson: document.getElementById("entity-json"),

    tabs: Array.prototype.slice.call(document.querySelectorAll(".tab")),
    tabPanels: Array.prototype.slice.call(document.querySelectorAll(".tabpanel")),

    loadHumanBtn: document.getElementById("load-human-btn"),
    applyHumanBtn: document.getElementById("apply-human-btn"),
    wizardTemplateBtn: document.getElementById("wizard-template-btn"),
    wizardLoadJsonBtn: document.getElementById("wizard-load-json-btn"),
    wizardGenerateBtn: document.getElementById("wizard-generate-btn"),
    wizardKindHint: document.getElementById("wizard-kind-hint"),

    humanId: document.getElementById("human-id"),
    humanName: document.getElementById("human-name"),
    humanTitle: document.getElementById("human-title"),
    humanDescription: document.getElementById("human-description"),
    humanVersion: document.getElementById("human-version"),
    humanRarity: document.getElementById("human-rarity"),
    humanWeaponType: document.getElementById("human-weaponType"),
    humanElement: document.getElementById("human-element"),
    humanPath: document.getElementById("human-path"),
    humanNation: document.getElementById("human-nation"),
    humanAffiliation: document.getElementById("human-affiliation"),
    humanMaterialRefs: document.getElementById("human-material-refs"),
    humanWeakness: document.getElementById("human-weakness"),
    humanBaseStats: document.getElementById("human-base-stats"),
    humanMaxStats: document.getElementById("human-max-stats"),
    humanStats: document.getElementById("human-stats"),
    humanResistance: document.getElementById("human-resistance"),
    humanSkills: document.getElementById("human-skills"),
    humanTalents: document.getElementById("human-talents"),
    humanNotes: document.getElementById("human-notes"),
    humanRawText: document.getElementById("human-raw-text"),
    humanCombat: document.getElementById("human-combat"),
    humanAnalysis: document.getElementById("human-analysis"),
    humanDetail: document.getElementById("human-detail"),
    humanSource: document.getElementById("human-source"),
    humanFeaturedFive: document.getElementById("human-featured-five"),
    humanFeaturedFour: document.getElementById("human-featured-four"),
    humanOtherJson: document.getElementById("human-other-json"),
    humanCharacterBlocks: document.getElementById("human-character-blocks"),
    humanGiAttackConfig: document.getElementById("human-gi-attack-config"),
    humanGiSkillPConfig: document.getElementById("human-gi-skillp-config"),
    humanGiDataConfig: document.getElementById("human-gi-data-config"),
    humanGiMats: document.getElementById("human-gi-mats"),
    humanGiCostumeConfig: document.getElementById("human-gi-costume-config"),
    humanGiAcsCache: document.getElementById("human-gi-acs-cache"),
    humanSrAvatarSkill: document.getElementById("human-sr-avatarskill"),
    humanSrSkillTree: document.getElementById("human-sr-skilltree"),
    humanSrRank: document.getElementById("human-sr-rank"),
    humanSrMtc: document.getElementById("human-sr-mtc"),
    humanSrAdiff: document.getElementById("human-sr-adiff"),
    humanSrNotes: document.getElementById("human-sr-notes"),

    wizardId: document.getElementById("wizard-id"),
    wizardName: document.getElementById("wizard-name"),
    wizardTitle: document.getElementById("wizard-title"),
    wizardDescription: document.getElementById("wizard-description"),
    wizardVersion: document.getElementById("wizard-version"),
    wizardRarity: document.getElementById("wizard-rarity"),
    wizardElement: document.getElementById("wizard-element"),
    wizardPath: document.getElementById("wizard-path"),
    wizardWeaponType: document.getElementById("wizard-weaponType"),
    wizardNation: document.getElementById("wizard-nation"),
    wizardAffiliation: document.getElementById("wizard-affiliation"),
    wizardPhase: document.getElementById("wizard-phase"),
    wizardBaseAtk: document.getElementById("wizard-base-atk"),
    wizardSubstatType: document.getElementById("wizard-substat-type"),
    wizardSubstatValue: document.getElementById("wizard-substat-value"),
    wizardSkillId: document.getElementById("wizard-skill-id"),
    wizardMaterialRefs: document.getElementById("wizard-material-refs"),
    wizardWeakness: document.getElementById("wizard-weakness"),
    wizardBaseStats: document.getElementById("wizard-base-stats"),
    wizardMaxStats: document.getElementById("wizard-max-stats"),
    wizardStats: document.getElementById("wizard-stats"),
    wizardResistance: document.getElementById("wizard-resistance"),
    wizardSkills: document.getElementById("wizard-skills"),
    wizardTalents: document.getElementById("wizard-talents"),
    wizardNotes: document.getElementById("wizard-notes"),
    wizardRawText: document.getElementById("wizard-raw-text"),
    wizardFeaturedFive: document.getElementById("wizard-featured-five"),
    wizardFeaturedFour: document.getElementById("wizard-featured-four"),
    wizardExtraJson: document.getElementById("wizard-extra-json"),

    loginBtn: document.getElementById("login-btn"),
    logoutBtn: document.getElementById("logout-btn"),
    refreshListBtn: document.getElementById("refresh-list-btn"),
    loadBtn: document.getElementById("load-btn"),
    newBtn: document.getElementById("new-btn"),
    previewBtn: document.getElementById("preview-btn"),
    saveBtn: document.getElementById("save-btn"),
    saveJsonBtn: document.getElementById("save-json-btn"),
    formatJsonBtn: document.getElementById("format-json-btn"),
    validateJsonBtn: document.getElementById("validate-json-btn"),

    ghRepo: document.getElementById("gh-repo"),
    ghBase: document.getElementById("gh-base"),
    ghToken: document.getElementById("gh-token"),
    ghTitle: document.getElementById("gh-title"),
    ghBody: document.getElementById("gh-body"),
    ghPaths: document.getElementById("gh-paths"),
    ghPrBtn: document.getElementById("gh-pr-btn"),

    adminPassword: document.getElementById("admin-password")
  };

  var persistIds = [
    "game",
    "kind",
    "entity-id",
    "entity-name",
    "entity-search",
    "entity-text",
    "skills-text",
    "materials-text",
    "talents-text",
    "notes-text",
    "entity-json",
    "human-name",
    "human-title",
    "human-description",
    "human-version",
    "human-rarity",
    "human-weaponType",
    "human-element",
    "human-path",
    "human-nation",
    "human-affiliation",
    "human-material-refs",
    "human-weakness",
    "human-base-stats",
    "human-max-stats",
    "human-stats",
    "human-resistance",
    "human-skills",
    "human-talents",
    "human-notes",
    "human-raw-text",
    "human-combat",
    "human-analysis",
    "human-detail",
    "human-source",
    "human-featured-five",
    "human-featured-four",
    "human-gi-attack-config",
    "human-gi-skillp-config",
    "human-gi-data-config",
    "human-gi-mats",
    "human-gi-costume-config",
    "human-gi-acs-cache",
    "human-sr-avatarskill",
    "human-sr-skilltree",
    "human-sr-rank",
    "human-sr-mtc",
    "human-sr-adiff",
    "human-sr-notes",
    "human-other-json",
    "wizard-name",
    "wizard-title",
    "wizard-description",
    "wizard-version",
    "wizard-rarity",
    "wizard-element",
    "wizard-path",
    "wizard-weaponType",
    "wizard-nation",
    "wizard-affiliation",
    "wizard-phase",
    "wizard-base-atk",
    "wizard-substat-type",
    "wizard-substat-value",
    "wizard-skill-id",
    "wizard-material-refs",
    "wizard-weakness",
    "wizard-base-stats",
    "wizard-max-stats",
    "wizard-stats",
    "wizard-resistance",
    "wizard-skills",
    "wizard-talents",
    "wizard-notes",
    "wizard-raw-text",
    "wizard-featured-five",
    "wizard-featured-four",
    "wizard-extra-json"
  ];

  function tr(key, params) {
    var dict = I18N_DICT[state.lang] || I18N_DICT.en;
    var fallback = I18N_DICT.en || {};
    var text = dict[key];
    if (text === undefined || text === null) text = fallback[key];
    if (text === undefined || text === null) text = key;
    if (!params) return String(text);
    return String(text).replace(/\{([a-zA-Z0-9_]+)\}/g, function (_all, token) {
      if (params[token] === undefined || params[token] === null) return "";
      return String(params[token]);
    });
  }

  function selectOne(selector) {
    return document.querySelector(selector);
  }

  function setText(selector, key, params) {
    var node = selectOne(selector);
    if (!node) return;
    node.textContent = tr(key, params);
  }

  function setPlaceholder(id, key, params) {
    var node = document.getElementById(id);
    if (!node) return;
    node.setAttribute("placeholder", tr(key, params));
  }

  function setLabel(forId, key, params) {
    var node = selectOne('label[for="' + forId + '"]');
    if (!node) return;
    node.textContent = tr(key, params);
  }

  function setSelectOption(selectId, optionValue, key) {
    var select = document.getElementById(selectId);
    if (!select) return;
    for (var i = 0; i < select.options.length; i += 1) {
      var opt = select.options[i];
      if (opt.value === optionValue) {
        opt.textContent = tr(key);
        return;
      }
    }
  }

  function applyI18nUI() {
    setText("#hero-title", "heroTitle");
    setText("#hero-subtitle", "heroSubtitle");
    setText("#lang-label", "langLabel");
    setText("#login-title", "loginTitle");
    setText("#navigator-title", "navigatorTitle");
    setText("#editor-title", "editorTitle");
    setText("#wizard-hint", "wizardHint");
    setText("#wizard-step-1", "wizardStep1");
    setText("#wizard-step-2", "wizardStep2");
    setText("#wizard-step-3", "wizardStep3");
    setText("#human-hint", "humanHint");
    setText("#human-character-blocks-legend", "humanCharacterBlocksLegend");
    setText("#human-character-blocks-hint", "humanCharacterBlocksHint");
    setText("#human-advanced-legend", "humanAdvancedLegend");

    setText("#tab-wizard", "tabWizard");
    setText("#tab-human", "tabHuman");
    setText("#tab-draft", "tabDraft");
    setText("#tab-json", "tabJson");
    setText("#tab-preview", "tabPreview");

    setText("#login-btn", "loginBtn");
    setText("#refresh-list-btn", "refreshListBtn");
    setText("#load-btn", "loadBtn");
    setText("#new-btn", "newBtn");
    setText("#wizard-template-btn", "wizardTemplateBtn");
    setText("#wizard-load-json-btn", "wizardLoadJsonBtn");
    setText("#wizard-generate-btn", "wizardGenerateBtn");
    setText("#load-human-btn", "loadHumanBtn");
    setText("#apply-human-btn", "applyHumanBtn");
    setText("#format-json-btn", "formatJsonBtn");
    setText("#validate-json-btn", "validateJsonBtn");
    setText("#preview-btn", "parseDraftBtn");
    setText("#save-btn", "saveDraftBtn");
    setText("#save-json-btn", "saveJsonBtn");
    setText("#logout-btn", "logoutBtn");
    setText("#gh-pr-btn", "ghPrBtn");
    setText("#entity-list-meta", "noIndexLoaded");

    setLabel("admin-password", "loginPasswordLabel");
    setLabel("game", "gameLabel");
    setLabel("kind", "kindLabel");
    setLabel("entity-id", "entityIdLabel");
    setLabel("entity-name", "entityNameLabel");
    setLabel("entity-search", "entitySearchLabel");
    setLabel("entity-text", "draftTextLabel");
    setLabel("entity-json", "jsonLabel");
    setLabel("human-combat", "humanCombatLabel");
    setLabel("human-gi-attack-config", "humanGiAttackConfigLabel");
    setLabel("human-gi-skillp-config", "humanGiSkillPConfigLabel");
    setLabel("human-gi-data-config", "humanGiDataConfigLabel");
    setLabel("human-gi-mats", "humanGiMatsLabel");
    setLabel("human-gi-costume-config", "humanGiCostumeConfigLabel");
    setLabel("human-gi-acs-cache", "humanGiAcsCacheLabel");
    setLabel("human-sr-avatarskill", "humanSrAvatarSkillLabel");
    setLabel("human-sr-skilltree", "humanSrSkillTreeLabel");
    setLabel("human-sr-rank", "humanSrRankLabel");
    setLabel("human-sr-mtc", "humanSrMtcLabel");
    setLabel("human-sr-adiff", "humanSrAdiffLabel");
    setLabel("human-sr-notes", "humanSrNotesLabel");
    setLabel("gh-repo", "ghRepoLabel");
    setLabel("gh-base", "ghBaseLabel");
    setLabel("gh-token", "ghTokenLabel");
    setLabel("gh-title", "ghTitleLabel");
    setLabel("gh-body", "ghBodyLabel");
    setLabel("gh-paths", "ghPathsLabel");

    setPlaceholder("admin-password", "loginPasswordPlaceholder");
    setPlaceholder("entity-id", "entityIdPlaceholder");
    setPlaceholder("entity-name", "entityNamePlaceholder");
    setPlaceholder("entity-search", "entitySearchPlaceholder");

    setSelectOption("game", "gi", "gameGi");
    setSelectOption("game", "sr", "gameSr");
    setSelectOption("kind", "character", "kindCharacter");
    setSelectOption("kind", "weapon", "kindWeapon");
    setSelectOption("kind", "artifact", "kindArtifact");
    setSelectOption("kind", "enemy", "kindEnemy");
    setSelectOption("kind", "banner", "kindBanner");
    setSelectOption("kind", "lightcone", "kindLightcone");
    setSelectOption("kind", "relic", "kindRelic");

    setText("#github-card summary h2", "githubTitle");
    setSessionBadge(!!state.token);
    if (state.listRows && state.listRows.length) {
      updateListMeta(state.listRows.length, state.listRows.length);
    } else {
      setText("#entity-list-meta", "noIndexLoaded");
    }
    updateWizardKindHint();
  }

  function setStatus(node, text, isError) {
    if (!node) return;
    node.textContent = text || "";
    node.classList.remove("status-ok");
    node.classList.remove("status-err");
    if (!text) return;
    node.classList.add(isError ? "status-err" : "status-ok");
  }

  function setSessionBadge(loggedIn) {
    if (!dom.sessionBadge) return;
    dom.sessionBadge.classList.remove("badge-online");
    dom.sessionBadge.classList.remove("badge-offline");
    dom.sessionBadge.classList.add(loggedIn ? "badge-online" : "badge-offline");
    dom.sessionBadge.textContent = loggedIn ? tr("sessionSignedIn") : tr("sessionSignedOut");
  }

  function setAuthState(loggedIn) {
    dom.loginCard.classList.toggle("hidden", loggedIn);
    dom.workspace.classList.toggle("hidden", !loggedIn);
    dom.workspace.setAttribute("aria-hidden", loggedIn ? "false" : "true");
    dom.githubCard.classList.toggle("hidden", !loggedIn);
    setSessionBadge(loggedIn);
  }

  function headers(hasBody) {
    var h = {};
    if (hasBody) h["Content-Type"] = "application/json";
    if (state.token) h.Authorization = "Bearer " + state.token;
    return h;
  }

  async function requestJson(path, method, payload) {
    var useMethod = method || "GET";
    var hasBody = useMethod !== "GET";
    var opts = {
      method: useMethod,
      headers: headers(hasBody)
    };
    if (hasBody) {
      opts.body = JSON.stringify(payload || {});
    }

    var res = await fetch(path, opts);
    var raw = await res.text();
    var data = null;
    try {
      data = JSON.parse(raw);
    } catch (_err) {
      data = null;
    }
    if (!data) {
      if (res.status === 404 || res.status === 405 || res.status === 501) {
        throw new Error(tr("errorApiNotRunning"));
      }
      throw new Error(tr("errorApiNonJson", { code: String(res.status) }));
    }
    if (!res.ok || data.ok === false) {
      throw new Error(data.error || ("Request failed: " + String(res.status)));
    }
    return data;
  }

  function apiGet(path) {
    return requestJson(path, "GET");
  }

  function apiPost(path, payload) {
    return requestJson(path, "POST", payload);
  }

  function currentGame() {
    return dom.game.value;
  }

  function currentKind() {
    return dom.kind.value;
  }

  function allowedKinds(game) {
    return GAME_KIND_MAP[game] || [];
  }

  function syncKindOptions() {
    var game = currentGame();
    var allow = allowedKinds(game);
    var opts = Array.prototype.slice.call(dom.kind.options);
    for (var i = 0; i < opts.length; i += 1) {
      var option = opts[i];
      var isAllowed = allow.indexOf(option.value) >= 0;
      option.disabled = !isAllowed;
      option.hidden = !isAllowed;
    }
    if (allow.indexOf(currentKind()) < 0 && allow.length) {
      dom.kind.value = allow[0];
    }
  }

  function wizardKindHint(game, kind) {
    if (kind === "character") {
      return game === "gi"
        ? tr("wizardHintCharacterGi")
        : tr("wizardHintCharacterSr");
    }
    if (kind === "weapon") return tr("wizardHintWeapon");
    if (kind === "lightcone") return tr("wizardHintLightcone");
    if (kind === "artifact" || kind === "relic") return tr("wizardHintRelic");
    if (kind === "enemy") return tr("wizardHintEnemy");
    if (kind === "banner") return tr("wizardHintBanner");
    return tr("wizardHintDefault");
  }

  function updateWizardKindHint() {
    if (!dom.wizardKindHint) return;
    dom.wizardKindHint.textContent = wizardKindHint(currentGame(), currentKind());
  }

  function isPlainObject(value) {
    return !!value && typeof value === "object" && !Array.isArray(value);
  }

  function isEmptyPlainObject(value) {
    return isPlainObject(value) && Object.keys(value).length === 0;
  }

  function deepClone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function setModeNodesVisible(selector, visible) {
    var nodes = Array.prototype.slice.call(document.querySelectorAll(selector));
    for (var i = 0; i < nodes.length; i += 1) {
      var node = nodes[i];
      node.classList.toggle("mode-hidden", !visible);
      var fields = Array.prototype.slice.call(node.querySelectorAll("input, textarea, select, button"));
      for (var j = 0; j < fields.length; j += 1) {
        fields[j].disabled = !visible;
      }
    }
  }

  function clearHumanCharacterBlockFields() {
    var fields = [
      dom.humanGiAttackConfig,
      dom.humanGiSkillPConfig,
      dom.humanGiDataConfig,
      dom.humanGiMats,
      dom.humanGiCostumeConfig,
      dom.humanGiAcsCache,
      dom.humanSrAvatarSkill,
      dom.humanSrSkillTree,
      dom.humanSrRank,
      dom.humanSrMtc,
      dom.humanSrAdiff,
      dom.humanSrNotes
    ];
    for (var i = 0; i < fields.length; i += 1) {
      if (fields[i]) fields[i].value = "";
    }
  }

  function updateHumanCharacterBlocksVisibility() {
    var isCharacter = currentKind() === "character";
    var game = currentGame();
    if (dom.humanCharacterBlocks) {
      dom.humanCharacterBlocks.classList.toggle("mode-hidden", !isCharacter);
    }
    setModeNodesVisible(".gi-character-only", isCharacter && game === "gi");
    setModeNodesVisible(".sr-character-only", isCharacter && game === "sr");
    if (!isCharacter) {
      clearHumanCharacterBlockFields();
    }
  }

  function setTextAreaJson(node, value) {
    if (!node) return;
    node.value = value === undefined ? "" : toPrettyJson(value);
  }

  function sanitizeOtherCombatBlocks(value) {
    if (value === undefined) return undefined;
    if (isEmptyPlainObject(value)) return undefined;
    return value;
  }

  function assignParsedBlock(target, key, rawText, label) {
    var parsed = parseOptionalJson(rawText, label);
    if (parsed !== undefined) {
      target[key] = parsed;
    }
  }

  function extractCharacterBlocksFromCombat(combatInput, game) {
    if (!isPlainObject(combatInput)) {
      clearHumanCharacterBlockFields();
      return undefined;
    }
    var combat = deepClone(combatInput);

    if (game === "gi") {
      var detail1 = isPlainObject(combat.detail_1) ? combat.detail_1 : {};
      var detail2 = isPlainObject(combat.detail_2) ? combat.detail_2 : {};
      setTextAreaJson(dom.humanGiAttackConfig, detail1._AvatarAttackConfig_);
      setTextAreaJson(dom.humanGiSkillPConfig, detail1._AvatarSkillPConfig_);
      setTextAreaJson(dom.humanGiDataConfig, detail1._AvatarDataConfig_);
      setTextAreaJson(dom.humanGiMats, detail1._AvatarMats_);
      setTextAreaJson(dom.humanGiCostumeConfig, detail2._AvatarCostumeConfig_);
      setTextAreaJson(dom.humanGiAcsCache, detail2.acs_cache_);

      delete detail1._AvatarAttackConfig_;
      delete detail1._AvatarSkillPConfig_;
      delete detail1._AvatarDataConfig_;
      delete detail1._AvatarMats_;
      delete detail2._AvatarCostumeConfig_;
      delete detail2.acs_cache_;

      if (isEmptyPlainObject(detail1)) {
        delete combat.detail_1;
      } else {
        combat.detail_1 = detail1;
      }
      if (isEmptyPlainObject(detail2)) {
        delete combat.detail_2;
      } else {
        combat.detail_2 = detail2;
      }
      return sanitizeOtherCombatBlocks(combat);
    }

    if (game === "sr") {
      setTextAreaJson(dom.humanSrAvatarSkill, combat._avatarskill_);
      setTextAreaJson(dom.humanSrSkillTree, combat._avatarskilltree_);
      setTextAreaJson(dom.humanSrRank, combat._avatarrank_);
      setTextAreaJson(dom.humanSrMtc, combat._mtc_);
      setTextAreaJson(dom.humanSrAdiff, combat._adiff_);
      setTextAreaJson(dom.humanSrNotes, combat._notes_);

      delete combat._avatarskill_;
      delete combat._avatarskilltree_;
      delete combat._avatarrank_;
      delete combat._mtc_;
      delete combat._adiff_;
      delete combat._notes_;

      return sanitizeOtherCombatBlocks(combat);
    }

    clearHumanCharacterBlockFields();
    return sanitizeOtherCombatBlocks(combat);
  }

  function buildCharacterCombatBlocks() {
    if (currentKind() !== "character") return undefined;

    if (currentGame() === "gi") {
      var detail1 = {};
      var detail2 = {};
      assignParsedBlock(detail1, "_AvatarAttackConfig_", dom.humanGiAttackConfig.value, "GI _AvatarAttackConfig_");
      assignParsedBlock(detail1, "_AvatarSkillPConfig_", dom.humanGiSkillPConfig.value, "GI _AvatarSkillPConfig_");
      assignParsedBlock(detail1, "_AvatarDataConfig_", dom.humanGiDataConfig.value, "GI _AvatarDataConfig_");
      assignParsedBlock(detail1, "_AvatarMats_", dom.humanGiMats.value, "GI _AvatarMats_");
      assignParsedBlock(detail2, "_AvatarCostumeConfig_", dom.humanGiCostumeConfig.value, "GI _AvatarCostumeConfig_");
      assignParsedBlock(detail2, "acs_cache_", dom.humanGiAcsCache.value, "GI acs_cache_");

      var outGi = {};
      if (!isEmptyPlainObject(detail1)) outGi.detail_1 = detail1;
      if (!isEmptyPlainObject(detail2)) outGi.detail_2 = detail2;
      return sanitizeOtherCombatBlocks(outGi);
    }

    if (currentGame() === "sr") {
      var outSr = {};
      assignParsedBlock(outSr, "_avatarskill_", dom.humanSrAvatarSkill.value, "SR _avatarskill_");
      assignParsedBlock(outSr, "_avatarskilltree_", dom.humanSrSkillTree.value, "SR _avatarskilltree_");
      assignParsedBlock(outSr, "_avatarrank_", dom.humanSrRank.value, "SR _avatarrank_");
      assignParsedBlock(outSr, "_mtc_", dom.humanSrMtc.value, "SR _mtc_");
      assignParsedBlock(outSr, "_adiff_", dom.humanSrAdiff.value, "SR _adiff_");
      assignParsedBlock(outSr, "_notes_", dom.humanSrNotes.value, "SR _notes_");
      return sanitizeOtherCombatBlocks(outSr);
    }

    return undefined;
  }

  function updateUrlState() {
    var params = new URLSearchParams(window.location.search);
    params.set("game", currentGame());
    params.set("kind", currentKind());
    var entityId = dom.entityId.value.trim();
    var tab = state.currentTab || "tab-human";
    params.set("tab", tab);
    if (entityId) {
      params.set("id", entityId);
    } else {
      params.delete("id");
    }
    var next = window.location.pathname + "?" + params.toString();
    window.history.replaceState({}, "", next);
  }

  function applyUrlState() {
    var params = new URLSearchParams(window.location.search);
    var game = params.get("game");
    var kind = params.get("kind");
    var id = params.get("id");
    var tab = params.get("tab");

    if (game && GAME_KIND_MAP[game]) {
      dom.game.value = game;
      syncKindOptions();
    }
    if (kind && allowedKinds(dom.game.value).indexOf(kind) >= 0) {
      dom.kind.value = kind;
    }
    updateWizardKindHint();
    if (id) {
      dom.entityId.value = id;
      dom.humanId.value = id;
      dom.wizardId.value = id;
    }
    if (tab && document.getElementById(tab)) {
      state.currentTab = tab;
    }
  }

  function openTab(tabButtonId, skipUrlWrite) {
    var targetPanelId = "";
    state.currentTab = tabButtonId;
    for (var i = 0; i < dom.tabs.length; i += 1) {
      var tab = dom.tabs[i];
      var active = tab.id === tabButtonId;
      if (active) {
        targetPanelId = tab.getAttribute("data-panel") || "";
      }
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", active ? "true" : "false");
      tab.setAttribute("tabindex", active ? "0" : "-1");
    }
    for (var j = 0; j < dom.tabPanels.length; j += 1) {
      var panel = dom.tabPanels[j];
      var show = panel.id === targetPanelId;
      panel.classList.toggle("active", show);
      panel.hidden = !show;
    }
    if (!skipUrlWrite) {
      updateUrlState();
    }
  }

  function setChangedPaths(paths) {
    dom.ghPaths.value = (paths || []).join("\n");
  }

  function splitLines(rawText) {
    return String(rawText || "")
      .split(/\r?\n/)
      .map(function (x) { return x.trim(); })
      .filter(function (x) { return !!x; });
  }

  function parseLooseScalar(value) {
    var text = String(value || "").trim();
    if (!text) return "";
    if (text === "true") return true;
    if (text === "false") return false;
    if (text === "null") return null;
    if (/^-?\d+(\.\d+)?$/.test(text)) return Number(text);
    return text;
  }

  function objectToKeyValueText(value) {
    if (!value || typeof value !== "object" || Array.isArray(value)) {
      return "";
    }
    var keys = Object.keys(value);
    if (!keys.length) return "";
    var lines = [];
    for (var i = 0; i < keys.length; i += 1) {
      var key = keys[i];
      lines.push(key + ": " + String(value[key]));
    }
    return lines.join("\n");
  }

  function parseKeyValueText(rawText, fieldLabel) {
    var text = String(rawText || "").trim();
    if (!text) return undefined;
    if (text[0] === "{") {
      var parsedObject = null;
      try {
        parsedObject = JSON.parse(text);
      } catch (_err0) {
        throw new Error(fieldLabel + " must be valid JSON object or `key: value` lines.");
      }
      if (!parsedObject || typeof parsedObject !== "object" || Array.isArray(parsedObject)) {
        throw new Error(fieldLabel + " must be a JSON object.");
      }
      return parsedObject;
    }

    var lines = splitLines(text);
    var out = {};
    for (var i = 0; i < lines.length; i += 1) {
      var line = lines[i];
      var splitAt = line.indexOf(":");
      if (splitAt <= 0) {
        throw new Error(fieldLabel + " line " + String(i + 1) + " must use `key: value` format.");
      }
      var key = line.slice(0, splitAt).trim();
      var value = line.slice(splitAt + 1).trim();
      if (!key) {
        throw new Error(fieldLabel + " line " + String(i + 1) + " has empty key.");
      }
      out[key] = parseLooseScalar(value);
    }
    return out;
  }

  function parseOptionalJson(rawText, fieldLabel, expectType) {
    var text = String(rawText || "").trim();
    if (!text) return undefined;
    var parsed = null;
    try {
      parsed = JSON.parse(text);
    } catch (_err) {
      throw new Error(fieldLabel + " must be valid JSON.");
    }

    if (expectType === "object") {
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
        throw new Error(fieldLabel + " must be a JSON object.");
      }
    }
    if (expectType === "array") {
      if (!Array.isArray(parsed)) {
        throw new Error(fieldLabel + " must be a JSON array.");
      }
    }
    return parsed;
  }

  function toPrettyJson(value) {
    if (value === undefined) return "";
    if (value === null) return "null";
    return JSON.stringify(value, null, 2);
  }

  function assignOptionalText(target, key, value) {
    var text = String(value || "").trim();
    if (text) {
      target[key] = text;
      return;
    }
    delete target[key];
  }

  function assignOptionalNumber(target, key, value) {
    var text = String(value || "").trim();
    if (!text) {
      delete target[key];
      return;
    }
    var num = Number(text);
    if (!Number.isFinite(num)) {
      throw new Error(key + " must be numeric.");
    }
    target[key] = num;
  }

  function composeDraftText() {
    var chunks = [];
    var base = dom.entityText.value.trim();
    var skills = dom.skillsText.value.trim();
    var materials = dom.materialsText.value.trim();
    var talents = dom.talentsText.value.trim();
    var notes = dom.notesText.value.trim();

    if (base) chunks.push(base);
    if (skills) chunks.push("Skills:\n" + skills);
    if (materials) chunks.push("Materials:\n" + materials);
    if (talents) chunks.push("Talents:\n" + talents);
    if (notes) chunks.push("Notes:\n" + notes);
    return chunks.join("\n\n");
  }

  function readEditorInput() {
    return {
      game: currentGame(),
      kind: currentKind(),
      id: dom.entityId.value.trim() || null,
      name: dom.entityName.value.trim() || null,
      text: composeDraftText()
    };
  }

  function parseJsonEditor() {
    var raw = dom.entityJson.value.trim();
    if (!raw) {
      throw new Error(tr("errorEntityJsonRequired"));
    }
    var entity = null;
    try {
      entity = JSON.parse(raw);
    } catch (_err) {
      throw new Error(tr("errorEntityJsonParse"));
    }
    if (!entity || typeof entity !== "object" || Array.isArray(entity)) {
      throw new Error(tr("errorEntityJsonObject"));
    }
    return entity;
  }

  function buildTemplateEntity() {
    var game = currentGame();
    var kind = currentKind();
    var id = dom.entityId.value.trim() || ("new_" + game + "_" + kind);
    var name = dom.entityName.value.trim() || "";
    return {
      id: id,
      name: name,
      game: game,
      entityType: kind,
      kind: kind,
      materialRefs: [],
      manualSections: {
        skills: [],
        talents: [],
        notes: []
      },
      rawText: ""
    };
  }

  function buildWizardTemplateEntity() {
    var entity = buildTemplateEntity();
    var game = currentGame();
    var kind = currentKind();

    if (kind === "character") {
      entity.title = "";
      entity.version = "";
      entity.rarity = game === "gi" ? 5 : 4;
      entity.element = "";
      if (game === "gi") {
        entity.weaponType = "";
        entity.nation = "";
        entity.affiliation = "";
        entity.baseStats = {};
        entity.maxStats = {};
      } else {
        entity.path = "";
        entity.baseStats = {};
      }
      return entity;
    }

    if (kind === "weapon") {
      entity.version = "";
      entity.rarity = 4;
      entity.weaponType = "";
      entity.baseAtk = 0;
      entity.subStatType = "";
      entity.subStatValue = 0;
      return entity;
    }

    if (kind === "lightcone") {
      entity.version = "";
      entity.rarity = 4;
      entity.path = "";
      entity.skillId = 0;
      entity.baseStats = {};
      return entity;
    }

    if (kind === "artifact" || kind === "relic") {
      entity.version = "";
      entity.rarity = 5;
      entity.detail = {};
      return entity;
    }

    if (kind === "enemy") {
      entity.stats = {};
      entity.resistance = {};
      entity.weakness = [];
      entity.analysis = null;
      return entity;
    }

    if (kind === "banner") {
      entity.version = "";
      entity.phase = 1;
      entity.featuredFiveStar = [];
      entity.featuredFourStar = [];
      return entity;
    }

    return entity;
  }

  function clearEditor() {
    dom.entityId.value = "";
    dom.humanId.value = "";
    dom.wizardId.value = "";
    dom.entityName.value = "";
    dom.entityText.value = "";
    dom.skillsText.value = "";
    dom.materialsText.value = "";
    dom.talentsText.value = "";
    dom.notesText.value = "";
    dom.entityJson.value = "";
    dom.previewJson.textContent = "";
    state.activeListId = "";
    setChangedPaths([]);
    populateHumanFromEntity({});
    populateWizardFromEntity({});
    renderEntityList(state.listRows);
    updateUrlState();
  }

  function extractUnknownTopLevel(payload) {
    var unknown = {};
    var keys = Object.keys(payload || {});
    for (var i = 0; i < keys.length; i += 1) {
      var key = keys[i];
      if (HUMAN_KNOWN_TOP_LEVEL_KEYS[key]) continue;
      unknown[key] = payload[key];
    }
    return unknown;
  }

  function populateHumanFromEntity(entity) {
    var payload = entity || {};
    var manual = payload.manualSections && typeof payload.manualSections === "object" && !Array.isArray(payload.manualSections)
      ? payload.manualSections
      : {};

    dom.humanId.value = payload.id !== undefined && payload.id !== null ? String(payload.id) : "";
    dom.humanName.value = payload.name || "";
    dom.humanTitle.value = payload.title || "";
    dom.humanDescription.value = payload.description || "";
    dom.humanVersion.value = payload.version !== undefined && payload.version !== null ? String(payload.version) : "";
    dom.humanRarity.value = payload.rarity !== undefined && payload.rarity !== null ? String(payload.rarity) : "";
    dom.humanWeaponType.value = payload.weaponType !== undefined && payload.weaponType !== null ? String(payload.weaponType) : "";

    dom.humanElement.value = payload.element || "";
    dom.humanPath.value = payload.path || "";
    dom.humanNation.value = payload.nation || "";
    dom.humanAffiliation.value = payload.affiliation || "";

    dom.humanMaterialRefs.value = Array.isArray(payload.materialRefs) ? payload.materialRefs.map(String).join("\n") : "";
    dom.humanWeakness.value = Array.isArray(payload.weakness) ? payload.weakness.map(String).join("\n") : "";

    dom.humanBaseStats.value = objectToKeyValueText(payload.baseStats);
    dom.humanMaxStats.value = objectToKeyValueText(payload.maxStats);
    dom.humanStats.value = objectToKeyValueText(payload.stats);
    dom.humanResistance.value = objectToKeyValueText(payload.resistance);

    dom.humanSkills.value = Array.isArray(manual.skills) ? manual.skills.join("\n") : "";
    dom.humanTalents.value = Array.isArray(manual.talents) ? manual.talents.join("\n") : "";
    dom.humanNotes.value = Array.isArray(manual.notes) ? manual.notes.join("\n") : "";
    dom.humanRawText.value = typeof payload.rawText === "string" ? payload.rawText : "";

    var combatForOther = payload.combat;
    clearHumanCharacterBlockFields();
    if (currentKind() === "character") {
      combatForOther = extractCharacterBlocksFromCombat(payload.combat, currentGame());
    }
    dom.humanCombat.value = combatForOther !== undefined ? toPrettyJson(combatForOther) : "";
    dom.humanAnalysis.value = payload.analysis !== undefined ? toPrettyJson(payload.analysis) : "";
    dom.humanDetail.value = payload.detail !== undefined ? toPrettyJson(payload.detail) : "";
    dom.humanSource.value = payload.source !== undefined ? toPrettyJson(payload.source) : "";
    dom.humanFeaturedFive.value = payload.featuredFiveStar !== undefined ? toPrettyJson(payload.featuredFiveStar) : "";
    dom.humanFeaturedFour.value = payload.featuredFourStar !== undefined ? toPrettyJson(payload.featuredFourStar) : "";

    var other = extractUnknownTopLevel(payload);
    dom.humanOtherJson.value = Object.keys(other).length ? JSON.stringify(other, null, 2) : "";
    updateHumanCharacterBlocksVisibility();
  }

  function populateWizardFromEntity(entity) {
    var payload = entity || {};
    var manual = payload.manualSections && typeof payload.manualSections === "object" && !Array.isArray(payload.manualSections)
      ? payload.manualSections
      : {};

    dom.wizardId.value = payload.id !== undefined && payload.id !== null ? String(payload.id) : dom.entityId.value.trim();
    dom.wizardName.value = payload.name || dom.entityName.value || "";
    dom.wizardTitle.value = payload.title || "";
    dom.wizardDescription.value = payload.description || "";
    dom.wizardVersion.value = payload.version !== undefined && payload.version !== null ? String(payload.version) : "";
    dom.wizardRarity.value = payload.rarity !== undefined && payload.rarity !== null ? String(payload.rarity) : "";
    dom.wizardElement.value = payload.element || "";
    dom.wizardPath.value = payload.path || "";
    dom.wizardWeaponType.value = payload.weaponType !== undefined && payload.weaponType !== null ? String(payload.weaponType) : "";
    dom.wizardNation.value = payload.nation || "";
    dom.wizardAffiliation.value = payload.affiliation || "";
    dom.wizardPhase.value = payload.phase !== undefined && payload.phase !== null ? String(payload.phase) : "";
    dom.wizardBaseAtk.value = payload.baseAtk !== undefined && payload.baseAtk !== null ? String(payload.baseAtk) : "";
    dom.wizardSubstatType.value = payload.subStatType || "";
    dom.wizardSubstatValue.value = payload.subStatValue !== undefined && payload.subStatValue !== null ? String(payload.subStatValue) : "";
    dom.wizardSkillId.value = payload.skillId !== undefined && payload.skillId !== null ? String(payload.skillId) : "";
    dom.wizardMaterialRefs.value = Array.isArray(payload.materialRefs) ? payload.materialRefs.map(String).join("\n") : "";
    dom.wizardWeakness.value = Array.isArray(payload.weakness) ? payload.weakness.map(String).join("\n") : "";
    dom.wizardBaseStats.value = objectToKeyValueText(payload.baseStats);
    dom.wizardMaxStats.value = objectToKeyValueText(payload.maxStats);
    dom.wizardStats.value = objectToKeyValueText(payload.stats);
    dom.wizardResistance.value = objectToKeyValueText(payload.resistance);
    dom.wizardSkills.value = Array.isArray(manual.skills) ? manual.skills.join("\n") : "";
    dom.wizardTalents.value = Array.isArray(manual.talents) ? manual.talents.join("\n") : "";
    dom.wizardNotes.value = Array.isArray(manual.notes) ? manual.notes.join("\n") : "";
    dom.wizardRawText.value = typeof payload.rawText === "string" ? payload.rawText : "";
    dom.wizardFeaturedFive.value = payload.featuredFiveStar !== undefined ? toPrettyJson(payload.featuredFiveStar) : "";
    dom.wizardFeaturedFour.value = payload.featuredFourStar !== undefined ? toPrettyJson(payload.featuredFourStar) : "";

    var other = extractUnknownTopLevel(payload);
    dom.wizardExtraJson.value = Object.keys(other).length ? JSON.stringify(other, null, 2) : "";
    updateWizardKindHint();
  }

  function applyWizardToEntity(baseEntity) {
    var entity = {};
    if (baseEntity && typeof baseEntity === "object" && !Array.isArray(baseEntity)) {
      entity = JSON.parse(JSON.stringify(baseEntity));
    }

    var id = dom.entityId.value.trim() || dom.wizardId.value.trim() || (entity.id ? String(entity.id).trim() : "");
    if (!id) {
      throw new Error(tr("errorIdRequired"));
    }
    entity.id = id;
    entity.game = currentGame();
    entity.entityType = currentKind();
    entity.kind = currentKind();

    assignOptionalText(entity, "name", dom.wizardName.value);
    assignOptionalText(entity, "title", dom.wizardTitle.value);
    assignOptionalText(entity, "description", dom.wizardDescription.value);
    assignOptionalText(entity, "version", dom.wizardVersion.value);
    assignOptionalText(entity, "element", dom.wizardElement.value);
    assignOptionalText(entity, "path", dom.wizardPath.value);
    assignOptionalText(entity, "nation", dom.wizardNation.value);
    assignOptionalText(entity, "affiliation", dom.wizardAffiliation.value);

    assignOptionalNumber(entity, "rarity", dom.wizardRarity.value);
    assignOptionalNumber(entity, "phase", dom.wizardPhase.value);
    assignOptionalNumber(entity, "baseAtk", dom.wizardBaseAtk.value);
    assignOptionalNumber(entity, "subStatValue", dom.wizardSubstatValue.value);
    assignOptionalNumber(entity, "skillId", dom.wizardSkillId.value);

    var weaponTypeRaw = String(dom.wizardWeaponType.value || "").trim();
    if (!weaponTypeRaw) {
      delete entity.weaponType;
    } else if (/^-?\d+$/.test(weaponTypeRaw)) {
      entity.weaponType = Number(weaponTypeRaw);
    } else {
      entity.weaponType = weaponTypeRaw;
    }

    assignOptionalText(entity, "subStatType", dom.wizardSubstatType.value);

    var materialRefs = splitLines(dom.wizardMaterialRefs.value);
    if (materialRefs.length) entity.materialRefs = materialRefs; else delete entity.materialRefs;

    var weakness = splitLines(dom.wizardWeakness.value);
    if (weakness.length) entity.weakness = weakness; else delete entity.weakness;

    var baseStats = parseKeyValueText(dom.wizardBaseStats.value, "Wizard Base Stats");
    var maxStats = parseKeyValueText(dom.wizardMaxStats.value, "Wizard Max Stats");
    var stats = parseKeyValueText(dom.wizardStats.value, "Wizard Enemy Stats");
    var resistance = parseKeyValueText(dom.wizardResistance.value, "Wizard Resistance");
    if (baseStats !== undefined) entity.baseStats = baseStats; else delete entity.baseStats;
    if (maxStats !== undefined) entity.maxStats = maxStats; else delete entity.maxStats;
    if (stats !== undefined) entity.stats = stats; else delete entity.stats;
    if (resistance !== undefined) entity.resistance = resistance; else delete entity.resistance;

    var manual = entity.manualSections && typeof entity.manualSections === "object" && !Array.isArray(entity.manualSections)
      ? entity.manualSections
      : {};
    var manualSkills = splitLines(dom.wizardSkills.value);
    var manualTalents = splitLines(dom.wizardTalents.value);
    var manualNotes = splitLines(dom.wizardNotes.value);
    if (manualSkills.length) manual.skills = manualSkills; else delete manual.skills;
    if (manualTalents.length) manual.talents = manualTalents; else delete manual.talents;
    if (manualNotes.length) manual.notes = manualNotes; else delete manual.notes;
    if (Object.keys(manual).length) entity.manualSections = manual; else delete entity.manualSections;

    assignOptionalText(entity, "rawText", dom.wizardRawText.value);

    var featuredFiveJson = parseOptionalJson(dom.wizardFeaturedFive.value, "Wizard Featured Five Star", "array");
    var featuredFourJson = parseOptionalJson(dom.wizardFeaturedFour.value, "Wizard Featured Four Star", "array");
    if (featuredFiveJson !== undefined) entity.featuredFiveStar = featuredFiveJson; else delete entity.featuredFiveStar;
    if (featuredFourJson !== undefined) entity.featuredFourStar = featuredFourJson; else delete entity.featuredFourStar;

    var extraText = String(dom.wizardExtraJson.value || "").trim();
    if (extraText) {
      var extraObject = parseOptionalJson(extraText, "Wizard Extra Fields", "object") || {};
      var extraKeys = Object.keys(extraObject);
      for (var i = 0; i < extraKeys.length; i += 1) {
        var k = extraKeys[i];
        entity[k] = extraObject[k];
      }
    }

    return entity;
  }

  function applyHumanToEntity(baseEntity) {
    var entity = {};
    if (baseEntity && typeof baseEntity === "object" && !Array.isArray(baseEntity)) {
      entity = JSON.parse(JSON.stringify(baseEntity));
    }

    var id = dom.entityId.value.trim() || dom.humanId.value.trim() || (entity.id ? String(entity.id).trim() : "");
    if (!id) {
      throw new Error(tr("errorIdRequired"));
    }
    entity.id = id;
    entity.game = currentGame();
    entity.entityType = currentKind();
    entity.kind = currentKind();

    assignOptionalText(entity, "name", dom.humanName.value);
    assignOptionalText(entity, "title", dom.humanTitle.value);
    assignOptionalText(entity, "description", dom.humanDescription.value);
    assignOptionalText(entity, "version", dom.humanVersion.value);
    assignOptionalText(entity, "element", dom.humanElement.value);
    assignOptionalText(entity, "path", dom.humanPath.value);
    assignOptionalText(entity, "nation", dom.humanNation.value);
    assignOptionalText(entity, "affiliation", dom.humanAffiliation.value);

    assignOptionalNumber(entity, "rarity", dom.humanRarity.value);

    var weaponTypeRaw = String(dom.humanWeaponType.value || "").trim();
    if (!weaponTypeRaw) {
      delete entity.weaponType;
    } else if (/^-?\d+$/.test(weaponTypeRaw)) {
      entity.weaponType = Number(weaponTypeRaw);
    } else {
      entity.weaponType = weaponTypeRaw;
    }

    var materialRefs = splitLines(dom.humanMaterialRefs.value);
    if (materialRefs.length) {
      entity.materialRefs = materialRefs;
    } else {
      delete entity.materialRefs;
    }

    var weakness = splitLines(dom.humanWeakness.value);
    if (weakness.length) {
      entity.weakness = weakness;
    } else {
      delete entity.weakness;
    }

    var baseStats = parseKeyValueText(dom.humanBaseStats.value, "Base Stats");
    var maxStats = parseKeyValueText(dom.humanMaxStats.value, "Max Stats");
    var stats = parseKeyValueText(dom.humanStats.value, "Enemy Stats");
    var resistance = parseKeyValueText(dom.humanResistance.value, "Resistance");

    if (baseStats !== undefined) {
      entity.baseStats = baseStats;
    } else {
      delete entity.baseStats;
    }
    if (maxStats !== undefined) {
      entity.maxStats = maxStats;
    } else {
      delete entity.maxStats;
    }
    if (stats !== undefined) {
      entity.stats = stats;
    } else {
      delete entity.stats;
    }
    if (resistance !== undefined) {
      entity.resistance = resistance;
    } else {
      delete entity.resistance;
    }

    var manual = entity.manualSections && typeof entity.manualSections === "object" && !Array.isArray(entity.manualSections)
      ? entity.manualSections
      : {};
    var manualSkills = splitLines(dom.humanSkills.value);
    var manualTalents = splitLines(dom.humanTalents.value);
    var manualNotes = splitLines(dom.humanNotes.value);

    if (manualSkills.length) {
      manual.skills = manualSkills;
    } else {
      delete manual.skills;
    }
    if (manualTalents.length) {
      manual.talents = manualTalents;
    } else {
      delete manual.talents;
    }
    if (manualNotes.length) {
      manual.notes = manualNotes;
    } else {
      delete manual.notes;
    }
    if (Object.keys(manual).length) {
      entity.manualSections = manual;
    } else {
      delete entity.manualSections;
    }

    assignOptionalText(entity, "rawText", dom.humanRawText.value);

    var combatJson = parseOptionalJson(dom.humanCombat.value, "Combat JSON", "object");
    var characterCombatJson = buildCharacterCombatBlocks();
    var analysisJson = parseOptionalJson(dom.humanAnalysis.value, "Analysis JSON");
    var detailJson = parseOptionalJson(dom.humanDetail.value, "Detail JSON");
    var sourceJson = parseOptionalJson(dom.humanSource.value, "Source JSON", "object");
    var featuredFiveJson = parseOptionalJson(dom.humanFeaturedFive.value, "Featured Five Star", "array");
    var featuredFourJson = parseOptionalJson(dom.humanFeaturedFour.value, "Featured Four Star", "array");

    var mergedCombat = undefined;
    if (combatJson !== undefined) {
      mergedCombat = deepClone(combatJson);
    }
    if (characterCombatJson !== undefined) {
      if (mergedCombat === undefined) mergedCombat = {};
      var characterKeys = Object.keys(characterCombatJson);
      for (var ck = 0; ck < characterKeys.length; ck += 1) {
        var combatKey = characterKeys[ck];
        mergedCombat[combatKey] = characterCombatJson[combatKey];
      }
    }

    if (mergedCombat !== undefined && !isEmptyPlainObject(mergedCombat)) {
      entity.combat = mergedCombat;
    } else {
      delete entity.combat;
    }
    if (analysisJson !== undefined) entity.analysis = analysisJson; else delete entity.analysis;
    if (detailJson !== undefined) entity.detail = detailJson; else delete entity.detail;
    if (sourceJson !== undefined) entity.source = sourceJson; else delete entity.source;
    if (featuredFiveJson !== undefined) entity.featuredFiveStar = featuredFiveJson; else delete entity.featuredFiveStar;
    if (featuredFourJson !== undefined) entity.featuredFourStar = featuredFourJson; else delete entity.featuredFourStar;

    var otherText = String(dom.humanOtherJson.value || "").trim();
    if (otherText) {
      var otherObject = parseOptionalJson(otherText, "Other Top-Level Fields", "object") || {};
      var keys = Object.keys(entity);
      for (var i = 0; i < keys.length; i += 1) {
        var key = keys[i];
        if (HUMAN_KNOWN_TOP_LEVEL_KEYS[key]) continue;
        delete entity[key];
      }
      var otherKeys = Object.keys(otherObject);
      for (var j = 0; j < otherKeys.length; j += 1) {
        var k = otherKeys[j];
        entity[k] = otherObject[k];
      }
    }

    return entity;
  }

  function syncDraftFromHuman() {
    dom.entityName.value = dom.humanName.value.trim();
    dom.skillsText.value = dom.humanSkills.value;
    dom.talentsText.value = dom.humanTalents.value;
    dom.notesText.value = dom.humanNotes.value;
    dom.materialsText.value = dom.humanMaterialRefs.value;
    dom.entityText.value = dom.humanRawText.value;
  }

  function syncDraftFromWizard() {
    dom.entityName.value = dom.wizardName.value.trim();
    dom.skillsText.value = dom.wizardSkills.value;
    dom.talentsText.value = dom.wizardTalents.value;
    dom.notesText.value = dom.wizardNotes.value;
    dom.materialsText.value = dom.wizardMaterialRefs.value;
    dom.entityText.value = dom.wizardRawText.value;
  }

  function fillFormFromEntity(entity) {
    var payload = entity || {};
    if (payload.id !== undefined && payload.id !== null) {
      dom.entityId.value = String(payload.id);
      dom.humanId.value = String(payload.id);
      dom.wizardId.value = String(payload.id);
      state.activeListId = String(payload.id);
    }
    dom.entityName.value = payload.name || payload.title || "";
    dom.entityJson.value = JSON.stringify(payload, null, 2);

    var manual = payload.manualSections || {};
    dom.skillsText.value = Array.isArray(manual.skills) ? manual.skills.join("\n") : "";
    dom.talentsText.value = Array.isArray(manual.talents) ? manual.talents.join("\n") : "";
    dom.notesText.value = Array.isArray(manual.notes) ? manual.notes.join("\n") : "";
    dom.materialsText.value = Array.isArray(payload.materialRefs) ? payload.materialRefs.join("\n") : "";
    dom.entityText.value = typeof payload.rawText === "string" ? payload.rawText : "";

    populateHumanFromEntity(payload);
    populateWizardFromEntity(payload);
    dom.previewJson.textContent = JSON.stringify(payload, null, 2);
    renderEntityList(state.listRows);
    updateUrlState();
  }

  function renderEntityList(rows) {
    dom.entityList.innerHTML = "";
    if (!rows || !rows.length) {
      var empty = document.createElement("li");
      empty.className = "entity-item";
      empty.textContent = tr("listNoEntities");
      dom.entityList.appendChild(empty);
      return;
    }
    for (var i = 0; i < rows.length; i += 1) {
      var row = rows[i];
      var id = row.id ? String(row.id) : "";
      var name = row.name ? String(row.name) : "";

      var li = document.createElement("li");
      li.className = "entity-item";
      li.setAttribute("role", "button");
      li.setAttribute("tabindex", "0");
      if (id && id === state.activeListId) {
        li.classList.add("active");
      }
      li.setAttribute("data-id", id);

      var left = document.createElement("span");
      left.className = "entity-item-id";
      left.textContent = id || tr("listNoId");
      var right = document.createElement("span");
      right.className = "entity-item-name";
      right.textContent = name || tr("listNoName");

      li.appendChild(left);
      li.appendChild(right);
      li.addEventListener("click", onEntityListItemClick);
      li.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onEntityListItemClick(event);
        }
      });
      dom.entityList.appendChild(li);
    }
  }

  function updateListMeta(count, total) {
    dom.entityListMeta.textContent = tr("listShownTotal", {
      shown: String(count),
      total: String(total)
    });
  }

  async function refreshEntityList() {
    try {
      var game = currentGame();
      var kind = currentKind();
      var q = dom.entitySearch.value.trim();
      var path = "/api/entities/" + encodeURIComponent(game) + "/" + encodeURIComponent(kind) + "?limit=500";
      if (q) {
        path += "&q=" + encodeURIComponent(q);
      }
      var res = await apiGet(path);
      state.listRows = Array.isArray(res.rows) ? res.rows : [];
      renderEntityList(state.listRows);
      updateListMeta(state.listRows.length, res.total || state.listRows.length);
      setStatus(dom.editorStatus, "", false);
    } catch (err) {
      state.listRows = [];
      renderEntityList([]);
      updateListMeta(0, 0);
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  async function loadExisting() {
    try {
      var game = currentGame();
      var kind = currentKind();
      var entityId = dom.entityId.value.trim();
      if (!entityId) throw new Error(tr("errorEntityIdRequired"));
      var path = "/api/entity/" + encodeURIComponent(game) + "/" + encodeURIComponent(kind) + "/" + encodeURIComponent(entityId);
      var res = await apiGet(path);
      fillFormFromEntity(res.entity || {});
      openTab("tab-human");
      setStatus(dom.editorStatus, tr("statusLoadedEntity", { id: entityId }), false);
      persistDraft();
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  function createTemplate() {
    clearEditor();
    var template = buildWizardTemplateEntity();
    dom.entityId.value = template.id;
    dom.humanId.value = template.id;
    dom.wizardId.value = template.id;
    dom.entityName.value = template.name || "";
    dom.entityJson.value = JSON.stringify(template, null, 2);
    dom.previewJson.textContent = JSON.stringify(template, null, 2);
    populateHumanFromEntity(template);
    populateWizardFromEntity(template);
    openTab("tab-wizard");
    setStatus(dom.editorStatus, tr("statusCreatedTemplate"), false);
    persistDraft();
  }

  async function previewDraft() {
    try {
      var input = readEditorInput();
      if (!input.text) throw new Error(tr("errorDraftEmpty"));
      var res = await apiPost("/api/ingest", {
        game: input.game,
        kind: input.kind,
        id: input.id,
        name: input.name,
        text: input.text,
        apply: false
      });
      if (res.result && res.result.payload) {
        fillFormFromEntity(res.result.payload);
      }
      dom.previewJson.textContent = JSON.stringify(res.result || {}, null, 2);
      openTab("tab-preview");
      setStatus(dom.editorStatus, tr("statusDraftParsed"), false);
      persistDraft();
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  async function saveDraftAndSync() {
    try {
      var input = readEditorInput();
      if (!input.text) throw new Error(tr("errorDraftEmpty"));
      var res = await apiPost("/api/ingest", {
        game: input.game,
        kind: input.kind,
        id: input.id,
        name: input.name,
        text: input.text,
        apply: true
      });

      if (res.result && res.result.payload) {
        fillFormFromEntity(res.result.payload);
      }
      dom.previewJson.textContent = JSON.stringify(res.result || {}, null, 2);
      setChangedPaths((res.result && res.result.changedFiles) || []);
      setStatus(dom.editorStatus, tr("statusDraftSaved"), false);
      await refreshEntityList();
      persistDraft();
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  async function saveJsonAndSync() {
    try {
      var entity = parseJsonEditor();
      var game = currentGame();
      var kind = currentKind();
      var inputId = dom.entityId.value.trim() || "";
      var requestId = inputId || (entity.id ? String(entity.id).trim() : "");
      if (!requestId) throw new Error(tr("errorJsonNeedId"));

      var res = await apiPost("/api/entity/upsert", {
        game: game,
        kind: kind,
        id: requestId,
        entity: entity,
        sync: true
      });

      dom.entityId.value = requestId;
      dom.humanId.value = requestId;
      dom.wizardId.value = requestId;
      state.activeListId = requestId;
      if (!dom.entityName.value.trim()) {
        dom.entityName.value = entity.name || entity.title || "";
      }
      populateWizardFromEntity(entity);
      setChangedPaths(res.changedFiles || []);
      dom.previewJson.textContent = JSON.stringify(res, null, 2);
      openTab("tab-preview");
      setStatus(dom.editorStatus, tr("statusJsonSaved"), false);
      await refreshEntityList();
      persistDraft();
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  function formatJson() {
    try {
      var entity = parseJsonEditor();
      dom.entityJson.value = JSON.stringify(entity, null, 2);
      populateHumanFromEntity(entity);
      populateWizardFromEntity(entity);
      setStatus(dom.editorStatus, tr("statusJsonFormatted"), false);
      persistDraft();
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  function validateJson() {
    try {
      var entity = parseJsonEditor();
      var id = dom.entityId.value.trim() || (entity.id ? String(entity.id).trim() : "");
      if (!id) throw new Error(tr("errorJsonNoId"));
      setStatus(dom.editorStatus, tr("statusJsonValid"), false);
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  function loadHumanFromJson() {
    try {
      var entity = parseJsonEditor();
      populateHumanFromEntity(entity);
      populateWizardFromEntity(entity);
      setStatus(dom.editorStatus, tr("statusHumanLoaded"), false);
      persistDraft();
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  function applyHumanToJson() {
    try {
      var baseEntity = null;
      var raw = dom.entityJson.value.trim();
      if (raw) {
        baseEntity = parseJsonEditor();
      }
      var merged = applyHumanToEntity(baseEntity);
      dom.entityId.value = String(merged.id || "");
      dom.humanId.value = String(merged.id || "");
      dom.wizardId.value = String(merged.id || "");
      dom.entityName.value = merged.name || merged.title || "";
      syncDraftFromHuman();
      dom.entityJson.value = JSON.stringify(merged, null, 2);
      dom.previewJson.textContent = JSON.stringify(merged, null, 2);
      populateWizardFromEntity(merged);
      setStatus(dom.editorStatus, tr("statusHumanApplied"), false);
      persistDraft();
      updateUrlState();
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  function loadWizardTemplate() {
    try {
      var template = buildWizardTemplateEntity();
      fillFormFromEntity(template);
      openTab("tab-wizard");
      var gameLabel = dom.game.options[dom.game.selectedIndex]
        ? dom.game.options[dom.game.selectedIndex].textContent
        : currentGame().toUpperCase();
      var kindLabel = dom.kind.options[dom.kind.selectedIndex]
        ? dom.kind.options[dom.kind.selectedIndex].textContent
        : currentKind();
      setStatus(dom.editorStatus, tr("statusWizardLoaded", { game: gameLabel, kind: kindLabel }), false);
      persistDraft();
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  function loadWizardFromJson() {
    try {
      var entity = parseJsonEditor();
      populateWizardFromEntity(entity);
      setStatus(dom.editorStatus, tr("statusWizardFromJson"), false);
      persistDraft();
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  function generateJsonFromWizard() {
    try {
      var baseEntity = null;
      var raw = dom.entityJson.value.trim();
      if (raw) {
        baseEntity = parseJsonEditor();
      }
      var merged = applyWizardToEntity(baseEntity);
      dom.entityId.value = String(merged.id || "");
      dom.humanId.value = String(merged.id || "");
      dom.wizardId.value = String(merged.id || "");
      dom.entityName.value = merged.name || merged.title || "";
      syncDraftFromWizard();
      dom.entityJson.value = JSON.stringify(merged, null, 2);
      dom.previewJson.textContent = JSON.stringify(merged, null, 2);
      populateHumanFromEntity(merged);
      setStatus(dom.editorStatus, tr("statusWizardGenerated"), false);
      persistDraft();
      updateUrlState();
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  async function createPrFromLocalFiles() {
    try {
      var repo = dom.ghRepo.value.trim();
      var base = dom.ghBase.value.trim() || "main";
      var tokenInput = dom.ghToken.value.trim();
      var title = dom.ghTitle.value.trim();
      var body = dom.ghBody.value;
      var paths = dom.ghPaths.value.split("\n").map(function (x) {
        return x.trim();
      }).filter(function (x) {
        return !!x;
      });
      if (!repo || !tokenInput || !title || !paths.length) {
        throw new Error(tr("errorGithubRequired"));
      }
      var res = await apiPost("/api/github/pr-from-local", {
        repo: repo,
        token: tokenInput,
        title: title,
        body: body,
        base: base,
        paths: paths
      });
      setStatus(
        dom.ghStatus,
        tr("statusPrCreated", { url: res.pullRequestUrl || ("#" + String(res.pullRequestNumber || "")) }),
        false
      );
    } catch (err) {
      setStatus(dom.ghStatus, String(err.message || err), true);
    }
  }

  function persistDraft() {
    var payload = {
      game: dom.game.value,
      kind: dom.kind.value,
      entityId: dom.entityId.value,
      entityName: dom.entityName.value,
      entitySearch: dom.entitySearch.value,
      entityText: dom.entityText.value,
      skillsText: dom.skillsText.value,
      materialsText: dom.materialsText.value,
      talentsText: dom.talentsText.value,
      notesText: dom.notesText.value,
      entityJson: dom.entityJson.value,
      currentTab: state.currentTab
    };

    for (var i = 0; i < persistIds.length; i += 1) {
      var id = persistIds[i];
      var node = document.getElementById(id);
      if (!node) continue;
      payload[id] = node.value;
    }

    localStorage.setItem("admin_draft_v3", JSON.stringify(payload));
  }

  function restoreDraft() {
    var raw = localStorage.getItem("admin_draft_v3") || localStorage.getItem("admin_draft_v2");
    if (!raw) return;
    try {
      var payload = JSON.parse(raw);
      if (!payload || typeof payload !== "object") return;
      if (payload.game) dom.game.value = payload.game;
      syncKindOptions();
      if (payload.kind && allowedKinds(dom.game.value).indexOf(payload.kind) >= 0) {
        dom.kind.value = payload.kind;
      }

      for (var i = 0; i < persistIds.length; i += 1) {
        var id = persistIds[i];
        var node = document.getElementById(id);
        if (!node) continue;
        if (payload[id] !== undefined && payload[id] !== null) {
          node.value = payload[id];
        }
      }

      if (payload.entityId !== undefined) dom.entityId.value = payload.entityId;
      if (payload.entityName !== undefined) dom.entityName.value = payload.entityName;
      if (payload.entitySearch !== undefined) dom.entitySearch.value = payload.entitySearch;
      if (payload.entityJson !== undefined) dom.entityJson.value = payload.entityJson;
      if (payload.currentTab) state.currentTab = payload.currentTab;

      if (dom.entityId.value.trim()) {
        dom.humanId.value = dom.entityId.value.trim();
        dom.wizardId.value = dom.entityId.value.trim();
      }
    } catch (_err) {
      // Ignore corrupted local draft payloads.
    }
  }

  function onEntityListItemClick(event) {
    var target = event.currentTarget;
    var entityId = target ? target.getAttribute("data-id") : "";
    if (!entityId) return;
    dom.entityId.value = entityId;
    dom.humanId.value = entityId;
    dom.wizardId.value = entityId;
    state.activeListId = entityId;
    updateUrlState();
    loadExisting();
  }

  function onSearchInput() {
    if (state.searchTimer) {
      clearTimeout(state.searchTimer);
    }
    state.searchTimer = window.setTimeout(function () {
      refreshEntityList();
      persistDraft();
    }, 180);
  }

  async function doLogin() {
    try {
      var password = dom.adminPassword.value;
      if (!password) throw new Error(tr("errorPasswordRequired"));
      var res = await apiPost("/api/login", { password: password });
      state.token = res.token || "";
      localStorage.setItem("admin_token", state.token);
      setAuthState(true);
      setStatus(dom.loginStatus, tr("statusLoginOk"), false);
      dom.adminPassword.value = "";
      await refreshEntityList();
    } catch (err) {
      setStatus(dom.loginStatus, String(err.message || err), true);
    }
  }

  async function doLogout() {
    try {
      await apiPost("/api/logout", {});
    } catch (_err) {
      // Ignore logout API errors.
    }
    state.token = "";
    localStorage.removeItem("admin_token");
    setAuthState(false);
    setStatus(dom.editorStatus, "", false);
    setStatus(dom.ghStatus, "", false);
    setStatus(dom.loginStatus, tr("statusLoggedOut"), false);
  }

  async function probeSession() {
    if (!state.token) {
      setAuthState(false);
      return;
    }
    try {
      await apiGet("/api/entities/gi/character?limit=1");
      setAuthState(true);
      await refreshEntityList();
    } catch (_err) {
      state.token = "";
      localStorage.removeItem("admin_token");
      setAuthState(false);
    }
  }

  function onTabKeydown(event) {
    var index = dom.tabs.indexOf(event.currentTarget);
    if (index < 0) return;
    var next = index;
    if (event.key === "ArrowRight") {
      next = (index + 1) % dom.tabs.length;
    } else if (event.key === "ArrowLeft") {
      next = (index - 1 + dom.tabs.length) % dom.tabs.length;
    } else if (event.key === "Home") {
      next = 0;
    } else if (event.key === "End") {
      next = dom.tabs.length - 1;
    } else {
      return;
    }
    event.preventDefault();
    var tab = dom.tabs[next];
    if (!tab) return;
    tab.focus();
    openTab(tab.id);
  }

  function bindEvents() {
    dom.loginBtn.addEventListener("click", doLogin);
    dom.logoutBtn.addEventListener("click", doLogout);
    dom.refreshListBtn.addEventListener("click", refreshEntityList);
    dom.loadBtn.addEventListener("click", loadExisting);
    dom.newBtn.addEventListener("click", createTemplate);
    dom.previewBtn.addEventListener("click", previewDraft);
    dom.saveBtn.addEventListener("click", saveDraftAndSync);
    dom.saveJsonBtn.addEventListener("click", saveJsonAndSync);
    dom.formatJsonBtn.addEventListener("click", formatJson);
    dom.validateJsonBtn.addEventListener("click", validateJson);
    dom.loadHumanBtn.addEventListener("click", loadHumanFromJson);
    dom.applyHumanBtn.addEventListener("click", applyHumanToJson);
    dom.wizardTemplateBtn.addEventListener("click", loadWizardTemplate);
    dom.wizardLoadJsonBtn.addEventListener("click", loadWizardFromJson);
    dom.wizardGenerateBtn.addEventListener("click", generateJsonFromWizard);
    dom.ghPrBtn.addEventListener("click", createPrFromLocalFiles);
    dom.entitySearch.addEventListener("input", onSearchInput);
    if (dom.langSelect) {
      dom.langSelect.addEventListener("change", function () {
        var next = String(dom.langSelect.value || "en");
        if (next !== "en" && next !== "zh") return;
        state.lang = next;
        localStorage.setItem("admin_lang", state.lang);
        applyI18nUI();
      });
    }

    dom.game.addEventListener("change", function () {
      syncKindOptions();
      updateWizardKindHint();
      updateHumanCharacterBlocksVisibility();
      refreshEntityList();
      updateUrlState();
      persistDraft();
    });

    dom.kind.addEventListener("change", function () {
      updateWizardKindHint();
      updateHumanCharacterBlocksVisibility();
      refreshEntityList();
      updateUrlState();
      persistDraft();
    });

    dom.entityId.addEventListener("input", function () {
      dom.humanId.value = dom.entityId.value.trim();
      dom.wizardId.value = dom.entityId.value.trim();
      updateUrlState();
      persistDraft();
    });

    dom.adminPassword.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        doLogin();
      }
    });

    dom.entityId.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        loadExisting();
      }
    });

    var fields = persistIds.map(function (id) {
      return document.getElementById(id);
    }).filter(function (node) {
      return !!node;
    });

    fields.forEach(function (node) {
      node.addEventListener("input", persistDraft);
      node.addEventListener("change", persistDraft);
    });

    dom.tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        openTab(tab.id);
        persistDraft();
      });
      tab.addEventListener("keydown", onTabKeydown);
    });
  }

  function init() {
    syncKindOptions();
    if (dom.langSelect) {
      dom.langSelect.value = state.lang;
    }
    updateWizardKindHint();
    restoreDraft();
    applyUrlState();
    bindEvents();
    openTab(state.currentTab || "tab-human", true);

    if (dom.entityJson.value.trim()) {
      try {
        var parsed = parseJsonEditor();
        populateHumanFromEntity(parsed);
        populateWizardFromEntity(parsed);
      } catch (_err) {
        var fallbackEntity = {
          id: dom.entityId.value.trim(),
          name: dom.entityName.value.trim(),
          rawText: dom.entityText.value
        };
        populateHumanFromEntity(fallbackEntity);
        populateWizardFromEntity(fallbackEntity);
      }
    } else {
      var baseEntity = {
        id: dom.entityId.value.trim(),
        name: dom.entityName.value.trim(),
        rawText: dom.entityText.value
      };
      populateHumanFromEntity(baseEntity);
      populateWizardFromEntity(baseEntity);
    }

    updateHumanCharacterBlocksVisibility();
    applyI18nUI();
    updateUrlState();
    probeSession();
  }

  init();
})();
