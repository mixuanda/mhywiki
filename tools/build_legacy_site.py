#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


GI_PAGE_DIRS = [
    "monster",
    "boss",
    "char",
    "3boss",
    "abyss",
    "maze",
    "banner",
    "ach",
    "tut",
    "change",
    "formulae",
]

SR_PAGE_DIRS = [
    "monster",
    "boss",
    "char",
    "chaos",
    "fiction",
    "shadow",
    "arbitration",
    "du",
    "du31",
    "banner",
    "ach",
    "stage",
    "effect",
    "change",
    "future",
    "formulae",
    "linecount",
]

GI_CH_FILES = [
    "avatar.js",
    "computer.js",
    "database.js",
    "database_extra.js",
    "maze.js",
    "bosschallenge.js",
    "ach.js",
    "tut_1.js",
    "tut_2.js",
]
GI_CH_DIRS = ["Avatar", "Weapon", "Relic"]

SR_CH_FILES = [
    "Avatar.js",
    "Monster_1.js",
    "Monster_2.js",
    "MonsterSkill.js",
    "Chaos_1.js",
    "Chaos_2.js",
    "Fiction_1.js",
    "Fiction_2.js",
    "AS.js",
    "AR.js",
    "BlessingDU.js",
    "BlessingDU31.js",
    "Achievement.js",
    "LineCount.js",
    "EMS.js",
]
SR_CH_DIRS = ["Avatar", "Weapon", "Relic"]

ROOT_COPY_DIRS = ["plugins", "stylesheets", "javascripts", "fonts", "index", "about", "yhb", "Char"]
ROOT_COPY_FILES = ["favicon.ico"]

ROOT_DATA_FILES = ["banner.js", "Stage.js", "New.js", "LevelCurves.js", "LevelCurvesSimple.js"]
GI_ROOT_FILES = ["avatar.js", "banner.js"]

ASSET_PREFIX_REWRITES = {
    "/images/": "https://homdgcat.wiki/images/",
    "/homdgcat-res/": "https://homdgcat.wiki/homdgcat-res/",
    "/EnemyChart/": "https://homdgcat.wiki/EnemyChart/",
    "/SREnemyChart/": "https://homdgcat.wiki/SREnemyChart/",
}


COMBAT_PATCH_JS = r"""(function () {
  const ALLOWED_PREFIXES = [
    "/",
    "/index",
    "/about",
    "/yhb",
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
    "/sr/linecount",
  ];

  const BLOCKED_EXACT = new Set([
    "/yunli",
    "/sr/yunli2",
    "/sr/yunli4",
    "/sr/yunli5",
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
      const maybeCard = anchor.closest(".hover-shadow, .panel, .panelw, .new_block, .new_section, .menu_CTRL section");
      const navLike = anchor.closest(".menu_GI, .menu_SR, .menu_GI_2, .menu_SR_2, .d1, .d2, .home_select");
      if (maybeCard && navLike) {
        maybeCard.remove();
      }
    }
  }

  document.addEventListener(
    "click",
    function (event) {
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
    },
    true
  );

  function hideTranslateUi() {
    document.querySelectorAll("._translate_, h3 .lang, .lang").forEach((n) => {
      n.style.display = "none";
    });
  }

  const observer = new MutationObserver(function () {
    sanitizeAnchors();
    hideTranslateUi();
  });
  observer.observe(document.documentElement, { subtree: true, childList: true });
  sanitizeAnchors();
  hideTranslateUi();
})();
"""


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".DS_Store"))


def _rewrite_text_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")

    text = text.replace('id="LANG" value=""', 'id="LANG" value="CH"')
    text = text.replace("id='LANG' value=''", "id='LANG' value='CH'")
    text = text.replace('id="IMGPRE" value="/"', 'id="IMGPRE" value="https://homdgcat.wiki/"')
    text = text.replace("id='IMGPRE' value='/'", "id='IMGPRE' value='https://homdgcat.wiki/'")

    if path.suffix == ".html":
        marker = '<script src="/javascripts/combat_patch.js" type="text/javascript"></script>'
        if marker not in text and "</html>" in text:
            text = text.replace("</html>", f"{marker}</html>")

    for before, after in ASSET_PREFIX_REWRITES.items():
        text = text.replace(before, after)

    # Fix known upstream typo: SR banner entries should route to SR characters.
    if path.name == "banner_sr.js":
        text = text.replace("/gi/char/", "/sr/char/")

    path.write_text(text, encoding="utf-8")


def _rewrite_all_text(root: Path) -> None:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".html", ".js", ".css"}:
            continue
        _rewrite_text_file(path)

    for junk in root.rglob(".DS_Store"):
        junk.unlink(missing_ok=True)


def _require(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required path missing: {path}")


def build(site_root: Path, out_root: Path, clean: bool) -> None:
    if clean and out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    for name in ROOT_COPY_DIRS:
        _require(site_root / name)
        _copy_tree(site_root / name, out_root / name)
    for name in ROOT_COPY_FILES:
        _require(site_root / name)
        _copy_file(site_root / name, out_root / name)

    # Home alias for legacy links that point to /home.
    _copy_tree(site_root / "index", out_root / "home")
    (out_root / "index.html").write_text(
        "<!doctype html><meta charset='utf-8'>"
        "<meta http-equiv='refresh' content='0; url=/index/'>"
        "<title>Redirecting...</title>",
        encoding="utf-8",
    )

    # GI pages and root assets.
    for name in GI_PAGE_DIRS:
        _require(site_root / "gi" / name)
        _copy_tree(site_root / "gi" / name, out_root / "gi" / name)
    for file_name in GI_ROOT_FILES:
        _require(site_root / "gi" / file_name)
        _copy_file(site_root / "gi" / file_name, out_root / "gi" / file_name)

    # SR pages.
    for name in SR_PAGE_DIRS:
        _require(site_root / "sr" / name)
        _copy_tree(site_root / "sr" / name, out_root / "sr" / name)

    # Root data files used by SR pages.
    for file_name in ROOT_DATA_FILES:
        _require(site_root / "data" / file_name)
        _copy_file(site_root / "data" / file_name, out_root / "data" / file_name)

    # GI CH data subset.
    (out_root / "gi" / "CH").mkdir(parents=True, exist_ok=True)
    for file_name in GI_CH_FILES:
        _require(site_root / "gi" / "CH" / file_name)
        _copy_file(site_root / "gi" / "CH" / file_name, out_root / "gi" / "CH" / file_name)
    for dir_name in GI_CH_DIRS:
        _require(site_root / "gi" / "CH" / dir_name)
        _copy_tree(site_root / "gi" / "CH" / dir_name, out_root / "gi" / "CH" / dir_name)

    # SR CH data subset.
    (out_root / "data" / "CH").mkdir(parents=True, exist_ok=True)
    for file_name in SR_CH_FILES:
        _require(site_root / "data" / "CH" / file_name)
        _copy_file(site_root / "data" / "CH" / file_name, out_root / "data" / "CH" / file_name)
    for dir_name in SR_CH_DIRS:
        _require(site_root / "data" / "CH" / dir_name)
        _copy_tree(site_root / "data" / "CH" / dir_name, out_root / "data" / "CH" / dir_name)

    # Combat navigation patch.
    patch_file = out_root / "javascripts" / "combat_patch.js"
    patch_file.write_text(COMBAT_PATCH_JS + "\n", encoding="utf-8")

    _rewrite_all_text(out_root)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a combat-only legacy-style static site from local raw site/")
    parser.add_argument("--site", required=True, help="Path to local raw site directory")
    parser.add_argument(
        "--out",
        default="web/legacy-site",
        help="Output path for generated static site (default: web/legacy-site)",
    )
    parser.add_argument("--clean", action="store_true", help="Clean output directory first")
    args = parser.parse_args()

    site_root = Path(args.site).resolve()
    out_root = Path(args.out).resolve()
    if not site_root.is_dir():
        raise NotADirectoryError(f"site directory not found: {site_root}")

    build(site_root, out_root, args.clean)
    print(f"[legacy-build] done: {out_root}")


if __name__ == "__main__":
    main()
