(function () {
  var GAME_KIND_MAP = {
    gi: ["character", "weapon", "artifact", "enemy", "banner"],
    sr: ["character", "lightcone", "relic", "enemy", "banner"]
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

  var state = {
    token: localStorage.getItem("admin_token") || "",
    listRows: [],
    activeListId: "",
    searchTimer: 0,
    currentTab: "tab-human"
  };

  var dom = {
    loginCard: document.getElementById("login-card"),
    loginStatus: document.getElementById("login-status"),
    workspace: document.getElementById("workspace"),
    editorStatus: document.getElementById("editor-status"),
    githubCard: document.getElementById("github-card"),
    ghStatus: document.getElementById("gh-status"),
    sessionBadge: document.getElementById("session-badge"),
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
    dom.sessionBadge.textContent = loggedIn ? "Signed in" : "Signed out";
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
        throw new Error("Admin API is not running. Start `npm run dev:admin` and open http://127.0.0.1:8899/admin/");
      }
      throw new Error("Admin API returned non-JSON response (HTTP " + String(res.status) + ").");
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
        ? "Character wizard: fill element / weapon type / talents / base-max stats and material refs."
        : "Character wizard: fill path / element / traces / base stats and material refs.";
    }
    if (kind === "weapon") return "Weapon wizard (GI): use base ATK, sub stat type/value, and material refs.";
    if (kind === "lightcone") return "Light Cone wizard (SR): use path, skill ID, base stats, and materials.";
    if (kind === "artifact" || kind === "relic") return "Artifact/Relic wizard: fill name/version and put set effects in Extra Fields JSON.";
    if (kind === "enemy") return "Enemy wizard: use stats/resistance/weakness and optional analysis/detail blocks.";
    if (kind === "banner") return "Banner wizard: set version + phase and featured five/four star JSON arrays.";
    return "Fill applicable fields and generate JSON.";
  }

  function updateWizardKindHint() {
    if (!dom.wizardKindHint) return;
    dom.wizardKindHint.textContent = wizardKindHint(currentGame(), currentKind());
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
      throw new Error("Entity JSON is required.");
    }
    var entity = null;
    try {
      entity = JSON.parse(raw);
    } catch (_err) {
      throw new Error("Entity JSON parse failed.");
    }
    if (!entity || typeof entity !== "object" || Array.isArray(entity)) {
      throw new Error("Entity JSON must be an object.");
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

    dom.humanCombat.value = payload.combat !== undefined ? toPrettyJson(payload.combat) : "";
    dom.humanAnalysis.value = payload.analysis !== undefined ? toPrettyJson(payload.analysis) : "";
    dom.humanDetail.value = payload.detail !== undefined ? toPrettyJson(payload.detail) : "";
    dom.humanSource.value = payload.source !== undefined ? toPrettyJson(payload.source) : "";
    dom.humanFeaturedFive.value = payload.featuredFiveStar !== undefined ? toPrettyJson(payload.featuredFiveStar) : "";
    dom.humanFeaturedFour.value = payload.featuredFourStar !== undefined ? toPrettyJson(payload.featuredFourStar) : "";

    var other = extractUnknownTopLevel(payload);
    dom.humanOtherJson.value = Object.keys(other).length ? JSON.stringify(other, null, 2) : "";
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
      throw new Error("ID is required.");
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
      throw new Error("ID is required.");
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

    var combatJson = parseOptionalJson(dom.humanCombat.value, "Combat JSON");
    var analysisJson = parseOptionalJson(dom.humanAnalysis.value, "Analysis JSON");
    var detailJson = parseOptionalJson(dom.humanDetail.value, "Detail JSON");
    var sourceJson = parseOptionalJson(dom.humanSource.value, "Source JSON", "object");
    var featuredFiveJson = parseOptionalJson(dom.humanFeaturedFive.value, "Featured Five Star", "array");
    var featuredFourJson = parseOptionalJson(dom.humanFeaturedFour.value, "Featured Four Star", "array");

    if (combatJson !== undefined) entity.combat = combatJson; else delete entity.combat;
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
      empty.textContent = "No entities found.";
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
      left.textContent = id || "(no-id)";
      var right = document.createElement("span");
      right.className = "entity-item-name";
      right.textContent = name || "(no-name)";

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
    dom.entityListMeta.textContent = String(count) + " shown / " + String(total) + " total";
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
      if (!entityId) throw new Error("Entity ID is required.");
      var path = "/api/entity/" + encodeURIComponent(game) + "/" + encodeURIComponent(kind) + "/" + encodeURIComponent(entityId);
      var res = await apiGet(path);
      fillFormFromEntity(res.entity || {});
      openTab("tab-human");
      setStatus(dom.editorStatus, "Loaded entity " + entityId + ".", false);
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
    setStatus(dom.editorStatus, "New wizard template created. Fill fields and generate JSON.", false);
    persistDraft();
  }

  async function previewDraft() {
    try {
      var input = readEditorInput();
      if (!input.text) throw new Error("Draft text is empty.");
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
      setStatus(dom.editorStatus, "Draft parsed successfully.", false);
      persistDraft();
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  async function saveDraftAndSync() {
    try {
      var input = readEditorInput();
      if (!input.text) throw new Error("Draft text is empty.");
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
      setStatus(dom.editorStatus, "Saved draft and synced legacy web.", false);
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
      if (!requestId) throw new Error("ID is required in Entity ID or JSON id.");

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
      setStatus(dom.editorStatus, "Saved JSON and synced legacy web.", false);
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
      setStatus(dom.editorStatus, "JSON formatted.", false);
      persistDraft();
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  function validateJson() {
    try {
      var entity = parseJsonEditor();
      var id = dom.entityId.value.trim() || (entity.id ? String(entity.id).trim() : "");
      if (!id) throw new Error("JSON has no id.");
      setStatus(dom.editorStatus, "JSON is valid for save.", false);
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  function loadHumanFromJson() {
    try {
      var entity = parseJsonEditor();
      populateHumanFromEntity(entity);
      populateWizardFromEntity(entity);
      setStatus(dom.editorStatus, "Loaded category editor from JSON.", false);
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
      setStatus(dom.editorStatus, "Applied category edits to JSON.", false);
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
      setStatus(dom.editorStatus, "Wizard template loaded for " + currentGame().toUpperCase() + " " + currentKind() + ".", false);
      persistDraft();
    } catch (err) {
      setStatus(dom.editorStatus, String(err.message || err), true);
    }
  }

  function loadWizardFromJson() {
    try {
      var entity = parseJsonEditor();
      populateWizardFromEntity(entity);
      setStatus(dom.editorStatus, "Loaded wizard fields from JSON.", false);
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
      setStatus(dom.editorStatus, "Generated JSON from wizard.", false);
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
        throw new Error("repo/token/title/paths are required.");
      }
      var res = await apiPost("/api/github/pr-from-local", {
        repo: repo,
        token: tokenInput,
        title: title,
        body: body,
        base: base,
        paths: paths
      });
      setStatus(dom.ghStatus, "PR created: " + (res.pullRequestUrl || ("#" + String(res.pullRequestNumber || ""))), false);
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
      if (!password) throw new Error("Password is required.");
      var res = await apiPost("/api/login", { password: password });
      state.token = res.token || "";
      localStorage.setItem("admin_token", state.token);
      setAuthState(true);
      setStatus(dom.loginStatus, "Login successful.", false);
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
    setStatus(dom.loginStatus, "Logged out.", false);
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

    dom.game.addEventListener("change", function () {
      syncKindOptions();
      updateWizardKindHint();
      refreshEntityList();
      updateUrlState();
      persistDraft();
    });

    dom.kind.addEventListener("change", function () {
      updateWizardKindHint();
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

    updateUrlState();
    probeSession();
  }

  init();
})();
