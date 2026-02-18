#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/local_admin.py --port 9000
