#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GODOT_TEMPLATE_ID="4.7.2.stable"
SDKMANAGER="$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager"
yes | "$SDKMANAGER" --licenses >/dev/null || true
"$SDKMANAGER" 'platform-tools' 'build-tools;36.1.0' 'platforms;android-36'

python3 tools/auditSamsungHarness.py
python3 tools/auditFinalInstallRoute.py

curl -fL --retry 5 -o /tmp/godot.zip https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64.zip
curl -fL --retry 5 -o /tmp/templates.tpz https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_export_templates.tpz
echo 'cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4  /tmp/godot.zip' | sha256sum -c -
echo 'f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011  /tmp/templates.tpz' | sha256sum -c -
rm -rf /tmp/godot /tmp/tpl
unzip -q /tmp/godot.zip -d /tmp/godot
GODOT=/tmp/godot/Godot_v4.7.2-stable_linux.x86_64
chmod +x "$GODOT"
TEMPLATE_DIR="$HOME/.local/share/godot/export_templates/$GODOT_TEMPLATE_ID"
mkdir -p "$TEMPLATE_DIR"
unzip -q /tmp/templates.tpz -d /tmp/tpl
cp -a /tmp/tpl/templates/. "$TEMPLATE_DIR/"
mkdir -p "$HOME/.config/godot"
printf '[gd_resource type="EditorSettings" format=3]\n[resource]\nexport/android/android_sdk_path = "%s"\nexport/android/java_sdk_path = "%s"\n' "$ANDROID_HOME" "$JAVA_HOME" > "$HOME/.config/godot/editor_settings-4.tres"

KEYSTORE="$RUNNER_TEMP/luhm-kai9000-proposed-debug.keystore"
keytool -genkeypair -keystore "$KEYSTORE" -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname 'CN=LuHm KAI9000 Proposed Debug,O=LuHm OS,C=US'
chmod 600 "$KEYSTORE"
export GODOT_ANDROID_KEYSTORE_DEBUG_PATH="$KEYSTORE"
export GODOT_ANDROID_KEYSTORE_DEBUG_USER=androiddebugkey
export GODOT_ANDROID_KEYSTORE_DEBUG_PASSWORD=android

(
  cd cockpit
  npm install --package-lock-only --ignore-scripts --no-audit --no-fund
  npm ci --ignore-scripts --no-audit --no-fund
  npm run stage:vendor
)
ASSETS=native/kaiwebview/kaiwebview/src/main/assets/cockpit
rm -rf "$ASSETS"
mkdir -p "$ASSETS"
cp cockpit/index.html cockpit/app.js cockpit/styles.css "$ASSETS/"
cp -a cockpit/jquery cockpit/cms cockpit/vendor "$ASSETS/"
test -s "$ASSETS/jquery/luhm.delivery.js"
test -s "$ASSETS/vendor/jquery/jquery.min.js"
test -s "$ASSETS/vendor/vue/vue.global.prod.js"

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

python3 - <<'PY'
from pathlib import Path
p=Path('export_presets.cfg')
s=p.read_text()
for old,new in {
  'version/code=111':'version/code=123',
  'version/name="1.0.11-cleanplay.1"':'version/name="1.0.23-kai9000.proposed.1"',
  'package/unique_name="art.eggiebagelface.luhmos.cleanplay"':'package/unique_name="art.eggiebagelface.luhmos.kai9000proposed"',
  'package/name="LuHm OS Clean Play"':'package/name="LuHm OS KAI 9000 Proposed"'}.items():
    if old not in s:
        raise SystemExit(f'missing export identity: {old}')
    s=s.replace(old,new,1)
p.write_text(s)
PY

grep -q 'art.eggiebagelface.luhmos.kai9000proposed' export_presets.cfg
grep -q 'architectures/arm64-v8a=true' export_presets.cfg
grep -q 'permissions/internet=false' export_presets.cfg

mkdir -p build/android
"$GODOT" --headless --path . --export-debug 'Android Proposed' build/android/luhmos-kai9000-proposed.apk
test -s build/android/luhmos-kai9000-proposed.apk

APK=build/android/luhmos-kai9000-proposed.apk
BT="$ANDROID_HOME/build-tools/36.1.0"
"$BT/aapt" dump badging "$APK" | tee build/android/badging.txt
"$BT/aapt" dump xmltree "$APK" AndroidManifest.xml | tee build/android/manifest.txt
"$BT/aapt" dump permissions "$APK" | tee build/android/permissions.txt
"$BT/apksigner" verify --verbose --print-certs "$APK" | tee build/android/signature.txt
"$BT/zipalign" -c -P 16 -v 4 "$APK" > build/android/zipalign.txt
unzip -l "$APK" | tee build/android/ziplist.txt
sha256sum "$APK" | tee build/android/sha256.txt

grep -q "package: name='art.eggiebagelface.luhmos.kai9000proposed'" build/android/badging.txt
grep -q "versionCode='123'" build/android/badging.txt
grep -q 'org.godotengine.plugin.v2.KAIWebView' build/android/manifest.txt
grep -q 'com.google.android.webview.canary' build/android/manifest.txt
grep -q 'com.chrome.canary' build/android/manifest.txt
grep -q 'assets/cockpit/index.html' build/android/ziplist.txt
grep -q 'assets/cockpit/jquery/luhm.delivery.js' build/android/ziplist.txt
grep -q 'lib/arm64-v8a/' build/android/ziplist.txt
! grep -q 'android.permission.INTERNET' build/android/permissions.txt
! grep -q 'android.permission.REQUEST_INSTALL_PACKAGES' build/android/permissions.txt
! grep -q 'android.permission.MANAGE_EXTERNAL_STORAGE' build/android/permissions.txt
! grep -R -nE 'addJavascriptInterface|Runtime\.getRuntime\(\)\.exec|ProcessBuilder\(|setenforce 0|allowUniversalAccessFromFileURLs|MIXED_CONTENT_ALWAYS_ALLOW' native/kaiwebview cockpit

grep -q 'WebView.getCurrentWebViewPackage' native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/SamsungSystemProfile.kt
grep -q 'WebViewAssetLoader' native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/KAIWebView.kt

cat > build/android/drive-delivery-manifest.json <<HYDRA_AI_JSON
{
  "schema": "luhm.drive.delivery.v1",
  "source_sha": "${GITHUB_SHA:-unknown}",
  "workflow": "${GITHUB_WORKFLOW:-local}",
  "run_id": "${GITHUB_RUN_ID:-local}",
  "drive_root": "LuHm OS • NEW REPO SOURCE OF TRUTH • 2026-09-24",
  "drive_path": "builds/KAI9000/proposed/2026-09-26",
  "package": "art.eggiebagelface.luhmos.kai9000proposed",
  "version": "1.0.23-kai9000.proposed.1",
  "upload_state": "PENDING_LUM_CONNECTOR_RECEIPT",
  "physical_install": "HUMAN_ONLY"
}
HYDRA_AI_JSON

printf 'source_sha=%s\nworkflow=%s\nrun_id=%s\nstatus=GREEN_SOURCE_BUILD_CANDIDATE\npackage=art.eggiebagelface.luhmos.kai9000proposed\nversion=1.0.23-kai9000.proposed.1\ndrive_route=builds/KAI9000/proposed/2026-09-26\nphysical_install=HUMAN_ONLY\n' "${GITHUB_SHA:-unknown}" "${GITHUB_WORKFLOW:-local}" "${GITHUB_RUN_ID:-local}" > build/android/final-install-receipt.txt

cp doctrine/finalInstallRoute-20260926.json build/android/
cp agents/luhm-agent-mesh/finalInstallWorkflow.json build/android/
cp doctrine/s24feCanaryAdminHarness-20260926.json build/android/
cp cockpit/package-lock.json build/android/package-lock.json
sha256sum addons/kai_webview/bin/kaiwebview-debug.aar cockpit/package-lock.json doctrine/finalInstallRoute-20260926.json agents/luhm-agent-mesh/finalInstallWorkflow.json >> build/android/source-components-sha256.txt

echo 'KAI 9000 FINAL PROPOSED INSTALL CANDIDATE BUILD GREEN'
