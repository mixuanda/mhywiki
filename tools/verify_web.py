#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable

from normalize import parse_js_assignments


CORE_ROUTES = [
    "/",
    "/index/",
    "/gi/char/",
    "/gi/monster/",
    "/gi/banner/",
    "/gi/abyss/",
    "/gi/3boss/",
    "/gi/ach/",
    "/gi/tut/",
    "/gi/change/",
    "/gi/formulae/",
    "/sr/char/",
    "/sr/monster/",
    "/sr/banner/",
    "/sr/chaos/",
    "/sr/fiction/",
    "/sr/shadow/",
    "/sr/arbitration/",
    "/sr/du/",
    "/sr/du31/",
    "/sr/ach/",
    "/sr/stage/",
    "/sr/effect/",
    "/sr/change/",
    "/sr/future/",
    "/sr/formulae/",
    "/sr/linecount/",
    "/yhb/",
    "/admin/",
]

BLOCKED_ROUTES = [
    "/yunli/",
    "/sr/yunli2/",
    "/sr/yunli4/",
    "/sr/yunli5/",
    "/gi/quest/",
    "/sr/readable/",
    "/about/",
]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _http_get(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url=url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            return resp.getcode(), body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        return exc.code, body


def _extract_local_refs(html: str) -> list[str]:
    refs: list[str] = []
    for value in re.findall(r"""(?:src|href)=["']([^"']+)["']""", html):
        if value.startswith(("http://", "https://", "mailto:", "javascript:", "data:", "#")):
            continue
        if value.startswith("//"):
            continue
        refs.append(value)
    return refs


def _resolve_ref(web_root: Path, route: str, ref: str) -> Path:
    pure = ref.split("?", 1)[0].split("#", 1)[0]
    if pure.startswith("/"):
        return (web_root / pure.lstrip("/")).resolve()
    route_dir = route
    if not route_dir.endswith("/"):
        route_dir = route_dir.rsplit("/", 1)[0] + "/"
    joined = urllib.parse.urljoin(route_dir, pure)
    return (web_root / joined.lstrip("/")).resolve()


def _verify_resources(web_root: Path, route: str, html: str) -> list[str]:
    issues: list[str] = []
    for ref in _extract_local_refs(html):
        if ref.startswith("/cdn-cgi/"):
            # Upstream Cloudflare runtime scripts are not required for functionality.
            continue
        target = _resolve_ref(web_root, route, ref)
        if not str(target).startswith(str(web_root.resolve())):
            issues.append(f"{route}: suspicious path traversal ref `{ref}`")
            continue
        if not target.exists():
            issues.append(f"{route}: missing local asset `{ref}` -> `{target.relative_to(web_root)}`")
    return issues


def _verify_character_details(web_root: Path) -> list[str]:
    issues: list[str] = []

    gi_avatar = parse_js_assignments(web_root / "gi" / "CH" / "avatar.js")
    gi_rows = gi_avatar.get("__AvatarInfoConfig", [])
    if isinstance(gi_rows, list) and gi_rows:
        sample = gi_rows[0]
        code_name = str(sample.get("_name", "")).strip()
        if not code_name:
            issues.append("GI character list exists but first row has empty `_name`.")
        else:
            file_1 = web_root / "gi" / "CH" / "Avatar" / f"{code_name}_1.js"
            file_2 = web_root / "gi" / "CH" / "Avatar" / f"{code_name}_2.js"
            if not file_1.exists():
                issues.append(f"Missing GI character detail file: {file_1.relative_to(web_root)}")
            if not file_2.exists():
                issues.append(f"Missing GI character detail file: {file_2.relative_to(web_root)}")
            if file_1.exists():
                d1 = parse_js_assignments(file_1)
                for key in ["_AvatarDataConfig_", "_AvatarMats_", "_AvatarSkillPConfig_", "_AvatarAttackConfig_"]:
                    if key not in d1:
                        issues.append(f"{file_1.relative_to(web_root)} missing `{key}`")
            if file_2.exists():
                d2 = parse_js_assignments(file_2)
                for key in ["_AvatarFetterConfig_", "_AvatarCostumeConfig_", "acs_cache_"]:
                    if key not in d2:
                        issues.append(f"{file_2.relative_to(web_root)} missing `{key}`")
    else:
        issues.append("GI character list (`__AvatarInfoConfig`) is empty.")

    sr_avatar = parse_js_assignments(web_root / "data" / "CH" / "Avatar.js")
    sr_rows = sr_avatar.get("_avatar", [])
    if isinstance(sr_rows, list) and sr_rows:
        sample = sr_rows[0]
        sid = sample.get("_id")
        if sid is None:
            issues.append("SR character list exists but first row has empty `_id`.")
        else:
            file_sr = web_root / "data" / "CH" / "Avatar" / f"{sid}.js"
            if not file_sr.exists():
                issues.append(f"Missing SR character detail file: {file_sr.relative_to(web_root)}")
            else:
                d = parse_js_assignments(file_sr)
                for key in [
                    "_avatarskill_",
                    "_avatarskilltree_",
                    "_avatarrank_",
                    "_story_",
                    "_voice_",
                    "_notes_",
                    "_adiff_",
                    "_mtc_",
                ]:
                    if key not in d:
                        issues.append(f"{file_sr.relative_to(web_root)} missing `{key}`")
    else:
        issues.append("SR character list (`_avatar`) is empty.")

    return issues


def _start_server(web_root: Path, port: int) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd=web_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def _wait_server(base_url: str, timeout_sec: float = 8.0) -> None:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            code, _ = _http_get(base_url + "/")
            if code in {200, 301, 302, 404}:
                return
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.2)
    raise TimeoutError("Timed out waiting for local web server.")


def run_checks(web_root: Path, base_url: str) -> list[str]:
    issues: list[str] = []

    for route in CORE_ROUTES:
        code, body = _http_get(base_url + route)
        if code != 200:
            issues.append(f"{route} expected 200, got {code}")
            continue
        issues.extend(_verify_resources(web_root, route, body))

    for route in BLOCKED_ROUTES:
        code, _ = _http_get(base_url + route)
        if code == 200:
            issues.append(f"{route} expected non-200 (blocked), got 200")

    issues.extend(_verify_character_details(web_root))
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify legacy web routes and resource integrity.")
    parser.add_argument("--web", default="./web", help="Web root directory")
    parser.add_argument("--base-url", help="Optional running server base URL, e.g. http://127.0.0.1:3000")
    args = parser.parse_args()

    web_root = Path(args.web).resolve()
    if not web_root.is_dir():
        raise NotADirectoryError(f"Web root not found: {web_root}")

    server_proc: subprocess.Popen[str] | None = None
    if args.base_url:
        base_url = args.base_url.rstrip("/")
    else:
        port = _free_port()
        base_url = f"http://127.0.0.1:{port}"
        server_proc = _start_server(web_root, port)
        _wait_server(base_url)

    try:
        issues = run_checks(web_root, base_url)
    finally:
        if server_proc is not None:
            with contextlib.suppress(Exception):
                server_proc.terminate()
                server_proc.wait(timeout=3)
            with contextlib.suppress(Exception):
                if server_proc.poll() is None:
                    server_proc.kill()

    if issues:
        print(f"[verify-web] FAILED with {len(issues)} issue(s)")
        for issue in issues[:300]:
            print(f"- {issue}")
        if len(issues) > 300:
            print(f"- ... {len(issues) - 300} more")
        sys.exit(1)

    print("[verify-web] OK: routes, resources, and character detail structures passed")


if __name__ == "__main__":
    main()
