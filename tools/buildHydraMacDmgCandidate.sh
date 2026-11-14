#!/usr/bin/env bash
# macOS-only, opt-in UNNOTARIZED static cockpit disk image. NOT a native .app.
set -euo pipefail
umask 077
[[ "$(uname -s)" == "Darwin" ]] || { echo RED_MACOS_HOST_REQUIRED >&2; exit 2; }
command -v hdiutil >/dev/null || { echo RED_HDIUTIL_REQUIRED >&2; exit 3; }
NPM_TGZ="${1:?Provide hash-verified private npm preview tarball}"
DEST="${2:?Provide an output .dmg filename}"
test -s "$NPM_TGZ" || { echo RED_MISSING_INPUT >&2; exit 4; }
[[ "$DEST" == *.dmg ]] || { echo RED_DMG_EXTENSION >&2; exit 5; }
tar -tzf "$NPM_TGZ" | grep -qx 'package/dist/index.html' || {
  echo RED_NO_INDEX_HTML >&2; exit 6;
}
WORK="$(mktemp -d)"
trap 'rm -rf -- "$WORK"' EXIT
mkdir -p "$WORK/extracted" "$WORK/image/LuHm-OS Static Cockpit"
tar -xzf "$NPM_TGZ" -C "$WORK/extracted"
cp -R -- "$WORK/extracted/package/dist/." "$WORK/image/LuHm-OS Static Cockpit/"
cat > "$WORK/image/READ-ME-FIRST.txt" <<'TXT'
LuHm-OS static HTML cockpit PREVIEW.
This is an unnotarized HFS+ disk image of browser files, NOT a signed macOS .app.
Use local files through your trusted browser or an approved localhost-only server.
No Google/Apple signing, native agent runtime, auto-install or network service.
TXT
mkdir -p "$(dirname -- "$DEST")"
hdiutil create -quiet -volname 'LuHm-OS Static Preview' -srcfolder "$WORK/image" \
  -format UDZO -fs HFS+ -ov "$DEST"
test -s "$DEST"
shasum -a 256 "$DEST"
echo UNNOTARIZED_STATIC_MAC_DMG_SOURCE_CANDIDATE
