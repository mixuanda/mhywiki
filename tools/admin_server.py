#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import secrets
import time
import urllib.error
import urllib.request
from functools import wraps
from pathlib import Path
from typing import Any

from flask import Flask, abort, jsonify, request, send_from_directory

from ingest_human_text import ingest_entity
from legacy_sync import GI_ENTITY_DIRS, SR_ENTITY_DIRS, sync_entity, write_canonical_entity
from normalize import read_json, write_json


def _entity_file(data_root: Path, game: str, kind: str, entity_id: str) -> Path:
    if game == "gi":
        if kind not in GI_ENTITY_DIRS:
            raise ValueError(f"Unsupported GI entity kind: {kind}")
        rel = GI_ENTITY_DIRS[kind]
    elif game == "sr":
        if kind not in SR_ENTITY_DIRS:
            raise ValueError(f"Unsupported SR entity kind: {kind}")
        rel = SR_ENTITY_DIRS[kind]
    else:
        raise ValueError(f"Unsupported game: {game}")
    return data_root / rel / f"{entity_id}.json"


def _entity_dir(data_root: Path, game: str, kind: str) -> Path:
    if game == "gi":
        if kind not in GI_ENTITY_DIRS:
            raise ValueError(f"Unsupported GI entity kind: {kind}")
        rel = GI_ENTITY_DIRS[kind]
    elif game == "sr":
        if kind not in SR_ENTITY_DIRS:
            raise ValueError(f"Unsupported SR entity kind: {kind}")
        rel = SR_ENTITY_DIRS[kind]
    else:
        raise ValueError(f"Unsupported game: {game}")
    return data_root / rel


def _rebuild_index(data_root: Path, game: str, kind: str) -> Path:
    directory = _entity_dir(data_root, game, kind)
    rows: list[dict[str, Any]] = []
    for file_path in sorted(directory.glob("*.json")):
        if file_path.name == "index.json":
            continue
        try:
            payload = read_json(file_path)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(payload, dict):
            rows.append(
                {
                    "id": payload.get("id", file_path.stem),
                    "name": payload.get("name") or payload.get("title") or file_path.stem,
                    "path": file_path.name,
                }
            )
        else:
            rows.append({"id": file_path.stem, "name": file_path.stem, "path": file_path.name})
    index_path = directory / "index.json"
    write_json(index_path, rows)
    return index_path


def _json_response(payload: dict[str, Any], status: int = 200):
    return jsonify(payload), status


def _github_request(method: str, url: str, token: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "homdgcat-admin-server",
    }
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url=url, method=method, headers=headers, data=data)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"GitHub API {exc.code}: {raw}") from exc


def _parse_repo(repo: str) -> tuple[str, str]:
    parts = repo.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("repo must be in format owner/name")
    return parts[0], parts[1]


def create_app(*, project_root: Path, web_root: Path, data_root: Path, admin_password: str) -> Flask:
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False

    issued_tokens: dict[str, float] = {}

    def _token_ok(token: str) -> bool:
        now = time.time()
        exp = issued_tokens.get(token)
        if not exp:
            return False
        if exp < now:
            issued_tokens.pop(token, None)
            return False
        return True

    def _auth_required(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            token = ""
            if auth.startswith("Bearer "):
                token = auth[7:].strip()
            if not token:
                token = request.cookies.get("admin_token", "")
            if not token or not _token_ok(token):
                return _json_response({"ok": False, "error": "unauthorized"}, 401)
            return func(*args, **kwargs)

        return wrapped

    @app.route("/api/health", methods=["GET"])
    def api_health():
        return _json_response(
            {
                "ok": True,
                "webRoot": str(web_root),
                "dataRoot": str(data_root),
                "serverTime": int(time.time()),
            }
        )

    @app.route("/api/login", methods=["POST"])
    def api_login():
        payload = request.get_json(silent=True) or {}
        provided = str(payload.get("password", ""))
        if not admin_password:
            return _json_response({"ok": False, "error": "admin password is not configured"}, 500)
        if provided != admin_password:
            return _json_response({"ok": False, "error": "invalid password"}, 401)

        raw = f"{provided}:{secrets.token_hex(16)}:{time.time()}".encode("utf-8")
        token = hashlib.sha256(raw).hexdigest()
        issued_tokens[token] = time.time() + 60 * 60 * 12
        resp, status = _json_response({"ok": True, "token": token, "expiresInSeconds": 43200})
        resp.set_cookie("admin_token", token, httponly=True, samesite="Lax")
        return resp, status

    @app.route("/api/logout", methods=["POST"])
    @_auth_required
    def api_logout():
        auth = request.headers.get("Authorization", "")
        token = auth[7:].strip() if auth.startswith("Bearer ") else request.cookies.get("admin_token", "")
        issued_tokens.pop(token, None)
        resp, status = _json_response({"ok": True})
        resp.delete_cookie("admin_token")
        return resp, status

    @app.route("/api/ingest", methods=["POST"])
    @_auth_required
    def api_ingest():
        payload = request.get_json(silent=True) or {}
        game = str(payload.get("game", "")).strip()
        kind = str(payload.get("kind", "")).strip()
        text = str(payload.get("text", "")).strip()
        if not game or not kind or not text:
            return _json_response({"ok": False, "error": "game/kind/text are required"}, 400)

        apply_changes = bool(payload.get("apply", False))
        try:
            result = ingest_entity(
                data_root=data_root,
                web_root=web_root,
                game=game,
                kind=kind,
                entity_id=payload.get("id"),
                name=payload.get("name"),
                text=text,
                apply_changes=apply_changes,
            )
        except Exception as exc:  # noqa: BLE001
            return _json_response({"ok": False, "error": str(exc)}, 400)
        return _json_response({"ok": True, "result": result})

    @app.route("/api/sync", methods=["POST"])
    @_auth_required
    def api_sync():
        payload = request.get_json(silent=True) or {}
        game = str(payload.get("game", "")).strip()
        kind = str(payload.get("kind", "")).strip()
        entity_id = str(payload.get("id", "")).strip()
        if not game or not kind or not entity_id:
            return _json_response({"ok": False, "error": "game/kind/id are required"}, 400)
        try:
            result = sync_entity(
                data_root=data_root,
                web_root=web_root,
                game=game,
                kind=kind,
                entity_id=entity_id,
            )
        except Exception as exc:  # noqa: BLE001
            return _json_response({"ok": False, "error": str(exc)}, 400)
        return _json_response(
            {
                "ok": True,
                "changedFiles": [str(p) for p in result.changed_files],
                "notes": result.notes,
            }
        )

    @app.route("/api/entity/<game>/<kind>/<entity_id>", methods=["GET"])
    @_auth_required
    def api_get_entity(game: str, kind: str, entity_id: str):
        try:
            path = _entity_file(data_root, game, kind, entity_id)
        except Exception as exc:  # noqa: BLE001
            return _json_response({"ok": False, "error": str(exc)}, 400)
        if not path.exists():
            return _json_response({"ok": False, "error": "entity not found"}, 404)
        try:
            data = read_json(path)
        except Exception as exc:  # noqa: BLE001
            return _json_response({"ok": False, "error": str(exc)}, 500)
        return _json_response({"ok": True, "path": str(path), "entity": data})

    @app.route("/api/entity/upsert", methods=["POST"])
    @_auth_required
    def api_upsert_entity():
        payload = request.get_json(silent=True) or {}
        game = str(payload.get("game", "")).strip()
        kind = str(payload.get("kind", "")).strip()
        raw_id = str(payload.get("id", "")).strip()
        entity = payload.get("entity")
        apply_sync = bool(payload.get("sync", True))
        if not game or not kind:
            return _json_response({"ok": False, "error": "game/kind are required"}, 400)
        if not isinstance(entity, dict):
            return _json_response({"ok": False, "error": "entity object is required"}, 400)

        entity_id = raw_id or str(entity.get("id", "")).strip()
        if not entity_id:
            return _json_response({"ok": False, "error": "id is required (payload.id or entity.id)"}, 400)

        try:
            to_write = dict(entity)
            to_write["id"] = entity_id
            to_write.setdefault("game", game)
            canonical_path = write_canonical_entity(
                data_root=data_root,
                game=game,
                kind=kind,
                entity_id=entity_id,
                payload=to_write,
            )
            index_path = _rebuild_index(data_root, game, kind)

            changed_files: list[str] = [str(canonical_path), str(index_path)]
            notes: list[str] = []
            if apply_sync:
                sync_result = sync_entity(
                    data_root=data_root,
                    web_root=web_root,
                    game=game,
                    kind=kind,
                    entity_id=entity_id,
                )
                changed_files.extend(str(p) for p in sync_result.changed_files)
                notes.extend(sync_result.notes)

            return _json_response(
                {
                    "ok": True,
                    "canonicalPath": str(canonical_path),
                    "indexPath": str(index_path),
                    "changedFiles": changed_files,
                    "notes": notes,
                }
            )
        except Exception as exc:  # noqa: BLE001
            return _json_response({"ok": False, "error": str(exc)}, 400)

    @app.route("/api/github/pr-from-local", methods=["POST"])
    @_auth_required
    def api_github_pr_from_local():
        payload = request.get_json(silent=True) or {}
        token = str(payload.get("token", "")).strip()
        repo = str(payload.get("repo", "")).strip()
        base_branch = str(payload.get("base", "main")).strip() or "main"
        title = str(payload.get("title", "")).strip()
        body = str(payload.get("body", "")).strip()
        paths = payload.get("paths", [])
        if not token or not repo or not title or not isinstance(paths, list) or not paths:
            return _json_response(
                {"ok": False, "error": "token/repo/title/paths are required"},
                400,
            )

        try:
            owner, repo_name = _parse_repo(repo)
            repo_api = f"https://api.github.com/repos/{owner}/{repo_name}"

            base_ref = _github_request("GET", f"{repo_api}/git/ref/heads/{base_branch}", token)
            base_sha = base_ref["object"]["sha"]
            new_branch = str(payload.get("head", "")).strip() or f"admin-update-{int(time.time())}"

            _github_request(
                "POST",
                f"{repo_api}/git/refs",
                token,
                {"ref": f"refs/heads/{new_branch}", "sha": base_sha},
            )

            committed_paths: list[str] = []
            for rel in paths:
                rel_path = str(rel).strip().lstrip("/")
                abs_path = (project_root / rel_path).resolve()
                if not str(abs_path).startswith(str(project_root.resolve())):
                    raise RuntimeError(f"Refuse to read outside project: {rel_path}")
                if not abs_path.exists():
                    raise RuntimeError(f"File not found: {rel_path}")
                content = abs_path.read_text(encoding="utf-8")
                encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
                content_api = f"{repo_api}/contents/{rel_path}"

                sha = None
                try:
                    existing = _github_request(
                        "GET",
                        f"{content_api}?ref={new_branch}",
                        token,
                    )
                    sha = existing.get("sha")
                except RuntimeError:
                    sha = None

                commit_payload = {
                    "message": f"admin: update {rel_path}",
                    "content": encoded,
                    "branch": new_branch,
                }
                if sha:
                    commit_payload["sha"] = sha
                _github_request("PUT", content_api, token, commit_payload)
                committed_paths.append(rel_path)

            pr = _github_request(
                "POST",
                f"{repo_api}/pulls",
                token,
                {
                    "title": title,
                    "body": body,
                    "head": new_branch,
                    "base": base_branch,
                },
            )
            return _json_response(
                {
                    "ok": True,
                    "branch": new_branch,
                    "committedPaths": committed_paths,
                    "pullRequestUrl": pr.get("html_url"),
                    "pullRequestNumber": pr.get("number"),
                }
            )
        except Exception as exc:  # noqa: BLE001
            return _json_response({"ok": False, "error": str(exc)}, 400)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def static_files(path: str):
        candidate = (web_root / path).resolve()
        if path and str(candidate).startswith(str(web_root.resolve())) and candidate.is_file():
            return send_from_directory(web_root, path)
        if path and str(candidate).startswith(str(web_root.resolve())) and candidate.is_dir():
            index_file = candidate / "index.html"
            if index_file.exists():
                rel = str(index_file.relative_to(web_root))
                return send_from_directory(web_root, rel)
        if not path:
            index_file = web_root / "index.html"
            if index_file.exists():
                return send_from_directory(web_root, "index.html")
        abort(404)

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local admin API + static web server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3000)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--web", default="./web")
    parser.add_argument("--data", default="./combat-wiki/data")
    parser.add_argument(
        "--password",
        default=os.getenv("ADMIN_PASSWORD", "admin123"),
        help="Admin password (or set ADMIN_PASSWORD env)",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    web_root = Path(args.web).resolve()
    data_root = Path(args.data).resolve()
    password = args.password

    if not web_root.is_dir():
        raise NotADirectoryError(f"Web root not found: {web_root}")
    if not data_root.is_dir():
        raise NotADirectoryError(f"Data root not found: {data_root}")
    if not password:
        raise ValueError("Admin password is required. Use --password or ADMIN_PASSWORD env.")
    if password == "admin123":
        print("[admin] using default password: admin123 (set ADMIN_PASSWORD to override)")

    app = create_app(
        project_root=project_root,
        web_root=web_root,
        data_root=data_root,
        admin_password=password,
    )
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
