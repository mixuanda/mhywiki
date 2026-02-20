(function () {
  const loginCard = document.getElementById("login-card");
  const editorCard = document.getElementById("editor-card");
  const githubCard = document.getElementById("github-card");
  const loginStatus = document.getElementById("login-status");
  const editorStatus = document.getElementById("editor-status");
  const ghStatus = document.getElementById("gh-status");
  const previewJson = document.getElementById("preview-json");
  let token = localStorage.getItem("admin_token") || "";
  function setStatus(node, text, isError) {
    node.textContent = text || "";
    node.style.color = isError ? "#fca5a5" : "#86efac";
  }
  function headers() {
    const h = {
      "Content-Type": "application/json"
    };
    if (token) h.Authorization = "Bearer " + token;
    return h;
  }
  async function requestJson(path, options) {
    const method = options && options.method || "POST";
    const body = options ? options.body : undefined;
    const reqHeaders = headers();
    if (method === "GET") {
      delete reqHeaders["Content-Type"];
    }
    const fetchOptions = {
      method: method,
      headers: reqHeaders
    };
    if (body !== undefined && method !== "GET") {
      fetchOptions.body = JSON.stringify(body || {});
    }
    const res = await fetch(path, fetchOptions);
    const raw = await res.text();
    let data = null;
    try {
      data = JSON.parse(raw);
    } catch (_err) {
      data = null;
    }
    if (!data) {
      if (res.status === 404 || res.status === 405 || res.status === 501) {
        throw new Error("Admin API is not running. Start `npm run dev:admin` and open http://127.0.0.1:8899/admin/");
      }
      throw new Error("Admin API returned non-JSON response (HTTP " + res.status + ").");
    }
    if (!res.ok || !data.ok) {
      throw new Error(data.error || "Request failed: " + res.status);
    }
    return data;
  }
  async function api(path, body) {
    return requestJson(path, {
      method: "POST",
      body: body
    });
  }
  async function apiGet(path) {
    return requestJson(path, {
      method: "GET"
    });
  }
  function readEditorInput() {
    const text = document.getElementById("entity-text").value.trim();
    const skillsText = document.getElementById("skills-text").value.trim();
    const materialsText = document.getElementById("materials-text").value.trim();
    const talentsText = document.getElementById("talents-text").value.trim();
    const notesText = document.getElementById("notes-text").value.trim();
    const composed = [text, skillsText ? "Skills:\n" + skillsText : "", materialsText ? "Materials:\n" + materialsText : "", talentsText ? "Talents:\n" + talentsText : "", notesText ? "Notes:\n" + notesText : ""].filter(Boolean).join("\n\n");
    return {
      game: document.getElementById("game").value,
      kind: document.getElementById("kind").value,
      id: document.getElementById("entity-id").value.trim() || null,
      name: document.getElementById("entity-name").value.trim() || null,
      text: composed
    };
  }
  function setChangedPaths(paths) {
    document.getElementById("gh-paths").value = (paths || []).join("\n");
  }
  function clearDraft() {
    document.getElementById("entity-id").value = "";
    document.getElementById("entity-name").value = "";
    document.getElementById("entity-text").value = "";
    document.getElementById("skills-text").value = "";
    document.getElementById("materials-text").value = "";
    document.getElementById("talents-text").value = "";
    document.getElementById("notes-text").value = "";
    document.getElementById("entity-json").value = "";
    previewJson.textContent = "";
    setChangedPaths([]);
  }
  async function doLogin() {
    try {
      const password = document.getElementById("admin-password").value;
      const res = await api("/api/login", {
        password: password
      });
      token = res.token || "";
      localStorage.setItem("admin_token", token);
      setStatus(loginStatus, "Login successful.", false);
      loginCard.classList.add("hidden");
      editorCard.classList.remove("hidden");
      githubCard.classList.remove("hidden");
    } catch (err) {
      setStatus(loginStatus, String(err.message || err), true);
    }
  }
  async function doLogout() {
    try {
      await api("/api/logout", {});
    } catch (_err) {
      // Ignore logout API failures and clear local token anyway.
    }
    token = "";
    localStorage.removeItem("admin_token");
    editorCard.classList.add("hidden");
    githubCard.classList.add("hidden");
    loginCard.classList.remove("hidden");
    setStatus(editorStatus, "", false);
    setStatus(loginStatus, "Logged out.", false);
  }
  async function preview() {
    try {
      const input = readEditorInput();
      if (!input.text) throw new Error("Text input is required.");
      const res = await api("/api/ingest", {
        ...input,
        apply: false
      });
      if (res.result && res.result.payload) {
        document.getElementById("entity-json").value = JSON.stringify(res.result.payload, null, 2);
      }
      previewJson.textContent = JSON.stringify(res.result, null, 2);
      setStatus(editorStatus, "Draft parsed successfully.", false);
    } catch (err) {
      setStatus(editorStatus, String(err.message || err), true);
    }
  }
  async function saveAndSync() {
    try {
      const input = readEditorInput();
      if (!input.text) throw new Error("Text input is required.");
      const res = await api("/api/ingest", {
        ...input,
        apply: true
      });
      if (res.result && res.result.payload) {
        document.getElementById("entity-json").value = JSON.stringify(res.result.payload, null, 2);
      }
      previewJson.textContent = JSON.stringify(res.result, null, 2);
      if (res.result && res.result.payload && res.result.payload.id) {
        document.getElementById("entity-id").value = String(res.result.payload.id);
      }
      setChangedPaths(res.result && res.result.changedFiles || []);
      setStatus(editorStatus, "Saved canonical data and synced legacy files.", false);
    } catch (err) {
      setStatus(editorStatus, String(err.message || err), true);
    }
  }
  async function loadExisting() {
    try {
      const game = document.getElementById("game").value;
      const kind = document.getElementById("kind").value;
      const entityId = document.getElementById("entity-id").value.trim();
      if (!entityId) throw new Error("Entity ID is required.");
      const res = await apiGet("/api/entity/" + encodeURIComponent(game) + "/" + encodeURIComponent(kind) + "/" + encodeURIComponent(entityId));
      const entity = res.entity || {};
      document.getElementById("entity-name").value = entity.name || entity.title || "";
      document.getElementById("entity-json").value = JSON.stringify(entity, null, 2);
      const manual = entity.manualSections || {};
      if (Array.isArray(manual.skills)) document.getElementById("skills-text").value = manual.skills.join("\n");
      if (Array.isArray(manual.talents)) document.getElementById("talents-text").value = manual.talents.join("\n");
      if (Array.isArray(manual.notes)) document.getElementById("notes-text").value = manual.notes.join("\n");
      if (Array.isArray(entity.materialRefs)) document.getElementById("materials-text").value = entity.materialRefs.join("\n");
      if (typeof entity.rawText === "string") document.getElementById("entity-text").value = entity.rawText;
      previewJson.textContent = JSON.stringify(entity, null, 2);
      setStatus(editorStatus, "Loaded existing entity.", false);
    } catch (err) {
      setStatus(editorStatus, String(err.message || err), true);
    }
  }
  async function saveJsonAndSync() {
    try {
      const game = document.getElementById("game").value;
      const kind = document.getElementById("kind").value;
      const inputId = document.getElementById("entity-id").value.trim();
      const rawJson = document.getElementById("entity-json").value.trim();
      if (!rawJson) throw new Error("Entity JSON is required.");
      let entity = null;
      try {
        entity = JSON.parse(rawJson);
      } catch (_err) {
        throw new Error("Entity JSON parse failed.");
      }
      const res = await api("/api/entity/upsert", {
        game: game,
        kind: kind,
        id: inputId || null,
        entity: entity,
        sync: true
      });
      setChangedPaths(res.changedFiles || []);
      previewJson.textContent = JSON.stringify(res, null, 2);
      if (entity && entity.id) {
        document.getElementById("entity-id").value = String(entity.id);
      }
      setStatus(editorStatus, "Saved JSON and synced legacy web.", false);
    } catch (err) {
      setStatus(editorStatus, String(err.message || err), true);
    }
  }
  async function createPrFromLocalFiles() {
    try {
      const repo = document.getElementById("gh-repo").value.trim();
      const base = document.getElementById("gh-base").value.trim() || "main";
      const tokenInput = document.getElementById("gh-token").value.trim();
      const title = document.getElementById("gh-title").value.trim();
      const body = document.getElementById("gh-body").value;
      const paths = document.getElementById("gh-paths").value.split("\n").map(x => x.trim()).filter(Boolean);
      if (!repo || !tokenInput || !title || !paths.length) {
        throw new Error("repo/token/title/paths are required.");
      }
      const res = await api("/api/github/pr-from-local", {
        repo: repo,
        token: tokenInput,
        title: title,
        body: body,
        base: base,
        paths: paths
      });
      setStatus(ghStatus, "PR created: " + (res.pullRequestUrl || "#" + String(res.pullRequestNumber || "")), false);
    } catch (err) {
      setStatus(ghStatus, String(err.message || err), true);
    }
  }
  async function probeSession() {
    if (!token) return;
    try {
      const res = await fetch("/api/health", {
        headers: headers()
      });
      if (!res.ok) throw new Error("Session expired");
      loginCard.classList.add("hidden");
      editorCard.classList.remove("hidden");
      githubCard.classList.remove("hidden");
    } catch (_err) {
      token = "";
      localStorage.removeItem("admin_token");
    }
  }
  document.getElementById("login-btn").addEventListener("click", doLogin);
  document.getElementById("logout-btn").addEventListener("click", doLogout);
  document.getElementById("load-btn").addEventListener("click", loadExisting);
  document.getElementById("new-btn").addEventListener("click", clearDraft);
  document.getElementById("preview-btn").addEventListener("click", preview);
  document.getElementById("save-btn").addEventListener("click", saveAndSync);
  document.getElementById("save-json-btn").addEventListener("click", saveJsonAndSync);
  document.getElementById("gh-pr-btn").addEventListener("click", createPrFromLocalFiles);
  probeSession();
})();