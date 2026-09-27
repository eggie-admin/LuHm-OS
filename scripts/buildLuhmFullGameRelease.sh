#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
SOURCE_SHA="${SOURCE_SHA:-${GITHUB_SHA:-local}}"

python3 tools/luhmFullGameAudit.py
python3 tools/stageLuhmGameDonors.py
python3 tools/luhmFullGameAudit.py --with-donor-receipt --output build/luhm-game-donors/source-audit.json

# Existing hardened Cathedral release forge remains the Android authority.
bash scripts/buildCathedralReleaseCandidate.sh

# Prove donor resources survive Godot export, not merely source checkout.
GODOT="${RUNNER_TEMP:-/tmp}/godot/Godot_v4.7.2-stable_linux.x86_64"
test -x "$GODOT"
PACK="build/android/luhm-full-game-donor-proof.pck"
"$GODOT" --headless --path . --export-pack 'Android Proposed' "$PACK"
test -s "$PACK"
"$GODOT" --headless --main-pack "$PACK" --script res://tests/finalCoffeeHouseSmoke.gd
rm -f "$PACK"

cp build/luhm-game-donors/receipt.json build/android/luhm-game-donor-receipt.json
cp build/luhm-game-donors/source-audit.json build/android/luhm-full-game-source-audit.json
cp assets/donor/luhm-game-donors.json build/android/luhm-game-donor-manifest.json

python3 tools/luhmFullGameAudit.py --with-donor-receipt --output build/android/luhm-full-game-final-audit.json

DONOR_RECEIPT_SHA="$(sha256sum build/android/luhm-game-donor-receipt.json | awk '{print $1}')"
DONOR_MANIFEST_SHA="$(sha256sum build/android/luhm-game-donor-manifest.json | awk '{print $1}')"
FINAL_AUDIT_SHA="$(sha256sum build/android/luhm-full-game-final-audit.json | awk '{print $1}')"
APK_SHA="$(awk '{print $1}' build/android/sha256.txt)"
SIGNING_MODE="$(awk -F= '$1=="signing" {print $2}' build/android/release-hardening.txt)"

cat > build/android/luhm-full-game-receipt.txt <<EOF
source_sha=$SOURCE_SHA
status=LUHM_FULL_GAME_RELEASE_CANDIDATE_GREEN
donor_assets=2_GIT_VENDORED_HASH_PINNED_PRIVATE_DRIVE_PROVENANCE
donor_receipt_sha256=$DONOR_RECEIPT_SHA
donor_manifest_sha256=$DONOR_MANIFEST_SHA
full_game_audit_sha256=$FINAL_AUDIT_SHA
apk_sha256=$APK_SHA
signing_mode=$SIGNING_MODE
kai9000=DONOR_ONLY_NOT_AUTHORITY
widget_authority=false
private_relic_payloads=false
apk_runtime_network=false
EOF

echo 'LUHM FULL GAME RELEASE FORGE GREEN'
