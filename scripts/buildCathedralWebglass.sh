#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
TMP="${RUNNER_TEMP:-/tmp}"
SOURCE_SHA="${SOURCE_SHA:-${GITHUB_SHA:-local}}"
GODOT_TEMPLATE_ID="4.7.2.stable"
APK="build/android/luhmos-cathedral-atelier-1.0.25.apk"
PCK="build/android/luhmos-cathedral-atelier-1.0.25.pck"

SDKMANAGER="$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager"
yes | "$SDKMANAGER" --licenses >/dev/null || true
"$SDKMANAGER" 'platform-tools' 'build-tools;36.1.0' 'platforms;android-36'

curl -fL --retry 5 -o "$TMP/godot.zip" https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64.zip
curl -fL --retry 5 -o "$TMP/templates.tpz" https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_export_templates.tpz
echo "cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4  $TMP/godot.zip" | sha256sum -c -
echo "f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011  $TMP/templates.tpz" | sha256sum -c -
rm -rf "$TMP/godot" "$TMP/tpl"
unzip -q "$TMP/godot.zip" -d "$TMP/godot"
GODOT="$TMP/godot/Godot_v4.7.2-stable_linux.x86_64"
chmod +x "$GODOT"
TEMPLATE_DIR="$HOME/.local/share/godot/export_templates/$GODOT_TEMPLATE_ID"
mkdir -p "$TEMPLATE_DIR" "$HOME/.config/godot"
unzip -q "$TMP/templates.tpz" -d "$TMP/tpl"
cp -a "$TMP/tpl/templates/." "$TEMPLATE_DIR/"
printf '[gd_resource type="EditorSettings" format=3]\n[resource]\nexport/android/android_sdk_path = "%s"\nexport/android/java_sdk_path = "%s"\n' "$ANDROID_HOME" "$JAVA_HOME" > "$HOME/.config/godot/editor_settings-4.tres"

KEYSTORE="$TMP/luhm-cathedral-atelier-debug.keystore"
keytool -genkeypair -keystore "$KEYSTORE" -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname 'CN=LuHm Cathedral Oni Atelier Candidate,O=LuHm OS,C=US'
chmod 600 "$KEYSTORE"
export GODOT_ANDROID_KEYSTORE_DEBUG_PATH="$KEYSTORE"
export GODOT_ANDROID_KEYSTORE_DEBUG_USER=androiddebugkey
export GODOT_ANDROID_KEYSTORE_DEBUG_PASSWORD=android

# Pinned Professor-approved Lum donor.
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
  if curl -fL --retry 4 --retry-all-errors --connect-timeout 20 --max-time 240 -A 'Mozilla/5.0 LuHmOS-CI' -o "$BUNDLE" "$url" && test -s "$BUNDLE"; then break; fi
done
echo "$BUNDLE_SHA  $BUNDLE" | sha256sum -c -
rm -rf "$OUT" && mkdir -p "$OUT" assets/lum
unzip -q "$BUNDLE" -d "$OUT"
BASE="$OUT/Meshy_AI_Lum_Midnight_1996_biped/Meshy_AI_Lum_Midnight_1996_biped_Character_output.glb"
RUN="$OUT/Meshy_AI_Lum_Midnight_1996_biped/Meshy_AI_Lum_Midnight_1996_biped_Animation_Running_withSkin.glb"
echo "$BASE_SHA  $BASE" | sha256sum -c -
echo "$RUN_SHA  $RUN" | sha256sum -c -
cp "$BASE" assets/lum/luhm.glb
cp "$RUN" assets/lum/luhmRunning.glb

python3 -m json.tool doctrine/cathedralWebglassFinal-20260926.json >/dev/null
python3 -m json.tool doctrine/oniAtelierBodyForge-20260926.json >/dev/null
python3 scripts/auditCathedralWebglass.py
python3 tests/testCandidateGate.py
python3 tools/candidateGate.py
python3 tools/communityAssetAudit.py
python3 tools/stageCommunityAssets.py
python3 - <<'PY'
import json
from pathlib import Path
r=json.loads(Path('build/community-assets/receipt.json').read_text())
assert r['asset_count']==77, r['asset_count']
assert r['license']=='CC0'
assert r['runtime_network'] is False
assert r['total_asset_bytes'] <= 8*1024*1024
print('COMMUNITY_ASSETS=GREEN',r['asset_count'],r['total_asset_bytes'])
PY

(
  cd cockpit
  npm ci --ignore-scripts --no-audit --no-fund
  npm run check
  npm run stage:vendor
)
ASSETS=native/kaiwebview/kaiwebview/src/main/assets/cockpit
rm -rf "$ASSETS" && mkdir -p "$ASSETS"
cp cockpit/index.html cockpit/app.js cockpit/styles.css "$ASSETS/"
cp -a cockpit/jquery cockpit/cms cockpit/vendor "$ASSETS/"
test -s "$ASSETS/vendor/jquery/jquery.min.js"
test -s "$ASSETS/vendor/jquery-ui/jquery-ui.min.js"
test -s "$ASSETS/vendor/bootstrap/bootstrap.bundle.min.js"
test -s "$ASSETS/vendor/vue/vue.global.prod.js"
test -s "$ASSETS/jquery/luhm.atelier.js"

ANDROID_SOURCE="$(find "$TEMPLATE_DIR" -type f -name 'android_source.zip' -print -quit)"
test -n "$ANDROID_SOURCE"
rm -rf android/build
mkdir -p android/build
unzip -q "$ANDROID_SOURCE" -d android/build
chmod +x android/build/gradlew
printf '%s\n' "$GODOT_TEMPLATE_ID" > android/.build_version
android/build/gradlew -p native/kaiwebview :kaiwebview:assembleDebug :kaiwebview:assembleRelease --no-daemon
mkdir -p addons/kai_webview/bin
cp native/kaiwebview/kaiwebview/build/outputs/aar/kaiwebview-debug.aar addons/kai_webview/bin/kaiwebview-debug.aar
cp native/kaiwebview/kaiwebview/build/outputs/aar/kaiwebview-release.aar addons/kai_webview/bin/kaiwebview-release.aar
test -s addons/kai_webview/bin/kaiwebview-debug.aar

"$GODOT" --headless --editor --path . --quit
"$GODOT" --headless --path . --script tests/communityAssetSmoke.gd
"$GODOT" --headless --path . --script tests/characterCreatorSmoke.gd
python3 tools/runGodotSmoke.py "$GODOT" runtimeSmoke
python3 tools/runGodotSmoke.py "$GODOT" lumRigV2Phase1Smoke

mkdir -p build/android
"$GODOT" --headless --path . --export-debug 'Android Proposed' "$APK"
"$GODOT" --headless --path . --export-pack 'Android Proposed' "$PCK"
test -s "$APK" && test -s "$PCK"
"$GODOT" --headless --main-pack "$PCK" --script res://tests/communityAssetSmoke.gd
"$GODOT" --headless --main-pack "$PCK" --script res://tests/characterCreatorSmoke.gd

BT="$ANDROID_HOME/build-tools/36.1.0"
"$BT/aapt" dump badging "$APK" | tee build/android/badging.txt
"$BT/aapt" dump xmltree "$APK" AndroidManifest.xml | tee build/android/manifest.txt
"$BT/apksigner" verify --verbose --print-certs "$APK" | tee build/android/signature.txt
"$BT/zipalign" -c -P 16 -v 4 "$APK" > build/android/zipalign.txt
unzip -l "$APK" | tee build/android/ziplist.txt
sha256sum "$APK" | tee build/android/sha256.txt
grep -q "package: name='art.eggiebagelface.luhmos.cathedraltoy.atelier'" build/android/badging.txt
grep -q "versionCode='125'" build/android/badging.txt
grep -q 'org.godotengine.plugin.v2.KAIWebView' build/android/manifest.txt
grep -q 'assets/cockpit/index.html' build/android/ziplist.txt
grep -q 'assets/cockpit/jquery/luhm.atelier.js' build/android/ziplist.txt
grep -q 'assets/cockpit/vendor/jquery/jquery.min.js' build/android/ziplist.txt
grep -q 'assets/cockpit/vendor/vue/vue.global.prod.js' build/android/ziplist.txt
! grep -R -nE 'addJavascriptInterface|allowUniversalAccessFromFileURLs|allowFileAccessFromFileURLs|MIXED_CONTENT_ALWAYS_ALLOW' native/kaiwebview
! grep -R -nE '(sk-proj-|AIza|hf_[A-Za-z0-9]{20,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY)' native/kaiwebview cockpit scripts/platform scripts/game

cp build/community-assets/receipt.json build/android/community-assets-receipt.json
cp assets/community/selected-assets.json build/android/community-assets-selection.json
cp doctrine/oniAtelierBodyForge-20260926.json build/android/oni-atelier-doctrine.json
printf '%s\n' "$SOURCE_SHA" > build/android/source-commit.txt
printf 'source_sha=%s\nworkflow=%s\nrun_id=%s\nstatus=CATHEDRAL_ONI_ATELIER_CI_PROOF\npackage=art.eggiebagelface.luhmos.cathedraltoy.atelier\nversion=1.0.25-cathedral.atelier.1\n' "$SOURCE_SHA" "${GITHUB_WORKFLOW:-local}" "${GITHUB_RUN_ID:-local}" > build/android/cathedral-atelier-receipt.txt
cp cockpit/package-lock.json build/android/package-lock.json
sha256sum addons/kai_webview/bin/kaiwebview-debug.aar cockpit/package-lock.json >> build/android/source-components-sha256.txt
rm -f "$PCK"

rm -rf build/installPortal
python3 tools/stageInstallPortal.py --apk "$APK" --out build/installPortal --commit "$SOURCE_SHA"
(cd build/installPortal && sha256sum -c SHA256SUMS.txt)

echo 'CATHEDRAL ONI ATELIER APK BUILD GREEN'
