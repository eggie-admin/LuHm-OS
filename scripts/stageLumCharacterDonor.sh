#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OUT_DIR="assets/lum/forge"
OUT="$OUT_DIR/vroidFemaleBase.glb"
RECEIPT="build/character-forge/vroidFemaleBase-receipt.json"
COMMIT='d053bc241c6e6d8f2bc41fc12bb2fe42272d6791'
BLOB='e5584a604d926473829e3bac8e22e570b5a165bc'
URL="https://raw.githubusercontent.com/CambrianTech/continuum/${COMMIT}/models/avatars/vroid-female-base.glb"
mkdir -p "$OUT_DIR" "$(dirname "$RECEIPT")"
rm -f "$OUT"
curl -fL --retry 5 --retry-all-errors --connect-timeout 20 --max-time 240 \
  -A 'LuHmOS-CharacterForge-CI' -o "$OUT" "$URL"
test -s "$OUT"
python3 tools/auditCharacterDonor.py "$OUT" --expected-git-blob "$BLOB" --receipt "$RECEIPT"
python3 - <<'PY'
import json
from pathlib import Path
r=json.loads(Path('build/character-forge/vroidFemaleBase-receipt.json').read_text())
Path('assets/lum/forge/vroidFemaleBoneMap.json').write_text(json.dumps({
  'schema':'luhm.rig.vrmBoneMap.v1',
  'source':'vroidFemaleBase.glb',
  'required':r['canonicalBoneMap']
}, indent=2)+'\n')
PY
printf 'CHARACTER_DONOR_STAGED=GREEN\n'
