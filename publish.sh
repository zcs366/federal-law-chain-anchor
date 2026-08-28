#!/usr/bin/env bash
# publish.sh — 从本地立法史链生成锚并推送到本仓库（在链宿主机上运行）
# 用法: ./publish.sh [anchor-gen 之后自动调用，或手动]
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
ANCHOR_SRC="$HOME/.hermes/federal/anchors/latest_anchor.json"
ANCHOR_DST="$REPO_DIR/anchors/anchor-latest.json"

test -f "$ANCHOR_SRC" || { echo "anchor not found: $ANCHOR_SRC (run anchor_gen.py first)"; exit 1; }
mkdir -p "$REPO_DIR/anchors"
cp "$ANCHOR_SRC" "$ANCHOR_DST"

cd "$REPO_DIR"
git add anchors/anchor-latest.json
tip=$(python3 -c "import json;a=json.load(open('anchors/anchor-latest.json'));print(a['tip_event_id'],a['tip_hash'])")
git commit -m "anchor: $tip" || echo "anchor unchanged"
git push origin master
echo "✅ published: $tip"
