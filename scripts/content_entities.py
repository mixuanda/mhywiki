#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import shutil
import subprocess
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT_DIR / "site"
BACKUP_ROOT = ROOT_DIR / "easy_updates" / "entity_backups"

SR_AVATAR_FILE = SITE_DIR / "data" / "CH" / "Avatar.js"
GI_AVATAR_FILE = SITE_DIR / "gi" / "CH" / "avatar.js"
SR_WEAPON_DIR = SITE_DIR / "data" / "CH" / "Weapon"
GI_WEAPON_DIR = SITE_DIR / "gi" / "CH" / "Weapon"


def _run_node(script: str, *args: str) -> str:
    proc = subprocess.run(
        ["node", "-e", script, *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout


def _node_eval_file(file_path: Path, var_names: list[str]) -> dict:
    script = r"""
const fs = require("fs");
const vm = require("vm");
const file = process.argv[1];
const vars = JSON.parse(process.argv[2]);
const code = fs.readFileSync(file, "utf8");
const sandbox = {};
vm.createContext(sandbox);
vm.runInContext(code, sandbox, { filename: file });
const out = {};
for (const k of vars) out[k] = sandbox[k];
process.stdout.write(JSON.stringify(out));
"""
    raw = _run_node(script, str(file_path), json.dumps(var_names, ensure_ascii=False))
    return json.loads(raw)


def _node_eval_many(specs: list[dict]) -> list[dict]:
    script = r"""
const fs = require("fs");
const vm = require("vm");
const specs = JSON.parse(process.argv[1]);
const out = [];
for (const s of specs) {
  const code = fs.readFileSync(s.file, "utf8");
  const sandbox = {};
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox, { filename: s.file });
  const values = {};
  for (const k of s.vars) values[k] = sandbox[k];
  out.push({ id: s.id, file: s.file, values });
}
process.stdout.write(JSON.stringify(out));
"""
    raw = _run_node(script, json.dumps(specs, ensure_ascii=False))
    return json.loads(raw)


def _auto_generated_content(assignments: list[tuple[str, object]]) -> str:
    parts = ["// Auto Generated", ""]
    for i, (name, data) in enumerate(assignments):
        parts.append(
            f"var {name} = {json.dumps(data, ensure_ascii=False, indent=4)}"
        )
        if i != len(assignments) - 1:
            parts.append("")
    parts.append("")
    return "\n".join(parts)


def _create_backup_dir() -> Path:
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_dir = BACKUP_ROOT / ts
    backup_dir.mkdir(parents=True, exist_ok=False)
    return backup_dir


def _backup_file(src: Path, backup_dir: Path) -> None:
    rel = src.relative_to(ROOT_DIR)
    dst = backup_dir / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _latest_backup_dir() -> Path | None:
    if not BACKUP_ROOT.exists():
        return None
    dirs = [p for p in BACKUP_ROOT.iterdir() if p.is_dir()]
    if not dirs:
        return None
    return sorted(dirs)[-1]


def backup_status() -> dict:
    if not BACKUP_ROOT.exists():
        return {"count": 0, "latest": ""}
    dirs = [p for p in BACKUP_ROOT.iterdir() if p.is_dir()]
    if not dirs:
        return {"count": 0, "latest": ""}
    latest = sorted(dirs)[-1].name
    return {"count": len(dirs), "latest": latest}


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


class ContentRepository:
    def __init__(self) -> None:
        self.characters: dict[str, list[dict]] = {"sr": [], "gi": []}
        self.weapons: dict[str, dict[str, dict]] = {"sr": {}, "gi": {}}
        self.refresh()

    @staticmethod
    def _short(text: str, max_len: int = 80) -> str:
        t = (text or "").replace("<br>", " ").replace("\n", " ").strip()
        if len(t) <= max_len:
            return t
        return t[: max_len - 1] + "..."

    def refresh(self) -> None:
        self.characters["sr"] = self._load_sr_characters()
        self.characters["gi"] = self._load_gi_characters()
        self.weapons["sr"] = self._load_sr_weapons()
        self.weapons["gi"] = self._load_gi_weapons()

    def _load_sr_characters(self) -> list[dict]:
        payload = _node_eval_file(SR_AVATAR_FILE, ["_avatar"])
        rows = payload.get("_avatar") or []
        out = []
        for x in rows:
            out.append(
                {
                    "id": str(x.get("_id", "")),
                    "name": str(x.get("Name", "")),
                    "desc": str(x.get("Desc", "")),
                    "title": str(x.get("Title", "")),
                }
            )
        return out

    def _load_gi_characters(self) -> list[dict]:
        payload = _node_eval_file(GI_AVATAR_FILE, ["__AvatarInfoConfig"])
        rows = payload.get("__AvatarInfoConfig") or []
        out = []
        for x in rows:
            out.append(
                {
                    "id": str(x.get("_id", "")),
                    "name": str(x.get("Name", "")),
                    "desc": str(x.get("Desc", "")),
                    "title": str(x.get("Title", "")),
                }
            )
        return out

    def _load_sr_weapons(self) -> dict[str, dict]:
        files = sorted(SR_WEAPON_DIR.glob("*.js"))
        specs = [
            {
                "id": f.stem,
                "file": str(f),
                "vars": ["_weapondesc_", "_weaponskill_"],
            }
            for f in files
        ]
        rows = _node_eval_many(specs) if specs else []
        out: dict[str, dict] = {}
        for row in rows:
            wid = str(row["id"])
            vals = row["values"] or {}
            desc_map = vals.get("_weapondesc_") or {}
            skill_map = vals.get("_weaponskill_") or {}
            live = {}
            if isinstance(skill_map, dict):
                live = (skill_map.get(wid) or {}).get("Live") or {}
            skill_desc = ""
            if isinstance(live.get("Desc"), list) and live["Desc"]:
                skill_desc = str(live["Desc"][0])
            out[wid] = {
                "id": wid,
                "name": str(live.get("Name") or f"光锥 {wid}"),
                "desc": str(desc_map.get(wid) or ""),
                "skill_name": str(live.get("Name") or ""),
                "skill_desc": skill_desc,
            }
        return out

    def _load_gi_weapons(self) -> dict[str, dict]:
        files = sorted(GI_WEAPON_DIR.glob("*.js"))
        specs = [
            {
                "id": f.stem,
                "file": str(f),
                "vars": ["_WeaponAffixPConfig_", "weapon_story_cache_"],
            }
            for f in files
        ]
        rows = _node_eval_many(specs) if specs else []
        out: dict[str, dict] = {}
        for row in rows:
            wid = str(row["id"])
            vals = row["values"] or {}
            affix_map = vals.get("_WeaponAffixPConfig_") or {}
            story_map = vals.get("weapon_story_cache_") or {}
            affix_key = next(iter(affix_map.keys()), "")
            affix_desc = ""
            if affix_key:
                ver_map = (affix_map.get(affix_key) or {}).get("Ver") or {}
                v1 = (ver_map.get("1") or {}) if isinstance(ver_map, dict) else {}
                affix = v1.get("Affix") if isinstance(v1, dict) else None
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
                "name": f"武器 {wid}",
                "affix_desc": affix_desc,
                "story": story,
            }
        return out

    def list_items(self, kind: str, game: str, query: str = "") -> list[dict]:
        q = query.strip().lower()
        items: list[dict] = []
        if kind == "character":
            for row in self.characters.get(game, []):
                text = f"{row['id']} {row['name']} {row.get('title', '')} {row['desc']}".lower()
                if q and q not in text:
                    continue
                items.append(
                    {
                        "id": row["id"],
                        "name": row["name"] or f"角色 {row['id']}",
                        "summary": self._short(row["desc"]),
                    }
                )
        elif kind == "weapon":
            for wid, row in self.weapons.get(game, {}).items():
                search_blob = (
                    f"{wid} {row.get('name','')} {row.get('desc','')} "
                    f"{row.get('skill_desc','')} {row.get('affix_desc','')}"
                ).lower()
                if q and q not in search_blob:
                    continue
                summary_base = (
                    row.get("desc")
                    or row.get("skill_desc")
                    or row.get("affix_desc")
                    or ""
                )
                items.append(
                    {
                        "id": wid,
                        "name": row.get("name") or f"武器 {wid}",
                        "summary": self._short(summary_base),
                    }
                )
        items.sort(key=lambda x: x["id"])
        return items

    def get_item(self, kind: str, game: str, item_id: str) -> dict:
        if kind == "character":
            rows = self.characters.get(game, [])
            row = next((x for x in rows if x["id"] == item_id), None)
            if not row:
                raise ValueError(f"Character not found: {item_id}")
            fields = [
                {"key": "name", "label": "名称", "type": "text", "value": row["name"]},
                {"key": "desc", "label": "简介", "type": "textarea", "value": row["desc"]},
            ]
            if game == "gi":
                fields.append(
                    {
                        "key": "title",
                        "label": "称号",
                        "type": "text",
                        "value": row.get("title", ""),
                    }
                )
            return {
                "kind": kind,
                "game": game,
                "id": row["id"],
                "title": row["name"] or f"角色 {row['id']}",
                "fields": fields,
            }

        rows_w = self.weapons.get(game, {})
        row = rows_w.get(item_id)
        if not row:
            raise ValueError(f"Weapon not found: {item_id}")
        if game == "sr":
            fields = [
                {"key": "desc", "label": "光锥描述", "type": "textarea", "value": row.get("desc", "")},
                {"key": "skill_name", "label": "技能名", "type": "text", "value": row.get("skill_name", "")},
                {"key": "skill_desc", "label": "技能描述(首段)", "type": "textarea", "value": row.get("skill_desc", "")},
            ]
        else:
            fields = [
                {"key": "affix_desc", "label": "武器效果(1阶)", "type": "textarea", "value": row.get("affix_desc", "")},
                {"key": "story", "label": "武器故事(首段)", "type": "textarea", "value": row.get("story", "")},
            ]
        return {
            "kind": kind,
            "game": game,
            "id": row["id"],
            "title": row.get("name") or f"武器 {row['id']}",
            "fields": fields,
        }

    def save_item(self, kind: str, game: str, item_id: str, fields: dict[str, str]) -> str:
        backup_dir = _create_backup_dir()
        if kind == "character":
            self._save_character(game, item_id, fields, backup_dir)
        elif kind == "weapon":
            self._save_weapon(game, item_id, fields, backup_dir)
        else:
            raise ValueError(f"Unknown kind: {kind}")
        self.refresh()
        return backup_dir.name

    def _save_character(
        self, game: str, item_id: str, fields: dict[str, str], backup_dir: Path
    ) -> None:
        if game == "sr":
            file_path, var_name = SR_AVATAR_FILE, "_avatar"
        elif game == "gi":
            file_path, var_name = GI_AVATAR_FILE, "__AvatarInfoConfig"
        else:
            raise ValueError(f"Unknown game: {game}")

        payload = _node_eval_file(file_path, [var_name])
        rows = payload.get(var_name) or []
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
        file_path.write_text(
            _auto_generated_content([(var_name, rows)]),
            encoding="utf-8",
        )

    def _save_weapon(
        self, game: str, item_id: str, fields: dict[str, str], backup_dir: Path
    ) -> None:
        if game == "sr":
            file_path = SR_WEAPON_DIR / f"{item_id}.js"
            if not file_path.exists():
                raise ValueError(f"Weapon file not found: {file_path}")
            payload = _node_eval_file(file_path, ["_weapondesc_", "_weaponskill_"])
            desc_map = payload.get("_weapondesc_") or {}
            skill_map = payload.get("_weaponskill_") or {}

            desc_map[item_id] = str(fields.get("desc", desc_map.get(item_id, "")))
            if item_id not in skill_map or not isinstance(skill_map[item_id], dict):
                skill_map[item_id] = {"Live": {"Name": "", "Desc": [""]}}

            for ver, cfg in skill_map[item_id].items():
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
                _auto_generated_content(
                    [
                        ("_weapondesc_", desc_map),
                        ("_weaponskill_", skill_map),
                    ]
                ),
                encoding="utf-8",
            )
            return

        if game == "gi":
            file_path = GI_WEAPON_DIR / f"{item_id}.js"
            if not file_path.exists():
                raise ValueError(f"Weapon file not found: {file_path}")
            payload = _node_eval_file(file_path, ["_WeaponAffixPConfig_", "weapon_story_cache_"])
            affix_map = payload.get("_WeaponAffixPConfig_") or {}
            story_map = payload.get("weapon_story_cache_") or {}

            affix_key = next(iter(affix_map.keys()), "")
            if affix_key:
                ver_map = (affix_map.get(affix_key) or {}).get("Ver") or {}
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
                _auto_generated_content(
                    [
                        ("_WeaponAffixPConfig_", affix_map),
                        ("weapon_story_cache_", story_map),
                    ]
                ),
                encoding="utf-8",
            )
            return

        raise ValueError(f"Unknown game: {game}")
