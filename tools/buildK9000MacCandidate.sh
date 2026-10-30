#!/usr/bin/env bash
# Run on a macOS development machine with Godot 4.7.2 and matching export templates.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
[[ "$(uname -s)" == "Darwin" ]] || { echo "RED_MACOS_HOST_REQUIRED" >&2; exit 2; }
command -v git >/dev/null
GODOT_BIN="${GODOT_BIN:-godot}"
command -v "$GODOT_BIN" >/dev/null || { echo "RED_GODOT_NOT_INSTALLED" >&2; exit 2; }
VERSION="$("$GODOT_BIN" --version)"
[[ "$VERSION" == 4.7.2.stable* ]] || { echo "RED_GODOT_VERSION_EXPECTED_4.7.2 observed=$VERSION" >&2; exit 2; }
git diff --quiet && git diff --cached --quiet || { echo "RED_DIRTY_SOURCE" >&2; exit 2; }
SOURCE_REF="$(git rev-parse HEAD)"
export LUHM_SOURCE_REF="$SOURCE_REF"
python3 tools/hardSystemAudit200.py > /tmp/k9000-hard-200.log
python3 tools/k9000CandidateAudit.py
mkdir -p build/k9000
"$GODOT_BIN" --headless --path "$ROOT" --export-release "macOS K9000 Candidate" "$ROOT/build/k9000/K9000-development.dmg"
test -s build/k9000/K9000-development.dmg
hdiutil verify build/k9000/K9000-development.dmg
shasum -a 256 build/k9000/K9000-development.dmg | tee build/k9000/K9000-development.sha256
echo "K9000_DEV_DMG_ONLY; UNSIGNED_FOR_PUBLIC_DISTRIBUTION; NOT_NOTARIZED; source=$SOURCE_REF"
