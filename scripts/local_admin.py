#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, unquote, urlparse

import content_cms
import content_simple_entities as simple_entities


ROOT_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT_DIR / "site"
ADMIN_HTML_PATH = Path(__file__).resolve().parent / "admin_simple.html"

ADMIN_HTML = ADMIN_HTML_PATH.read_text(encoding="utf-8")

SIMPLE_REPO = None
SIMPLE_REPO_ERROR = ""
try:
    SIMPLE_REPO = simple_entities.SimpleEntityRepository()
except Exception as exc:
    SIMPLE_REPO_ERROR = str(exc)

CMS_REPO = None
CMS_REPO_ERROR = ""
CMS_REPO_INITIALIZED = False


def ensure_cms_repo() -> bool:
    global CMS_REPO, CMS_REPO_ERROR, CMS_REPO_INITIALIZED
    if CMS_REPO_INITIALIZED:
        return CMS_REPO is not None
    CMS_REPO_INITIALIZED = True
    try:
        CMS_REPO = content_cms.UniversalCMSRepository()
        CMS_REPO_ERROR = ""
    except Exception as exc:
        CMS_REPO_ERROR = str(exc)
        CMS_REPO = None
    return CMS_REPO is not None

REPO_LOCK = Lock()


def _response_charset_type(path: Path, default_ctype: str) -> str:
    ext = path.suffix.lower()
    if ext == ".html":
        return "text/html; charset=utf-8"
    if ext == ".js":
        return "application/javascript; charset=utf-8"
    if ext == ".css":
        return "text/css; charset=utf-8"
    if ext == ".json":
        return "application/json; charset=utf-8"
    if ext in {".txt", ".xml"}:
        return f"{default_ctype}; charset=utf-8"
    return default_ctype


class Handler(BaseHTTPRequestHandler):
    server_version = "HomDGCatLocalAdmin/3.2"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path in {"/__admin", "/__admin/"}:
            self._send_html(ADMIN_HTML)
            return

        if path == "/__admin/api/status":
            with REPO_LOCK:
                payload = {
                    "site_dir": str(SITE_DIR),
                    "backups": simple_entities.backup_status(),
                    "simple_ready": bool(SIMPLE_REPO),
                    "simple_error": SIMPLE_REPO_ERROR,
                    "simple_counts": SIMPLE_REPO.counts() if SIMPLE_REPO else {},
                    "cms_ready": bool(CMS_REPO),
                    "cms_error": CMS_REPO_ERROR if CMS_REPO_INITIALIZED else "CMS lazy mode (not initialized)",
                }
            self._send_json(payload)
            return

        if path == "/__admin/api/catalog":
            if SIMPLE_REPO is None:
                self._send_json(
                    {"error": f"Simple repository unavailable: {SIMPLE_REPO_ERROR}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            game = (query.get("game", ["sr"])[0] or "sr").strip().lower()
            locale = (query.get("locale", ["CH"])[0] or "CH").strip().upper()
            kind = (query.get("kind", ["character"])[0] or "character").strip().lower()
            q = (query.get("q", [""])[0] or "").strip()
            try:
                with REPO_LOCK:
                    items = SIMPLE_REPO.list_items(game=game, locale=locale, kind=kind, query=q)
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"items": items, "total": len(items)})
            return

        if path == "/__admin/api/item":
            if SIMPLE_REPO is None:
                self._send_json(
                    {"error": f"Simple repository unavailable: {SIMPLE_REPO_ERROR}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            game = (query.get("game", ["sr"])[0] or "sr").strip().lower()
            locale = (query.get("locale", ["CH"])[0] or "CH").strip().upper()
            kind = (query.get("kind", ["character"])[0] or "character").strip().lower()
            item_id = (query.get("id", [""])[0] or "").strip()
            if not item_id:
                self._send_json({"error": "Missing id"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                with REPO_LOCK:
                    item = SIMPLE_REPO.get_item(
                        game=game,
                        locale=locale,
                        kind=kind,
                        item_id=item_id,
                    )
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"item": item})
            return

        # v2 API compatibility (advanced/general CMS)
        if path == "/__admin/api/v2/sources":
            if not ensure_cms_repo():
                self._send_json(
                    {"error": f"CMS repository unavailable: {CMS_REPO_ERROR}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            game = (query.get("game", [""])[0] or "").strip().lower()
            locale = (query.get("locale", [""])[0] or "").strip().upper()
            q = (query.get("q", [""])[0] or "").strip()
            with REPO_LOCK:
                sources = CMS_REPO.list_sources(game=game, locale=locale, q=q)
            self._send_json({"sources": sources})
            return

        if path == "/__admin/api/v2/records":
            if not ensure_cms_repo():
                self._send_json(
                    {"error": f"CMS repository unavailable: {CMS_REPO_ERROR}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            source_id = (query.get("source_id", [""])[0] or "").strip()
            q = (query.get("q", [""])[0] or "").strip()
            page_raw = (query.get("page", ["1"])[0] or "1").strip()
            page_size_raw = (query.get("page_size", ["50"])[0] or "50").strip()
            if not source_id:
                self._send_json({"error": "Missing source_id"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                page = int(page_raw)
                page_size = int(page_size_raw)
                with REPO_LOCK:
                    payload = CMS_REPO.list_records(source_id=source_id, q=q, page=page, page_size=page_size)
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json(payload)
            return

        if path == "/__admin/api/v2/record":
            if not ensure_cms_repo():
                self._send_json(
                    {"error": f"CMS repository unavailable: {CMS_REPO_ERROR}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            source_id = (query.get("source_id", [""])[0] or "").strip()
            record_id = (query.get("record_id", [""])[0] or "").strip()
            if not source_id or not record_id:
                self._send_json({"error": "Missing source_id or record_id"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                with REPO_LOCK:
                    record = CMS_REPO.get_record(source_id=source_id, record_id=record_id)
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"record": record})
            return

        self._serve_site(path, head_only=False)

    def do_HEAD(self) -> None:
        path = urlparse(self.path).path
        if path in {"/__admin", "/__admin/"}:
            raw = ADMIN_HTML.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            return
        self._serve_site(path, head_only=True)

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path == "/__admin/api/reload":
            try:
                with REPO_LOCK:
                    if SIMPLE_REPO is not None:
                        SIMPLE_REPO.refresh()
                    if CMS_REPO is not None:
                        CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"message": "reloaded"})
            return

        if path == "/__admin/api/item":
            if SIMPLE_REPO is None:
                self._send_json(
                    {"error": f"Simple repository unavailable: {SIMPLE_REPO_ERROR}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            body = self._read_json()
            game = str(body.get("game", "sr")).strip().lower()
            locale = str(body.get("locale", "CH")).strip().upper()
            kind = str(body.get("kind", "character")).strip().lower()
            item_id = str(body.get("id", "")).strip()
            fields = body.get("fields", {})
            if not item_id:
                self._send_json({"error": "Missing id"}, HTTPStatus.BAD_REQUEST)
                return
            if not isinstance(fields, dict):
                self._send_json({"error": "fields must be object"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                with REPO_LOCK:
                    backup_name = SIMPLE_REPO.save_item(
                        game=game,
                        locale=locale,
                        kind=kind,
                        item_id=item_id,
                        fields={k: str(v) for k, v in fields.items()},
                    )
                    if CMS_REPO is not None:
                        CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"message": f"保存成功，备份: {backup_name}"})
            return

        if path == "/__admin/api/item/record/save":
            if SIMPLE_REPO is None:
                self._send_json(
                    {"error": f"Simple repository unavailable: {SIMPLE_REPO_ERROR}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            body = self._read_json()
            game = str(body.get("game", "sr")).strip().lower()
            locale = str(body.get("locale", "CH")).strip().upper()
            item_id = str(body.get("id", "")).strip()
            record_ref = body.get("record_ref", {})
            value = body.get("value")
            if not item_id:
                self._send_json({"error": "Missing id"}, HTTPStatus.BAD_REQUEST)
                return
            if not isinstance(record_ref, dict):
                self._send_json({"error": "record_ref must be object"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                with REPO_LOCK:
                    backup_name = SIMPLE_REPO.save_character_record(
                        game=game,
                        locale=locale,
                        item_id=item_id,
                        record_ref=record_ref,
                        value=value,
                    )
                    if CMS_REPO is not None:
                        CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"message": f"保存成功，备份: {backup_name}"})
            return

        if path == "/__admin/api/item/record/add":
            if SIMPLE_REPO is None:
                self._send_json(
                    {"error": f"Simple repository unavailable: {SIMPLE_REPO_ERROR}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            body = self._read_json()
            game = str(body.get("game", "sr")).strip().lower()
            locale = str(body.get("locale", "CH")).strip().upper()
            item_id = str(body.get("id", "")).strip()
            record_ref = body.get("record_ref", {})
            mode = str(body.get("mode", "")).strip().lower()
            key = str(body.get("key", "")).strip()
            value = body.get("value")
            index_raw = body.get("index")
            index = None
            if index_raw is not None and index_raw != "":
                try:
                    index = int(index_raw)
                except Exception:
                    self._send_json({"error": "index must be integer"}, HTTPStatus.BAD_REQUEST)
                    return
            if not item_id:
                self._send_json({"error": "Missing id"}, HTTPStatus.BAD_REQUEST)
                return
            if not isinstance(record_ref, dict):
                self._send_json({"error": "record_ref must be object"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                with REPO_LOCK:
                    backup_name = SIMPLE_REPO.add_character_record(
                        game=game,
                        locale=locale,
                        item_id=item_id,
                        record_ref=record_ref,
                        mode=mode,
                        key=key,
                        value=value,
                        index=index,
                    )
                    if CMS_REPO is not None:
                        CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"message": f"新增成功，备份: {backup_name}"})
            return

        if path == "/__admin/api/item/record/delete":
            if SIMPLE_REPO is None:
                self._send_json(
                    {"error": f"Simple repository unavailable: {SIMPLE_REPO_ERROR}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            body = self._read_json()
            game = str(body.get("game", "sr")).strip().lower()
            locale = str(body.get("locale", "CH")).strip().upper()
            item_id = str(body.get("id", "")).strip()
            record_ref = body.get("record_ref", {})
            mode = str(body.get("mode", "")).strip().lower()
            key = str(body.get("key", "")).strip()
            index_raw = body.get("index")
            index = None
            if index_raw is not None and index_raw != "":
                try:
                    index = int(index_raw)
                except Exception:
                    self._send_json({"error": "index must be integer"}, HTTPStatus.BAD_REQUEST)
                    return
            if not item_id:
                self._send_json({"error": "Missing id"}, HTTPStatus.BAD_REQUEST)
                return
            if not isinstance(record_ref, dict):
                self._send_json({"error": "record_ref must be object"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                with REPO_LOCK:
                    backup_name = SIMPLE_REPO.delete_character_record(
                        game=game,
                        locale=locale,
                        item_id=item_id,
                        record_ref=record_ref,
                        mode=mode,
                        key=key,
                        index=index,
                    )
                    if CMS_REPO is not None:
                        CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"message": f"删除成功，备份: {backup_name}"})
            return

        if path == "/__admin/api/undo":
            try:
                with REPO_LOCK:
                    message = simple_entities.undo_latest_backup()
                    if SIMPLE_REPO is not None:
                        SIMPLE_REPO.refresh()
                    if CMS_REPO is not None:
                        CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"code": 1, "message": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"code": 0, "message": message})
            return

        # v2 API compatibility
        if path == "/__admin/api/v2/record/save":
            if not ensure_cms_repo():
                self._send_json(
                    {"error": f"CMS repository unavailable: {CMS_REPO_ERROR}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            body = self._read_json()
            source_id = str(body.get("source_id", "")).strip()
            record_id = str(body.get("record_id", "")).strip()
            mode = str(body.get("mode", "form")).strip().lower() or "form"
            fields = body.get("fields", {})
            raw_json = str(body.get("raw_json", ""))
            if not source_id or not record_id:
                self._send_json({"error": "Missing source_id or record_id"}, HTTPStatus.BAD_REQUEST)
                return
            if not isinstance(fields, dict):
                self._send_json({"error": "fields must be object"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                with REPO_LOCK:
                    payload = CMS_REPO.save_record(
                        source_id=source_id,
                        record_id=record_id,
                        fields=fields,
                        raw_json=raw_json,
                        mode=mode,
                    )
                    if SIMPLE_REPO is not None:
                        SIMPLE_REPO.refresh()
                    CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json(payload)
            return

        if path == "/__admin/api/v2/record/preview-diff":
            if not ensure_cms_repo():
                self._send_json(
                    {"error": f"CMS repository unavailable: {CMS_REPO_ERROR}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            body = self._read_json()
            source_id = str(body.get("source_id", "")).strip()
            record_id = str(body.get("record_id", "")).strip()
            mode = str(body.get("mode", "form")).strip().lower() or "form"
            fields = body.get("fields", {})
            raw_json = str(body.get("raw_json", ""))
            if not source_id or not record_id:
                self._send_json({"error": "Missing source_id or record_id"}, HTTPStatus.BAD_REQUEST)
                return
            if not isinstance(fields, dict):
                self._send_json({"error": "fields must be object"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                with REPO_LOCK:
                    payload = CMS_REPO.preview_record_diff(
                        source_id=source_id,
                        record_id=record_id,
                        fields=fields,
                        raw_json=raw_json,
                        mode=mode,
                    )
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json(payload)
            return

        if path == "/__admin/api/v2/search-global":
            if not ensure_cms_repo():
                self._send_json(
                    {"error": f"CMS repository unavailable: {CMS_REPO_ERROR}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            body = self._read_json()
            q = str(body.get("q", "")).strip()
            limit = int(body.get("limit", 200) or 200)
            try:
                with REPO_LOCK:
                    payload = CMS_REPO.search_global(q=q, limit=limit)
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json(payload)
            return

        if path == "/__admin/api/v2/undo":
            if not ensure_cms_repo():
                self._send_json(
                    {"error": f"CMS repository unavailable: {CMS_REPO_ERROR}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            body = self._read_json()
            backup_id = str(body.get("backup_id", "")).strip() or None
            try:
                with REPO_LOCK:
                    message = content_cms.undo_backup(backup_id=backup_id)
                    if SIMPLE_REPO is not None:
                        SIMPLE_REPO.refresh()
                    CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"code": 1, "message": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"code": 0, "message": message})
            return

        if path == "/__admin/api/v2/rebuild-index":
            if not ensure_cms_repo():
                self._send_json(
                    {"error": f"CMS repository unavailable: {CMS_REPO_ERROR}"},
                    HTTPStatus.BAD_REQUEST,
                )
                return
            try:
                with REPO_LOCK:
                    payload = CMS_REPO.rebuild_index()
                    if SIMPLE_REPO is not None:
                        SIMPLE_REPO.refresh()
                    CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json(payload)
            return

        self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def _serve_site(self, path: str, head_only: bool = False) -> None:
        if not SITE_DIR.exists():
            self._send_text("site/ directory not found.", HTTPStatus.NOT_FOUND)
            return

        if path == "/":
            self._redirect("/index/")
            return
        if path == "/home":
            self._redirect("/index/")
            return

        rel = unquote(path).lstrip("/")
        target = (SITE_DIR / rel).resolve()
        site_root = SITE_DIR.resolve()
        if site_root not in target.parents and target != site_root:
            self._send_text("Invalid path", HTTPStatus.BAD_REQUEST)
            return

        if target.is_dir():
            target = target / "index.html"
        elif not target.is_file() and (target / "index.html").is_file():
            target = target / "index.html"

        if not target.exists() or not target.is_file():
            self._send_text("404 Not Found", HTTPStatus.NOT_FOUND)
            return

        guessed = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        ctype = _response_charset_type(target, guessed)

        try:
            raw = target.read_bytes()
        except OSError:
            self._send_text("500 Internal Server Error", HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if not head_only:
            self._safe_write(raw)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self._safe_write(raw)

    def _send_html(self, html: str) -> None:
        raw = html.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self._safe_write(raw)

    def _send_text(self, text: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self._safe_write(raw)

    def _safe_write(self, raw: bytes) -> None:
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError, OSError):
            return

    def _redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", location)
        self.end_headers()

    def log_message(self, fmt: str, *args) -> None:
        return


def main() -> int:
    parser = argparse.ArgumentParser(description="HomDGCat local simple visual backend")
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()

    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    print("=" * 60)
    print("HomDGCat Local Simple Backend")
    print("=" * 60)
    print(f"Website: http://localhost:{args.port}/index/")
    print(f"Admin:   http://localhost:{args.port}/__admin")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
