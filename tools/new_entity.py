#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from normalize import write_json


KIND_PATHS = {
    "gi:character": "gi/characters",
    "gi:weapon": "gi/weapons",
    "gi:artifact": "gi/artifacts",
    "gi:enemy": "gi/enemies",
    "gi:material": "gi/materials",
    "gi:banner": "gi/banners",
    "gi:achievement": "gi/achievements",
    "sr:character": "sr/characters",
    "sr:lightcone": "sr/lightcones",
    "sr:relic": "sr/relics",
    "sr:enemy": "sr/enemies",
    "sr:material": "sr/materials",
    "sr:banner": "sr/banners",
    "sr:achievement": "sr/achievements",
    "sr:stage": "sr/stages",
    "sr:glossary-effect": "sr/glossary/effects",
    "sr:glossary-term": "sr/glossary/terms",
}


def _template(game: str, kind: str, entity_id: str, name: str | None) -> dict[str, Any]:
    title = name or f"New {kind} {entity_id}"
    payload = {
        "id": entity_id,
        "game": game,
        "entityType": kind,
        "name": title,
        "source": {"note": "Created with tools/new_entity.py"},
    }

    if kind in {"character", "weapon", "lightcone", "relic", "artifact"}:
        payload.update({"description": "", "rarity": None, "materialRefs": []})
    if kind in {"enemy"}:
        payload.update({"description": "", "stats": {}, "analysis": None})
    if kind in {"banner"}:
        payload.update({"version": "", "phase": 1, "featuredFiveStar": [], "featuredFourStar": []})
    if kind in {"achievement"}:
        payload.update({"description": "", "reward": 0, "version": ""})
    if kind in {"stage"}:
        payload.update({"level": 1, "waves": []})
    if kind in {"glossary-effect", "glossary-term"}:
        payload.update({"description": ""})

    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a normalized entity JSON file")
    parser.add_argument("--out", default="./combat-wiki/data", help="Data root path")
    parser.add_argument("--game", required=True, choices=["gi", "sr"])
    parser.add_argument(
        "--kind",
        required=True,
        choices=[
            "character",
            "weapon",
            "artifact",
            "enemy",
            "material",
            "banner",
            "achievement",
            "lightcone",
            "relic",
            "stage",
            "glossary-effect",
            "glossary-term",
        ],
    )
    parser.add_argument("--id", required=True, help="Entity id")
    parser.add_argument("--name", help="Entity display name")
    parser.add_argument("--force", action="store_true", help="Overwrite if file already exists")
    args = parser.parse_args()

    key = f"{args.game}:{args.kind}"
    rel = KIND_PATHS.get(key)
    if rel is None:
        raise ValueError(f"Unsupported combination: {key}")

    out_root = Path(args.out).resolve()
    file_path = out_root / rel / f"{args.id}.json"
    if file_path.exists() and not args.force:
        raise FileExistsError(f"File already exists: {file_path}")

    payload = _template(args.game, args.kind, args.id, args.name)
    write_json(file_path, payload)
    print(f"[new_entity] Created {file_path}")


if __name__ == "__main__":
    main()
