#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/scripts/buildCathedralWebglass.sh"
GEN="$ROOT/scripts/.buildCathedralReleaseCandidate.generated.sh"

cleanup() { rm -f "$GEN"; }
trap cleanup EXIT

python3 - "$SRC" "$GEN" <<'PY'
from pathlib import Path
import sys

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
text = src.read_text(encoding="utf-8")

old_key = '''KEYSTORE="$TMP/luhm-cathedral-atelier-debug.keystore"
keytool -genkeypair -keystore "$KEYSTORE" -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname 'CN=LuHm Cathedral Oni Atelier Candidate,O=LuHm OS,C=US'
chmod 600 "$KEYSTORE"
export GODOT_ANDROID_KEYSTORE_DEBUG_PATH="$KEYSTORE"
export GODOT_ANDROID_KEYSTORE_DEBUG_USER=androiddebugkey
export GODOT_ANDROID_KEYSTORE_DEBUG_PASSWORD=android
'''
new_key = '''CROWN_KEYSTORE_PATH="${LUHM_CROWN_KEYSTORE_PATH:-}"
CROWN_KEY_ALIAS="${LUHM_CROWN_KEY_ALIAS:-}"
CROWN_KEYSTORE_PASSWORD="${LUHM_CROWN_KEYSTORE_PASSWORD:-}"
if [[ -n "$CROWN_KEYSTORE_PATH" || -n "$CROWN_KEY_ALIAS" || -n "$CROWN_KEYSTORE_PASSWORD" ]]; then
  if [[ -z "$CROWN_KEYSTORE_PATH" || -z "$CROWN_KEY_ALIAS" || -z "$CROWN_KEYSTORE_PASSWORD" ]]; then
    echo 'RED_CROWN_SIGNING_INPUTS_INCOMPLETE' >&2
    exit 1
  fi
  if [[ ! -r "$CROWN_KEYSTORE_PATH" ]]; then
    echo 'RED_CROWN_KEYSTORE_UNREADABLE' >&2
    exit 1
  fi
  KEYSTORE="$CROWN_KEYSTORE_PATH"
  KEYSTORE_PASS="$CROWN_KEYSTORE_PASSWORD"
  KEY_ALIAS="$CROWN_KEY_ALIAS"
  SIGNING_MODE='crown_persistent_external'
else
  KEYSTORE="$TMP/luhm-cathedral-atelier-candidate-release.keystore"
  KEYSTORE_PASS="$(openssl rand -hex 24)"
  KEY_ALIAS='luhmcandidate'
  keytool -genkeypair -keystore "$KEYSTORE" -storepass "$KEYSTORE_PASS" -alias "$KEY_ALIAS" -keypass "$KEYSTORE_PASS" -keyalg RSA -keysize 2048 -validity 10000 -dname 'CN=LuHm Cathedral Oni Atelier Candidate Release,O=LuHm OS,C=US'
  chmod 600 "$KEYSTORE"
  SIGNING_MODE='ephemeral_ci_release_key'
fi
export GODOT_ANDROID_KEYSTORE_RELEASE_PATH="$KEYSTORE"
export GODOT_ANDROID_KEYSTORE_RELEASE_USER="$KEY_ALIAS"
export GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD="$KEYSTORE_PASS"
'''
if old_key not in text:
    raise SystemExit("RED_RELEASE_PATCH_KEYSTORE_PATTERN_MISSING")
text = text.replace(old_key, new_key, 1)

old_export = '"$GODOT" --headless --path . --export-debug \'Android Proposed\' "$APK"'
new_export = '"$GODOT" --headless --path . --export-release \'Android Proposed\' "$APK"'
if old_export not in text:
    raise SystemExit("RED_RELEASE_PATCH_EXPORT_PATTERN_MISSING")
text = text.replace(old_export, new_export, 1)

old_aar = 'test -s addons/kai_webview/bin/kaiwebview-debug.aar'
new_aar = 'test -s addons/kai_webview/bin/kaiwebview-debug.aar\ntest -s addons/kai_webview/bin/kaiwebview-release.aar'
if old_aar not in text:
    raise SystemExit("RED_RELEASE_PATCH_AAR_PATTERN_MISSING")
text = text.replace(old_aar, new_aar, 1)

old_source_unpack = 'unzip -q "$ANDROID_SOURCE" -d android/build'
new_source_unpack = r'''unzip -q "$ANDROID_SOURCE" -d android/build
python3 - <<'PY_PROFILE'
from pathlib import Path
import re

count = 0
pattern = re.compile(
    r'(<profileable\b[^>]*?android:shell=")true("[^>]*?android:enabled=")true("[^>]*/>)',
    re.S,
)
for manifest in Path("android/build").rglob("AndroidManifest.xml"):
    text = manifest.read_text(encoding="utf-8")
    updated, n = pattern.subn(r'\1false\2false\3', text)
    if n:
        manifest.write_text(updated, encoding="utf-8")
        count += n
if count < 1:
    raise SystemExit("RED_PROFILEABLE_TEMPLATE_PATTERN_MISSING")
print(f"ANDROID_PROFILEABLE_DISABLED={count}")
PY_PROFILE'''
if old_source_unpack not in text:
    raise SystemExit("RED_PROFILEABLE_SOURCE_UNPACK_PATTERN_MISSING")
text = text.replace(old_source_unpack, new_source_unpack, 1)

old_manifest = '"$BT/aapt" dump xmltree "$APK" AndroidManifest.xml | tee build/android/manifest.txt'
new_manifest = '''"$BT/aapt" dump xmltree "$APK" AndroidManifest.xml | tee build/android/manifest.txt
if grep -q 'android:debuggable.*0xffffffff' build/android/manifest.txt; then
  echo 'RED_APK_DEBUGGABLE_TRUE' >&2
  exit 1
fi
if grep -q 'android.permission.INTERNET' build/android/manifest.txt; then
  echo 'RED_APK_INTERNET_PERMISSION_PRESENT' >&2
  exit 1
fi
if grep -q 'android:shell.*0xffffffff' build/android/manifest.txt; then
  echo 'RED_APK_PROFILEABLE_SHELL_TRUE' >&2
  exit 1
fi
printf 'export_mode=release_candidate\\nsigning=%s\\ndebuggable=false\\ninternet_permission=false\\nprofileable_shell=false\\n' "$SIGNING_MODE" > build/android/release-hardening.txt'''
if old_manifest not in text:
    raise SystemExit("RED_RELEASE_PATCH_MANIFEST_PATTERN_MISSING")
text = text.replace(old_manifest, new_manifest, 1)

text = text.replace(
    'status=CATHEDRAL_ONI_ATELIER_CI_PROOF\\n',
    'status=CATHEDRAL_ONI_ATELIER_RELEASE_CANDIDATE_CI_PROOF\\n',
    1,
)
text = text.replace(
    'sha256sum addons/kai_webview/bin/kaiwebview-debug.aar cockpit/package-lock.json >> build/android/source-components-sha256.txt',
    'sha256sum addons/kai_webview/bin/kaiwebview-release.aar cockpit/package-lock.json >> build/android/source-components-sha256.txt',
    1,
)
dst.write_text(text, encoding="utf-8")
PY

chmod 700 "$GEN"
"$GEN"
