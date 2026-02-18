#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/content_manager.py apply
echo
echo "Press Enter to close..."
read -r _
