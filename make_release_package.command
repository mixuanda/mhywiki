#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p releases
stamp="$(date +%Y%m%d_%H%M%S)"
zip_path="releases/site_${stamp}.zip"
sum_path="releases/SHA256SUMS.txt"
echo "Creating $zip_path ..."
ditto -c -k --sequesterRsrc --keepParent site "$zip_path"
shasum -a 256 "$zip_path" >> "$sum_path"
echo "Done: $zip_path"
echo "Updated checksums: $sum_path"
echo
echo "Press Enter to close..."
read -r _
