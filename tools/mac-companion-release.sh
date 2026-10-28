#!/usr/bin/env bash
# LuHm macOS companion: exact-source, owner-signed, notarized DMG.
# Manual only. Never uploads or publishes artifacts.
set -euo pipefail
usage() {
  echo "Usage: mac-companion-release.sh --self-test | <40-char-source-sha> <output-dir>"
}
if [[ "$1" == "--self-test" ]]; then
  command -v python3 >/dev/null
  bash -n "$0"
  echo "MAC_COMPANION_STATIC=GREEN BUILD=NOT_RUN"
  exit 0
fi
[[ "$#" -eq 2 ]] || { usage >&2; exit 2; }
source_ref="$1"
[[ "$source_ref" =~ ^[0-9a-f]{40}$ ]] || { echo RED_SOURCE_SHA >&2; exit 2; }
[[ "$(uname -s)" == Darwin ]] || { echo RED_REQUIRES_MACOS >&2; exit 2; }
for cmd in git tar python3 codesign hdiutil xcrun shasum ditto; do
  command -v "$cmd" >/dev/null || { echo "RED_MISSING_$cmd" >&2; exit 2; }
done
: "${LUHM_MAC_DEVELOPER_ID:?RED_DEVELOPER_ID_REQUIRED}"
: "${LUHM_MAC_NOTARY_PROFILE:?RED_NOTARY_PROFILE_REQUIRED}"
godot_bin="${GODOT_BIN:-godot}"
command -v "$godot_bin" >/dev/null || { echo RED_GODOT_MISSING >&2; exit 2; }
[[ "$(git rev-parse HEAD)" == "$source_ref" ]] || { echo RED_HEAD_DRIFT >&2; exit 2; }
[[ -z "$(git status --porcelain)" ]] || { echo RED_DIRTY_SOURCE >&2; exit 2; }
[[ -f project.godot && -f export_presets.cfg ]] || { echo RED_NOT_GODOT_PROJECT >&2; exit 2; }
mkdir -p "$2"
out="$(cd "$2" && pwd -P)"
[[ "$out" != "$(pwd -P)" ]] || { echo RED_OUTPUT_REPO_ROOT >&2; exit 2; }
dmg="$out/LuHm-OS-Companion.dmg"
[[ ! -e "$dmg" ]] || { echo RED_ARTIFACT_ALREADY_EXISTS >&2; exit 2; }
tmp="$(mktemp -d "${TMPDIR:-/tmp}/luhm-mac.XXXXXXXX")"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/source" "$tmp/image"
git archive "$source_ref" | tar -x -C "$tmp/source"
[[ ! -f "$tmp/source/assets/lum/luhm.glb" && ! -f "$tmp/source/assets/lum/luhmRunning.glb" ]] || {
  echo RED_PRIVATE_ASSET_SOURCE >&2; exit 2;
}
python3 - "$tmp/source/export_presets.cfg" <<'PY'
import re,sys
from pathlib import Path
path=Path(sys.argv[1])
original=path.read_text(encoding="utf-8")
numbers=[int(x) for x in re.findall(r"^\[preset\.(\d+)\]$",original,re.M)]
if not numbers or 'name="macOS Companion"' in original or 'platform="macOS"' in original:
    raise SystemExit("RED_PRESET_CONFLICT")
n=max(numbers)+1
preset=f"""
[preset.{n}]
name="macOS Companion"
platform="macOS"
runnable=false
advanced_options=false
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path=""
patches=PackedStringArray()
encryption_include_filters=""
encryption_exclude_filters=""
seed=0
encrypt_pck=false
encrypt_directory=false
script_export_mode=2

[preset.{n}.options]
binary_format/architecture="universal"
application/bundle_identifier="art.eggiebagelface.luhmos.companion"
application/short_version="0.1.0"
application/version="1"
application/app_category="Games"
codesign/codesign=0
"""
path.write_text(original+"\n"+preset,encoding="utf-8")
PY
app="$tmp/LuHm OS Companion.app"
"$godot_bin" --headless --editor --path "$tmp/source" --quit
"$godot_bin" --headless --path "$tmp/source" --export-release "macOS Companion" "$app"
[[ -d "$app/Contents/MacOS" && -f "$app/Contents/Info.plist" ]] || { echo RED_APP_NOT_EXPORTED >&2; exit 2; }
/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" "$app/Contents/Info.plist" |
  grep -Fx "art.eggiebagelface.luhmos.companion"
# Sign library code first, then nested bundles, then the main app.
while IFS= read -r -d '' obj; do
  codesign --force --timestamp --sign "$LUHM_MAC_DEVELOPER_ID" "$obj"
done < <(find "$app/Contents" -type f \( -name "*.dylib" -o -name "*.so" \) -print0)
while IFS= read -r -d '' obj; do
  codesign --force --timestamp --sign "$LUHM_MAC_DEVELOPER_ID" "$obj"
done < <(find "$app/Contents" -depth -type d \( -name "*.framework" -o -name "*.app" -o -name "*.xpc" \) -print0)
codesign --force --options runtime --timestamp --sign "$LUHM_MAC_DEVELOPER_ID" "$app"
codesign --verify --deep --strict --verbose=2 "$app"
ditto "$app" "$tmp/image/LuHm OS Companion.app"
ln -s /Applications "$tmp/image/Applications"
hdiutil create -quiet -volname "LuHm OS Companion" -srcfolder "$tmp/image" \
  -format UDZO -ov "$dmg"
xcrun notarytool submit "$dmg" --keychain-profile "$LUHM_MAC_NOTARY_PROFILE" \
  --wait --output-format json > "$out/mac-notary-result.json"
python3 - "$out/mac-notary-result.json" <<'PY'
import json,sys
from pathlib import Path
if json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")).get("status")!="Accepted":
    raise SystemExit("RED_NOTARIZATION_NOT_ACCEPTED")
PY
xcrun stapler staple "$dmg"
xcrun stapler validate "$dmg"
shasum -a 256 "$dmg" > "$out/mac-companion-sha256.txt"
python3 - "$dmg" "$out" "$source_ref" <<'PY'
import hashlib,json,sys
from pathlib import Path
dmg,out,source=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
data={"schema":"luhmOs.macCompanionReceipt.v1","sourceRef":source,
      "bundleId":"art.eggiebagelface.luhmos.companion",
      "sha256":hashlib.sha256(dmg.read_bytes()).hexdigest(),
      "signed":True,"notarized":True,"stapled":True,
      "publicDistribution":False,"deviceLaunchProven":False,"crownStatus":"STOP"}
(out/"mac-companion-receipt.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
PY
echo "MAC_DMG_RELEASE_READY=SIGNED_NOTARIZED; DISTRIBUTION=NOT_PERFORMED"