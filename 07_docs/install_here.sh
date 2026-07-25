#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-$HOME/DISU_POLARIS_WS/DISU_WS}"

mkdir -p "$TARGET"
cp -a "$SCRIPT_DIR"/. "$TARGET"/
rm -f "$TARGET/install_here.sh"

echo "설치 완료: $TARGET"
echo "cd \"$TARGET\" && code ."
