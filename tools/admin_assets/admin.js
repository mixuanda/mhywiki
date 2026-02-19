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
    const h = { "Content-Type": "application/json" };
    if (token) h.Authorization = "Bearer " + token;
    return h;
  }

  async function api(path, body) {
    const res = await fetch(path, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify(body || {}),
    });
    const data = await res.json().catch(() => ({ ok: false, error: "Invalid JSON response" }));
    if (!res.ok || !data.ok) {
      throw new Error(data.error || ("Request failed: " + res.status));
    }
    return data;
  }

  function readEditorInput() {
    const text = document.getElementById("entity-text").value.trim();
    const skillsText = document.getElementById("skills-text").value.trim();
    const materialsText = document.getElementById("materials-text").value.trim();
    const talentsText = document.getElementById("talents-text").value.trim();
    const notesText = document.getElementById("notes-text").value.trim();
    const composed = [
      text,
      skillsText ? "Skills:\n" + skillsText : "",
      materialsText ? "Materials:\n" + materialsText : "",
      talentsText ? "Talents:\n" + talentsText : "",
      notesText ? "Notes:\n" + notesText : "",
    ]
      .filter(Boolean)
      .join("\n\n");

    return {
      game: document.getElementById("game").value,
      kind: document.getElementById("kind").value,
      id: document.getElementById("entity-id").value.trim() || null,
      name: document.getElementById("entity-name").value.trim() || null,
      text: composed,
    };
  }

  async function doLogin() {
    try {
      const password = document.getElementById("admin-password").value;
      const res = await api("/api/login", { password: password });
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
      const res = await api("/api/ingest", { ...input, apply: false });
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
      const res = await api("/api/ingest", { ...input, apply: true });
      previewJson.textContent = JSON.stringify(res.result, null, 2);
      const changed = (res.result.changedFiles || []).join("\n");
      document.getElementById("gh-paths").value = changed;
      setStatus(editorStatus, "Saved canonical data and synced legacy files.", false);
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
      const paths = document
        .getElementById("gh-paths")
        .value.split("\n")
        .map((x) => x.trim())
        .filter(Boolean);

      if (!repo || !tokenInput || !title || !paths.length) {
        throw new Error("repo/token/title/paths are required.");
      }

      const res = await api("/api/github/pr-from-local", {
        repo: repo,
        token: tokenInput,
        title: title,
        body: body,
        base: base,
        paths: paths,
      });
      setStatus(
        ghStatus,
        "PR created: " + (res.pullRequestUrl || ("#" + String(res.pullRequestNumber || ""))),
        false
      );
    } catch (err) {
      setStatus(ghStatus, String(err.message || err), true);
    }
  }

  async function probeSession() {
    if (!token) return;
    try {
      const res = await fetch("/api/health", { headers: headers() });
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
  document.getElementById("preview-btn").addEventListener("click", preview);
  document.getElementById("save-btn").addEventListener("click", saveAndSync);
  document.getElementById("gh-pr-btn").addEventListener("click", createPrFromLocalFiles);

  probeSession();
})();
