#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OUT_DIR="assets/lum/forge"
OUT="$OUT_DIR/mpfbFemaleBase.glb"
RECEIPT="build/character-forge/mpfbFemaleBase-receipt.json"
COMMIT='b3e277b3b46f88e557bf28a2c5612a5b04e075c3'
BLOB='cd2ebbe1fe8bcbf3d5b2dfbf1262a7f76814e68f'
URL="https://raw.githubusercontent.com/met4citizen/TalkingHead/${COMMIT}/avatars/mpfb.glb"
mkdir -p "$OUT_DIR" "$(dirname "$RECEIPT")"
rm -f "$OUT"
curl -fL --retry 5 --retry-all-errors --connect-timeout 20 --max-time 300 \
  -A 'LuHmOS-CharacterForge-CI' -o "$OUT" "$URL"
test -s "$OUT"
python3 tools/auditCharacterDonor.py "$OUT" \
  --expected-git-blob "$BLOB" --license CC0 --profile facial-glb --receipt "$RECEIPT"
python3 - <<'PY'
import json
from pathlib import Path
r=json.loads(Path('build/character-forge/mpfbFemaleBase-receipt.json').read_text())
Path('assets/lum/forge/mpfbFemaleBoneMap.json').write_text(json.dumps({
  'schema':'luhm.rig.facialGlbBoneMap.v1',
  'source':'mpfbFemaleBase.glb',
  'required':r['canonicalBoneMap'],
  'expressions':r['expressionNames']
}, indent=2)+'\n')
PY
printf 'CHARACTER_DONOR_STAGED=GREEN\n'
