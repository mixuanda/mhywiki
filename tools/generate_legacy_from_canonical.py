#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from legacy_sync import sync_entity


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate/update legacy web runtime files for one canonical entity."
    )
    parser.add_argument("--data", default="./combat-wiki/data", help="Canonical data root")
    parser.add_argument("--web", default="./web", help="Legacy web root")
    parser.add_argument("--game", required=True, choices=["gi", "sr"])
    parser.add_argument(
        "--kind",
        required=True,
        choices=["character", "weapon", "artifact", "enemy", "banner", "lightcone", "relic"],
    )
    parser.add_argument("--id", required=True, help="Entity id to sync")
    args = parser.parse_args()

    result = sync_entity(
        data_root=Path(args.data).resolve(),
        web_root=Path(args.web).resolve(),
        game=args.game,
        kind=args.kind,
        entity_id=args.id,
    )
    print("[legacy-sync] changed files:")
    for path in result.changed_files:
        print(f"- {path}")
    if result.notes:
        print("[legacy-sync] notes:")
        for note in result.notes:
            print(f"- {note}")


if __name__ == "__main__":
    main()
