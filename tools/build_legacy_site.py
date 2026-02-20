#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
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

GI_LOCALE_FILES = [
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
GI_LOCALE_DIRS = ["Avatar", "Weapon", "Relic"]

SR_LOCALE_FILES = [
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
SR_LOCALE_DIRS = ["Avatar", "Weapon", "Relic"]

ROOT_COPY_DIRS = ["plugins", "stylesheets", "javascripts", "fonts", "index", "yhb", "Char"]
ROOT_COPY_FILES = ["favicon.ico"]
ROOT_DATA_FILES = ["banner.js", "Stage.js", "New.js", "LevelCurves.js", "LevelCurvesSimple.js"]
GI_ROOT_FILES = ["avatar.js", "banner.js"]
LOCAL_ASSET_DIRS = ["images", "homdgcat-res", "EnemyChart", "SREnemyChart"]
ADMIN_ASSETS_DIR = Path(__file__).resolve().parent / "admin_assets"
ADMIN_ASSET_PATHS = [
    ("index.html", Path("admin/index.html")),
    ("admin.css", Path("stylesheets/admin.css")),
    ("admin.js", Path("javascripts/admin.js")),
]

REMOTE_ASSET_REWRITES = {
    "/images/": "https://homdgcat.wiki/images/",
    "/homdgcat-res/": "https://homdgcat.wiki/homdgcat-res/",
    "/EnemyChart/": "https://homdgcat.wiki/EnemyChart/",
    "/SREnemyChart/": "https://homdgcat.wiki/SREnemyChart/",
}
REMOTE_ASSET_PREFIXES = ("images", "homdgcat-res", "EnemyChart", "SREnemyChart")


COMBAT_PATCH_JS = r"""(function () {
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
      if (maybeCard && navLike) maybeCard.remove();
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
"""


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".DS_Store"))


def _require(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required path missing: {path}")


def _clean_output(path: Path) -> None:
    if not path.exists():
        return
    try:
        shutil.rmtree(path)
    except OSError:
        subprocess.run(["rm", "-rf", str(path)], check=True)
        if path.exists():
            shutil.rmtree(path)


def _sanitize_cloudflare_artifacts(text: str) -> str:
    text = re.sub(
        r"<script[^>]+/cdn-cgi/scripts/[^>]*></script>",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'\btype="[0-9a-f]{8,}-text/javascript"',
        'type="text/javascript"',
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\btype='[0-9a-f]{8,}-text/javascript'",
        "type='text/javascript'",
        text,
        flags=re.IGNORECASE,
    )
    return text


def _rewrite_text_file(
    path: Path,
    *,
    force_lang: str | None,
    remote_assets: bool,
) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = _sanitize_cloudflare_artifacts(text)

    if force_lang:
        text = text.replace('id="LANG" value=""', f'id="LANG" value="{force_lang}"')
        text = text.replace("id='LANG' value=''", f"id='LANG' value='{force_lang}'")

    if remote_assets:
        text = text.replace('id="IMGPRE" value="/"', 'id="IMGPRE" value="https://homdgcat.wiki/"')
        text = text.replace("id='IMGPRE' value='/'", "id='IMGPRE' value='https://homdgcat.wiki/'")
        for before, after in REMOTE_ASSET_REWRITES.items():
            text = re.sub(
                rf'([\'"`(=:\s]){re.escape(before)}',
                rf"\1{after}",
                text,
            )
            text = re.sub(
                rf'([\'"`(=:\s])(?:\.\./)+{re.escape(before.lstrip("/"))}',
                rf"\1{after}",
                text,
            )
            text = re.sub(
                rf'^{re.escape(before)}',
                after,
                text,
                flags=re.MULTILINE,
            )
        for prefix in REMOTE_ASSET_PREFIXES:
            text = text.replace(f"..https://homdgcat.wiki/{prefix}/", f"../{prefix}/")

    if path.suffix.lower() == ".html" and not str(path.as_posix()).endswith("/admin/index.html"):
        marker = '<script src="/javascripts/combat_patch.js" type="text/javascript"></script>'
        if marker not in text and "</html>" in text:
            text = text.replace("</html>", f"{marker}</html>")

    # Fix known upstream typo: SR banner entries should route to SR characters.
    if path.name == "banner_sr.js":
        text = text.replace("/gi/char/", "/sr/char/")

    path.write_text(text, encoding="utf-8")


def _rewrite_all_text(root: Path, *, force_lang: str | None, remote_assets: bool) -> None:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".html", ".js", ".css"}:
            continue
        _rewrite_text_file(path, force_lang=force_lang, remote_assets=remote_assets)

    for junk in root.rglob(".DS_Store"):
        junk.unlink(missing_ok=True)


def _copy_locale_data(site_root: Path, out_root: Path, locale: str) -> None:
    locale = locale.upper().strip()
    if not locale:
        return

    gi_locale_root = site_root / "gi" / locale
    sr_locale_root = site_root / "data" / locale
    _require(gi_locale_root)
    _require(sr_locale_root)

    gi_out_locale = out_root / "gi" / locale
    sr_out_locale = out_root / "data" / locale
    gi_out_locale.mkdir(parents=True, exist_ok=True)
    sr_out_locale.mkdir(parents=True, exist_ok=True)

    for file_name in GI_LOCALE_FILES:
        _require(gi_locale_root / file_name)
        _copy_file(gi_locale_root / file_name, gi_out_locale / file_name)
    for dir_name in GI_LOCALE_DIRS:
        _require(gi_locale_root / dir_name)
        _copy_tree(gi_locale_root / dir_name, gi_out_locale / dir_name)

    for file_name in SR_LOCALE_FILES:
        _require(sr_locale_root / file_name)
        _copy_file(sr_locale_root / file_name, sr_out_locale / file_name)
    for dir_name in SR_LOCALE_DIRS:
        _require(sr_locale_root / dir_name)
        _copy_tree(sr_locale_root / dir_name, sr_out_locale / dir_name)


def build(
    *,
    site_root: Path,
    out_root: Path,
    clean: bool,
    locales: list[str],
    asset_mode: str,
    force_lang: str | None,
) -> None:
    if clean and out_root.exists():
        _clean_output(out_root)
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

    for name in GI_PAGE_DIRS:
        _require(site_root / "gi" / name)
        _copy_tree(site_root / "gi" / name, out_root / "gi" / name)
    for file_name in GI_ROOT_FILES:
        _require(site_root / "gi" / file_name)
        _copy_file(site_root / "gi" / file_name, out_root / "gi" / file_name)

    for name in SR_PAGE_DIRS:
        _require(site_root / "sr" / name)
        _copy_tree(site_root / "sr" / name, out_root / "sr" / name)

    for file_name in ROOT_DATA_FILES:
        _require(site_root / "data" / file_name)
        _copy_file(site_root / "data" / file_name, out_root / "data" / file_name)

    for locale in locales:
        _copy_locale_data(site_root, out_root, locale)

    if asset_mode == "local":
        for name in LOCAL_ASSET_DIRS:
            src = site_root / name
            if src.exists():
                _copy_tree(src, out_root / name)

    if ADMIN_ASSETS_DIR.exists():
        for src_name, out_rel in ADMIN_ASSET_PATHS:
            src = ADMIN_ASSETS_DIR / src_name
            if src.exists():
                _copy_file(src, out_root / out_rel)

    patch_file = out_root / "javascripts" / "combat_patch.js"
    patch_file.write_text(COMBAT_PATCH_JS + "\n", encoding="utf-8")

    _rewrite_all_text(
        out_root,
        force_lang=force_lang,
        remote_assets=(asset_mode == "remote"),
    )
    _transpile_js_compat(out_root)


def _transpile_js_compat(out_root: Path) -> None:
    script = Path(__file__).resolve().parent / "transpile_js_compat.mjs"
    if not script.exists():
        return
    try:
        result = subprocess.run(
            ["node", str(script), "--web", str(out_root)],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print("[legacy-build] warning: node not found; skipped JS compatibility transpile.")
        return
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        print(f"[legacy-build] warning: JS compatibility transpile failed: {stderr or 'unknown error'}")


def _parse_locales(raw: str) -> list[str]:
    values = [x.strip().upper() for x in raw.split(",") if x.strip()]
    if not values:
        raise ValueError("At least one locale is required.")
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a combat-only legacy-style static site from local raw site/")
    parser.add_argument("--site", required=True, help="Path to local raw site directory")
    parser.add_argument("--out", default="web", help="Output path for generated static site (default: web)")
    parser.add_argument("--clean", action="store_true", help="Clean output directory first")
    parser.add_argument(
        "--locales",
        default="CH,EN",
        help="Comma-separated locales to copy for GI/SR runtime data (default: CH,EN)",
    )
    parser.add_argument(
        "--asset-mode",
        choices=["remote", "local"],
        default="remote",
        help="remote: keep repo light and rewrite heavy assets to homdgcat.wiki; local: copy local assets into web/",
    )
    parser.add_argument(
        "--force-lang",
        help="Force hidden LANG value in html (example: CH). Leave unset to preserve original behavior.",
    )
    args = parser.parse_args()

    site_root = Path(args.site).resolve()
    out_root = Path(args.out).resolve()
    if not site_root.is_dir():
        raise NotADirectoryError(f"site directory not found: {site_root}")

    locales = _parse_locales(args.locales)
    build(
        site_root=site_root,
        out_root=out_root,
        clean=args.clean,
        locales=locales,
        asset_mode=args.asset_mode,
        force_lang=args.force_lang,
    )
    print(f"[legacy-build] done: {out_root}")
    print(f"[legacy-build] locales: {', '.join(locales)}")
    print(f"[legacy-build] asset-mode: {args.asset_mode}")


if __name__ == "__main__":
    main()
