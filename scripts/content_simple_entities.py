#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT_DIR / "site"
BACKUP_ROOT = ROOT_DIR / "easy_updates" / "entity_backups"
LOCALES = ("CH", "EN")

_VAR_RE = re.compile(r"^\s*var\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=", re.MULTILINE)

_GI_CHARACTER_SECTIONS: list[tuple[str, dict[str, str]]] = [
    ("basic", {"CH": "基本信息", "EN": "Basic Info"}),
    ("skills", {"CH": "技能", "EN": "Skills"}),
    ("passive", {"CH": "被动 命之座", "EN": "Passives Constellations"}),
    ("material", {"CH": "养成计算", "EN": "Material Calculator"}),
    ("changes", {"CH": "改动汇总", "EN": "Track Updates"}),
    ("notes", {"CH": "妮可少女的研究", "EN": "HomDGCat's Notes"}),
    ("stories", {"CH": "故事", "EN": "Stories"}),
    ("voice", {"CH": "语音", "EN": "Voicelines"}),
]

_SR_CHARACTER_SECTIONS: list[tuple[str, dict[str, str]]] = [
    ("basic", {"CH": "基本信息", "EN": "Basic Info"}),
    ("skills", {"CH": "技能", "EN": "Skills"}),
    ("passive", {"CH": "行迹 星魂", "EN": "Traces Eidolons"}),
    ("material", {"CH": "养成计算", "EN": "Material Calculator"}),
    ("changes", {"CH": "改动汇总", "EN": "Track Updates"}),
    ("notes", {"CH": "妮可少女的研究", "EN": "HomDGCat's Notes"}),
    ("stories", {"CH": "故事", "EN": "Stories"}),
    ("voice", {"CH": "语音", "EN": "Voicelines"}),
]


def _auto_generated_content(assignments: list[tuple[str, Any]]) -> str:
    parts = ["// Auto Generated", ""]
    for idx, (name, value) in enumerate(assignments):
        parts.append(f"var {name} = {json.dumps(value, ensure_ascii=False, indent=4)}")
        if idx != len(assignments) - 1:
            parts.append("")
    parts.append("")
    return "\n".join(parts)


def _create_backup_dir() -> Path:
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = BACKUP_ROOT / ts
    path.mkdir(parents=True, exist_ok=False)
    return path


def _backup_file(src: Path, backup_dir: Path) -> None:
    rel = src.relative_to(ROOT_DIR)
    dst = backup_dir / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _latest_backup_dir() -> Path | None:
    if not BACKUP_ROOT.exists():
        return None
    dirs = [d for d in BACKUP_ROOT.iterdir() if d.is_dir()]
    if not dirs:
        return None
    return sorted(dirs)[-1]


def backup_status() -> dict[str, Any]:
    if not BACKUP_ROOT.exists():
        return {"count": 0, "latest": ""}
    dirs = [d for d in BACKUP_ROOT.iterdir() if d.is_dir()]
    if not dirs:
        return {"count": 0, "latest": ""}
    return {"count": len(dirs), "latest": sorted(dirs)[-1].name}


def undo_latest_backup() -> str:
    latest = _latest_backup_dir()
    if latest is None:
        return "No backup found."
    restored = 0
    for src in latest.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(latest)
        dst = ROOT_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        restored += 1
    return f"Restored {restored} file(s) from {latest.name}."


def _parse_js_vars(file_path: Path) -> tuple[list[str], dict[str, Any]]:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    if text.lstrip().startswith("<"):
        raise ValueError(f"Not a data JS file: {file_path}")
    matches = list(_VAR_RE.finditer(text))
    if not matches:
        raise ValueError(f"No var assignments found: {file_path}")

    order: list[str] = []
    values: dict[str, Any] = {}
    for idx, m in enumerate(matches):
        name = m.group(1)
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        blob = text[start:end].strip()
        if blob.endswith(";"):
            blob = blob[:-1].rstrip()
        values[name] = json.loads(blob)
        order.append(name)
    return order, values


def _parse_js_var(file_path: Path, var_name: str) -> Any:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    if text.lstrip().startswith("<"):
        raise ValueError(f"Not a data JS file: {file_path}")
    pat = re.compile(rf"^\s*var\s+{re.escape(var_name)}\s*=", re.MULTILINE)
    m = pat.search(text)
    if not m:
        raise ValueError(f"Var not found: {var_name} in {file_path}")
    start = m.end()
    m_next = _VAR_RE.search(text, start)
    end = m_next.start() if m_next else len(text)
    blob = text[start:end].strip()
    if blob.endswith(";"):
        blob = blob[:-1].rstrip()
    return json.loads(blob)


def _short(text: str, limit: int = 90) -> str:
    s = (text or "").replace("<br>", " ").replace("\n", " ").strip()
    if len(s) <= limit:
        return s
    return s[: limit - 1] + "..."


class SimpleEntityRepository:
    def __init__(self) -> None:
        self.characters: dict[str, dict[str, list[dict[str, Any]]]] = {"sr": {}, "gi": {}}
        self.weapons: dict[str, dict[str, dict[str, dict[str, Any]]]] = {"sr": {}, "gi": {}}
        self.relics: dict[str, dict[str, dict[str, dict[str, Any]]]] = {"sr": {}, "gi": {}}
        self.loaded: dict[str, dict[str, dict[str, bool]]] = {"sr": {}, "gi": {}}
        self.refresh()

    @staticmethod
    def _file_sr_avatar(locale: str) -> Path:
        return SITE_DIR / "data" / locale / "Avatar.js"

    @staticmethod
    def _file_gi_avatar(locale: str) -> Path:
        return SITE_DIR / "gi" / locale / "avatar.js"

    @staticmethod
    def _dir_sr_weapon(locale: str) -> Path:
        return SITE_DIR / "data" / locale / "Weapon"

    @staticmethod
    def _dir_gi_weapon(locale: str) -> Path:
        return SITE_DIR / "gi" / locale / "Weapon"

    @staticmethod
    def _dir_sr_relic(locale: str) -> Path:
        return SITE_DIR / "data" / locale / "Relic"

    @staticmethod
    def _dir_gi_relic(locale: str) -> Path:
        return SITE_DIR / "gi" / locale / "Relic"

    @staticmethod
    def _path_to_text(path: list[Any]) -> str:
        out = "$"
        for token in path:
            if isinstance(token, int):
                out += f"[{token}]"
            else:
                out += f".{token}"
        return out

    @staticmethod
    def _sections_for_character(game: str, locale: str) -> list[dict[str, Any]]:
        defs = _GI_CHARACTER_SECTIONS if game == "gi" else _SR_CHARACTER_SECTIONS
        return [
            {
                "id": sid,
                "label": labels["CH"] if locale == "CH" else labels["EN"],
                "records": [],
            }
            for sid, labels in defs
        ]

    @staticmethod
    def _rel_path(file_path: Path) -> str:
        return str(file_path.relative_to(ROOT_DIR)).replace("\\", "/")

    @staticmethod
    def _resolve_rel_path(rel_path: str) -> Path:
        raw = (ROOT_DIR / rel_path).resolve()
        site_root = SITE_DIR.resolve()
        if raw != site_root and site_root not in raw.parents:
            raise ValueError(f"Invalid file path: {rel_path}")
        if not raw.is_file():
            raise ValueError(f"File not found: {rel_path}")
        if raw.suffix.lower() != ".js":
            raise ValueError(f"Only JS data file is editable: {rel_path}")
        return raw

    @staticmethod
    def _path_get(root: Any, path: list[Any]) -> Any:
        cur = root
        for token in path:
            if isinstance(cur, list):
                if not isinstance(token, int):
                    raise ValueError(f"Array index must be integer: {token}")
                if token < 0 or token >= len(cur):
                    raise ValueError(f"Array index out of range: {token}")
                cur = cur[token]
                continue
            if isinstance(cur, dict):
                if token not in cur:
                    raise ValueError(f"Object key not found: {token}")
                cur = cur[token]
                continue
            raise ValueError(f"Path traversal failed on non-container type: {type(cur).__name__}")
        return cur

    @staticmethod
    def _path_set(root: Any, path: list[Any], value: Any) -> Any:
        if not path:
            return value
        parent = SimpleEntityRepository._path_get(root, path[:-1])
        token = path[-1]
        if isinstance(parent, list):
            if not isinstance(token, int):
                raise ValueError(f"Array index must be integer: {token}")
            if token < 0 or token >= len(parent):
                raise ValueError(f"Array index out of range: {token}")
            parent[token] = value
            return root
        if isinstance(parent, dict):
            parent[token] = value
            return root
        raise ValueError("Path parent is not editable container")

    @staticmethod
    def _record_kind(value: Any) -> str:
        if isinstance(value, list):
            return "array"
        if isinstance(value, dict):
            return "object"
        return "value"

    @staticmethod
    def _record_summary(value: Any) -> str:
        if isinstance(value, list):
            return f"数组，共 {len(value)} 项"
        if isinstance(value, dict):
            return f"对象，共 {len(value)} 个键"
        return _short(str(value), limit=120)

    def _make_record(
        self,
        *,
        title: str,
        file_path: Path,
        var_name: str,
        path: list[Any],
        value: Any,
    ) -> dict[str, Any]:
        rel = self._rel_path(file_path)
        ref_blob = f"{rel}|{var_name}|{json.dumps(path, ensure_ascii=False)}"
        rid = hashlib.md5(ref_blob.encode("utf-8")).hexdigest()[:16]
        kind = self._record_kind(value)
        return {
            "id": rid,
            "title": title,
            "kind": kind,
            "summary": self._record_summary(value),
            "path_text": self._path_to_text(path),
            "ref": {
                "file": rel,
                "var": var_name,
                "path": path,
            },
            "json": json.dumps(value, ensure_ascii=False, indent=2),
            "supports_add": kind in {"array", "object"},
            "supports_delete": kind in {"array", "object"},
        }

    @staticmethod
    def _first_key(data: dict[Any, Any], candidates: list[Any]) -> Any | None:
        for key in candidates:
            if key in data:
                return key
        return None

    def _add_record_from_path(
        self,
        section: dict[str, Any],
        *,
        title: str,
        file_path: Path,
        values: dict[str, Any],
        var_name: str,
        path: list[Any] | None = None,
        fallback_to_root: bool = False,
    ) -> None:
        if var_name not in values:
            return
        root = values[var_name]
        use_path = path or []
        try:
            val = self._path_get(root, use_path) if use_path else root
            section["records"].append(
                self._make_record(
                    title=title,
                    file_path=file_path,
                    var_name=var_name,
                    path=use_path,
                    value=val,
                )
            )
            return
        except Exception:
            if not fallback_to_root:
                return
        section["records"].append(
            self._make_record(
                title=f"{title}（根对象）",
                file_path=file_path,
                var_name=var_name,
                path=[],
                value=root,
            )
        )

    @staticmethod
    def _normalize_record_ref(record_ref: dict[str, Any]) -> tuple[str, str, list[Any]]:
        if not isinstance(record_ref, dict):
            raise ValueError("record_ref must be object")
        rel = str(record_ref.get("file", "")).strip()
        var_name = str(record_ref.get("var", "")).strip()
        path = record_ref.get("path", [])
        if not rel:
            raise ValueError("record_ref.file is required")
        if not var_name:
            raise ValueError("record_ref.var is required")
        if not isinstance(path, list):
            raise ValueError("record_ref.path must be array")
        norm: list[Any] = []
        for token in path:
            if isinstance(token, bool):
                raise ValueError("path token cannot be boolean")
            if isinstance(token, int):
                norm.append(token)
                continue
            if isinstance(token, float) and token.is_integer():
                norm.append(int(token))
                continue
            if isinstance(token, str):
                norm.append(token)
                continue
            raise ValueError(f"Unsupported path token type: {type(token).__name__}")
        return rel, var_name, norm

    @staticmethod
    def _write_js_file(path: Path, order: list[str], values: dict[str, Any]) -> None:
        assignments = [(name, values[name]) for name in order]
        path.write_text(_auto_generated_content(assignments), encoding="utf-8")

    def refresh(self) -> None:
        for game in ("sr", "gi"):
            self.characters[game] = {}
            self.weapons[game] = {}
            self.relics[game] = {}
            self.loaded[game] = {}
        for locale in LOCALES:
            self.characters["sr"][locale] = []
            self.characters["gi"][locale] = []
            self.weapons["sr"][locale] = {}
            self.weapons["gi"][locale] = {}
            self.relics["sr"][locale] = {}
            self.relics["gi"][locale] = {}
            self.loaded["sr"][locale] = {"character": False, "weapon": False, "relic": False}
            self.loaded["gi"][locale] = {"character": False, "weapon": False, "relic": False}

    def _ensure_loaded(self, game: str, locale: str, kind: str) -> None:
        if kind not in {"character", "weapon", "relic"}:
            return
        if self.loaded.get(game, {}).get(locale, {}).get(kind):
            return
        self._refresh_slice(game=game, locale=locale, kind=kind)

    def _refresh_slice(self, game: str, locale: str, kind: str) -> None:
        if kind == "character":
            if game == "sr":
                self.characters["sr"][locale] = self._load_sr_characters(locale)
            else:
                self.characters["gi"][locale] = self._load_gi_characters(locale)
            if game not in self.loaded:
                self.loaded[game] = {}
            if locale not in self.loaded[game]:
                self.loaded[game][locale] = {"character": False, "weapon": False, "relic": False}
            self.loaded[game][locale]["character"] = True
            return
        if kind == "weapon":
            if game == "sr":
                self.weapons["sr"][locale] = self._load_sr_weapons(locale)
            else:
                self.weapons["gi"][locale] = self._load_gi_weapons(locale)
            if game not in self.loaded:
                self.loaded[game] = {}
            if locale not in self.loaded[game]:
                self.loaded[game][locale] = {"character": False, "weapon": False, "relic": False}
            self.loaded[game][locale]["weapon"] = True
            return
        if kind == "relic":
            if game == "sr":
                self.relics["sr"][locale] = self._load_sr_relics(locale)
            else:
                self.relics["gi"][locale] = self._load_gi_relics(locale)
            if game not in self.loaded:
                self.loaded[game] = {}
            if locale not in self.loaded[game]:
                self.loaded[game][locale] = {"character": False, "weapon": False, "relic": False}
            self.loaded[game][locale]["relic"] = True
            return

    def counts(self) -> dict[str, dict[str, dict[str, int]]]:
        out: dict[str, dict[str, dict[str, int]]] = {"sr": {}, "gi": {}}
        for game in ("sr", "gi"):
            out[game]["character"] = {}
            out[game]["weapon"] = {}
            out[game]["relic"] = {}
            for locale in LOCALES:
                char_loaded = self.loaded.get(game, {}).get(locale, {}).get("character", False)
                weapon_loaded = self.loaded.get(game, {}).get(locale, {}).get("weapon", False)
                relic_loaded = self.loaded.get(game, {}).get(locale, {}).get("relic", False)
                if char_loaded:
                    out[game]["character"][locale] = len(self.characters[game].get(locale, []))
                else:
                    if game == "sr":
                        out[game]["character"][locale] = len(list((SITE_DIR / "data" / locale / "Avatar").glob("*.js")))
                    else:
                        out[game]["character"][locale] = len(list((SITE_DIR / "gi" / locale / "Avatar").glob("*_1.js")))
                if weapon_loaded:
                    out[game]["weapon"][locale] = len(self.weapons[game].get(locale, {}))
                else:
                    if game == "sr":
                        out[game]["weapon"][locale] = len(list(self._dir_sr_weapon(locale).glob("*.js")))
                    else:
                        out[game]["weapon"][locale] = len(list(self._dir_gi_weapon(locale).glob("*.js")))
                if relic_loaded:
                    out[game]["relic"][locale] = len(self.relics[game].get(locale, {}))
                else:
                    if game == "sr":
                        out[game]["relic"][locale] = len(list(self._dir_sr_relic(locale).glob("*.js")))
                    else:
                        out[game]["relic"][locale] = len(list(self._dir_gi_relic(locale).glob("*.js")))
        return out

    def _load_sr_characters(self, locale: str) -> list[dict[str, Any]]:
        path = self._file_sr_avatar(locale)
        rows = _parse_js_var(path, "_avatar") or []
        out = []
        for row in rows:
            out.append(
                {
                    "id": str(row.get("_id", "")),
                    "name": str(row.get("Name", "")),
                    "desc": str(row.get("Desc", "")),
                    "title": str(row.get("Title", "")),
                }
            )
        return out

    def _load_gi_characters(self, locale: str) -> list[dict[str, Any]]:
        path = self._file_gi_avatar(locale)
        rows = _parse_js_var(path, "__AvatarInfoConfig") or []
        out = []
        for row in rows:
            out.append(
                {
                    "id": str(row.get("_id", "")),
                    "name": str(row.get("Name", "")),
                    "desc": str(row.get("Desc", "")),
                    "title": str(row.get("Title", "")),
                }
            )
        return out

    def _load_sr_weapons(self, locale: str) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for file_path in sorted(self._dir_sr_weapon(locale).glob("*.js")):
            wid = file_path.stem
            _, values = _parse_js_vars(file_path)
            desc_map = values.get("_weapondesc_") or {}
            skill_map = values.get("_weaponskill_") or {}
            live = (skill_map.get(wid) or {}).get("Live") or {}
            skill_desc = ""
            if isinstance(live.get("Desc"), list) and live["Desc"]:
                skill_desc = str(live["Desc"][0])
            out[wid] = {
                "id": wid,
                "name": str(live.get("Name") or (f"光锥 {wid}" if locale == "CH" else f"Light Cone {wid}")),
                "desc": str(desc_map.get(wid) or ""),
                "skill_name": str(live.get("Name") or ""),
                "skill_desc": skill_desc,
            }
        return out

    def _load_gi_weapons(self, locale: str) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for file_path in sorted(self._dir_gi_weapon(locale).glob("*.js")):
            wid = file_path.stem
            _, values = _parse_js_vars(file_path)
            affix_map = values.get("_WeaponAffixPConfig_") or {}
            story_map = values.get("weapon_story_cache_") or {}
            affix_key = next(iter(affix_map.keys()), "")
            affix_desc = ""
            if affix_key:
                ver_map = (affix_map.get(affix_key) or {}).get("Ver") or {}
                v1 = ver_map.get("1") if isinstance(ver_map, dict) else None
                affix = (v1 or {}).get("Affix") if isinstance(v1, dict) else None
                if isinstance(affix, list) and affix:
                    affix_desc = str(affix[0])
            story_key = next(iter(story_map.keys()), "")
            story = ""
            if story_key:
                arr = story_map.get(story_key)
                if isinstance(arr, list) and arr:
                    story = str(arr[0])
            out[wid] = {
                "id": wid,
                "name": f"{'武器' if locale == 'CH' else 'Weapon'} {wid}",
                "affix_desc": affix_desc,
                "story": story,
            }
        return out

    def _load_sr_relics(self, locale: str) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for file_path in sorted(self._dir_sr_relic(locale).glob("*.js")):
            rid = file_path.stem
            _, values = _parse_js_vars(file_path)
            relic_map = values.get("_relicitem_") or {}
            parts = relic_map.get(rid) or []
            first = parts[0] if isinstance(parts, list) and parts else {}
            out[rid] = {
                "id": rid,
                "name": str(first.get("Name") or (f"遗器 {rid}" if locale == "CH" else f"Relic {rid}")),
                "summary": str(first.get("Desc") or ""),
                "parts": parts if isinstance(parts, list) else [],
            }
        return out

    def _load_gi_relics(self, locale: str) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for file_path in sorted(self._dir_gi_relic(locale).glob("*.js")):
            rid = file_path.stem
            _, values = _parse_js_vars(file_path)
            relic_map = values.get("relic_story_cache_") or {}
            cache_key = next(iter(relic_map.keys()), "")
            parts = relic_map.get(cache_key) if cache_key else []
            first = parts[0] if isinstance(parts, list) and parts else {}
            out[rid] = {
                "id": rid,
                "name": f"{'圣遗物' if locale == 'CH' else 'Artifact'} {rid}",
                "summary": str(first.get("Desc") or ""),
                "cache_key": cache_key,
                "parts": parts if isinstance(parts, list) else [],
            }
        return out

    def _ensure_params(self, game: str, locale: str, kind: str) -> tuple[str, str, str]:
        game = game.strip().lower()
        kind = kind.strip().lower()
        locale = locale.strip().upper()
        if game not in {"sr", "gi"}:
            raise ValueError(f"Unknown game: {game}")
        if kind not in {"character", "weapon", "relic"}:
            raise ValueError(f"Unknown kind: {kind}")
        if locale not in LOCALES:
            raise ValueError(f"Unsupported locale: {locale}")
        return game, locale, kind

    def list_items(self, game: str, locale: str, kind: str, query: str = "") -> list[dict[str, Any]]:
        game, locale, kind = self._ensure_params(game, locale, kind)
        self._ensure_loaded(game=game, locale=locale, kind=kind)
        q = query.strip().lower()
        items: list[dict[str, Any]] = []

        if kind == "character":
            rows = self.characters[game].get(locale, [])
            for row in rows:
                blob = f"{row['id']} {row['name']} {row.get('title','')} {row['desc']}".lower()
                if q and q not in blob:
                    continue
                items.append(
                    {
                        "id": row["id"],
                        "name": row["name"] or f"角色 {row['id']}",
                        "summary": _short(row["desc"]),
                    }
                )
        elif kind == "weapon":
            rows = self.weapons[game].get(locale, {})
            for wid, row in rows.items():
                blob = f"{wid} {row.get('name','')} {row.get('desc','')} {row.get('skill_desc','')} {row.get('affix_desc','')}".lower()
                if q and q not in blob:
                    continue
                summary = row.get("desc") or row.get("skill_desc") or row.get("affix_desc") or ""
                items.append(
                    {
                        "id": wid,
                        "name": row.get("name") or f"武器 {wid}",
                        "summary": _short(summary),
                    }
                )
        else:
            rows = self.relics[game].get(locale, {})
            for rid, row in rows.items():
                blob = f"{rid} {row.get('name','')} {row.get('summary','')}".lower()
                if q and q not in blob:
                    continue
                items.append(
                    {
                        "id": rid,
                        "name": row.get("name") or f"圣遗物 {rid}",
                        "summary": _short(row.get("summary", "")),
                    }
                )

        items.sort(key=lambda x: x["id"])
        return items

    def get_item(self, game: str, locale: str, kind: str, item_id: str) -> dict[str, Any]:
        game, locale, kind = self._ensure_params(game, locale, kind)
        self._ensure_loaded(game=game, locale=locale, kind=kind)
        item_id = str(item_id).strip()
        if not item_id:
            raise ValueError("Missing item id")

        if kind == "character":
            if game == "gi":
                return self._get_item_character_gi(locale=locale, item_id=item_id)
            return self._get_item_character_sr(locale=locale, item_id=item_id)

        if kind == "weapon":
            row = self.weapons[game].get(locale, {}).get(item_id)
            if row is None:
                raise ValueError(f"Weapon not found: {item_id}")
            if game == "sr":
                fields = [
                    {"key": "desc", "label": "武器描述", "type": "textarea", "value": row.get("desc", "")},
                    {"key": "skill_name", "label": "技能名", "type": "text", "value": row.get("skill_name", "")},
                    {"key": "skill_desc", "label": "技能描述(首段)", "type": "textarea", "value": row.get("skill_desc", "")},
                ]
            else:
                fields = [
                    {"key": "affix_desc", "label": "武器效果(1阶)", "type": "textarea", "value": row.get("affix_desc", "")},
                    {"key": "story", "label": "武器故事(首段)", "type": "textarea", "value": row.get("story", "")},
                ]
            return {"id": item_id, "title": row.get("name") or f"武器 {item_id}", "fields": fields}

        row = self.relics[game].get(locale, {}).get(item_id)
        if row is None:
            raise ValueError(f"Relic not found: {item_id}")
        fields: list[dict[str, Any]] = []
        if game == "sr":
            for idx, part in enumerate(row.get("parts", []), start=1):
                fields.extend(
                    [
                        {
                            "key": f"p{idx}_name",
                            "label": f"部件{idx} 名称/Name",
                            "type": "text",
                            "value": str(part.get("Name", "")),
                        },
                        {
                            "key": f"p{idx}_desc",
                            "label": f"部件{idx} 描述/Desc",
                            "type": "textarea",
                            "value": str(part.get("Desc", "")),
                        },
                        {
                            "key": f"p{idx}_story",
                            "label": f"部件{idx} 故事/Story",
                            "type": "textarea",
                            "value": str(part.get("Story", "")),
                        },
                    ]
                )
        else:
            for idx, part in enumerate(row.get("parts", []), start=1):
                story = part.get("Story")
                first_story = story[0] if isinstance(story, list) and story else ""
                fields.extend(
                    [
                        {
                            "key": f"p{idx}_desc",
                            "label": f"部件{idx} 描述/Desc",
                            "type": "textarea",
                            "value": str(part.get("Desc", "")),
                        },
                        {
                            "key": f"p{idx}_story",
                            "label": f"部件{idx} 故事/Story(首段)",
                            "type": "textarea",
                            "value": str(first_story),
                        },
                    ]
                )
        return {"id": item_id, "title": row.get("name") or f"圣遗物 {item_id}", "fields": fields}

    def _get_item_character_sr(self, locale: str, item_id: str) -> dict[str, Any]:
        base_path = self._file_sr_avatar(locale)
        rows = _parse_js_var(base_path, "_avatar") or []
        hit_index = -1
        hit_row: dict[str, Any] | None = None
        for idx, row in enumerate(rows):
            if str(row.get("_id", "")) == item_id:
                hit_index = idx
                hit_row = row
                break
        if hit_row is None:
            raise ValueError(f"Character not found: {item_id}")

        sections = self._sections_for_character("sr", locale)
        sec = {s["id"]: s for s in sections}
        sec["basic"]["records"].append(
            self._make_record(
                title="角色基础条目",
                file_path=base_path,
                var_name="_avatar",
                path=[hit_index],
                value=hit_row,
            )
        )
        if "Mat" in hit_row:
            sec["material"]["records"].append(
                self._make_record(
                    title="基础材料 ID 列表",
                    file_path=base_path,
                    var_name="_avatar",
                    path=[hit_index, "Mat"],
                    value=hit_row.get("Mat"),
                )
            )

        detail_path = SITE_DIR / "data" / locale / "Avatar" / f"{item_id}.js"
        warnings: list[str] = []
        if detail_path.exists():
            _, values = _parse_js_vars(detail_path)
            self._add_record_from_path(
                sec["skills"],
                title="技能数据",
                file_path=detail_path,
                values=values,
                var_name="_avatarskill_",
            )
            self._add_record_from_path(
                sec["passive"],
                title="行迹数据",
                file_path=detail_path,
                values=values,
                var_name="_avatarskilltree_",
            )
            self._add_record_from_path(
                sec["passive"],
                title="星魂数据",
                file_path=detail_path,
                values=values,
                var_name="_avatarrank_",
            )
            self._add_record_from_path(
                sec["material"],
                title="养成计算",
                file_path=detail_path,
                values=values,
                var_name="_mtc_",
                path=[item_id],
                fallback_to_root=True,
            )
            self._add_record_from_path(
                sec["changes"],
                title="改动数据",
                file_path=detail_path,
                values=values,
                var_name="_adiff_",
                path=[item_id],
                fallback_to_root=True,
            )
            self._add_record_from_path(
                sec["notes"],
                title="妮可少女的研究",
                file_path=detail_path,
                values=values,
                var_name="_notes_",
                path=[item_id],
                fallback_to_root=True,
            )
            self._add_record_from_path(
                sec["stories"],
                title="角色故事",
                file_path=detail_path,
                values=values,
                var_name="_story_",
                path=[item_id],
                fallback_to_root=True,
            )
            self._add_record_from_path(
                sec["voice"],
                title="角色语音",
                file_path=detail_path,
                values=values,
                var_name="_voice_",
                path=[item_id],
                fallback_to_root=True,
            )
        else:
            warnings.append(f"缺少角色详情文件：{self._rel_path(detail_path)}")

        return {
            "id": item_id,
            "title": str(hit_row.get("Name") or f"角色 {item_id}"),
            "mode": "character_sections",
            "sections": sections,
            "warnings": warnings,
        }

    def _get_item_character_gi(self, locale: str, item_id: str) -> dict[str, Any]:
        base_path = self._file_gi_avatar(locale)
        rows = _parse_js_var(base_path, "__AvatarInfoConfig") or []
        hit_index = -1
        hit_row: dict[str, Any] | None = None
        for idx, row in enumerate(rows):
            if str(row.get("_id", "")) == item_id:
                hit_index = idx
                hit_row = row
                break
        if hit_row is None:
            raise ValueError(f"Character not found: {item_id}")
        avatar_name = str(hit_row.get("_name", "")).strip()
        if not avatar_name:
            raise ValueError(f"Character _name missing: {item_id}")

        sections = self._sections_for_character("gi", locale)
        sec = {s["id"]: s for s in sections}
        sec["basic"]["records"].append(
            self._make_record(
                title="角色基础条目",
                file_path=base_path,
                var_name="__AvatarInfoConfig",
                path=[hit_index],
                value=hit_row,
            )
        )

        warnings: list[str] = []
        file_1 = SITE_DIR / "gi" / locale / "Avatar" / f"{avatar_name}_1.js"
        if file_1.exists():
            _, values_1 = _parse_js_vars(file_1)
            self._add_record_from_path(
                sec["material"],
                title="养成计算数据",
                file_path=file_1,
                values=values_1,
                var_name="_AvatarMats_",
                path=[avatar_name],
                fallback_to_root=True,
            )
            self._add_record_from_path(
                sec["notes"],
                title="高级数据",
                file_path=file_1,
                values=values_1,
                var_name="_AvatarDataConfig_",
                path=[avatar_name],
                fallback_to_root=True,
            )
            self._add_record_from_path(
                sec["notes"],
                title="攻击数据",
                file_path=file_1,
                values=values_1,
                var_name="_AvatarAttackConfig_",
                path=[avatar_name],
                fallback_to_root=True,
            )
            self._add_record_from_path(
                sec["changes"],
                title="版本技能数据",
                file_path=file_1,
                values=values_1,
                var_name="_AvatarSkillPConfig_",
                path=[avatar_name, "Ver"],
                fallback_to_root=True,
            )

            skill_root = None
            if "_AvatarSkillPConfig_" in values_1:
                try:
                    skill_root = self._path_get(values_1["_AvatarSkillPConfig_"], [avatar_name, "Ver"])
                except Exception:
                    skill_root = None
            if isinstance(skill_root, dict):
                for ver in sorted(skill_root.keys(), key=lambda x: str(x)):
                    self._add_record_from_path(
                        sec["skills"],
                        title=f"技能 ({ver})",
                        file_path=file_1,
                        values=values_1,
                        var_name="_AvatarSkillPConfig_",
                        path=[avatar_name, "Ver", ver, "BattleSkills"],
                    )
                    self._add_record_from_path(
                        sec["passive"],
                        title=f"被动 ({ver})",
                        file_path=file_1,
                        values=values_1,
                        var_name="_AvatarSkillPConfig_",
                        path=[avatar_name, "Ver", ver, "PassiveSkills"],
                    )
                    self._add_record_from_path(
                        sec["passive"],
                        title=f"命之座 ({ver})",
                        file_path=file_1,
                        values=values_1,
                        var_name="_AvatarSkillPConfig_",
                        path=[avatar_name, "Ver", ver, "Constellations"],
                    )
            else:
                self._add_record_from_path(
                    sec["skills"],
                    title="技能配置",
                    file_path=file_1,
                    values=values_1,
                    var_name="_AvatarSkillPConfig_",
                    path=[avatar_name],
                    fallback_to_root=True,
                )
        else:
            warnings.append(f"缺少角色详情文件：{self._rel_path(file_1)}")

        file_2 = SITE_DIR / "gi" / locale / "Avatar" / f"{avatar_name}_2.js"
        if file_2.exists():
            _, values_2 = _parse_js_vars(file_2)
            fetter_data = values_2.get("_AvatarFetterConfig_")
            if isinstance(fetter_data, dict):
                fetter_key = self._first_key(
                    fetter_data,
                    [
                        str(hit_row.get("Fetter", "")),
                        hit_row.get("Fetter"),
                        str(hit_row.get("_id", "")),
                        hit_row.get("_id"),
                    ],
                )
                if fetter_key is not None:
                    self._add_record_from_path(
                        sec["stories"],
                        title="角色故事",
                        file_path=file_2,
                        values=values_2,
                        var_name="_AvatarFetterConfig_",
                        path=[fetter_key, "StoryList"],
                        fallback_to_root=True,
                    )
                    self._add_record_from_path(
                        sec["voice"],
                        title="角色语音",
                        file_path=file_2,
                        values=values_2,
                        var_name="_AvatarFetterConfig_",
                        path=[fetter_key, "VoiceList"],
                        fallback_to_root=True,
                    )
                else:
                    self._add_record_from_path(
                        sec["stories"],
                        title="角色故事（Fetter 根对象）",
                        file_path=file_2,
                        values=values_2,
                        var_name="_AvatarFetterConfig_",
                    )

            costume_data = values_2.get("_AvatarCostumeConfig_")
            if isinstance(costume_data, dict):
                costume_key = self._first_key(
                    costume_data,
                    [
                        str(hit_row.get("_id", "")),
                        hit_row.get("_id"),
                        str(hit_row.get("Fetter", "")),
                        hit_row.get("Fetter"),
                    ],
                )
                if costume_key is not None:
                    self._add_record_from_path(
                        sec["stories"],
                        title="服装与故事",
                        file_path=file_2,
                        values=values_2,
                        var_name="_AvatarCostumeConfig_",
                        path=[costume_key],
                    )
                else:
                    self._add_record_from_path(
                        sec["stories"],
                        title="服装与故事（根对象）",
                        file_path=file_2,
                        values=values_2,
                        var_name="_AvatarCostumeConfig_",
                    )

            asc_mat = hit_row.get("AscMat") or hit_row.get("AscMatID")
            if asc_mat is not None:
                self._add_record_from_path(
                    sec["material"],
                    title="突破描述缓存",
                    file_path=file_2,
                    values=values_2,
                    var_name="acs_cache_",
                    path=[str(asc_mat)],
                    fallback_to_root=True,
                )
        else:
            warnings.append(f"缺少角色详情文件：{self._rel_path(file_2)}")

        return {
            "id": item_id,
            "title": str(hit_row.get("Name") or f"角色 {item_id}"),
            "mode": "character_sections",
            "sections": sections,
            "warnings": warnings,
        }

    def save_character_record(
        self,
        *,
        game: str,
        locale: str,
        item_id: str,
        record_ref: dict[str, Any],
        value: Any,
    ) -> str:
        game, locale, kind = self._ensure_params(game, locale, "character")
        if kind != "character":
            raise ValueError("Invalid kind for character record save")
        if not str(item_id).strip():
            raise ValueError("Missing character id")
        rel, var_name, path = self._normalize_record_ref(record_ref)
        file_path = self._resolve_rel_path(rel)
        order, values = _parse_js_vars(file_path)
        if var_name not in values:
            raise ValueError(f"Var not found in file: {var_name}")
        root = values[var_name]
        values[var_name] = self._path_set(root, path, value)
        backup_dir = _create_backup_dir()
        _backup_file(file_path, backup_dir)
        self._write_js_file(file_path, order, values)
        self._refresh_slice(game=game, locale=locale, kind="character")
        return backup_dir.name

    def add_character_record(
        self,
        *,
        game: str,
        locale: str,
        item_id: str,
        record_ref: dict[str, Any],
        mode: str,
        value: Any,
        key: str = "",
        index: int | None = None,
    ) -> str:
        game, locale, kind = self._ensure_params(game, locale, "character")
        if kind != "character":
            raise ValueError("Invalid kind for character record add")
        if not str(item_id).strip():
            raise ValueError("Missing character id")
        rel, var_name, path = self._normalize_record_ref(record_ref)
        file_path = self._resolve_rel_path(rel)
        order, values = _parse_js_vars(file_path)
        if var_name not in values:
            raise ValueError(f"Var not found in file: {var_name}")

        container = self._path_get(values[var_name], path) if path else values[var_name]
        mode = mode.strip().lower()
        if mode == "array":
            if not isinstance(container, list):
                raise ValueError("Current record is not an array")
            if index is None:
                container.append(value)
            else:
                if index < 0 or index > len(container):
                    raise ValueError(f"Array insert index out of range: {index}")
                container.insert(index, value)
        elif mode == "object":
            if not isinstance(container, dict):
                raise ValueError("Current record is not an object")
            k = str(key).strip()
            if not k:
                raise ValueError("Missing object key")
            container[k] = value
        else:
            raise ValueError(f"Unsupported add mode: {mode}")

        backup_dir = _create_backup_dir()
        _backup_file(file_path, backup_dir)
        self._write_js_file(file_path, order, values)
        self._refresh_slice(game=game, locale=locale, kind="character")
        return backup_dir.name

    def delete_character_record(
        self,
        *,
        game: str,
        locale: str,
        item_id: str,
        record_ref: dict[str, Any],
        mode: str,
        key: str = "",
        index: int | None = None,
    ) -> str:
        game, locale, kind = self._ensure_params(game, locale, "character")
        if kind != "character":
            raise ValueError("Invalid kind for character record delete")
        if not str(item_id).strip():
            raise ValueError("Missing character id")
        rel, var_name, path = self._normalize_record_ref(record_ref)
        file_path = self._resolve_rel_path(rel)
        order, values = _parse_js_vars(file_path)
        if var_name not in values:
            raise ValueError(f"Var not found in file: {var_name}")

        container = self._path_get(values[var_name], path) if path else values[var_name]
        mode = mode.strip().lower()
        if mode == "array":
            if not isinstance(container, list):
                raise ValueError("Current record is not an array")
            if index is None:
                raise ValueError("Missing array index")
            if index < 0 or index >= len(container):
                raise ValueError(f"Array index out of range: {index}")
            container.pop(index)
        elif mode == "object":
            if not isinstance(container, dict):
                raise ValueError("Current record is not an object")
            k = str(key).strip()
            if not k:
                raise ValueError("Missing object key")
            if k not in container:
                raise ValueError(f"Object key not found: {k}")
            del container[k]
        else:
            raise ValueError(f"Unsupported delete mode: {mode}")

        backup_dir = _create_backup_dir()
        _backup_file(file_path, backup_dir)
        self._write_js_file(file_path, order, values)
        self._refresh_slice(game=game, locale=locale, kind="character")
        return backup_dir.name

    def save_item(
        self, game: str, locale: str, kind: str, item_id: str, fields: dict[str, str]
    ) -> str:
        game, locale, kind = self._ensure_params(game, locale, kind)
        self._ensure_loaded(game=game, locale=locale, kind=kind)
        backup_dir = _create_backup_dir()
        if kind == "character":
            self._save_character(game, locale, item_id, fields, backup_dir)
        elif kind == "weapon":
            self._save_weapon(game, locale, item_id, fields, backup_dir)
        elif kind == "relic":
            self._save_relic(game, locale, item_id, fields, backup_dir)
        else:
            raise ValueError(f"Unknown kind: {kind}")
        self._refresh_slice(game=game, locale=locale, kind=kind)
        return backup_dir.name

    def _save_character(
        self,
        game: str,
        locale: str,
        item_id: str,
        fields: dict[str, str],
        backup_dir: Path,
    ) -> None:
        if game == "sr":
            file_path = self._file_sr_avatar(locale)
            var_name = "_avatar"
        else:
            file_path = self._file_gi_avatar(locale)
            var_name = "__AvatarInfoConfig"

        order, values = _parse_js_vars(file_path)
        rows = values.get(var_name) or []
        target = None
        for row in rows:
            if str(row.get("_id", "")) == str(item_id):
                target = row
                break
        if target is None:
            raise ValueError(f"Character not found: {item_id}")

        target["Name"] = str(fields.get("name", target.get("Name", "")))
        target["Desc"] = str(fields.get("desc", target.get("Desc", "")))
        if game == "gi" and "title" in fields:
            target["Title"] = str(fields.get("title", target.get("Title", "")))

        _backup_file(file_path, backup_dir)
        values[var_name] = rows
        self._write_js_file(file_path, order, values)

    def _save_weapon(
        self,
        game: str,
        locale: str,
        item_id: str,
        fields: dict[str, str],
        backup_dir: Path,
    ) -> None:
        if game == "sr":
            file_path = self._dir_sr_weapon(locale) / f"{item_id}.js"
            if not file_path.exists():
                raise ValueError(f"Weapon file not found: {file_path}")
            _, values = _parse_js_vars(file_path)
            desc_map = values.get("_weapondesc_") or {}
            skill_map = values.get("_weaponskill_") or {}
            desc_map[item_id] = str(fields.get("desc", desc_map.get(item_id, "")))

            if item_id not in skill_map or not isinstance(skill_map[item_id], dict):
                skill_map[item_id] = {"Live": {"Name": "", "Desc": [""]}}
            for _, cfg in skill_map[item_id].items():
                if not isinstance(cfg, dict):
                    continue
                cfg["Name"] = str(fields.get("skill_name", cfg.get("Name", "")))
                desc = cfg.get("Desc")
                if isinstance(desc, list) and desc:
                    desc[0] = str(fields.get("skill_desc", desc[0]))
                else:
                    cfg["Desc"] = [str(fields.get("skill_desc", ""))]

            _backup_file(file_path, backup_dir)
            file_path.write_text(
                _auto_generated_content([("_weapondesc_", desc_map), ("_weaponskill_", skill_map)]),
                encoding="utf-8",
            )
            return

        file_path = self._dir_gi_weapon(locale) / f"{item_id}.js"
        if not file_path.exists():
            raise ValueError(f"Weapon file not found: {file_path}")
        _, values = _parse_js_vars(file_path)
        affix_map = values.get("_WeaponAffixPConfig_") or {}
        story_map = values.get("weapon_story_cache_") or {}
        affix_key = next(iter(affix_map.keys()), "")
        if affix_key:
            ver_map = (affix_map.get(affix_key) or {}).get("Ver") or {}
            if isinstance(ver_map, dict):
                for _, cfg in ver_map.items():
                    if not isinstance(cfg, dict):
                        continue
                    affix = cfg.get("Affix")
                    if isinstance(affix, list) and affix:
                        affix[0] = str(fields.get("affix_desc", affix[0]))
                    else:
                        cfg["Affix"] = [str(fields.get("affix_desc", ""))]
        story_key = next(iter(story_map.keys()), "")
        if story_key:
            story_arr = story_map.get(story_key)
            if isinstance(story_arr, list) and story_arr:
                story_arr[0] = str(fields.get("story", story_arr[0]))
            else:
                story_map[story_key] = [str(fields.get("story", ""))]

        _backup_file(file_path, backup_dir)
        file_path.write_text(
            _auto_generated_content([("_WeaponAffixPConfig_", affix_map), ("weapon_story_cache_", story_map)]),
            encoding="utf-8",
        )

    def _save_relic(
        self,
        game: str,
        locale: str,
        item_id: str,
        fields: dict[str, str],
        backup_dir: Path,
    ) -> None:
        if game == "sr":
            file_path = self._dir_sr_relic(locale) / f"{item_id}.js"
            if not file_path.exists():
                raise ValueError(f"Relic file not found: {file_path}")
            _, values = _parse_js_vars(file_path)
            relic_map = values.get("_relicitem_") or {}
            map_key = item_id if item_id in relic_map else next(iter(relic_map.keys()), "")
            if not map_key:
                raise ValueError(f"Relic entry not found in file: {file_path}")
            parts = relic_map.get(map_key)
            if not isinstance(parts, list):
                raise ValueError(f"Relic entry invalid: {file_path}")
            for idx, part in enumerate(parts, start=1):
                if not isinstance(part, dict):
                    continue
                k_name = f"p{idx}_name"
                k_desc = f"p{idx}_desc"
                k_story = f"p{idx}_story"
                if k_name in fields:
                    part["Name"] = str(fields[k_name])
                if k_desc in fields:
                    part["Desc"] = str(fields[k_desc])
                if k_story in fields:
                    part["Story"] = str(fields[k_story])

            _backup_file(file_path, backup_dir)
            file_path.write_text(_auto_generated_content([("_relicitem_", relic_map)]), encoding="utf-8")
            return

        file_path = self._dir_gi_relic(locale) / f"{item_id}.js"
        if not file_path.exists():
            raise ValueError(f"Relic file not found: {file_path}")
        _, values = _parse_js_vars(file_path)
        relic_map = values.get("relic_story_cache_") or {}
        map_key = next(iter(relic_map.keys()), "")
        if not map_key:
            raise ValueError(f"Relic entry not found in file: {file_path}")
        parts = relic_map.get(map_key)
        if not isinstance(parts, list):
            raise ValueError(f"Relic entry invalid: {file_path}")
        for idx, part in enumerate(parts, start=1):
            if not isinstance(part, dict):
                continue
            k_desc = f"p{idx}_desc"
            k_story = f"p{idx}_story"
            if k_desc in fields:
                part["Desc"] = str(fields[k_desc])
            if k_story in fields:
                story = part.get("Story")
                if isinstance(story, list) and story:
                    story[0] = str(fields[k_story])
                else:
                    part["Story"] = [str(fields[k_story])]

        _backup_file(file_path, backup_dir)
        file_path.write_text(_auto_generated_content([("relic_story_cache_", relic_map)]), encoding="utf-8")
