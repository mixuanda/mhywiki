#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

VAR_RE = re.compile(r"^\s*(?:var|let|const)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=", re.MULTILINE)
DEFAULT_BANNED_FIELD_KEYWORDS = {
    "story",
    "voice",
    "cv",
    "quest",
    "chapter",
    "readable",
    "dialog",
    "talk",
    "cutscene",
}


class DataParseError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "unknown"


def _looks_like_html(text: str) -> bool:
    stripped = text.lstrip().lower()
    return stripped.startswith("<!doctype html") or stripped.startswith("<html")


def parse_js_literal(blob: str, *, context: str = "<inline>") -> Any:
    try:
        return json.loads(blob)
    except json.JSONDecodeError:
        return _parse_js_literal_with_node(blob, context=context)


def _parse_js_literal_with_node(blob: str, *, context: str) -> Any:
    script = (
        "const fs = require('node:fs');"
        "const src = fs.readFileSync(0, 'utf8');"
        "let out;"
        "try { out = (0, eval)('(' + src + ')'); }"
        "catch (err) { console.error(String(err)); process.exit(2); }"
        "process.stdout.write(JSON.stringify(out));"
    )
    try:
        result = subprocess.run(
            ["node", "-e", script],
            input=blob,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise DataParseError(
            f"Failed to parse non-JSON JS literal in {context}: Node.js is required"
        ) from exc

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise DataParseError(
            f"Failed to parse non-JSON JS literal in {context}: {stderr or 'unknown error'}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise DataParseError(f"Node parse output is not JSON in {context}") from exc


def parse_js_assignments(path: Path) -> dict[str, Any]:
    text = read_text(path)
    if _looks_like_html(text):
        raise DataParseError(f"Not a JS data file: {path}")

    matches = list(VAR_RE.finditer(text))
    if not matches:
        raise DataParseError(f"No JS variable assignments found: {path}")

    out: dict[str, Any] = {}
    for index, match in enumerate(matches):
        var_name = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blob = text[start:end].strip()
        if blob.endswith(";"):
            blob = blob[:-1].rstrip()
        out[var_name] = parse_js_literal(blob, context=f"{path}:{var_name}")
    return out


def parse_js_var(path: Path, var_name: str, default: Any = None) -> Any:
    values = parse_js_assignments(path)
    return values.get(var_name, default)


def drop_non_combat_fields(
    payload: Any,
    banned_keywords: Iterable[str] = DEFAULT_BANNED_FIELD_KEYWORDS,
) -> Any:
    banned = tuple(k.lower() for k in banned_keywords)

    if isinstance(payload, list):
        compacted = [drop_non_combat_fields(item, banned) for item in payload]
        return [item for item in compacted if item not in (None, {}, [])]

    if isinstance(payload, dict):
        filtered: dict[str, Any] = {}
        for key, value in payload.items():
            lowered = str(key).lower()
            if any(token in lowered for token in banned):
                continue
            cleaned = drop_non_combat_fields(value, banned)
            if cleaned in (None, {}, []):
                continue
            filtered[key] = cleaned
        return filtered

    return payload


def normalize_id(value: Any) -> str:
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not value.is_integer():
            return slugify(str(value))
        return str(int(value))
    return str(value).strip()
