#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
TEXTMAP_DIR = ROOT_DIR / "site" / "TextMap"
SHARD_COUNT = 64

GAME_MAP = {
    "gi": {
        "mono_file": TEXTMAP_DIR / "GI.json",
        "shard_dir": TEXTMAP_DIR / "GI_shards",
    },
    "sr": {
        "mono_file": TEXTMAP_DIR / "SR.json",
        "shard_dir": TEXTMAP_DIR / "SR_shards",
    },
}


def _entry_key(entry: dict[str, Any]) -> str:
    if "H" in entry and entry["H"] is not None:
        return str(entry["H"])
    if "I" in entry and entry["I"] is not None:
        return str(entry["I"])
    if "_id" in entry and entry["_id"] is not None:
        return str(entry["_id"])
    return json.dumps(entry, ensure_ascii=False, sort_keys=True)[:120]


def shard_of_key(key: str) -> int:
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % SHARD_COUNT


def has_shards(game: str) -> bool:
    info = GAME_MAP[game]
    shard_dir = info["shard_dir"]
    if not shard_dir.exists() or not shard_dir.is_dir():
        return False
    files = list(shard_dir.glob("*.json"))
    return len(files) >= SHARD_COUNT


def _shard_path(game: str, shard_id: int) -> Path:
    info = GAME_MAP[game]
    shard_dir = info["shard_dir"]
    return shard_dir / f"{shard_id:02x}.json"


def split_monolith(game: str) -> dict[str, Any]:
    info = GAME_MAP[game]
    mono_file = info["mono_file"]
    shard_dir = info["shard_dir"]
    if not mono_file.exists():
        raise FileNotFoundError(f"Missing monolith file: {mono_file}")

    rows = json.loads(mono_file.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError(f"TextMap monolith is not list: {mono_file}")

    buckets: list[list[Any]] = [[] for _ in range(SHARD_COUNT)]
    for row in rows:
        if not isinstance(row, dict):
            continue
        sid = shard_of_key(_entry_key(row))
        buckets[sid].append(row)

    shard_dir.mkdir(parents=True, exist_ok=True)
    for sid in range(SHARD_COUNT):
        target = _shard_path(game, sid)
        target.write_text(
            json.dumps(buckets[sid], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return {
        "game": game,
        "rows": len(rows),
        "shard_dir": str(shard_dir),
    }


def rebuild_from_shards(game: str) -> Path:
    info = GAME_MAP[game]
    mono_file = info["mono_file"]
    shard_dir = info["shard_dir"]
    if not shard_dir.exists():
        raise FileNotFoundError(f"Missing shard dir: {shard_dir}")

    merged: list[Any] = []
    for sid in range(SHARD_COUNT):
        shard_file = _shard_path(game, sid)
        if not shard_file.exists():
            continue
        rows = json.loads(shard_file.read_text(encoding="utf-8"))
        if isinstance(rows, list):
            merged.extend(rows)

    mono_file.write_text(
        json.dumps(merged, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )
    return mono_file


def rebuild_all_from_shards() -> list[str]:
    out: list[str] = []
    for game in ("gi", "sr"):
        if has_shards(game):
            path = rebuild_from_shards(game)
            out.append(str(path))
    return out


def status() -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for game, info in GAME_MAP.items():
        shard_dir = info["shard_dir"]
        mono_file = info["mono_file"]
        shards = sorted(shard_dir.glob("*.json")) if shard_dir.exists() else []
        payload[game] = {
            "mono_file": str(mono_file),
            "mono_exists": mono_file.exists(),
            "mono_size": mono_file.stat().st_size if mono_file.exists() else 0,
            "shard_dir": str(shard_dir),
            "shard_count": len(shards),
            "ready": has_shards(game),
        }
    return payload


def cmd_init() -> int:
    gi = split_monolith("gi")
    sr = split_monolith("sr")
    rebuild_from_shards("gi")
    rebuild_from_shards("sr")
    print(f"GI shards created: {gi['rows']} rows -> {gi['shard_dir']}")
    print(f"SR shards created: {sr['rows']} rows -> {sr['shard_dir']}")
    print("Rebuilt GI.json and SR.json from shards.")
    return 0


def cmd_rebuild() -> int:
    rebuilt = rebuild_all_from_shards()
    if not rebuilt:
        print("No shard set is ready. Run: python3 scripts/textmap_shards.py init")
        return 0
    for path in rebuilt:
        print(f"Rebuilt: {path}")
    return 0


def cmd_status() -> int:
    print(json.dumps(status(), ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="TextMap shard tools")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("init", help="Split GI.json/SR.json into 64 shards each")
    sub.add_parser("rebuild", help="Rebuild GI.json/SR.json from shards")
    sub.add_parser("status", help="Show shard status")
    args = parser.parse_args()

    if args.command == "init":
        return cmd_init()
    if args.command == "rebuild":
        return cmd_rebuild()
    if args.command == "status":
        return cmd_status()
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
