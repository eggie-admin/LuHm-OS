#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GODOT_VERSION=4.7.2-stable
GODOT_ZIP=/tmp/luhm-godot-web.zip
TEMPLATES_TPZ=/tmp/luhm-godot-web-templates.tpz
GODOT_DIR=/tmp/luhm-godot-web
TEMPLATE_DIR="$HOME/.local/share/godot/export_templates/4.7.2.stable"
GODOT_BIN="$GODOT_DIR/Godot_v4.7.2-stable_linux.x86_64"

curl -fL --retry 5 -o "$GODOT_ZIP" \
  "https://github.com/godotengine/godot/releases/download/${GODOT_VERSION}/Godot_v4.7.2-stable_linux.x86_64.zip"
curl -fL --retry 5 -o "$TEMPLATES_TPZ" \
  "https://github.com/godotengine/godot/releases/download/${GODOT_VERSION}/Godot_v4.7.2-stable_export_templates.tpz"
echo 'cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4  /tmp/luhm-godot-web.zip' | sha256sum -c -
echo 'f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011  /tmp/luhm-godot-web-templates.tpz' | sha256sum -c -
rm -rf "$GODOT_DIR" /tmp/luhm-godot-web-tpl
mkdir -p "$GODOT_DIR" /tmp/luhm-godot-web-tpl "$TEMPLATE_DIR"
unzip -q "$GODOT_ZIP" -d "$GODOT_DIR"
unzip -q "$TEMPLATES_TPZ" -d /tmp/luhm-godot-web-tpl
chmod +x "$GODOT_BIN"
cp -a /tmp/luhm-godot-web-tpl/templates/. "$TEMPLATE_DIR/"

# Public web export firewall:
# Keep private/right-uncleared donor GLBs out of the hosted Godot player.
# Private donor inspection remains in isolated, review-only CI workflows.
mkdir -p assets/lum
python3 tools/godot-public-asset-firewall-audit.py
python3 tools/canonAssetBuildAudit.py
echo 'PUBLIC_GODOT_ASSETS=PROCEDURAL_FALLBACK_ONLY'

PARSE_LOG=/tmp/luhm-godot-parse.log
set +e
"$GODOT_BIN" --headless --editor --path . --quit 2>&1 | tee "$PARSE_LOG"
GODOT_EDITOR_STATUS=${PIPESTATUS[0]}
set -e
if [[ "$GODOT_EDITOR_STATUS" -ne 0 ]] || grep -Eq 'SCRIPT ERROR:|ERROR: Failed to load script' "$PARSE_LOG"; then
  echo 'RED_GODOT_PARSE_GATE'
  exit 1
fi
echo 'GREEN_GODOT_PARSE_GATE'
"$GODOT_BIN" --headless --path . --script res://tools/godot-public-asset-firewall-smoke.gd

if [[ "${LUHM_WEB_SKIP_SMOKE:-0}" != "1" ]]; then
  python3 tools/runGodotSmoke.py "$GODOT_BIN" layoutSmoke
  python3 tools/runGodotSmoke.py "$GODOT_BIN" runtimeSmoke
  echo 'SKIP_LUM_DONOR_SMOKE=PRIVATE_REVIEW_WORKFLOW_ONLY'
else
  echo 'RENDER_BUILD_MODE: runtime smoke skipped; exact-source CI remains authoritative for runtime smoke proof'
fi

rm -rf host/harness/godot-export
mkdir -p host/harness/godot-export
"$GODOT_BIN" --headless --path . --export-release 'Web Harness' host/harness/godot-export/index.html

test -s host/harness/godot-export/index.html
find host/harness/godot-export -maxdepth 1 -type f -name '*.wasm' -size +0c | grep -q .
find host/harness/godot-export -maxdepth 1 -type f -name '*.pck' -size +0c | grep -q .
(
  cd host/harness/godot-export
  find . -maxdepth 1 -type f ! -name SHA256SUMS.txt -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
  sha256sum -c SHA256SUMS.txt
)
echo 'GREEN_GODOT_WEB_HARNESS_EXPORT'
