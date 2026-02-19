#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from normalize import normalize_id, parse_js_assignments, read_json, write_json


GI_ENTITY_DIRS = {
    "character": "gi/characters",
    "weapon": "gi/weapons",
    "artifact": "gi/artifacts",
    "enemy": "gi/enemies",
    "banner": "gi/banners",
}

SR_ENTITY_DIRS = {
    "character": "sr/characters",
    "lightcone": "sr/lightcones",
    "relic": "sr/relics",
    "enemy": "sr/enemies",
    "banner": "sr/banners",
}


@dataclass
class SyncResult:
    changed_files: list[Path]
    notes: list[str]


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit():
            return int(text)
    return None


def _safe_name(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _safe_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return str(value)


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _write_js_assignments(path: Path, mapping: dict[str, Any]) -> None:
    lines = ["// Auto Generated", ""]
    for key, value in mapping.items():
        lines.append(f"var {key} = {json.dumps(value, ensure_ascii=False, indent=4)}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _upsert_list_row(rows: list[dict[str, Any]], new_row: dict[str, Any], keys: list[str]) -> str:
    for idx, row in enumerate(rows):
        for key in keys:
            if key in row and key in new_row and str(row.get(key)) == str(new_row.get(key)):
                merged = dict(row)
                merged.update({k: v for k, v in new_row.items() if v is not None})
                rows[idx] = merged
                return "updated"
    rows.append(new_row)
    return "created"


def _ensure_route_from_template(
    *,
    template: Path,
    output: Path,
    hidden_id: str,
    value: str,
) -> None:
    text = template.read_text(encoding="utf-8", errors="ignore")
    pattern_dq = re.compile(rf'(id="{re.escape(hidden_id)}"\s+value=")[^"]*(")')
    pattern_sq = re.compile(rf"(id='{re.escape(hidden_id)}'\s+value=')[^']*(')")
    updated = pattern_dq.sub(lambda m: f"{m.group(1)}{value}{m.group(2)}", text)
    updated = pattern_sq.sub(lambda m: f"{m.group(1)}{value}{m.group(2)}", updated)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(updated, encoding="utf-8")


def _entity_file(data_root: Path, game: str, kind: str, entity_id: str) -> Path:
    if game == "gi":
        rel = GI_ENTITY_DIRS[kind]
    elif game == "sr":
        rel = SR_ENTITY_DIRS[kind]
    else:
        raise ValueError(f"Unsupported game: {game}")
    return data_root / rel / f"{entity_id}.json"


def _sync_gi_character(payload: dict[str, Any], web_root: Path) -> SyncResult:
    changed: list[Path] = []
    notes: list[str] = []

    code_name = _safe_name(payload.get("codeName"), normalize_id(payload.get("id", "new_avatar")))
    char_id = normalize_id(payload.get("id", code_name))
    char_id_num = _as_int(char_id) or _as_int(payload.get("legacyId"))
    if char_id_num is None:
        # GI legacy runtime strongly assumes numeric _id for many lookups.
        char_id_num = abs(hash(char_id)) % 900000 + 100000
        notes.append(f"GI character id `{char_id}` is non-numeric; generated legacy numeric id `{char_id_num}`.")

    avatar_js = web_root / "gi" / "CH" / "avatar.js"
    avatar_data = parse_js_assignments(avatar_js)
    rows = avatar_data.get("__AvatarInfoConfig", [])
    if not isinstance(rows, list):
        rows = []

    material_refs = [x for x in payload.get("materialRefs", []) if str(x).strip()]
    material_ids = [int(x) for x in material_refs if str(x).isdigit()]

    new_row = {
        "_name": code_name,
        "_id": char_id_num,
        "Name": _safe_name(payload.get("name"), code_name),
        "Desc": _safe_text(payload.get("description")),
        "Title": _safe_text(payload.get("title")),
        "Constellation": _safe_text(payload.get("constellation")),
        "Nation": _safe_text(payload.get("nation")),
        "Belong": _safe_text(payload.get("affiliation")),
        "Grade": payload.get("rarity"),
        "Weapon": payload.get("weaponType"),
        "Element": payload.get("element"),
        "Version": payload.get("version"),
        "ShowStats": payload.get("baseStats") or {},
        "ShowStats2": payload.get("maxStats") or {},
        "CommonMatt": material_ids[0] if len(material_ids) > 0 else 0,
        "TalentMatt": material_ids[1] if len(material_ids) > 1 else 0,
        "SpecialityMat": material_ids[2] if len(material_ids) > 2 else 0,
        "AscMat": material_ids[3] if len(material_ids) > 3 else 0,
        "WeekMat": material_ids[4] if len(material_ids) > 4 else 0,
        "NA": [],
        "NW": [],
        "NR": [],
        "VS": [],
    }
    _upsert_list_row(rows, new_row, ["_id", "_name"])
    avatar_data["__AvatarInfoConfig"] = rows
    _write_js_assignments(avatar_js, avatar_data)
    changed.append(avatar_js)

    combat = payload.get("combat") or {}
    detail_1 = combat.get("detail_1") if isinstance(combat, dict) else {}
    detail_2 = combat.get("detail_2") if isinstance(combat, dict) else {}
    if not isinstance(detail_1, dict):
        detail_1 = {}
    if not isinstance(detail_2, dict):
        detail_2 = {}

    manual_sections = payload.get("manualSections", {})
    skill_notes = []
    for key in ["skills", "talents", "constellation", "notes"]:
        values = manual_sections.get(key, [])
        if isinstance(values, list):
            skill_notes.extend([str(v) for v in values if str(v).strip()])

    default_detail_1 = {
        "_AvatarDataConfig_": {code_name: {"OtherDataList": skill_notes[:]}},
        "_AvatarMats_": {code_name: {}},
        "_AvatarSkillPConfig_": {code_name: {"Manual": skill_notes[:] }},
        "_AvatarAttackConfig_": {code_name: {}},
    }
    default_detail_2 = {
        "_AvatarFetterConfig_": {str(char_id_num): {"StoryTitle": [_safe_name(payload.get("name"), code_name)], "StoryContext": [_safe_text(payload.get("description"))]}},
        "_AvatarCostumeConfig_": {str(char_id_num): []},
        "acs_cache_": {},
    }

    detail_1_out = dict(default_detail_1)
    detail_1_out.update({k: v for k, v in detail_1.items() if isinstance(k, str)})
    detail_2_out = dict(default_detail_2)
    detail_2_out.update({k: v for k, v in detail_2.items() if isinstance(k, str)})

    detail_1_file = web_root / "gi" / "CH" / "Avatar" / f"{code_name}_1.js"
    detail_2_file = web_root / "gi" / "CH" / "Avatar" / f"{code_name}_2.js"
    _write_js_assignments(detail_1_file, detail_1_out)
    _write_js_assignments(detail_2_file, detail_2_out)
    changed.extend([detail_1_file, detail_2_file])

    gi_char_template = web_root / "gi" / "char" / "index.html"
    gi_char_route_name = web_root / "gi" / "char" / code_name / "index.html"
    gi_char_route_id = web_root / "gi" / "char" / str(char_id_num) / "index.html"
    _ensure_route_from_template(
        template=gi_char_template,
        output=gi_char_route_name,
        hidden_id="AVID",
        value=code_name,
    )
    _ensure_route_from_template(
        template=gi_char_template,
        output=gi_char_route_id,
        hidden_id="AVID",
        value=code_name,
    )
    changed.extend([gi_char_route_name, gi_char_route_id])

    return SyncResult(changed_files=changed, notes=notes)


def _sync_sr_character(payload: dict[str, Any], web_root: Path) -> SyncResult:
    changed: list[Path] = []
    notes: list[str] = []

    char_id = normalize_id(payload.get("id", "new_character"))
    char_id_num = _as_int(char_id)
    if char_id_num is None:
        raise ValueError("SR character id must be numeric for legacy runtime compatibility.")

    avatar_js = web_root / "data" / "CH" / "Avatar.js"
    avatar_data = parse_js_assignments(avatar_js)
    rows = avatar_data.get("_avatar", [])
    if not isinstance(rows, list):
        rows = []

    new_row = {
        "_id": char_id_num,
        "Ver": payload.get("version"),
        "Name": _safe_name(payload.get("name"), char_id),
        "Desc": _safe_text(payload.get("description")),
        "Rarity": payload.get("rarity"),
        "Element": payload.get("element"),
        "Path": payload.get("path"),
        "Skills": payload.get("skillIds", []),
        "Ranks": payload.get("rankIds", []),
        "Mat": [int(x) for x in payload.get("materialRefs", []) if str(x).isdigit()],
        "Stats": payload.get("baseStats") or {},
        "V": payload.get("vers") or [],
    }
    _upsert_list_row(rows, new_row, ["_id"])
    avatar_data["_avatar"] = rows
    _write_js_assignments(avatar_js, avatar_data)
    changed.append(avatar_js)

    combat = payload.get("combat")
    if not isinstance(combat, dict):
        combat = {}
    manual_sections = payload.get("manualSections", {})
    section_notes = []
    for key in ["skills", "talents", "eidolons", "traces", "notes"]:
        values = manual_sections.get(key, [])
        if isinstance(values, list):
            section_notes.extend([str(v) for v in values if str(v).strip()])

    if not combat:
        skill_id = int(f"{char_id_num}01")
        combat = {
            "_avatarskill_": {
                str(skill_id): {
                    "Pre": {
                        "Name": "Manual Skill",
                        "Type": "Manual",
                        "Desc": "<br>".join(section_notes) if section_notes else _safe_text(payload.get("description")),
                    }
                }
            },
            "_avatarskilltree_": {
                str(char_id_num): {
                    "Pre": {
                        "Add": {},
                        "Tree1": {"Name": "Trace 1", "Desc": ""},
                        "Tree2": {"Name": "Trace 2", "Desc": ""},
                        "Tree3": {"Name": "Trace 3", "Desc": ""},
                    }
                }
            },
            "_avatarrank_": {
                str(skill_id): {
                    "Pre": {"Rank": 1, "Name": "Eidolon 1", "Desc": ""}
                }
            },
            "_story_": {str(char_id_num): {}},
            "_voice_": {str(char_id_num): {}},
            "_notes_": {str(char_id_num): {"Pre": section_notes}},
            "_adiff_": {str(char_id_num): {}},
            "_mtc_": {str(char_id_num): {}},
        }

    required_vars = [
        "_avatarskill_",
        "_avatarskilltree_",
        "_avatarrank_",
        "_story_",
        "_voice_",
        "_notes_",
        "_adiff_",
        "_mtc_",
    ]
    detail_out: dict[str, Any] = {}
    for key in required_vars:
        value = combat.get(key)
        if isinstance(value, dict):
            detail_out[key] = value
        else:
            detail_out[key] = {}

    detail_file = web_root / "data" / "CH" / "Avatar" / f"{char_id_num}.js"
    _write_js_assignments(detail_file, detail_out)
    changed.append(detail_file)

    sr_char_template = web_root / "sr" / "char" / "index.html"
    sr_char_route = web_root / "sr" / "char" / str(char_id_num) / "index.html"
    _ensure_route_from_template(
        template=sr_char_template,
        output=sr_char_route,
        hidden_id="AVID",
        value=str(char_id_num),
    )
    changed.append(sr_char_route)

    return SyncResult(changed_files=changed, notes=notes)


def _sync_gi_weapon(payload: dict[str, Any], web_root: Path) -> SyncResult:
    changed: list[Path] = []
    weapon_id = normalize_id(payload.get("id", "0"))
    weapon_id_num = _as_int(weapon_id) or weapon_id

    avatar_js = web_root / "gi" / "CH" / "avatar.js"
    avatar_data = parse_js_assignments(avatar_js)
    rows = avatar_data.get("_WeaponConfig", [])
    if not isinstance(rows, list):
        rows = []

    affix_id = _as_int(payload.get("affixId")) or (_as_int(weapon_id) + 100000 if _as_int(weapon_id) else 100000)
    material_ids = [int(x) for x in payload.get("materialRefs", []) if str(x).isdigit()]
    new_row = {
        "_id": str(weapon_id_num),
        "Name": _safe_name(payload.get("name"), str(weapon_id_num)),
        "Desc": _safe_text(payload.get("description")),
        "Type": payload.get("weaponType"),
        "Rank": payload.get("rarity"),
        "Stat": payload.get("baseAtk"),
        "Custom": payload.get("subStatType"),
        "CustomStat": payload.get("subStatValue"),
        "AscMatID": material_ids[0] if material_ids else 0,
        "MatIDs": material_ids[1:],
        "EquipAffixID": affix_id,
        "EquipAffixName": _safe_text(payload.get("skillName")),
    }
    _upsert_list_row(rows, new_row, ["_id"])
    avatar_data["_WeaponConfig"] = rows
    _write_js_assignments(avatar_js, avatar_data)
    changed.append(avatar_js)

    affix = payload.get("affix")
    if not isinstance(affix, dict):
        affix = {
            str(affix_id): {
                "Ver": {
                    "1": {
                        "Affix": [line for line in payload.get("manualSections", {}).get("skills", []) if str(line).strip()]
                    }
                }
            }
        }
    detail_out = {
        "_WeaponAffixPConfig_": affix,
        "weapon_story_cache_": {},
    }
    detail_file = web_root / "gi" / "CH" / "Weapon" / f"{weapon_id}.js"
    _write_js_assignments(detail_file, detail_out)
    changed.append(detail_file)

    gi_char_template = web_root / "gi" / "char" / "index.html"
    gi_weapon_route = web_root / "gi" / "char" / str(weapon_id) / "index.html"
    _ensure_route_from_template(
        template=gi_char_template,
        output=gi_weapon_route,
        hidden_id="AVID",
        value=str(weapon_id),
    )
    changed.append(gi_weapon_route)

    return SyncResult(changed_files=changed, notes=[])


def _sync_sr_lightcone(payload: dict[str, Any], web_root: Path) -> SyncResult:
    changed: list[Path] = []
    lc_id = normalize_id(payload.get("id", "0"))
    lc_id_num = _as_int(lc_id)
    if lc_id_num is None:
        raise ValueError("SR light cone id must be numeric for legacy runtime.")

    avatar_js = web_root / "data" / "CH" / "Avatar.js"
    avatar_data = parse_js_assignments(avatar_js)
    rows = avatar_data.get("_weapon", [])
    if not isinstance(rows, list):
        rows = []

    row = {
        "_id": lc_id_num,
        "Name": _safe_name(payload.get("name"), str(lc_id_num)),
        "Rarity": payload.get("rarity"),
        "Path": payload.get("path"),
        "Skill": payload.get("skillId") or lc_id_num,
        "Mat": [int(x) for x in payload.get("materialRefs", []) if str(x).isdigit()],
        "Stats": payload.get("baseStats") or {},
    }
    _upsert_list_row(rows, row, ["_id"])
    avatar_data["_weapon"] = rows
    _write_js_assignments(avatar_js, avatar_data)
    changed.append(avatar_js)

    detail = payload.get("detail")
    if not isinstance(detail, dict):
        skills = payload.get("manualSections", {}).get("skills", [])
        detail = {
            "_weapondesc_": {str(lc_id_num): _safe_text(payload.get("description"))},
            "_weaponskill_": {
                str(lc_id_num): {
                    "v1": {
                        "Name": _safe_name(payload.get("skillName"), "Manual Skill"),
                        "Desc": ["<br>".join(str(x) for x in skills if str(x).strip())],
                    }
                }
            },
        }
    detail_out = {
        "_weapondesc_": detail.get("_weapondesc_", {}),
        "_weaponskill_": detail.get("_weaponskill_", {}),
    }
    detail_file = web_root / "data" / "CH" / "Weapon" / f"{lc_id_num}.js"
    _write_js_assignments(detail_file, detail_out)
    changed.append(detail_file)

    sr_char_template = web_root / "sr" / "char" / "index.html"
    sr_lc_route = web_root / "sr" / "char" / str(lc_id_num) / "index.html"
    _ensure_route_from_template(
        template=sr_char_template,
        output=sr_lc_route,
        hidden_id="AVID",
        value=str(lc_id_num),
    )
    changed.append(sr_lc_route)

    return SyncResult(changed_files=changed, notes=[])


def _sync_gi_artifact(payload: dict[str, Any], web_root: Path) -> SyncResult:
    avatar_js = web_root / "gi" / "CH" / "avatar.js"
    avatar_data = parse_js_assignments(avatar_js)
    rows = avatar_data.get("_RelicConfig", [])
    if not isinstance(rows, list):
        rows = []

    row = {
        "ID": _as_int(payload.get("id")) or payload.get("id"),
        "Name": _safe_name(payload.get("name"), str(payload.get("id"))),
        "Icon": payload.get("icon"),
        "Skills": payload.get("setBonuses", []),
        "Parts": payload.get("parts", []),
        "Extra": payload.get("extra", []),
    }
    _upsert_list_row(rows, row, ["ID"])
    avatar_data["_RelicConfig"] = rows
    _write_js_assignments(avatar_js, avatar_data)
    return SyncResult(changed_files=[avatar_js], notes=[])


def _sync_sr_relic(payload: dict[str, Any], web_root: Path) -> SyncResult:
    changed: list[Path] = []
    relic_id = normalize_id(payload.get("id", "0"))
    relic_id_num = _as_int(relic_id)
    if relic_id_num is None:
        raise ValueError("SR relic id must be numeric for legacy runtime.")

    avatar_js = web_root / "data" / "CH" / "Avatar.js"
    avatar_data = parse_js_assignments(avatar_js)
    rows = avatar_data.get("_relic", [])
    if not isinstance(rows, list):
        rows = []

    row = {
        "_id": relic_id_num,
        "Name": _safe_name(payload.get("name"), str(relic_id_num)),
        "Icon": payload.get("icon"),
        "Skills": payload.get("setBonuses", []),
    }
    _upsert_list_row(rows, row, ["_id"])
    avatar_data["_relic"] = rows
    _write_js_assignments(avatar_js, avatar_data)
    changed.append(avatar_js)

    detail = payload.get("detail")
    if not isinstance(detail, dict):
        detail = {
            "_relicitem_": {
                str(relic_id_num): payload.get("parts", []),
            }
        }
    detail_out = {"_relicitem_": detail.get("_relicitem_", {})}
    detail_file = web_root / "data" / "CH" / "Relic" / f"{relic_id_num}.js"
    _write_js_assignments(detail_file, detail_out)
    changed.append(detail_file)

    sr_char_template = web_root / "sr" / "char" / "index.html"
    sr_relic_route = web_root / "sr" / "char" / str(relic_id_num) / "index.html"
    _ensure_route_from_template(
        template=sr_char_template,
        output=sr_relic_route,
        hidden_id="AVID",
        value=str(relic_id_num),
    )
    changed.append(sr_relic_route)

    return SyncResult(changed_files=changed, notes=[])


def _sync_gi_enemy(payload: dict[str, Any], web_root: Path) -> SyncResult:
    changed: list[Path] = []
    enemy_id = normalize_id(payload.get("id", "0"))
    enemy_id_num = _as_int(enemy_id) or enemy_id
    enemy_row = {
        "_id": _as_int(enemy_id_num) or enemy_id_num,
        "Name": _safe_name(payload.get("name"), str(enemy_id_num)),
        "Desc": _safe_text(payload.get("description")),
        "Stats": payload.get("stats") or {},
        "Weak": payload.get("weakness") or payload.get("weak") or [],
        "RESBase": payload.get("resistance") or {},
        "Icon": payload.get("icon"),
        "Figure": payload.get("figure"),
    }

    for path in [web_root / "gi" / "CH" / "computer.js", web_root / "gi" / "CH" / "database.js"]:
        data = parse_js_assignments(path)
        monsters = data.get("_Monsters", {})
        if not isinstance(monsters, dict):
            monsters = {}
        monsters[str(enemy_id_num)] = enemy_row
        data["_Monsters"] = monsters
        _write_js_assignments(path, data)
        changed.append(path)

    gi_monster_template = web_root / "gi" / "monster" / "index.html"
    gi_monster_route = web_root / "gi" / "monster" / str(enemy_id_num) / "index.html"
    _ensure_route_from_template(
        template=gi_monster_template,
        output=gi_monster_route,
        hidden_id="MONSTERID",
        value=str(enemy_id_num),
    )
    changed.append(gi_monster_route)

    return SyncResult(changed_files=changed, notes=[])


def _sync_sr_enemy(payload: dict[str, Any], web_root: Path) -> SyncResult:
    changed: list[Path] = []
    enemy_id = normalize_id(payload.get("id", "0"))
    enemy_id_num = _as_int(enemy_id)
    if enemy_id_num is None:
        raise ValueError("SR enemy id must be numeric for legacy runtime.")

    monster_js = web_root / "data" / "CH" / "Monster_1.js"
    data = parse_js_assignments(monster_js)
    monsters = data.get("_monster", {})
    if not isinstance(monsters, dict):
        monsters = {}
    monsters[str(enemy_id_num)] = {
        "_id": enemy_id_num,
        "Name": _safe_name(payload.get("name"), str(enemy_id_num)),
        "Desc": _safe_text(payload.get("description")),
        "Stats": payload.get("stats") or {},
        "Weak": payload.get("weakness") or payload.get("weak") or [],
        "RESBase": payload.get("resistance") or {},
        "StatusRESBase": payload.get("statusResist"),
        "Icon": payload.get("icon"),
        "Figure": payload.get("figure"),
        "Camp": _as_int(payload.get("camp", 9999)) or 9999,
    }
    data["_monster"] = monsters
    _write_js_assignments(monster_js, data)
    changed.append(monster_js)

    sr_monster_template = web_root / "sr" / "monster" / "index.html"
    sr_monster_route = web_root / "sr" / "monster" / str(enemy_id_num) / "index.html"
    _ensure_route_from_template(
        template=sr_monster_template,
        output=sr_monster_route,
        hidden_id="MONSTERID",
        value=str(enemy_id_num),
    )
    changed.append(sr_monster_route)
    return SyncResult(changed_files=changed, notes=[])


def _sync_gi_banner(payload: dict[str, Any], web_root: Path) -> SyncResult:
    banner_js = web_root / "gi" / "banner.js"
    data = parse_js_assignments(banner_js)
    rows = data.get("_banners", [])
    if not isinstance(rows, list):
        rows = []

    version = _safe_name(payload.get("version"), "unknown")
    phase = _as_int(payload.get("phase")) or 1
    featured_5 = payload.get("featuredFiveStar", [])
    featured_4 = payload.get("featuredFourStar", [])

    target = None
    for row in rows:
        if str(row.get("V")) == version:
            target = row
            break
    if target is None:
        target = {"V": version, "P": []}
        rows.append(target)

    phases = target.get("P", [])
    if not isinstance(phases, list):
        phases = []
    replaced = False
    for idx, item in enumerate(phases):
        if _as_int(item.get("_id")) == phase:
            phases[idx] = {"_id": phase, "A": featured_5, "B": featured_4}
            replaced = True
            break
    if not replaced:
        phases.append({"_id": phase, "A": featured_5, "B": featured_4})
    target["P"] = phases

    data["_banners"] = rows
    _write_js_assignments(banner_js, data)
    return SyncResult(changed_files=[banner_js], notes=[])


def _sync_sr_banner(payload: dict[str, Any], web_root: Path) -> SyncResult:
    banner_js = web_root / "data" / "banner.js"
    data = parse_js_assignments(banner_js)
    rows = data.get("_banners", [])
    if not isinstance(rows, list):
        rows = []

    version = _safe_name(payload.get("version"), "unknown")
    phase = _as_int(payload.get("phase")) or 1
    featured_5 = payload.get("featuredFiveStar", [])
    featured_4 = payload.get("featuredFourStar", [])

    target = None
    for row in rows:
        if str(row.get("V")) == version:
            target = row
            break
    if target is None:
        target = {"V": version, "P": []}
        rows.append(target)

    phases = target.get("P", [])
    if not isinstance(phases, list):
        phases = []
    replaced = False
    for idx, item in enumerate(phases):
        if _as_int(item.get("I")) == phase:
            phases[idx] = {"I": phase, "A": featured_5, "B": featured_4}
            replaced = True
            break
    if not replaced:
        phases.append({"I": phase, "A": featured_5, "B": featured_4})
    target["P"] = phases

    data["_banners"] = rows
    _write_js_assignments(banner_js, data)
    return SyncResult(changed_files=[banner_js], notes=[])


def sync_entity(*, data_root: Path, web_root: Path, game: str, kind: str, entity_id: str) -> SyncResult:
    canonical_path = _entity_file(data_root, game, kind, entity_id)
    if not canonical_path.exists():
        raise FileNotFoundError(f"Canonical entity not found: {canonical_path}")
    payload = read_json(canonical_path)

    if game == "gi" and kind == "character":
        return _sync_gi_character(payload, web_root)
    if game == "sr" and kind == "character":
        return _sync_sr_character(payload, web_root)
    if game == "gi" and kind == "weapon":
        return _sync_gi_weapon(payload, web_root)
    if game == "sr" and kind == "lightcone":
        return _sync_sr_lightcone(payload, web_root)
    if game == "gi" and kind == "artifact":
        return _sync_gi_artifact(payload, web_root)
    if game == "sr" and kind == "relic":
        return _sync_sr_relic(payload, web_root)
    if game == "gi" and kind == "enemy":
        return _sync_gi_enemy(payload, web_root)
    if game == "sr" and kind == "enemy":
        return _sync_sr_enemy(payload, web_root)
    if game == "gi" and kind == "banner":
        return _sync_gi_banner(payload, web_root)
    if game == "sr" and kind == "banner":
        return _sync_sr_banner(payload, web_root)

    raise ValueError(f"Unsupported sync target: {game}:{kind}")


def write_canonical_entity(
    *,
    data_root: Path,
    game: str,
    kind: str,
    entity_id: str,
    payload: dict[str, Any],
) -> Path:
    canonical_path = _entity_file(data_root, game, kind, entity_id)
    write_json(canonical_path, payload)
    return canonical_path
