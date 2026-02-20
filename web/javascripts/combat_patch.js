(function () {
  const ALLOWED_PREFIXES = [
    "/",
    "/index",
    "/yhb",
    "/admin",
    "/gi/monster",
    "/gi/boss",
    "/gi/char",
    "/gi/3boss",
    "/gi/abyss",
    "/gi/maze",
    "/gi/banner",
    "/gi/ach",
    "/gi/tut",
    "/gi/change",
    "/gi/formulae",
    "/sr/monster",
    "/sr/boss",
    "/sr/char",
    "/sr/chaos",
    "/sr/fiction",
    "/sr/shadow",
    "/sr/arbitration",
    "/sr/du",
    "/sr/du31",
    "/sr/banner",
    "/sr/ach",
    "/sr/stage",
    "/sr/effect",
    "/sr/change",
    "/sr/future",
    "/sr/formulae",
    "/sr/linecount"
  ];

  const BLOCKED_EXACT = new Set([
    "/yunli",
    "/sr/yunli2",
    "/sr/yunli4",
    "/sr/yunli5"
  ]);

  function normalizePath(pathname) {
    if (!pathname) return "/";
    const clean = pathname.replace(/\/+$/, "");
    return clean || "/";
  }

  function isAllowed(pathname) {
    const p = normalizePath(pathname);
    if (p === "/home") return true;
    if (BLOCKED_EXACT.has(p)) return false;
    for (const prefix of ALLOWED_PREFIXES) {
      const n = normalizePath(prefix);
      if (n === "/") {
        if (p === "/") return true;
        continue;
      }
      if (p === n || p.startsWith(n + "/")) return true;
    }
    return false;
  }

  function isLocalHref(href) {
    try {
      const url = new URL(href, window.location.origin);
      return url.origin === window.location.origin;
    } catch {
      return false;
    }
  }

  function markBlockedLink(anchor) {
    anchor.dataset.combatBlocked = "1";
    anchor.style.opacity = "0.65";
    anchor.title = "Removed in combat-only mode";
    anchor.style.pointerEvents = "none";
    anchor.style.cursor = "not-allowed";
  }

  function sanitizeAnchors() {
    const anchors = document.querySelectorAll("a[href]");
    for (const anchor of anchors) {
      if (!isLocalHref(anchor.href)) continue;
      const url = new URL(anchor.href, window.location.origin);
      const path = normalizePath(url.pathname);
      if (path === "/home") {
        anchor.setAttribute("href", "/index");
        continue;
      }
      if (isAllowed(path)) continue;
      markBlockedLink(anchor);
      if (BLOCKED_EXACT.has(path)) {
        const maybeCard = anchor.closest(".hover-shadow, .new_block, .new_section, .dir");
        if (maybeCard) {
          maybeCard.remove();
        }
      }
    }
  }

  document.addEventListener("click", function (event) {
    const anchor = event.target && event.target.closest ? event.target.closest("a[href]") : null;
    if (!anchor || !isLocalHref(anchor.href)) return;
    const url = new URL(anchor.href, window.location.origin);
    const path = normalizePath(url.pathname);
    if (path === "/home") {
      event.preventDefault();
      window.location.href = "/index";
      return;
    }
    if (isAllowed(path)) return;
    event.preventDefault();
    event.stopPropagation();
  }, true);

  const observer = new MutationObserver(function () {
    sanitizeAnchors();
  });
  observer.observe(document.documentElement, { subtree: true, childList: true });
  sanitizeAnchors();
})();
