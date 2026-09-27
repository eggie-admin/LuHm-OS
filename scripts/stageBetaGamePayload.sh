#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
TMP="${RUNNER_TEMP:-/tmp}/luhm-beta-payload"
rm -rf "$TMP"
mkdir -p "$TMP" assets/lum

# Stage the exact rigged Lum payload already used by the proven Cathedral build.
DRIVE_ID='1FenqwXoCWTkcwvv-2ANUloMaTC7zVSen'
BUNDLE_SHA='fedaf37220d5f9477560fdc0b5624d30e95191db989f5b8428ca4d1a19b1d3da'
BASE_SHA='06bdfcc196e147c4cb92c7c5489110a8feb30ee8a8f362fac585802eced33b69'
RUN_SHA='750f54b2b3618767bdad3f9399a2f0cb8be70b46e39a65affe178b4745c964f0'
BUNDLE="$TMP/lum-biped.zip"
OUT="$TMP/lum-biped"
for url in \
  "https://drive.usercontent.google.com/download?id=${DRIVE_ID}&export=download&confirm=t" \
  "https://drive.google.com/uc?export=download&id=${DRIVE_ID}&confirm=t"; do
  rm -f "$BUNDLE"
  if curl -fL --retry 4 --retry-all-errors --connect-timeout 20 --max-time 240 -A 'Mozilla/5.0 LuHmOS-BetaCI' -o "$BUNDLE" "$url" && test -s "$BUNDLE"; then
    break
  fi
done
echo "$BUNDLE_SHA  $BUNDLE" | sha256sum -c -
mkdir -p "$OUT"
unzip -q "$BUNDLE" -d "$OUT"
BASE="$OUT/Meshy_AI_Lum_Midnight_1996_biped/Meshy_AI_Lum_Midnight_1996_biped_Character_output.glb"
RUN="$OUT/Meshy_AI_Lum_Midnight_1996_biped/Meshy_AI_Lum_Midnight_1996_biped_Animation_Running_withSkin.glb"
echo "$BASE_SHA  $BASE" | sha256sum -c -
echo "$RUN_SHA  $RUN" | sha256sum -c -
cp "$BASE" assets/lum/luhm.glb
cp "$RUN" assets/lum/luhmRunning.glb

# Stage the exact rights-cleared 77-asset runtime set used by the Cathedral build.
python3 tools/communityAssetAudit.py
python3 tools/stageCommunityAssets.py
python3 - <<'PY'
import json
from pathlib import Path
r=json.loads(Path('build/community-assets/receipt.json').read_text())
assert r['asset_count'] == 77, r
assert r['license'] == 'CC0', r
assert r['runtime_network'] is False, r
print('BETA_GAME_PAYLOAD=STAGED lum=rigged community_assets=77')
PY
