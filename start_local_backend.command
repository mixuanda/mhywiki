#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

DEFAULT_PORT="${PORT:-9000}"
LOG_DIR="easy_updates"
LOG_FILE="${LOG_DIR}/local_backend.log"
PID_FILE="${LOG_DIR}/local_backend.pid"
PORT_FILE="${LOG_DIR}/local_backend.port"

mkdir -p "${LOG_DIR}"

is_port_in_use() {
  local port="$1"
  lsof -nP -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1
}

local_admin_pid_by_port() {
  local port="$1"
  local pids
  pids="$(lsof -nP -iTCP:"${port}" -sTCP:LISTEN -t 2>/dev/null || true)"
  if [ -z "${pids}" ]; then
    return 1
  fi
  for pid in ${pids}; do
    if ps -p "${pid}" -o command= | grep -q "scripts/local_admin.py"; then
      echo "${pid}"
      return 0
    fi
  done
  return 1
}

choose_port() {
  local start="$1"
  local port
  port="${start}"
  while [ "${port}" -le 9099 ]; do
    if ! is_port_in_use "${port}"; then
      echo "${port}"
      return 0
    fi
    port=$((port + 1))
  done
  return 1
}

open_pages() {
  local port="$1"
  open "http://localhost:${port}/__admin" >/dev/null 2>&1 || true
  open "http://localhost:${port}/index/" >/dev/null 2>&1 || true
}

port="${DEFAULT_PORT}"
existing_pid=""
if existing_pid="$(local_admin_pid_by_port "${port}" 2>/dev/null)"; then
  echo "${existing_pid}" > "${PID_FILE}"
  echo "${port}" > "${PORT_FILE}"
  echo "后台已在运行: PID ${existing_pid}, 端口 ${port}"
  echo "Admin:   http://localhost:${port}/__admin"
  echo "Preview: http://localhost:${port}/index/"
  open_pages "${port}"
  exit 0
fi

if is_port_in_use "${port}"; then
  alt_port="$(choose_port $((port + 1)) || true)"
  if [ -z "${alt_port}" ]; then
    echo "启动失败：${port}-9099 端口都被占用。"
    exit 1
  fi
  port="${alt_port}"
fi

nohup python3 scripts/local_admin.py --port "${port}" > "${LOG_FILE}" 2>&1 &
pid="$!"

ok=0
for _ in $(seq 1 80); do
  if curl -sS -m 1 "http://localhost:${port}/__admin/api/status" >/dev/null 2>&1; then
    ok=1
    break
  fi
  if ! kill -0 "${pid}" 2>/dev/null; then
    break
  fi
  sleep 0.25
done

if [ "${ok}" -ne 1 ]; then
  echo "启动失败，请查看日志: ${LOG_FILE}"
  tail -n 60 "${LOG_FILE}" || true
  kill "${pid}" >/dev/null 2>&1 || true
  exit 1
fi

echo "${pid}" > "${PID_FILE}"
echo "${port}" > "${PORT_FILE}"

echo "后台启动成功: PID ${pid}, 端口 ${port}"
echo "Admin:   http://localhost:${port}/__admin"
echo "Preview: http://localhost:${port}/index/"
echo "日志: ${LOG_FILE}"

open_pages "${port}"
