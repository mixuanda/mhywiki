#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from normalize import read_json

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print("[validate] Missing dependency: jsonschema")
    print("Install with: python3 -m pip install jsonschema")
    sys.exit(2)


SCHEMA_MAP = {
    "gi/characters": "character.schema.json",
    "sr/characters": "character.schema.json",
    "gi/weapons": "weapon.schema.json",
    "sr/lightcones": "lightcone.schema.json",
    "gi/artifacts": "artifact.schema.json",
    "sr/relics": "relic.schema.json",
    "gi/enemies": "enemy.schema.json",
    "sr/enemies": "enemy.schema.json",
    "gi/endgame/abyss": "endgame_cycle.schema.json",
    "gi/endgame/theater": "endgame_cycle.schema.json",
    "gi/endgame/youjing": "endgame_cycle.schema.json",
    "sr/endgame/moc": "endgame_cycle.schema.json",
    "sr/endgame/purefiction": "endgame_cycle.schema.json",
    "sr/endgame/apocalypticshadow": "endgame_cycle.schema.json",
    "sr/endgame/yixiangzhongcai": "endgame_cycle.schema.json",
    "sr/endgame/divergentuniverse/2.7": "endgame_cycle.schema.json",
    "sr/endgame/divergentuniverse/3.8": "endgame_cycle.schema.json",
    "gi/banners": "banner.schema.json",
    "sr/banners": "banner.schema.json",
    "sr/glossary/effects": "glossary_entry.schema.json",
    "sr/glossary/terms": "glossary_entry.schema.json",
    "gi/achievements": "achievement.schema.json",
    "sr/achievements": "achievement.schema.json",
    "sr/stages": "stage.schema.json",
    "sr/dialogue_line_stats": "dialogue_stats.schema.json",
}


def _iter_json_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    out = []
    for item in sorted(path.glob("*.json")):
        if item.name == "index.json" or item.stem.startswith("_"):
            continue
        out.append(item)
    return out


def _collect_ids(path: Path) -> set[str]:
    ids = set()
    for json_file in _iter_json_files(path):
        data = read_json(json_file)
        if isinstance(data, dict):
            ids.add(str(data.get("id", json_file.stem)))
        else:
            ids.add(json_file.stem)
    return ids


def _extract_sr_enemy_ids_from_cycle(payload: Any) -> set[str]:
    out: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "Monsters" and isinstance(child, list):
                    for wave in child:
                        if isinstance(wave, list):
                            for monster in wave:
                                if not isinstance(monster, dict):
                                    continue
                                mid = monster.get("ID")
                                if isinstance(mid, (int, str)):
                                    out.add(str(mid))
                        elif isinstance(wave, dict):
                            mid = wave.get("ID")
                            if isinstance(mid, (int, str)):
                                out.add(str(mid))
                else:
                    walk(child)
            return
        if isinstance(value, list):
            for child in value:
                walk(child)

    walk(payload)
    return out


def _extract_gi_enemy_ids_from_abyss(payload: dict[str, Any]) -> set[str]:
    out: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "Monsters" and isinstance(child, list):
                    for monster in child:
                        if not isinstance(monster, dict):
                            continue
                        mid = monster.get("ID")
                        if isinstance(mid, (int, str)):
                            out.add(str(mid))
                else:
                    walk(child)
            return
        if isinstance(value, list):
            for child in value:
                walk(child)

    walk(payload.get("floors", []))
    return out


def _extract_stage_enemy_ids(payload: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for wave in payload.get("waves", []) or []:
        if not isinstance(wave, list):
            continue
        for part in wave:
            if isinstance(part, list):
                for item in part:
                    if isinstance(item, (int, str)):
                        out.add(str(item))
            elif isinstance(part, (int, str)):
                out.add(str(part))
    return out


def _validate_schema(data_root: Path, schema_root: Path) -> list[str]:
    errors: list[str] = []
    validators: dict[str, Draft202012Validator] = {}

    for rel_dir, schema_name in SCHEMA_MAP.items():
        schema_file = schema_root / schema_name
        if schema_name not in validators:
            schema = read_json(schema_file)
            validators[schema_name] = Draft202012Validator(schema)

        validator = validators[schema_name]
        directory = data_root / rel_dir
        for json_file in _iter_json_files(directory):
            payload = read_json(json_file)
            for issue in validator.iter_errors(payload):
                path = ".".join(str(part) for part in issue.absolute_path)
                pointer = f" ({path})" if path else ""
                errors.append(f"{json_file}: {issue.message}{pointer}")

    return errors


def _validate_references(data_root: Path) -> list[str]:
    errors: list[str] = []

    gi_materials = _collect_ids(data_root / "gi" / "materials")
    sr_materials = _collect_ids(data_root / "sr" / "materials")
    gi_enemies = _collect_ids(data_root / "gi" / "enemies")
    sr_enemies = _collect_ids(data_root / "sr" / "enemies")

    gi_characters = {}
    for path in _iter_json_files(data_root / "gi" / "characters"):
        payload = read_json(path)
        char_id = str(payload.get("id", path.stem))
        gi_characters[char_id] = payload

    sr_characters = _collect_ids(data_root / "sr" / "characters")

    gi_codes = {str(payload.get("codeName", "")): cid for cid, payload in gi_characters.items()}

    for path in _iter_json_files(data_root / "gi" / "characters"):
        payload = read_json(path)
        for mat in payload.get("materialRefs", []) or []:
            if str(mat) not in gi_materials:
                errors.append(f"{path}: missing GI material reference `{mat}`")

    for path in _iter_json_files(data_root / "gi" / "weapons"):
        payload = read_json(path)
        for mat in payload.get("materialRefs", []) or []:
            if str(mat) not in gi_materials:
                errors.append(f"{path}: missing GI material reference `{mat}`")

    for path in _iter_json_files(data_root / "sr" / "characters"):
        payload = read_json(path)
        for mat in payload.get("materialRefs", []) or []:
            if str(mat) not in sr_materials:
                errors.append(f"{path}: missing SR material reference `{mat}`")

    for path in _iter_json_files(data_root / "sr" / "lightcones"):
        payload = read_json(path)
        for mat in payload.get("materialRefs", []) or []:
            if str(mat) not in sr_materials:
                errors.append(f"{path}: missing SR material reference `{mat}`")

    for path in _iter_json_files(data_root / "gi" / "banners"):
        payload = read_json(path)
        for bucket in ["featuredFiveStar", "featuredFourStar"]:
            for row in payload.get(bucket, []) or []:
                code = str(row.get("N", ""))
                if code and code not in gi_codes:
                    errors.append(f"{path}: GI banner character code not found `{code}`")

    for path in _iter_json_files(data_root / "sr" / "banners"):
        payload = read_json(path)
        for bucket in ["featuredFiveStar", "featuredFourStar"]:
            for row in payload.get(bucket, []) or []:
                char_id = str(row.get("N"))
                if char_id and char_id not in sr_characters:
                    errors.append(f"{path}: SR banner character id not found `{char_id}`")

    for path in _iter_json_files(data_root / "gi" / "endgame" / "abyss"):
        payload = read_json(path)
        for enemy_id in _extract_gi_enemy_ids_from_abyss(payload):
            if enemy_id not in gi_enemies:
                errors.append(f"{path}: GI abyss enemy reference missing `{enemy_id}`")

    for path in _iter_json_files(data_root / "gi" / "endgame" / "youjing"):
        payload = read_json(path)
        for level in payload.get("levels", []) or []:
            if not isinstance(level, dict):
                continue
            for monster in level.get("monsters", []) or []:
                if not isinstance(monster, dict):
                    continue
                enemy_id = str(monster.get("id"))
                if enemy_id and enemy_id not in gi_enemies:
                    errors.append(f"{path}: GI youjing enemy reference missing `{enemy_id}`")

    for rel in [
        "sr/endgame/moc",
        "sr/endgame/purefiction",
        "sr/endgame/apocalypticshadow",
        "sr/endgame/yixiangzhongcai",
        "sr/endgame/divergentuniverse/2.7",
        "sr/endgame/divergentuniverse/3.8",
    ]:
        for path in _iter_json_files(data_root / rel):
            payload = read_json(path)
            for enemy_id in _extract_sr_enemy_ids_from_cycle(payload):
                if enemy_id.isdigit() and enemy_id not in sr_enemies:
                    errors.append(f"{path}: SR endgame enemy reference missing `{enemy_id}`")

    for path in _iter_json_files(data_root / "sr" / "stages"):
        payload = read_json(path)
        for enemy_id in _extract_stage_enemy_ids(payload):
            # Stage.js frequently uses generated encounter ids (for example 7002xxx),
            # which are not direct monster catalog ids.
            if enemy_id.startswith("7"):
                continue
            if enemy_id not in sr_enemies:
                errors.append(f"{path}: SR stage enemy reference missing `{enemy_id}`")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate normalized combat wiki JSON data")
    parser.add_argument("--data", required=True, help="Path to combat-wiki/data")
    parser.add_argument("--schemas", required=True, help="Path to schemas directory")
    args = parser.parse_args()

    data_root = Path(args.data).resolve()
    schema_root = Path(args.schemas).resolve()

    if not data_root.is_dir():
        raise NotADirectoryError(f"Data directory not found: {data_root}")
    if not schema_root.is_dir():
        raise NotADirectoryError(f"Schema directory not found: {schema_root}")

    schema_errors = _validate_schema(data_root, schema_root)
    reference_errors = _validate_references(data_root)

    all_errors = [*schema_errors, *reference_errors]
    if all_errors:
        print(f"[validate] FAILED with {len(all_errors)} issue(s)")
        for issue in all_errors:
            print(f"- {issue}")
        sys.exit(1)

    print("[validate] OK: schemas and references are valid")


if __name__ == "__main__":
    main()
