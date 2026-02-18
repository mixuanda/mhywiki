#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import difflib
import hashlib
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import textmap_shards


ROOT_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT_DIR / "site"
BACKUP_ROOT = ROOT_DIR / "easy_updates" / "entity_backups"

SCAN_ROOTS = [
    SITE_DIR / "gi" / "CH",
    SITE_DIR / "gi" / "EN",
    SITE_DIR / "data" / "CH",
    SITE_DIR / "data" / "EN",
    SITE_DIR / "TextMap",
]

SUPPORTED_EXTS = {".js", ".json", ".html"}
BACKUP_META_FILE = "_cms_meta.json"


def _short_text(value: str, max_len: int = 90) -> str:
    text = (value or "").replace("\n", " ").replace("\r", " ").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "..."


def _looks_like_html(text: str) -> bool:
    s = text.lstrip().lower()
    return s.startswith("<!doctype html") or s.startswith("<html") or s.startswith("<")


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


def _write_backup_meta(backup_dir: Path, payload: dict[str, Any]) -> None:
    (backup_dir / BACKUP_META_FILE).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


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


def undo_backup(backup_id: str | None = None) -> str:
    if backup_id:
        target = BACKUP_ROOT / backup_id
        if not target.exists() or not target.is_dir():
            raise ValueError(f"Backup not found: {backup_id}")
    else:
        target = _latest_backup_dir()
        if target is None:
            return "No backup found."

    restored = 0
    for src in target.rglob("*"):
        if not src.is_file() or src.name == BACKUP_META_FILE:
            continue
        rel = src.relative_to(target)
        dst = ROOT_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        restored += 1
    return f"Restored {restored} file(s) from {target.name}."


def _auto_generated_content(assignments: list[tuple[str, Any]]) -> str:
    parts = ["// Auto Generated", ""]
    for idx, (name, value) in enumerate(assignments):
        parts.append(f"var {name} = {json.dumps(value, ensure_ascii=False, indent=4)}")
        if idx != len(assignments) - 1:
            parts.append("")
    parts.append("")
    return "\n".join(parts)


def _run_node_eval_js_vars(file_path: Path) -> tuple[list[str], dict[str, Any]]:
    script = r"""
const fs = require("fs");
const vm = require("vm");
const file = process.argv[1];
const code = fs.readFileSync(file, "utf8");
if (/^\s*</.test(code)) {
  throw new Error("File looks like HTML, not js-var.");
}
const varNames = [...code.matchAll(/\bvar\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=/g)]
  .map((m) => m[1]);
if (!varNames.length) {
  throw new Error("No var assignments found.");
}
const uniqueNames = [...new Set(varNames)];
const sandbox = {};
vm.createContext(sandbox);
vm.runInContext(code, sandbox, { filename: file });
const values = {};
for (const name of uniqueNames) {
  if (Object.prototype.hasOwnProperty.call(sandbox, name)) {
    values[name] = sandbox[name];
  }
}
process.stdout.write(JSON.stringify({ var_names: uniqueNames, values }));
"""
    proc = subprocess.run(
        ["node", "-e", script, str(file_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    var_names = payload.get("var_names") or []
    values = payload.get("values") or {}
    return [str(x) for x in var_names], values


@dataclass
class SourceMeta:
    id: str
    game: str
    locale: str
    category: str
    file_path: Path
    format: str
    editable: bool
    readonly_reason: str
    record_count: int


@dataclass
class ParsedSource:
    meta: SourceMeta
    root_data: Any
    js_var_order: list[str] | None


class UniversalCMSRepository:
    def __init__(self) -> None:
        self.sources: dict[str, SourceMeta] = {}
        self._record_count_cache: dict[str, int] = {}
        self._source_mtime_cache: dict[str, int] = {}
        self.refresh_registry()

    def refresh_registry(self) -> None:
        discovered: dict[str, SourceMeta] = {}
        textmap_has_gi_shards = textmap_shards.has_shards("gi")
        textmap_has_sr_shards = textmap_shards.has_shards("sr")

        for root in SCAN_ROOTS:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                if path.name == ".DS_Store":
                    continue
                if path.suffix.lower() not in SUPPORTED_EXTS:
                    continue
                rel = path.relative_to(SITE_DIR).as_posix()
                source_id = rel
                game, locale, category = self._derive_dimensions(rel)
                fmt = self._derive_format(path)
                editable = True
                readonly_reason = ""

                if fmt == "js-var":
                    try:
                        head = path.read_text(encoding="utf-8", errors="ignore")[:240]
                    except OSError:
                        head = ""
                    if _looks_like_html(head):
                        editable = False
                        readonly_reason = "File content looks like HTML, not data JS."

                if rel == "TextMap/GI.json" and textmap_has_gi_shards:
                    editable = False
                    readonly_reason = "Managed by TextMap shards: TextMap/GI_shards/*."
                if rel == "TextMap/SR.json" and textmap_has_sr_shards:
                    editable = False
                    readonly_reason = "Managed by TextMap shards: TextMap/SR_shards/*."

                discovered[source_id] = SourceMeta(
                    id=source_id,
                    game=game,
                    locale=locale,
                    category=category,
                    file_path=path,
                    format=fmt,
                    editable=editable,
                    readonly_reason=readonly_reason,
                    record_count=self._record_count_cache.get(source_id, -1),
                )

        self.sources = dict(sorted(discovered.items(), key=lambda x: x[0]))

    def list_sources(
        self, game: str = "", locale: str = "", q: str = ""
    ) -> list[dict[str, Any]]:
        game = game.strip().lower()
        locale = locale.strip().upper()
        ql = q.strip().lower()

        out = []
        for source in self.sources.values():
            if game and source.game != game:
                continue
            if locale and source.locale.upper() != locale:
                continue
            blob = (
                f"{source.id} {source.category} {source.game} "
                f"{source.locale} {source.file_path.as_posix()}"
            ).lower()
            if ql and ql not in blob:
                continue
            out.append(self._source_to_dict(source))
        return out

    def get_source(self, source_id: str) -> SourceMeta:
        source = self.sources.get(source_id)
        if source is None:
            raise ValueError(f"Unknown source_id: {source_id}")
        return source

    def list_records(
        self, source_id: str, q: str = "", page: int = 1, page_size: int = 50
    ) -> dict[str, Any]:
        source = self.get_source(source_id)
        parsed = self._parse_source(source)
        root = parsed.root_data

        page = max(1, page)
        page_size = max(1, min(page_size, 200))
        query = q.strip().lower()

        records: list[dict[str, Any]] = []
        total = 0

        if isinstance(root, list):
            if not query:
                total = len(root)
                start = (page - 1) * page_size
                end = min(total, start + page_size)
                for idx in range(start, end):
                    record = root[idx]
                    rid, title, summary = self._record_meta_from_list_item(record, idx)
                    records.append(
                        {
                            "record_id": rid,
                            "title": title,
                            "summary": summary,
                        }
                    )
            else:
                start = (page - 1) * page_size
                end = start + page_size
                matched = 0
                for idx, record in enumerate(root):
                    rid, title, summary = self._record_meta_from_list_item(record, idx)
                    text_blob = f"{rid} {title} {summary} {self._search_blob(record)}"
                    if query not in text_blob.lower():
                        continue
                    if matched >= start and matched < end:
                        records.append(
                            {
                                "record_id": rid,
                                "title": title,
                                "summary": summary,
                            }
                        )
                    matched += 1
                total = matched

        elif isinstance(root, dict):
            keys = list(root.keys())
            if query:
                keys = [
                    k
                    for k in keys
                    if query in f"{k} {self._search_blob(root.get(k))}".lower()
                ]
            total = len(keys)
            start = (page - 1) * page_size
            end = min(total, start + page_size)
            for key in keys[start:end]:
                value = root[key]
                records.append(
                    {
                        "record_id": str(key),
                        "title": str(key),
                        "summary": _short_text(self._summary_from_obj(value)),
                    }
                )
        else:
            total = 1
            if page == 1:
                records.append(
                    {
                        "record_id": "__root__",
                        "title": "root",
                        "summary": _short_text(self._summary_from_obj(root)),
                    }
                )

        self._record_count_cache[source_id] = total
        self.sources[source_id].record_count = total
        return {
            "source": self._source_to_dict(source),
            "records": records,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_record(self, source_id: str, record_id: str) -> dict[str, Any]:
        source = self.get_source(source_id)
        parsed = self._parse_source(source)
        record = self._resolve_record(parsed.root_data, record_id)
        fields = self._build_fields(record["value"])
        return {
            "source": self._source_to_dict(source),
            "record_id": record["record_id"],
            "title": record["title"],
            "fields": fields,
            "raw_json": json.dumps(record["value"], ensure_ascii=False, indent=2),
        }

    def preview_record_diff(
        self,
        source_id: str,
        record_id: str,
        fields: dict[str, Any] | None = None,
        raw_json: str = "",
        mode: str = "form",
    ) -> dict[str, Any]:
        source = self.get_source(source_id)
        parsed = self._parse_source(source)
        resolved = self._resolve_record(parsed.root_data, record_id)
        before_obj = resolved["value"]
        after_obj = self._apply_record_update(
            before_obj=before_obj,
            fields=fields or {},
            raw_json=raw_json,
            mode=mode,
        )
        before_text = json.dumps(before_obj, ensure_ascii=False, indent=2, sort_keys=True)
        after_text = json.dumps(after_obj, ensure_ascii=False, indent=2, sort_keys=True)
        diff = "".join(
            difflib.unified_diff(
                before_text.splitlines(keepends=True),
                after_text.splitlines(keepends=True),
                fromfile="before",
                tofile="after",
                n=2,
            )
        )
        return {"diff": diff, "changed": before_text != after_text}

    def save_record(
        self,
        source_id: str,
        record_id: str,
        fields: dict[str, Any] | None = None,
        raw_json: str = "",
        mode: str = "form",
    ) -> dict[str, Any]:
        source = self.get_source(source_id)
        if not source.editable:
            raise ValueError(source.readonly_reason or "Source is read-only.")

        parsed = self._parse_source(source)
        root = parsed.root_data
        resolved = self._resolve_record(root, record_id)
        before_obj = resolved["value"]
        after_obj = self._apply_record_update(
            before_obj=before_obj,
            fields=fields or {},
            raw_json=raw_json,
            mode=mode,
        )
        resolved["setter"](after_obj)
        if "wrapper" in resolved:
            root = resolved["wrapper"]["value"]

        file_text = self._serialize_source(parsed, root)
        parse_validated = self._validate_serialized(source.format, file_text)

        rel = source.file_path.relative_to(SITE_DIR).as_posix()
        rebuild_targets: list[Path] = []
        if rel.startswith("TextMap/GI_shards/"):
            rebuild_targets.append(textmap_shards.GAME_MAP["gi"]["mono_file"])
        elif rel.startswith("TextMap/SR_shards/"):
            rebuild_targets.append(textmap_shards.GAME_MAP["sr"]["mono_file"])

        backup_dir = _create_backup_dir()
        _backup_file(source.file_path, backup_dir)
        for target in rebuild_targets:
            if target.exists():
                _backup_file(target, backup_dir)

        source.file_path.write_text(file_text, encoding="utf-8")

        meta = {
            "type": "cms-save",
            "source_id": source_id,
            "record_id": record_id,
            "file_path": source.file_path.relative_to(ROOT_DIR).as_posix(),
            "saved_at": dt.datetime.now().isoformat(),
            "mode": mode,
        }

        rebuilt_files: list[str] = []
        if rel.startswith("TextMap/GI_shards/"):
            out = textmap_shards.rebuild_from_shards("gi")
            rebuilt_files.append(out.relative_to(ROOT_DIR).as_posix())
        elif rel.startswith("TextMap/SR_shards/"):
            out = textmap_shards.rebuild_from_shards("sr")
            rebuilt_files.append(out.relative_to(ROOT_DIR).as_posix())

        if rebuilt_files:
            for rel_path in rebuilt_files:
                meta.setdefault("rebuilt_files", []).append(rel_path)

        _write_backup_meta(backup_dir, meta)
        self.refresh_registry()

        return {
            "ok": True,
            "backup_id": backup_dir.name,
            "changed_files": [source.file_path.relative_to(ROOT_DIR).as_posix(), *rebuilt_files],
            "parse_validated": parse_validated,
            "message": f"Saved record {record_id}. Backup: {backup_dir.name}",
        }

    def search_global(self, q: str, limit: int = 200) -> dict[str, Any]:
        query = q.strip()
        if not query:
            return {"query": "", "results": []}
        results: list[dict[str, Any]] = []
        for source in self.sources.values():
            if len(results) >= limit:
                break
            if not source.editable:
                continue
            try:
                payload = self.list_records(
                    source_id=source.id,
                    q=query,
                    page=1,
                    page_size=min(20, max(1, limit - len(results))),
                )
            except Exception:
                continue
            for row in payload["records"]:
                results.append(
                    {
                        "source_id": source.id,
                        "record_id": row["record_id"],
                        "title": row["title"],
                        "summary": row["summary"],
                    }
                )
                if len(results) >= limit:
                    break
        return {"query": query, "results": results}

    def rebuild_index(self) -> dict[str, Any]:
        ok = 0
        failed = 0
        for source in self.sources.values():
            try:
                count = self._fast_count(source)
                self._record_count_cache[source.id] = count
                self.sources[source.id].record_count = count
                ok += 1
            except Exception:
                failed += 1
        return {"ok": ok, "failed": failed}

    def _fast_count(self, source: SourceMeta) -> int:
        if source.format == "html":
            return 1
        if source.format == "json":
            data = json.loads(source.file_path.read_text(encoding="utf-8"))
            if isinstance(data, (list, dict)):
                return len(data)
            return 1
        text = source.file_path.read_text(encoding="utf-8", errors="ignore")
        if _looks_like_html(text):
            return 1
        # Fast index mode for js-var: count top-level var assignments.
        # Deep per-record indexing still happens lazily in list_records/get_record.
        return len(re.findall(r"\bvar\s+[A-Za-z_$][A-Za-z0-9_$]*\s*=", text))

    def _derive_dimensions(self, rel: str) -> tuple[str, str, str]:
        parts = rel.split("/")
        if len(parts) >= 2 and parts[0] == "gi":
            game = "gi"
            locale = parts[1].upper()
            category = parts[2] if len(parts) >= 4 else Path(parts[-1]).stem
            return game, locale, category
        if len(parts) >= 2 and parts[0] == "data":
            game = "sr"
            locale = parts[1].upper()
            category = parts[2] if len(parts) >= 4 else Path(parts[-1]).stem
            return game, locale, category
        if parts[0] == "TextMap":
            name = Path(parts[-1]).name
            if name.startswith("GI") or (len(parts) >= 2 and parts[1] == "GI_shards"):
                game = "gi"
            elif name.startswith("SR") or (len(parts) >= 2 and parts[1] == "SR_shards"):
                game = "sr"
            else:
                game = "global"
            locale = "CH+EN"
            category = parts[1] if len(parts) >= 2 else "TextMap"
            return game, locale, category
        return "global", "N/A", Path(parts[-1]).stem

    @staticmethod
    def _derive_format(path: Path) -> str:
        ext = path.suffix.lower()
        if ext == ".json":
            return "json"
        if ext == ".html":
            return "html"
        return "js-var"

    def _parse_source(self, source: SourceMeta) -> ParsedSource:
        stat = source.file_path.stat()
        mtime_ns = int(stat.st_mtime_ns)
        cached_mtime = self._source_mtime_cache.get(source.id)
        if cached_mtime == mtime_ns:
            # Lightweight: parse on demand, cache only mtime + counts.
            # We intentionally do not keep large file objects in memory.
            pass

        if source.format == "json":
            root = json.loads(source.file_path.read_text(encoding="utf-8"))
            self._source_mtime_cache[source.id] = mtime_ns
            return ParsedSource(meta=source, root_data=root, js_var_order=None)

        if source.format == "html":
            text = source.file_path.read_text(encoding="utf-8", errors="ignore")
            self._source_mtime_cache[source.id] = mtime_ns
            return ParsedSource(meta=source, root_data=text, js_var_order=None)

        var_order, values = _run_node_eval_js_vars(source.file_path)
        if len(var_order) == 1:
            root = values.get(var_order[0])
        else:
            root = values
        self._source_mtime_cache[source.id] = mtime_ns
        return ParsedSource(meta=source, root_data=root, js_var_order=var_order)

    def _serialize_source(self, parsed: ParsedSource, root: Any) -> str:
        if parsed.meta.format == "json":
            return json.dumps(root, ensure_ascii=False, indent=4) + "\n"
        if parsed.meta.format == "html":
            return str(root)
        if not parsed.js_var_order:
            raise ValueError("Missing js_var_order for js-var serialization.")
        if len(parsed.js_var_order) == 1:
            assignments = [(parsed.js_var_order[0], root)]
        else:
            if not isinstance(root, dict):
                raise ValueError("Multi-var JS source requires dict root object.")
            assignments = [(name, root.get(name)) for name in parsed.js_var_order]
        return _auto_generated_content(assignments)

    @staticmethod
    def _validate_serialized(fmt: str, text: str) -> bool:
        if fmt == "json":
            json.loads(text)
            return True
        if fmt == "html":
            return True
        if not text.startswith("// Auto Generated"):
            raise ValueError("Serialized JS content missing auto-generated header.")
        return True

    def _record_meta_from_list_item(self, record: Any, idx: int) -> tuple[str, str, str]:
        base_id = str(idx)
        title = f"#{idx}"
        summary = _short_text(self._summary_from_obj(record))
        if isinstance(record, dict):
            for key in ("_id", "id", "H", "I"):
                if key in record and record[key] is not None:
                    base_id = str(record[key])
                    break
            title = str(record.get("Name") or record.get("Title") or base_id)
            summary = _short_text(
                str(
                    record.get("Desc")
                    or record.get("Summary")
                    or record.get("C")
                    or record.get("E")
                    or record.get("T")
                    or record.get("S")
                    or self._summary_from_obj(record)
                )
            )
        return f"{base_id}@{idx}", title, summary

    def _resolve_record(self, root: Any, record_id: str) -> dict[str, Any]:
        if isinstance(root, list):
            idx = self._resolve_list_index(root, record_id)
            if idx < 0 or idx >= len(root):
                raise ValueError(f"Record not found: {record_id}")

            def setter(value: Any) -> None:
                root[idx] = value

            _, title, _ = self._record_meta_from_list_item(root[idx], idx)
            return {
                "record_id": record_id,
                "title": title,
                "value": root[idx],
                "setter": setter,
            }

        if isinstance(root, dict):
            if record_id not in root:
                raise ValueError(f"Record not found: {record_id}")

            def setter(value: Any) -> None:
                root[record_id] = value

            return {
                "record_id": record_id,
                "title": record_id,
                "value": root[record_id],
                "setter": setter,
            }

        if record_id not in {"__root__", "root"}:
            raise ValueError(f"Record not found: {record_id}")

        wrapper = {"value": root}

        def setter(value: Any) -> None:
            wrapper["value"] = value

        return {
            "record_id": "__root__",
            "title": "root",
            "value": wrapper["value"],
            "setter": setter,
            "wrapper": wrapper,
        }

    def _resolve_list_index(self, rows: list[Any], record_id: str) -> int:
        if "@" in record_id:
            suffix = record_id.rsplit("@", 1)[1]
            if suffix.isdigit():
                return int(suffix)
        for idx, row in enumerate(rows):
            rid, _, _ = self._record_meta_from_list_item(row, idx)
            if rid == record_id:
                return idx
        raise ValueError(f"Record not found: {record_id}")

    @staticmethod
    def _build_fields(value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, dict):
            return []
        out: list[dict[str, Any]] = []
        for key, val in value.items():
            if isinstance(val, (dict, list)):
                continue
            text = "" if val is None else str(val)
            ftype = "textarea" if len(text) > 100 or "\n" in text else "text"
            out.append({"key": key, "label": key, "type": ftype, "value": text})
        return out

    def _apply_record_update(
        self,
        before_obj: Any,
        fields: dict[str, Any],
        raw_json: str,
        mode: str,
    ) -> Any:
        if mode == "raw":
            if not raw_json.strip():
                raise ValueError("raw_json is empty.")
            return json.loads(raw_json)

        if not isinstance(before_obj, dict):
            if raw_json.strip():
                return json.loads(raw_json)
            raise ValueError("Form mode only supports object records.")

        out = json.loads(json.dumps(before_obj, ensure_ascii=False))
        for key, value in fields.items():
            prev = out.get(key)
            out[key] = self._coerce_value(str(value), prev)
        return out

    @staticmethod
    def _coerce_value(raw: str, prev: Any) -> Any:
        if isinstance(prev, bool):
            return raw.strip().lower() in {"1", "true", "yes", "on", "y", "是"}
        if isinstance(prev, int):
            try:
                return int(raw)
            except ValueError:
                return prev
        if isinstance(prev, float):
            try:
                return float(raw)
            except ValueError:
                return prev
        if prev is None and raw.strip().lower() == "null":
            return None
        return raw

    @staticmethod
    def _summary_from_obj(value: Any) -> str:
        if isinstance(value, dict):
            preferred = ["Name", "Title", "Desc", "Summary", "C", "E", "T", "S"]
            for key in preferred:
                if key in value and value[key]:
                    return str(value[key])
            parts = []
            for key, v in value.items():
                if isinstance(v, (dict, list)):
                    continue
                parts.append(f"{key}:{v}")
                if len(parts) >= 5:
                    break
            return " | ".join(parts)
        if isinstance(value, list):
            return f"List({len(value)})"
        return str(value)

    @staticmethod
    def _search_blob(value: Any, budget: int = 3000) -> str:
        chunks: list[str] = []

        def walk(node: Any) -> None:
            if len(" ".join(chunks)) >= budget:
                return
            if isinstance(node, dict):
                for k, v in node.items():
                    chunks.append(str(k))
                    walk(v)
            elif isinstance(node, list):
                for x in node[:30]:
                    walk(x)
            elif node is not None:
                chunks.append(str(node))

        walk(value)
        text = " ".join(chunks)
        if len(text) > budget:
            return text[:budget]
        return text

    @staticmethod
    def _source_to_dict(source: SourceMeta) -> dict[str, Any]:
        return {
            "id": source.id,
            "game": source.game,
            "locale": source.locale,
            "category": source.category,
            "file_path": str(source.file_path),
            "format": source.format,
            "editable": source.editable,
            "readonly_reason": source.readonly_reason,
            "record_count": source.record_count,
            "size_bytes": source.file_path.stat().st_size if source.file_path.exists() else 0,
            "hash_hint": hashlib.md5(source.id.encode("utf-8")).hexdigest()[:10],
        }
