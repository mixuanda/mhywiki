#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/textmap_shards.py init
echo
echo "Press Enter to close..."
read -r _
