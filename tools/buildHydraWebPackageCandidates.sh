#!/usr/bin/env bash
# Source-only, unsigned Debian + private npm static-cockpit candidates.
# No sudo, installation, package publishing, Drive uploads or script execution.
set -euo pipefail
export LC_ALL=C
umask 077
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
OUTPUT="${1:?Provide isolated output directory}"
mkdir -p "$OUTPUT"
OUTPUT="$(cd -- "$OUTPUT" && pwd -P)"
if [[ "$OUTPUT" == "$ROOT" || "$OUTPUT" == "$ROOT/"* ]]; then
  echo 'RED_OUTPUT_INSIDE_SOURCE_CHECKOUT' >&2
  exit 2
fi
SOURCE_SHA="$(git -C "$ROOT" rev-parse HEAD)"
[[ "$SOURCE_SHA" =~ ^[0-9a-f]{40}$ ]] || exit 3

FRONT="$ROOT/frontEnd"
for f in index.html styles.css app.js \
  jquery/luhm.codingRoleplay.js jquery/luhm.parallax.js \
  jquery/luhm.cockpit.js jquery/luhm.cast.js \
  vendor/jquery-3.7.1.min.js vendor/jquery-LICENSE.txt; do
  test -f "$FRONT/$f" || { echo "RED_MISSING_STATIC_ASSET:$f" >&2; exit 4; }
done

WORK="$(mktemp -d)"
trap 'rm -rf -- "$WORK"' EXIT
STAGED="$WORK/staged"
mkdir -p "$STAGED/jquery" "$STAGED/vendor"
for f in index.html styles.css app.js; do cp -- "$FRONT/$f" "$STAGED/$f"; done
for f in luhm.codingRoleplay.js luhm.parallax.js luhm.cockpit.js luhm.cast.js; do
  cp -- "$FRONT/jquery/$f" "$STAGED/jquery/$f"
done
cp -- "$FRONT/vendor/jquery-3.7.1.min.js" "$STAGED/vendor/"
cp -- "$FRONT/vendor/jquery-LICENSE.txt" "$STAGED/vendor/"
printf '%s\n' "$SOURCE_SHA" > "$STAGED/source-ref.txt"
cat > "$STAGED/README-CANDIDATE.txt" <<'TXT'
LuHm-OS local static HTML cockpit, SOURCE-ONLY preview.
This is not an installed Lum agent, native Android application or notarized macOS app.
Use a browser with file:// support or serve these files from a trusted local origin.
No external model or private artwork has been included.
TXT

DEB_ROOT="$WORK/deb-root"
mkdir -p "$DEB_ROOT/DEBIAN" "$DEB_ROOT/usr/share/luhm-os/cockpit"
cp -R -- "$STAGED/." "$DEB_ROOT/usr/share/luhm-os/cockpit/"
cat > "$DEB_ROOT/DEBIAN/control" <<'CONTROL'
Package: luhm-os-cockpit-preview
Version: 0.1.0~proposed1
Section: web
Priority: optional
Architecture: all
Maintainer: LuHm-OS source candidate <packaging@example.invalid>
Description: LuHm-OS local static cockpit preview, source-only candidate
 This package contains portable HTML, CSS and JavaScript plus the
 local jQuery 3.7.1 license. It has no service, post-install hooks,
 independent AI runtime, remote agent execution or release authority.
CONTROL
dpkg-deb --root-owner-group --build "$DEB_ROOT" \
  "$OUTPUT/luhm-os-cockpit-preview_0.1.0~proposed1_all.deb" >/dev/null

NPM_ROOT="$WORK/npm-package"
mkdir -p "$NPM_ROOT/dist"
cp -R -- "$STAGED/." "$NPM_ROOT/dist/"
cat > "$NPM_ROOT/package.json" <<'JSON'
{
  "name": "@luhm-os/cockpit-preview",
  "version": "0.0.0-proposed.1",
  "description": "Private source-only LuHm-OS static cockpit preview, not an agent",
  "private": true,
  "license": "UNLICENSED",
  "files": ["dist/"],
  "scripts": {}
}
JSON
# npm pack does not publish. Ignore arbitrary install/prepack scripts.
npm pack "$NPM_ROOT" --pack-destination "$OUTPUT" --ignore-scripts \
  --json > "$OUTPUT/npm-pack-summary.json"
test -s "$OUTPUT/luhm-os-cockpit-preview_0.1.0~proposed1_all.deb"
test -s "$OUTPUT/luhm-os-cockpit-preview-0.0.0-proposed.1.tgz" ||
  { echo 'RED_NPM_TGZ_NAME_OR_BUILD' >&2; exit 5; }
(
  cd "$OUTPUT"
  sha256sum luhm-os-cockpit-preview_0.1.0~proposed1_all.deb \
    luhm-os-cockpit-preview-0.0.0-proposed.1.tgz > SHA256SUMS
)
echo "GREEN_UNSIGNED_PACKAGE_CANDIDATES sourceRef=$SOURCE_SHA output=$OUTPUT"
