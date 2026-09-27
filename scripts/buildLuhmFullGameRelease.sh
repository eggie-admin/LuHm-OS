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

# Prove that the donor resources survive Godot export, not just source checkout.
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
printf 'source_sha=%s\nstatus=LUHM_FULL_GAME_RELEASE_CANDIDATE_GREEN\ndonor_assets=2_HASH_PINNED_DRIVE_STAGED\nkai9000=DONOR_ONLY_NOT_AUTHORITY\nwidget_authority=false\nprivate_relic_payloads=false\n' "$SOURCE_SHA" > build/android/luhm-full-game-receipt.txt

echo 'LUHM FULL GAME RELEASE FORGE GREEN'
