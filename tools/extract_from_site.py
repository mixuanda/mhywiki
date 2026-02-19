#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from normalize import (
    DataParseError,
    drop_non_combat_fields,
    normalize_id,
    parse_js_assignments,
    parse_js_literal,
    read_json,
    slugify,
    write_json,
)


def _warn(msg: str) -> None:
    print(f"[extract] warning: {msg}")


def _require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Required source file not found: {path}")


def _parse_js_file(path: Path, *, optional: bool = False) -> dict[str, Any]:
    if optional and not path.exists():
        return {}
    try:
        _require_file(path)
        return parse_js_assignments(path)
    except (DataParseError, FileNotFoundError) as exc:
        if optional:
            _warn(str(exc))
            return {}
        raise


def _to_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _string_or_default(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value if value.strip() else default
    if value is None:
        return default
    if isinstance(value, (int, float, bool)):
        return str(value)
    return default


def _string_or_none(value: Any) -> str | None:
    if isinstance(value, str):
        return value or None
    if value is None:
        return None
    if isinstance(value, (int, float, bool)):
        return str(value)
    return None


def _collect_numeric_ids_from_mats(payload: Any) -> set[int]:
    ids: set[int] = set()
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_id = _to_int(key)
            if key_id and key_id > 0:
                ids.add(key_id)
            ids.update(_collect_numeric_ids_from_mats(value))
    elif isinstance(payload, list):
        for item in payload:
            ids.update(_collect_numeric_ids_from_mats(item))
    return ids


def _ensure_unique_slug(base: str, seen: set[str]) -> str:
    if base not in seen:
        seen.add(base)
        return base
    index = 2
    while f"{base}-{index}" in seen:
        index += 1
    value = f"{base}-{index}"
    seen.add(value)
    return value


def _extract_inline_js_var(js_path: Path, var_name: str) -> Any:
    text = js_path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(rf"\bvar\s+{re.escape(var_name)}\s*=", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        raise DataParseError(f"Inline JS var `{var_name}` not found in {js_path}")

    index = match.end()
    while index < len(text) and text[index].isspace():
        index += 1
    if index >= len(text):
        raise DataParseError(f"Inline JS var `{var_name}` has no value in {js_path}")

    first = text[index]
    if first not in "[{":
        end = text.find(";", index)
        if end == -1:
            end = len(text)
        expr = text[index:end].strip()
        return parse_js_literal(expr, context=f"{js_path}:{var_name}")

    stack = [first]
    close_for = {"[": "]", "{": "}"}
    i = index + 1
    in_string = False
    quote_char = ""
    escape = False

    while i < len(text):
        char = text[i]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote_char:
                in_string = False
            i += 1
            continue

        if char in "'\"":
            in_string = True
            quote_char = char
            i += 1
            continue

        if char in "[{":
            stack.append(char)
        elif char in "]}":
            if not stack:
                raise DataParseError(f"Unexpected token while parsing {js_path}:{var_name}")
            opening = stack.pop()
            if close_for[opening] != char:
                raise DataParseError(f"Unbalanced token while parsing {js_path}:{var_name}")
            if not stack:
                expr = text[index : i + 1]
                return parse_js_literal(expr, context=f"{js_path}:{var_name}")
        i += 1

    raise DataParseError(f"Failed to parse inline JS var `{var_name}` in {js_path}")


def _safe_remove_tree(path: Path) -> None:
    try:
        shutil.rmtree(path)
        return
    except OSError:
        # Cloud-synced folders can transiently race rmtree with metadata writes.
        subprocess.run(["rm", "-rf", str(path)], check=True)
    if path.exists():
        raise OSError(f"Unable to clean output directory: {path}")


def _write_entities(directory: Path, entities: dict[str, Any]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for entity_id, payload in entities.items():
        write_json(directory / f"{entity_id}.json", payload)


def _write_index(directory: Path, *, skip_prefix: str = "_") -> None:
    rows: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        if path.name == "index.json":
            continue
        if skip_prefix and path.stem.startswith(skip_prefix):
            continue
        try:
            data = read_json(path)
        except json.JSONDecodeError:
            continue

        if isinstance(data, dict):
            rows.append(
                {
                    "id": data.get("id", path.stem),
                    "name": data.get("name") or data.get("title") or path.stem,
                    "path": path.name,
                }
            )
        else:
            rows.append({"id": path.stem, "name": path.stem, "path": path.name})

    write_json(directory / "index.json", rows)


def _extract_gi(site_root: Path, out_root: Path, locale: str) -> dict[str, Any]:
    gi_root = site_root / "gi" / locale
    avatar_vars = _parse_js_file(gi_root / "avatar.js")
    database_vars = _parse_js_file(gi_root / "database.js")
    database_extra_vars = _parse_js_file(gi_root / "database_extra.js", optional=True)
    computer_vars = _parse_js_file(gi_root / "computer.js")
    bosschallenge_vars = _parse_js_file(gi_root / "bosschallenge.js", optional=True)
    maze_vars = _parse_js_file(gi_root / "maze.js", optional=True)
    achievement_vars = _parse_js_file(gi_root / "ach.js", optional=True)
    tutorial_vars = _parse_js_file(gi_root / "tut_1.js", optional=True)
    banner_vars = _parse_js_file(site_root / "gi" / "banner.js", optional=True)
    yhb_vars = _parse_js_file(site_root / "javascripts" / "yhb_data.js", optional=True)

    formulae_data = _extract_inline_js_var(site_root / "javascripts" / "formulae_gi.js", "data")
    formulae_data_en = _extract_inline_js_var(site_root / "javascripts" / "formulae_gi.js", "stuff")

    characters_dir = out_root / "characters"
    weapons_dir = out_root / "weapons"
    artifacts_dir = out_root / "artifacts"
    enemies_dir = out_root / "enemies"
    materials_dir = out_root / "materials"
    abyss_dir = out_root / "endgame" / "abyss"
    theater_dir = out_root / "endgame" / "theater"
    youjing_dir = out_root / "endgame" / "youjing"
    banners_dir = out_root / "banners"
    effects_dir = out_root / "glossary" / "effects"
    terms_dir = out_root / "glossary" / "terms"
    achievements_dir = out_root / "achievements"
    tutorials_dir = out_root / "tutorials"
    change_summary_dir = out_root / "change_summary"
    formulae_dir = out_root / "formulae"
    donor_credits_dir = out_root / "donor_credits"

    material_refs: set[int] = set()

    gi_chars = avatar_vars.get("__AvatarInfoConfig", [])
    for row in gi_chars:
        code = str(row.get("_name", "")).strip()
        character_id = normalize_id(row.get("_id", code))

        detail_1 = _parse_js_file(gi_root / "Avatar" / f"{code}_1.js", optional=True)
        detail_2 = _parse_js_file(gi_root / "Avatar" / f"{code}_2.js", optional=True)

        detail_data = drop_non_combat_fields(
            {
                "detail_1": detail_1,
                "detail_2": detail_2,
            }
        )

        mats_raw = ((detail_1.get("_AvatarMats_") or {}).get(code) or {}) if detail_1 else {}
        mats_ids = _collect_numeric_ids_from_mats(mats_raw)

        for key in ("CommonMatt", "TalentMatt", "SpecialityMat", "AscMat", "WeekMat"):
            mat_id = _to_int(row.get(key))
            if mat_id and mat_id > 0:
                mats_ids.add(mat_id)

        material_refs.update(mats_ids)

        payload = {
            "id": character_id,
            "game": "gi",
            "entityType": "character",
            "name": row.get("Name", code),
            "codeName": code,
            "title": row.get("Title", ""),
            "description": row.get("Desc", ""),
            "version": row.get("Version"),
            "rarity": row.get("Grade"),
            "element": row.get("Element"),
            "weaponType": row.get("Weapon"),
            "nation": row.get("Nation"),
            "affiliation": row.get("Belong"),
            "baseStats": row.get("ShowStats", {}),
            "maxStats": row.get("ShowStats2", {}),
            "materialRefs": sorted(str(x) for x in mats_ids),
            "combat": detail_data,
            "source": {
                "listFile": f"gi/{locale}/avatar.js",
                "detailFiles": [
                    f"gi/{locale}/Avatar/{code}_1.js",
                    f"gi/{locale}/Avatar/{code}_2.js",
                ],
            },
        }
        write_json(characters_dir / f"{character_id}.json", payload)

    weapon_rows = avatar_vars.get("_WeaponConfig", [])
    for row in weapon_rows:
        weapon_id = normalize_id(row.get("_id"))
        detail = _parse_js_file(gi_root / "Weapon" / f"{weapon_id}.js", optional=True)
        mats = set()
        asc = _to_int(row.get("AscMatID"))
        if asc and asc > 0:
            mats.add(asc)
        for value in row.get("MatIDs", []) or []:
            mat_id = _to_int(value)
            if mat_id and mat_id > 0:
                mats.add(mat_id)
        material_refs.update(mats)

        payload = {
            "id": weapon_id,
            "game": "gi",
            "entityType": "weapon",
            "name": row.get("Name", weapon_id),
            "description": row.get("Desc", ""),
            "rarity": row.get("Rank"),
            "weaponType": row.get("Type"),
            "baseAtk": row.get("Stat"),
            "subStatType": row.get("Custom"),
            "subStatValue": row.get("CustomStat"),
            "materialRefs": sorted(str(x) for x in mats),
            "affix": drop_non_combat_fields(detail.get("_WeaponAffixPConfig_", {})),
            "source": {
                "listFile": f"gi/{locale}/avatar.js",
                "detailFile": f"gi/{locale}/Weapon/{weapon_id}.js",
            },
        }
        write_json(weapons_dir / f"{weapon_id}.json", payload)

    artifact_rows = avatar_vars.get("_RelicConfig", [])
    for row in artifact_rows:
        artifact_id = normalize_id(row.get("ID"))
        payload = {
            "id": artifact_id,
            "game": "gi",
            "entityType": "artifact",
            "name": row.get("Name", artifact_id),
            "icon": row.get("Icon"),
            "setBonuses": row.get("Skills", []),
            "parts": row.get("Parts", []),
            "extra": row.get("Extra", []),
            "source": {"listFile": f"gi/{locale}/avatar.js"},
        }
        write_json(artifacts_dir / f"{artifact_id}.json", payload)

    monsters: dict[str, dict[str, Any]] = {}
    for source_monsters in [computer_vars.get("_Monsters", {}), database_vars.get("_Monsters", {})]:
        if not isinstance(source_monsters, dict):
            continue
        for mid, payload in source_monsters.items():
            monsters[str(mid)] = drop_non_combat_fields(payload)

    bosschallenge_monsters = bosschallenge_vars.get("BossChallenge_Monsters", {})
    if isinstance(bosschallenge_monsters, dict):
        for mid, payload in bosschallenge_monsters.items():
            data = drop_non_combat_fields(payload)
            data.setdefault("_id", _to_int(mid) or mid)
            monsters[str(mid)] = data

    groups_by_monster: dict[str, list[str]] = {}
    for kingdom in computer_vars.get("_Kingdoms", []) or []:
        kingdom_name = kingdom.get("Name", "")
        for class_info in kingdom.get("Classes", []) or []:
            class_name = class_info.get("Name", "")
            label = " > ".join([x for x in [kingdom_name, class_name] if x])
            for monster_id in class_info.get("Monsters", []) or []:
                key = normalize_id(monster_id)
                groups_by_monster.setdefault(key, []).append(label)

    bossguides: dict[str, Any] = {}
    for source in [computer_vars.get("_bossguide", {}), database_vars.get("_bossguide", {})]:
        if isinstance(source, dict):
            for key, value in source.items():
                bossguides[normalize_id(key)] = value

    for monster_id, payload in monsters.items():
        data = {
            "id": normalize_id(payload.get("_id", monster_id)),
            "game": "gi",
            "entityType": "enemy",
            "name": _string_or_default(payload.get("Name"), normalize_id(payload.get("_id", monster_id))),
            "description": _string_or_none(payload.get("Desc")),
            "stats": payload.get("Stats", {}),
            "resistance": payload.get("RESBase", {}),
            "weakness": payload.get("Weak", []),
            "icon": payload.get("Icon"),
            "figure": payload.get("Figure"),
            "groups": sorted(set(groups_by_monster.get(monster_id, []))),
            "analysis": bossguides.get(monster_id),
            "source": {
                "files": [
                    f"gi/{locale}/computer.js",
                    f"gi/{locale}/database.js",
                    f"gi/{locale}/bosschallenge.js",
                ]
            },
        }
        write_json(enemies_dir / f"{data['id']}.json", data)

    material_map = avatar_vars.get("_MaterialConfig", {})
    for mat_id in sorted(material_refs):
        raw = material_map.get(str(mat_id), material_map.get(mat_id))
        if isinstance(raw, dict):
            name = _string_or_default(raw.get("Name") or raw.get("name"), str(mat_id))
            icon = raw.get("Icon")
            desc = _string_or_none(raw.get("Desc") or raw.get("description"))
        else:
            name = _string_or_default(raw, str(mat_id))
            icon = None
            desc = None

        write_json(
            materials_dir / f"{mat_id}.json",
            {
                "id": str(mat_id),
                "game": "gi",
                "entityType": "material",
                "name": name,
                "icon": icon,
                "description": desc,
                "source": {"file": f"gi/{locale}/avatar.js"},
            },
        )

    floors = database_vars.get("_SpiralAbyssFloorConfig", {})
    floors_extra = database_extra_vars.get("_SpiralAbyssFloorConfig_2", {})
    if isinstance(floors, dict) and isinstance(floors_extra, dict):
        floors = {**floors, **floors_extra}

    blessings = database_vars.get("_SpiralAbyssBlessingConfig", {})
    abyss_seen: set[str] = set()
    for index, cycle in enumerate(database_vars.get("_SpiralAbyssSchedule", []) or []):
        base_id = slugify(str(cycle.get("Name", f"cycle-{index + 1}")))
        cycle_id = _ensure_unique_slug(base_id, abyss_seen)
        floor_data = []
        for floor_id in cycle.get("Floors", []) or []:
            floor_key = str(floor_id)
            floor_data.append(
                {
                    "floorId": floor_key,
                    "config": floors.get(floor_key, floors.get(floor_id, {})),
                }
            )
        blessing_data = []
        for blessing_id in cycle.get("Blessings", []) or []:
            blessing_key = str(blessing_id)
            blessing_data.append(
                {
                    "blessingId": blessing_key,
                    "config": blessings.get(blessing_key, blessings.get(blessing_id, {})),
                }
            )

        write_json(
            abyss_dir / f"{cycle_id}.json",
            {
                "id": cycle_id,
                "game": "gi",
                "entityType": "endgameCycle",
                "mode": "abyss",
                "name": cycle.get("Name", cycle_id),
                "openTime": cycle.get("OpenTime"),
                "generation": cycle.get("Generation"),
                "phases": cycle.get("Phases", []),
                "floors": floor_data,
                "blessings": blessing_data,
                "source": {"files": [f"gi/{locale}/database.js", f"gi/{locale}/database_extra.js"]},
            },
        )

    theater_shared = {
        "groups": maze_vars.get("_groups", []),
        "blessings": maze_vars.get("_blessings", []),
        "slips": maze_vars.get("_slips", []),
        "monsters": maze_vars.get("_mons", {}),
        "monsterDescriptions": maze_vars.get("_mon_desc", {}),
        "talentLevels": maze_vars.get("_tl", []),
        "poses": maze_vars.get("_poses", []),
        "tarot": maze_vars.get("_tarot", []),
    }
    write_json(theater_dir / "_shared.json", theater_shared)

    theater_seen: set[str] = set()
    overall = maze_vars.get("_overall", [])
    plane = maze_vars.get("_plane", [])
    for index, season in enumerate(overall):
        version = None
        hp_profile = None
        if index < len(plane) and isinstance(plane[index], dict):
            version = plane[index].get("Ver")
            hp_profile = plane[index]
        base_id = slugify(str(version or season.get("Time") or f"season-{index + 1}"))
        season_id = _ensure_unique_slug(base_id, theater_seen)

        write_json(
            theater_dir / f"{season_id}.json",
            {
                "id": season_id,
                "game": "gi",
                "entityType": "endgameCycle",
                "mode": "theater",
                "name": f"{version or season_id}",
                "version": version,
                "time": season.get("Time"),
                "elements": season.get("Elem", []),
                "initialCast": season.get("Initial", []),
                "invitationCast": season.get("Invitation", []),
                "chambers": season.get("Chambers", []),
                "hpProfile": hp_profile,
                "shared": "_shared.json",
                "source": {"file": f"gi/{locale}/maze.js"},
            },
        )

    for cycle in bosschallenge_vars.get("BossChallenge_Schedule", []) or []:
        cycle_id = slugify(str(cycle.get("Ver", cycle.get("Name", "youjing"))))
        levels = []
        for level in cycle.get("Levels", []) or []:
            monsters_data = []
            for monster_id in level.get("Monsters", []) or []:
                monster_key = normalize_id(monster_id)
                monsters_data.append(
                    {
                        "id": monster_key,
                        "data": bosschallenge_monsters.get(monster_key, bosschallenge_monsters.get(monster_id, {})),
                    }
                )
            levels.append(
                {
                    "level": level.get("Level"),
                    "monsters": monsters_data,
                }
            )

        write_json(
            youjing_dir / f"{cycle_id}.json",
            {
                "id": cycle_id,
                "game": "gi",
                "entityType": "endgameCycle",
                "mode": "youjing",
                "name": cycle.get("Name", cycle_id),
                "version": cycle.get("Ver"),
                "time": cycle.get("Time"),
                "levels": levels,
                "source": {"file": f"gi/{locale}/bosschallenge.js"},
            },
        )

    banner_seen: set[str] = set()
    for version in banner_vars.get("_banners", []) or []:
        ver_name = str(version.get("V", "unknown"))
        for idx, phase in enumerate(version.get("P", []) or [], start=1):
            phase_num = phase.get("_id", idx)
            banner_id = _ensure_unique_slug(slugify(f"{ver_name}-phase-{phase_num}"), banner_seen)
            write_json(
                banners_dir / f"{banner_id}.json",
                {
                    "id": banner_id,
                    "game": "gi",
                    "entityType": "banner",
                    "version": ver_name,
                    "phase": phase_num,
                    "featuredFiveStar": phase.get("A", []),
                    "featuredFourStar": phase.get("B", []),
                    "source": {"file": "gi/banner.js"},
                },
            )

    achievement_groups = {
        str(row.get("ID")): row for row in achievement_vars.get("_AchievementGroup", []) or []
    }
    for row in achievement_vars.get("_Achievement", []) or []:
        aid = normalize_id(row.get("ID", row.get("_id")))
        gid = normalize_id(row.get("Group", "")) if row.get("Group") is not None else None
        write_json(
            achievements_dir / f"{aid}.json",
            {
                "id": aid,
                "game": "gi",
                "entityType": "achievement",
                "name": row.get("Name", aid),
                "description": row.get("Desc", ""),
                "reward": row.get("Reward"),
                "version": row.get("Ver"),
                "group": achievement_groups.get(gid, {"id": gid} if gid else None),
                "source": {"file": f"gi/{locale}/ach.js"},
            },
        )

    for row in tutorial_vars.get("_tut_1", []) or []:
        tid = normalize_id(row.get("_id", row.get("ID", slugify(str(row.get("Name", "tutorial"))))))
        write_json(
            tutorials_dir / f"{tid}.json",
            {
                "id": tid,
                "game": "gi",
                "entityType": "tutorial",
                "name": row.get("Name", tid),
                "tags": row.get("Tag", []),
                "content": row,
                "source": {"file": f"gi/{locale}/tut_1.js"},
            },
        )

    char_index = read_json(site_root / "Char" / "GI.json")
    for row in char_index:
        sid = slugify(str(row.get("N", "entry")))
        write_json(
            change_summary_dir / f"{sid}.json",
            {
                "id": sid,
                "game": "gi",
                "entityType": "changeSummary",
                "name": row.get("N"),
                "versions": row.get("V", []),
                "source": {"file": "Char/GI.json"},
            },
        )

    write_json(
        change_summary_dir / "_avatar_changelog.json",
        {
            "id": "avatar-changelog",
            "game": "gi",
            "entityType": "changeSummary",
            "changelog": avatar_vars.get("_changelog", {}),
            "relicChangelog": avatar_vars.get("_relic_changelog", {}),
            "awc": drop_non_combat_fields(avatar_vars.get("_awc", {})),
            "source": {"file": f"gi/{locale}/avatar.js"},
        },
    )

    formula_seen: set[str] = set()
    for row in formulae_data:
        fid = _ensure_unique_slug(slugify(str(row.get("Title", "formula"))), formula_seen)
        write_json(
            formulae_dir / f"{fid}.json",
            {
                "id": fid,
                "game": "gi",
                "entityType": "formula",
                "language": "CH",
                "title": row.get("Title", fid),
                "subtitle": row.get("Subtitle"),
                "content": row.get("DescList", []),
                "source": {"file": "javascripts/formulae_gi.js"},
            },
        )

    for row in formulae_data_en:
        fid = _ensure_unique_slug(slugify(f"en-{row.get('Title', 'formula')}"), formula_seen)
        write_json(
            formulae_dir / f"{fid}.json",
            {
                "id": fid,
                "game": "gi",
                "entityType": "formula",
                "language": "EN",
                "title": row.get("Title", fid),
                "subtitle": row.get("Subtitle"),
                "content": row.get("DescList", []),
                "source": {"file": "javascripts/formulae_gi.js"},
            },
        )

    write_json(
        donor_credits_dir / "index.json",
        {
            "id": "donor-credits",
            "game": "gi",
            "entityType": "donorCredits",
            "notes": "Legacy page content kept as-is from yhb data source",
            "content": yhb_vars,
            "source": {"file": "javascripts/yhb_data.js"},
        },
    )

    write_json(effects_dir / "index.json", [])
    write_json(terms_dir / "index.json", [])

    for path in [
        characters_dir,
        weapons_dir,
        artifacts_dir,
        enemies_dir,
        materials_dir,
        abyss_dir,
        theater_dir,
        youjing_dir,
        banners_dir,
        achievements_dir,
        tutorials_dir,
        change_summary_dir,
        formulae_dir,
    ]:
        _write_index(path)

    return {
        "characters": len(list(characters_dir.glob("*.json"))) - 1,
        "weapons": len(list(weapons_dir.glob("*.json"))) - 1,
        "artifacts": len(list(artifacts_dir.glob("*.json"))) - 1,
        "enemies": len(list(enemies_dir.glob("*.json"))) - 1,
        "materials": len(list(materials_dir.glob("*.json"))) - 1,
        "abyssCycles": len(list(abyss_dir.glob("*.json"))) - 1,
        "theaterSeasons": len(list(theater_dir.glob("*.json"))) - 2,
        "youjingCycles": len(list(youjing_dir.glob("*.json"))) - 1,
        "banners": len(list(banners_dir.glob("*.json"))) - 1,
    }


def _extract_sr(site_root: Path, out_root: Path, locale: str) -> dict[str, Any]:
    data_root = site_root / "data" / locale
    avatar_vars = _parse_js_file(data_root / "Avatar.js")
    monster_1_vars = _parse_js_file(data_root / "Monster_1.js")
    monster_2_vars = _parse_js_file(data_root / "Monster_2.js", optional=True)
    chaos_1_vars = _parse_js_file(data_root / "Chaos_1.js")
    chaos_2_vars = _parse_js_file(data_root / "Chaos_2.js", optional=True)
    fiction_1_vars = _parse_js_file(data_root / "Fiction_1.js")
    fiction_2_vars = _parse_js_file(data_root / "Fiction_2.js", optional=True)
    as_vars = _parse_js_file(data_root / "AS.js")
    ar_vars = _parse_js_file(data_root / "AR.js")
    du_27_vars = _parse_js_file(data_root / "BlessingDU.js")
    du_38_vars = _parse_js_file(data_root / "BlessingDU31.js")
    achievement_vars = _parse_js_file(data_root / "Achievement.js")
    linecount_vars = _parse_js_file(data_root / "LineCount.js")
    stage_vars = _parse_js_file(site_root / "data" / "Stage.js")
    banner_vars = _parse_js_file(site_root / "data" / "banner.js")
    ems_vars = _parse_js_file(data_root / "EMS.js")

    formulae_data = _extract_inline_js_var(site_root / "javascripts" / "formulae_sr.js", "data")

    characters_dir = out_root / "characters"
    lightcones_dir = out_root / "lightcones"
    relics_dir = out_root / "relics"
    enemies_dir = out_root / "enemies"
    materials_dir = out_root / "materials"
    moc_dir = out_root / "endgame" / "moc"
    purefiction_dir = out_root / "endgame" / "purefiction"
    apocalypticshadow_dir = out_root / "endgame" / "apocalypticshadow"
    yixiang_dir = out_root / "endgame" / "yixiangzhongcai"
    du27_dir = out_root / "endgame" / "divergentuniverse" / "2.7"
    du38_dir = out_root / "endgame" / "divergentuniverse" / "3.8"
    banners_dir = out_root / "banners"
    effects_dir = out_root / "glossary" / "effects"
    terms_dir = out_root / "glossary" / "terms"
    achievements_dir = out_root / "achievements"
    stages_dir = out_root / "stages"
    change_summary_dir = out_root / "change_summary"
    future_intel_dir = out_root / "future_intel"
    formulae_dir = out_root / "formulae"
    dialogue_stats_dir = out_root / "dialogue_line_stats"

    material_refs: set[int] = set()

    for row in avatar_vars.get("_avatar", []) or []:
        char_id = normalize_id(row.get("_id"))
        detail = _parse_js_file(data_root / "Avatar" / f"{char_id}.js", optional=True)
        mats = set()
        for value in row.get("Mat", []) or []:
            mat_id = _to_int(value)
            if mat_id and mat_id > 0:
                mats.add(mat_id)
        material_refs.update(mats)

        payload = {
            "id": char_id,
            "game": "sr",
            "entityType": "character",
            "name": row.get("Name", char_id),
            "description": row.get("Desc", ""),
            "version": row.get("Ver"),
            "rarity": row.get("Rarity"),
            "element": row.get("Element"),
            "path": row.get("Path"),
            "baseStats": row.get("Stats", {}),
            "materialRefs": sorted(str(x) for x in mats),
            "combat": drop_non_combat_fields(detail),
            "source": {
                "listFile": f"data/{locale}/Avatar.js",
                "detailFile": f"data/{locale}/Avatar/{char_id}.js",
            },
        }
        write_json(characters_dir / f"{char_id}.json", payload)

    for row in avatar_vars.get("_weapon", []) or []:
        lc_id = normalize_id(row.get("_id"))
        detail = _parse_js_file(data_root / "Weapon" / f"{lc_id}.js", optional=True)
        mats = set()
        for value in row.get("Mat", []) or []:
            mat_id = _to_int(value)
            if mat_id and mat_id > 0:
                mats.add(mat_id)
        material_refs.update(mats)

        payload = {
            "id": lc_id,
            "game": "sr",
            "entityType": "lightcone",
            "name": row.get("Name", lc_id),
            "rarity": row.get("Rarity"),
            "path": row.get("Path"),
            "skillId": row.get("Skill"),
            "baseStats": row.get("Stats", {}),
            "materialRefs": sorted(str(x) for x in mats),
            "detail": drop_non_combat_fields(detail),
            "source": {
                "listFile": f"data/{locale}/Avatar.js",
                "detailFile": f"data/{locale}/Weapon/{lc_id}.js",
            },
        }
        write_json(lightcones_dir / f"{lc_id}.json", payload)

    for row in avatar_vars.get("_relic", []) or []:
        relic_id = normalize_id(row.get("_id"))
        detail = _parse_js_file(data_root / "Relic" / f"{relic_id}.js", optional=True)
        payload = {
            "id": relic_id,
            "game": "sr",
            "entityType": "relic",
            "name": row.get("Name", relic_id),
            "icon": row.get("Icon"),
            "setBonuses": row.get("Skills", []),
            "detail": drop_non_combat_fields(detail),
            "source": {
                "listFile": f"data/{locale}/Avatar.js",
                "detailFile": f"data/{locale}/Relic/{relic_id}.js",
            },
        }
        write_json(relics_dir / f"{relic_id}.json", payload)

    monsters = {}
    for source in [monster_1_vars.get("_monster", {}), monster_2_vars.get("_monster_2", {})]:
        if not isinstance(source, dict):
            continue
        for mid, payload in source.items():
            monsters[str(mid)] = drop_non_combat_fields(payload)

    kingdoms = {}
    for row in monster_1_vars.get("_kingdoms", []) or []:
        kid = normalize_id(row.get("_id"))
        kingdoms[kid] = row.get("Name")

    sr_bossguide = monster_1_vars.get("_bossguide", {}) if isinstance(monster_1_vars.get("_bossguide"), dict) else {}

    for mid, payload in monsters.items():
        camp_id = normalize_id(payload.get("Camp", "")) if payload.get("Camp") is not None else None
        data = {
            "id": normalize_id(payload.get("_id", mid)),
            "game": "sr",
            "entityType": "enemy",
            "name": _string_or_default(payload.get("Name"), normalize_id(payload.get("_id", mid))),
            "description": _string_or_none(payload.get("Desc")),
            "stats": payload.get("Stats", {}),
            "weakness": payload.get("Weak", []),
            "resistance": payload.get("RESBase", {}),
            "statusResist": payload.get("StatusRESBase"),
            "icon": payload.get("Icon"),
            "figure": payload.get("Figure"),
            "camp": {
                "id": camp_id,
                "name": kingdoms.get(camp_id),
            }
            if camp_id
            else None,
            "analysis": sr_bossguide.get(str(payload.get("_id", mid))),
            "source": {
                "files": [f"data/{locale}/Monster_1.js", f"data/{locale}/Monster_2.js"],
            },
        }
        write_json(enemies_dir / f"{data['id']}.json", data)

    material_map = avatar_vars.get("_item", {})
    for mat_id in sorted(material_refs):
        raw = material_map.get(str(mat_id), material_map.get(mat_id))
        if isinstance(raw, dict):
            name = _string_or_default(raw.get("Name"), str(mat_id))
            icon = raw.get("Icon")
        else:
            name = _string_or_default(raw, str(mat_id))
            icon = None
        write_json(
            materials_dir / f"{mat_id}.json",
            {
                "id": str(mat_id),
                "game": "sr",
                "entityType": "material",
                "name": name,
                "icon": icon,
                "source": {"file": f"data/{locale}/Avatar.js"},
            },
        )

    def write_endgame_cycles(directory: Path, mode: str, rows: list[dict[str, Any]], source_files: list[str]) -> None:
        seen: set[str] = set()
        for index, cycle in enumerate(rows):
            cid = normalize_id(cycle.get("_id", f"{mode}-{index + 1}"))
            cid = _ensure_unique_slug(slugify(cid), seen)
            write_json(
                directory / f"{cid}.json",
                {
                    "id": cid,
                    "game": "sr",
                    "entityType": "endgameCycle",
                    "mode": mode,
                    "name": cycle.get("Name", cid),
                    "content": cycle,
                    "source": {"files": source_files},
                },
            )

    write_endgame_cycles(
        moc_dir,
        "moc",
        [*(chaos_1_vars.get("_chaos", []) or []), *(chaos_2_vars.get("_chaos_2", []) or [])],
        [f"data/{locale}/Chaos_1.js", f"data/{locale}/Chaos_2.js"],
    )

    write_endgame_cycles(
        purefiction_dir,
        "purefiction",
        [*(fiction_1_vars.get("_fiction", []) or []), *(fiction_2_vars.get("_fiction_2", []) or [])],
        [f"data/{locale}/Fiction_1.js", f"data/{locale}/Fiction_2.js"],
    )

    write_endgame_cycles(
        apocalypticshadow_dir,
        "apocalypticshadow",
        as_vars.get("_chaos", []) or [],
        [f"data/{locale}/AS.js"],
    )

    schedule = ar_vars.get("_schedule", []) or []
    maze_map = ar_vars.get("_maze", {}) or {}
    for row in schedule:
        cycle_id = normalize_id(row.get("_id"))
        content = maze_map.get(str(row.get("_id")), maze_map.get(row.get("_id"), {}))
        write_json(
            yixiang_dir / f"{cycle_id}.json",
            {
                "id": cycle_id,
                "game": "sr",
                "entityType": "endgameCycle",
                "mode": "yixiangzhongcai",
                "name": row.get("Name", cycle_id),
                "time": row.get("Time"),
                "content": content,
                "source": {"file": f"data/{locale}/AR.js"},
            },
        )

    for weekly in du_27_vars.get("_weekly", []) or []:
        cid = normalize_id(weekly.get("_id"))
        write_json(
            du27_dir / f"{cid}.json",
            {
                "id": cid,
                "game": "sr",
                "entityType": "endgameCycle",
                "mode": "divergentuniverse",
                "version": "2.7",
                "name": weekly.get("Name", cid),
                "content": weekly,
                "shared": {
                    "blessings": du_27_vars.get("_blessing", []),
                    "blessingTypes": du_27_vars.get("_blessingtypes", []),
                    "blessingExtra": du_27_vars.get("_blessingextra", {}),
                    "curios": du_27_vars.get("_curio", []),
                    "protocols": du_27_vars.get("_protocols", []),
                    "keywords": du_27_vars.get("_keyword", []),
                },
                "source": {"file": f"data/{locale}/BlessingDU.js"},
            },
        )

    for weekly in du_38_vars.get("_weekly", []) or []:
        cid = normalize_id(weekly.get("_id"))
        write_json(
            du38_dir / f"{cid}.json",
            {
                "id": cid,
                "game": "sr",
                "entityType": "endgameCycle",
                "mode": "divergentuniverse",
                "version": "3.8",
                "name": weekly.get("Name", cid),
                "content": weekly,
                "shared": {
                    "blessings": du_38_vars.get("_blessing", []),
                    "blessingTypes": du_38_vars.get("_blessingtypes", []),
                    "blessingExtra": du_38_vars.get("_blessingextra", {}),
                    "curios": du_38_vars.get("_curio", []),
                    "protocols": du_38_vars.get("_protocols", []),
                    "keywords": du_38_vars.get("_keyword", []),
                    "titans": du_38_vars.get("_titan", []),
                },
                "source": {"file": f"data/{locale}/BlessingDU31.js"},
            },
        )

    banner_seen: set[str] = set()
    for version in banner_vars.get("_banners", []) or []:
        ver_name = str(version.get("V", "unknown"))
        for index, phase in enumerate(version.get("P", []) or [], start=1):
            phase_num = phase.get("I", index)
            banner_id = _ensure_unique_slug(slugify(f"{ver_name}-phase-{phase_num}"), banner_seen)
            write_json(
                banners_dir / f"{banner_id}.json",
                {
                    "id": banner_id,
                    "game": "sr",
                    "entityType": "banner",
                    "version": ver_name,
                    "phase": phase_num,
                    "featuredFiveStar": phase.get("A", []),
                    "featuredFourStar": phase.get("B", []),
                    "source": {"file": "data/banner.js"},
                },
            )

    forbidden = {str(x) for x in (ems_vars.get("_forbid", []) or [])}
    for row in ems_vars.get("_as", []) or []:
        effect_id = normalize_id(row.get("_id"))
        if effect_id in forbidden:
            continue
        write_json(
            effects_dir / f"{effect_id}.json",
            {
                "id": effect_id,
                "game": "sr",
                "entityType": "glossaryEffect",
                "name": _string_or_default(row.get("Name"), effect_id),
                "description": _string_or_none(row.get("Desc")),
                "effectType": "character",
                "content": row,
                "source": {"file": f"data/{locale}/EMS.js"},
            },
        )

    for row in ems_vars.get("_ms", []) or []:
        effect_id = normalize_id(row.get("_id"))
        if effect_id in forbidden:
            continue
        write_json(
            effects_dir / f"{effect_id}.json",
            {
                "id": effect_id,
                "game": "sr",
                "entityType": "glossaryEffect",
                "name": _string_or_default(row.get("Name"), effect_id),
                "description": _string_or_none(row.get("Desc")),
                "effectType": "monster",
                "content": row,
                "source": {"file": f"data/{locale}/EMS.js"},
            },
        )

    for row in ems_vars.get("_ee", []) or []:
        term_id = normalize_id(row.get("_id"))
        if term_id in forbidden:
            continue
        write_json(
            terms_dir / f"{term_id}.json",
            {
                "id": term_id,
                "game": "sr",
                "entityType": "glossaryTerm",
                "name": _string_or_default(row.get("Name"), term_id),
                "description": _string_or_none(row.get("Desc")),
                "content": row,
                "source": {"file": f"data/{locale}/EMS.js"},
            },
        )

    series = {str(row.get("_id")): row for row in achievement_vars.get("_achievementseries", []) or []}
    for row in achievement_vars.get("_achievement", []) or []:
        aid = normalize_id(row.get("_id"))
        sid = normalize_id(row.get("Series"))
        write_json(
            achievements_dir / f"{aid}.json",
            {
                "id": aid,
                "game": "sr",
                "entityType": "achievement",
                "name": row.get("Name", aid),
                "description": row.get("Desc", ""),
                "reward": row.get("Reward"),
                "version": row.get("Ver"),
                "series": series.get(sid, {"id": sid}),
                "source": {"file": f"data/{locale}/Achievement.js"},
            },
        )

    for stage_id, row in (stage_vars.get("_stage", {}) or {}).items():
        sid = normalize_id(stage_id)
        write_json(
            stages_dir / f"{sid}.json",
            {
                "id": sid,
                "game": "sr",
                "entityType": "stage",
                "level": row.get("Level"),
                "enemyGroup": row.get("EG"),
                "waves": row.get("Mons", []),
                "source": {"file": "data/Stage.js"},
            },
        )

    for row in linecount_vars.get("_data", []) or []:
        ver = str(row.get("Ver", "unknown"))
        sid = slugify(ver)
        write_json(
            dialogue_stats_dir / f"{sid}.json",
            {
                "id": sid,
                "game": "sr",
                "entityType": "dialogueLineStats",
                "version": ver,
                "talk": row.get("Talk", {}),
                "roles": row.get("Roles", {}),
                "source": {"file": f"data/{locale}/LineCount.js"},
            },
        )

    sr_char_index = read_json(site_root / "Char" / "HSR.json")
    for row in sr_char_index:
        sid = slugify(str(row.get("N", "entry")))
        payload = {
            "id": sid,
            "game": "sr",
            "entityType": "futureIntel",
            "name": row.get("N"),
            "versions": row.get("V", []),
            "source": {"file": "Char/HSR.json"},
        }
        write_json(future_intel_dir / f"{sid}.json", payload)

    write_json(
        change_summary_dir / "avatar_changelog.json",
        {
            "id": "avatar-changelog",
            "game": "sr",
            "entityType": "changeSummary",
            "avatarChangelog": avatar_vars.get("_changelog_avatar", {}),
            "relicChangelog": avatar_vars.get("_changelog_relic", {}),
            "versionAdditions": avatar_vars.get("_changelog_veradd", {}),
            "source": {"file": f"data/{locale}/Avatar.js"},
        },
    )

    for row in formulae_data:
        fid = slugify(str(row.get("Title", "formula")))
        write_json(
            formulae_dir / f"{fid}.json",
            {
                "id": fid,
                "game": "sr",
                "entityType": "formula",
                "language": "CH",
                "title": row.get("Title", fid),
                "subtitle": row.get("Subtitle"),
                "content": row.get("DescList", []),
                "source": {"file": "javascripts/formulae_sr.js"},
            },
        )

    for path in [
        characters_dir,
        lightcones_dir,
        relics_dir,
        enemies_dir,
        materials_dir,
        moc_dir,
        purefiction_dir,
        apocalypticshadow_dir,
        yixiang_dir,
        du27_dir,
        du38_dir,
        banners_dir,
        effects_dir,
        terms_dir,
        achievements_dir,
        stages_dir,
        change_summary_dir,
        future_intel_dir,
        formulae_dir,
        dialogue_stats_dir,
    ]:
        _write_index(path)

    return {
        "characters": len(list(characters_dir.glob("*.json"))) - 1,
        "lightcones": len(list(lightcones_dir.glob("*.json"))) - 1,
        "relics": len(list(relics_dir.glob("*.json"))) - 1,
        "enemies": len(list(enemies_dir.glob("*.json"))) - 1,
        "materials": len(list(materials_dir.glob("*.json"))) - 1,
        "mocCycles": len(list(moc_dir.glob("*.json"))) - 1,
        "pureFictionCycles": len(list(purefiction_dir.glob("*.json"))) - 1,
        "apocalypticShadowCycles": len(list(apocalypticshadow_dir.glob("*.json"))) - 1,
        "yixiangCycles": len(list(yixiang_dir.glob("*.json"))) - 1,
        "banners": len(list(banners_dir.glob("*.json"))) - 1,
    }


def _validate_expected_inputs(site_root: Path, locale: str) -> None:
    required = [
        site_root / "gi" / locale / "avatar.js",
        site_root / "data" / locale / "Avatar.js",
        site_root / "Char" / "GI.json",
        site_root / "Char" / "HSR.json",
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        lines = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(f"Missing required source files:\n{lines}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Extract and normalize combat-only wiki data from a local HomDGCat raw `site/` mirror."
        )
    )
    parser.add_argument("--site", required=True, help="Path to local raw site folder")
    parser.add_argument(
        "--out",
        required=True,
        help="Output directory for normalized data (e.g. ./combat-wiki/data)",
    )
    parser.add_argument(
        "--locale",
        default="CH",
        help="Locale to extract from site data (default: CH)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete existing output directory content before extraction",
    )

    args = parser.parse_args()
    site_root = Path(args.site).resolve()
    out_root = Path(args.out).resolve()
    locale = args.locale.upper().strip()

    if not site_root.is_dir():
        raise NotADirectoryError(f"site folder not found: {site_root}")

    _validate_expected_inputs(site_root, locale)

    if args.clean and out_root.exists():
        _safe_remove_tree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    gi_out = out_root / "gi"
    sr_out = out_root / "sr"
    gi_out.mkdir(parents=True, exist_ok=True)
    sr_out.mkdir(parents=True, exist_ok=True)

    gi_summary = _extract_gi(site_root, gi_out, locale)
    sr_summary = _extract_sr(site_root, sr_out, locale)

    extraction_report = {
        "locale": locale,
        "sourceSite": str(site_root),
        "output": str(out_root),
        "gi": gi_summary,
        "sr": sr_summary,
        "notes": [
            "Story/lore/quest/admin-oriented fields are removed during normalization.",
            "Yunli score pages are intentionally excluded from extracted output.",
            "Raw site assets are not copied into combat-wiki/data.",
        ],
    }

    write_json(out_root / "_extraction_report.json", extraction_report)
    print("[extract] Completed extraction")
    print(json.dumps(extraction_report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
