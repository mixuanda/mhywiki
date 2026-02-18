#!/usr/bin/env python3
"""
Simple content update manager for non-technical users.

Workflow:
1) Edit easy_updates/updates.csv
2) Run: python3 scripts/content_manager.py apply
3) If needed, rollback latest change: python3 scripts/content_manager.py undo
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT_DIR / "site"
UPDATES_DIR = ROOT_DIR / "easy_updates"
UPDATES_CSV = UPDATES_DIR / "updates.csv"
BACKUPS_DIR = UPDATES_DIR / "backups"
CSV_HEADERS = ["启用", "文件路径", "查找文本", "替换文本", "备注"]
TEXT_EXTS = {".html", ".js", ".css", ".json", ".txt", ".xml", ".md"}
ENABLED_VALUES = {"1", "y", "yes", "true", "on", "是", "启用", "开启"}


@dataclass
class Rule:
    row: int
    enabled: bool
    file_path: str
    find_text: str
    replace_text: str
    note: str

    def to_dict(self) -> dict[str, str]:
        return {
            "enabled": "是" if self.enabled else "否",
            "file_path": self.file_path,
            "find_text": self.find_text,
            "replace_text": self.replace_text,
            "note": self.note,
        }


def normalize_enabled(value: str) -> bool:
    return value.strip().lower() in ENABLED_VALUES


def pick_value(row: dict[str, str], keys: list[str]) -> str:
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return ""


def load_rules() -> list[Rule]:
    if not UPDATES_CSV.exists():
        raise FileNotFoundError(f"Missing updates file: {UPDATES_CSV}")

    rules: list[Rule] = []
    with UPDATES_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            enabled = normalize_enabled(
                pick_value(row, ["启用", "enabled", "Enable", "是否启用"])
            )
            file_path = pick_value(row, ["文件路径", "file_path", "path", "文件"]).strip()
            find_text = pick_value(row, ["查找文本", "find_text", "find", "查找"]).strip()
            replace_text = pick_value(row, ["替换文本", "replace_text", "replace", "替换"])
            note = pick_value(row, ["备注", "note", "说明"]).strip()

            rules.append(
                Rule(
                    row=i,
                    enabled=enabled,
                    file_path=file_path,
                    find_text=find_text,
                    replace_text=replace_text,
                    note=note,
                )
            )
    return rules


def load_rule_dicts() -> list[dict[str, str]]:
    """For UI/API use."""
    return [rule.to_dict() for rule in load_rules()]


def save_rule_dicts(rows: list[dict[str, str]]) -> None:
    UPDATES_DIR.mkdir(parents=True, exist_ok=True)
    with UPDATES_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        for row in rows:
            enabled_raw = str(row.get("enabled", "")).strip().lower()
            enabled = "是" if enabled_raw in ENABLED_VALUES else "否"
            writer.writerow(
                [
                    enabled,
                    str(row.get("file_path", "")),
                    str(row.get("find_text", "")),
                    str(row.get("replace_text", "")),
                    str(row.get("note", "")),
                ]
            )


def ensure_site_exists() -> None:
    if not SITE_DIR.exists():
        raise FileNotFoundError(
            f"Missing site directory: {SITE_DIR}. "
            "Please make sure all website files are under site/."
        )


def resolve_file(path_str: str) -> Path:
    rel = path_str.strip().lstrip("/")
    target = (SITE_DIR / rel).resolve()
    if SITE_DIR.resolve() not in target.parents and target != SITE_DIR.resolve():
        raise ValueError(f"Blocked path outside site/: {path_str}")
    return target


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for p in SITE_DIR.rglob("*"):
        if p.is_file() and p.suffix.lower() in TEXT_EXTS:
            files.append(p)
    return files


def create_backup_dir() -> Path:
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BACKUPS_DIR / ts
    backup_dir.mkdir(parents=True, exist_ok=False)
    return backup_dir


def backup_file(src: Path, backup_dir: Path) -> None:
    rel = src.relative_to(SITE_DIR)
    dst = backup_dir / rel
    if dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def read_text_safe(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def apply_rule_to_file(rule: Rule, path: Path, backup_dir: Path) -> int:
    text = read_text_safe(path)
    if text is None or not rule.find_text:
        return 0
    count = text.count(rule.find_text)
    if count <= 0:
        return 0
    backup_file(path, backup_dir)
    updated = text.replace(rule.find_text, rule.replace_text)
    path.write_text(updated, encoding="utf-8")
    return count


def apply_updates() -> int:
    ensure_site_exists()
    rules = load_rules()
    enabled_rules = [r for r in rules if r.enabled and r.find_text]
    if not enabled_rules:
        print("No enabled update rules found.")
        return 0

    backup_dir: Path | None = None
    touched_files: set[Path] = set()
    changed_rows = 0
    total_replacements = 0
    all_text_files: list[Path] | None = None

    for rule in enabled_rules:
        if backup_dir is None:
            backup_dir = create_backup_dir()

        targets: list[Path] = []
        if rule.file_path:
            target = resolve_file(rule.file_path)
            if not target.exists() or not target.is_file():
                print(f"[Row {rule.row}] file not found, skipped: {rule.file_path}")
                continue
            targets = [target]
        else:
            if all_text_files is None:
                all_text_files = iter_text_files()
            targets = all_text_files

        row_replacements = 0
        for target in targets:
            count = apply_rule_to_file(rule, target, backup_dir)
            if count > 0:
                touched_files.add(target)
                row_replacements += count

        if row_replacements > 0:
            changed_rows += 1
            total_replacements += row_replacements
            scope = rule.file_path if rule.file_path else "[all text files]"
            print(
                f"[Row {rule.row}] updated ({row_replacements} replacements): {scope}"
            )
        else:
            print(f"[Row {rule.row}] no match found, skipped.")

    if not touched_files:
        if backup_dir is not None and backup_dir.exists():
            shutil.rmtree(backup_dir)
        print("No file changed.")
        return 0

    print("-" * 55)
    print(f"Backup: {backup_dir}")
    print(f"Changed files: {len(touched_files)}")
    print(f"Changed rules: {changed_rows}")
    print(f"Total replacements: {total_replacements}")
    print("Done.")
    return 0


def latest_backup_dir() -> Path | None:
    if not BACKUPS_DIR.exists():
        return None
    dirs = [d for d in BACKUPS_DIR.iterdir() if d.is_dir()]
    if not dirs:
        return None
    return sorted(dirs)[-1]


def undo_latest() -> int:
    ensure_site_exists()
    latest = latest_backup_dir()
    if latest is None:
        print("No backup found.")
        return 0

    restored = 0
    for src in latest.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(latest)
        dst = SITE_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        restored += 1

    print(f"Restored {restored} files from: {latest}")
    return 0


def init_updates_file() -> int:
    UPDATES_DIR.mkdir(parents=True, exist_ok=True)
    if UPDATES_CSV.exists():
        print(f"Already exists: {UPDATES_CSV}")
        return 0

    with UPDATES_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        writer.writerow(
            ["否", "/about/index.html", "HomDGCat Wiki", "我的网站标题", "示例：修改标题"]
        )
        writer.writerow(
            ["否", "/about/index.html", "Genshin Impact", "原神资料站", "示例：修改简介文案"]
        )

    print(f"Created template: {UPDATES_CSV}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Content update manager")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("init", help="Create easy_updates/updates.csv template")
    sub.add_parser("apply", help="Apply enabled rules from CSV")
    sub.add_parser("undo", help="Restore files from latest backup")
    args = parser.parse_args()

    try:
        if args.command == "init":
            return init_updates_file()
        if args.command == "apply":
            return apply_updates()
        if args.command == "undo":
            return undo_latest()
        parser.print_help()
        return 1
    except Exception as exc:  # keep this user-facing for non-technical users
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
