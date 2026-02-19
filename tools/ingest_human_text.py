#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from legacy_sync import sync_entity, write_canonical_entity


SECTION_ALIASES = {
    "skills": {"skills", "skill", "技能", "skill list"},
    "talents": {"talents", "talent", "天赋"},
    "constellation": {"constellation", "命座", "cons"},
    "eidolons": {"eidolons", "eidolon", "星魂"},
    "traces": {"traces", "trace", "行迹"},
    "materials": {"materials", "material", "升级材料", "突破材料", "mat", "mats"},
    "notes": {"notes", "note", "备注", "说明", "other"},
}


FIELD_ALIASES = {
    "id": {"id", "编号", "id号", "角色id", "weapon id", "lightcone id"},
    "name": {"name", "名称", "角色名", "名字"},
    "codeName": {"codename", "code", "代号", "内部名"},
    "title": {"title", "subname", "称号", "副标题"},
    "description": {"desc", "description", "简介", "介绍"},
    "version": {"version", "ver", "版本"},
    "rarity": {"rarity", "rank", "星级"},
    "element": {"element", "属性"},
    "path": {"path", "命途"},
    "weaponType": {"weapon", "weapon type", "武器类型"},
    "nation": {"nation", "国家", "阵营"},
    "affiliation": {"affiliation", "belong", "所属"},
    "phase": {"phase", "卡池阶段"},
}


def _norm_key(key: str) -> str:
    return re.sub(r"\s+", " ", key.strip().lower())


def _find_field(key: str) -> str | None:
    nk = _norm_key(key)
    for field, aliases in FIELD_ALIASES.items():
        if nk in aliases:
            return field
    return None


def _find_section(key: str) -> str | None:
    nk = _norm_key(key).rstrip(":：")
    for section, aliases in SECTION_ALIASES.items():
        if nk in aliases:
            return section
    return None


def _maybe_number(value: str) -> Any:
    text = value.strip()
    if text == "":
        return ""
    if re.fullmatch(r"-?\d+", text):
        try:
            return int(text)
        except ValueError:
            return text
    if re.fullmatch(r"-?\d+\.\d+", text):
        try:
            return float(text)
        except ValueError:
            return text
    return text


def _split_values(value: str) -> list[str]:
    return [x.strip() for x in re.split(r"[;,，；、]", value) if x.strip()]


def _collect_material_ids(values: list[str]) -> list[str]:
    out: list[str] = []
    for raw in values:
        for token in re.findall(r"\d{3,}", raw):
            if token not in out:
                out.append(token)
    return out


def parse_human_text_to_payload(
    *,
    game: str,
    kind: str,
    entity_id: str | None,
    name: str | None,
    text: str,
) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    sections: dict[str, list[str]] = {k: [] for k in SECTION_ALIASES}
    current_section: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        section_guess = _find_section(line)
        if section_guess:
            current_section = section_guess
            continue

        m = re.match(r"^([^:：]{1,40})[:：]\s*(.+)$", line)
        if m:
            k = m.group(1).strip()
            v = m.group(2).strip()
            section_key = _find_section(k)
            if section_key:
                current_section = section_key
                sections[section_key].append(v)
                continue

            field_key = _find_field(k)
            if field_key:
                fields[field_key] = _maybe_number(v)
                continue

        bullet = re.sub(r"^[-*•\d\)\.]+\s*", "", line).strip()
        if current_section:
            sections[current_section].append(bullet)
        else:
            sections["notes"].append(bullet)

    resolved_id = str(entity_id or fields.get("id") or "").strip()
    resolved_name = str(name or fields.get("name") or "").strip()
    if not resolved_id:
        if resolved_name:
            resolved_id = re.sub(r"\W+", "_", resolved_name).strip("_").lower() or "new_entity"
        else:
            resolved_id = "new_entity"
    if not resolved_name:
        resolved_name = resolved_id

    material_refs = _collect_material_ids(
        sections.get("materials", []) + _split_values(str(fields.get("materials", "")))
    )

    payload: dict[str, Any] = {
        "id": resolved_id,
        "game": game,
        "entityType": kind,
        "name": resolved_name,
        "title": fields.get("title", ""),
        "description": fields.get("description", ""),
        "version": fields.get("version", ""),
        "rarity": fields.get("rarity"),
        "element": fields.get("element"),
        "path": fields.get("path"),
        "weaponType": fields.get("weaponType"),
        "nation": fields.get("nation"),
        "affiliation": fields.get("affiliation"),
        "materialRefs": material_refs,
        "manualSections": {k: v for k, v in sections.items() if v},
        "rawText": text.strip(),
        "source": {
            "ingest": "tools/ingest_human_text.py",
            "mode": "human_text",
        },
    }

    stats_map = {}
    for stat_key in ["hp", "atk", "def", "spd"]:
        if stat_key in fields:
            stats_map[stat_key.upper()] = fields[stat_key]
    if stats_map:
        payload["baseStats"] = stats_map

    if kind == "character" and game == "gi":
        code_name = str(fields.get("codeName") or resolved_id).strip()
        payload["codeName"] = code_name
        skill_lines = sections.get("skills", []) + sections.get("talents", [])
        cons_lines = sections.get("constellation", [])
        payload["combat"] = {
            "detail_1": {
                "_AvatarDataConfig_": {code_name: {"OtherDataList": sections.get("notes", [])}},
                "_AvatarMats_": {code_name: {}},
                "_AvatarSkillPConfig_": {code_name: {"Manual": skill_lines}},
                "_AvatarAttackConfig_": {code_name: {}},
            },
            "detail_2": {
                "_AvatarFetterConfig_": {str(resolved_id): {"StoryTitle": [resolved_name], "StoryContext": sections.get("notes", [])}},
                "_AvatarCostumeConfig_": {str(resolved_id): []},
                "acs_cache_": {"constellation": cons_lines},
            },
        }

    if kind == "character" and game == "sr":
        sid = str(resolved_id)
        skill_lines = sections.get("skills", [])
        trace_lines = sections.get("traces", [])
        eidolon_lines = sections.get("eidolons", [])
        payload["combat"] = {
            "_avatarskill_": {
                f"{sid}01": {
                    "Pre": {
                        "Name": "Manual Skill",
                        "Type": "Manual",
                        "Desc": "<br>".join(skill_lines) if skill_lines else payload.get("description", ""),
                    }
                }
            },
            "_avatarskilltree_": {
                sid: {
                    "Pre": {
                        "Add": {},
                        "Tree1": {"Name": "Trace 1", "Desc": trace_lines[0] if len(trace_lines) > 0 else ""},
                        "Tree2": {"Name": "Trace 2", "Desc": trace_lines[1] if len(trace_lines) > 1 else ""},
                        "Tree3": {"Name": "Trace 3", "Desc": trace_lines[2] if len(trace_lines) > 2 else ""},
                    }
                }
            },
            "_avatarrank_": {
                f"{sid}01": {
                    "Pre": {
                        "Rank": 1,
                        "Name": "Eidolon 1",
                        "Desc": eidolon_lines[0] if eidolon_lines else "",
                    }
                }
            },
            "_story_": {sid: {}},
            "_voice_": {sid: {}},
            "_notes_": {sid: {"Pre": sections.get("notes", [])}},
            "_adiff_": {sid: {}},
            "_mtc_": {sid: {}},
        }

    if kind in {"weapon", "lightcone"}:
        payload["skillName"] = fields.get("title", "Manual Skill")
        payload.setdefault("detail", {})

    if kind == "banner":
        payload["phase"] = fields.get("phase", 1)
        payload.setdefault("featuredFiveStar", [])
        payload.setdefault("featuredFourStar", [])

    return payload


def ingest_entity(
    *,
    data_root: Path,
    web_root: Path,
    game: str,
    kind: str,
    entity_id: str | None,
    name: str | None,
    text: str,
    apply_changes: bool,
) -> dict[str, Any]:
    payload = parse_human_text_to_payload(
        game=game,
        kind=kind,
        entity_id=entity_id,
        name=name,
        text=text,
    )
    result: dict[str, Any] = {"payload": payload, "changedFiles": [], "notes": []}

    if not apply_changes:
        return result

    canonical_path = write_canonical_entity(
        data_root=data_root,
        game=game,
        kind=kind,
        entity_id=str(payload["id"]),
        payload=payload,
    )
    sync_result = sync_entity(
        data_root=data_root,
        web_root=web_root,
        game=game,
        kind=kind,
        entity_id=str(payload["id"]),
    )
    result["canonicalPath"] = str(canonical_path)
    result["changedFiles"] = [str(p) for p in sync_result.changed_files]
    result["notes"] = sync_result.notes
    return result


def _read_input_text(args: argparse.Namespace) -> str:
    if args.text and args.text_file:
        raise ValueError("Use either --text or --text-file, not both.")
    if args.text:
        return args.text
    if args.text_file:
        return Path(args.text_file).read_text(encoding="utf-8")
    raise ValueError("Provide input content using --text or --text-file.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest free-form human text into canonical entity JSON and legacy runtime files."
    )
    parser.add_argument("--data", default="./combat-wiki/data", help="Canonical data root")
    parser.add_argument("--web", default="./web", help="Legacy web root")
    parser.add_argument("--game", required=True, choices=["gi", "sr"])
    parser.add_argument(
        "--kind",
        required=True,
        choices=["character", "weapon", "artifact", "enemy", "banner", "lightcone", "relic"],
    )
    parser.add_argument("--id", help="Entity id (optional if present in text)")
    parser.add_argument("--name", help="Entity name (optional if present in text)")
    parser.add_argument("--text", help="Human-readable entity text")
    parser.add_argument("--text-file", help="Path to text file containing entity description")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write canonical file and sync legacy runtime files",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    text = _read_input_text(args)
    result = ingest_entity(
        data_root=Path(args.data).resolve(),
        web_root=Path(args.web).resolve(),
        game=args.game,
        kind=args.kind,
        entity_id=args.id,
        name=args.name,
        text=text,
        apply_changes=args.apply,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
