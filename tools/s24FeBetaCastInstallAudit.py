#!/usr/bin/env python3
from pathlib import Path
import sys, json

root=Path(__file__).resolve().parents[1]
path=root/"tools/s24FeBetaCastInstall.sh"
errors=[]
text=path.read_text() if path.is_file() else ""

def req(ok,msg):
    if not ok: errors.append(msg)

for token in (
  'BRANCH="beta/yumeArtChatV1-20261002"',
  'WORKFLOW="android-testing-build.yml"',
  '[ "$CAST_WORD" = "cast" ]',
  'gh auth status',
  'PROFESSOR_ACTOR="$(gh api user --jq',
  'branches/$BRANCH',
  '--ref "$BRANCH"',
  '-f sourceRef="$SOURCE_REF"',
  '-f professorActor="$PROFESSOR_ACTOR"',
  '-f castOriginRunId=direct',
  '-f publishPrerelease=true',
  'gh run watch "$RUN_ID"',
  'gh release view "$TAG"',
  'exec bash "$SCRIPT_DIR/s24FeBetaInstall.sh" "$TAG"',
):
    req(token in text,f"missing {token}")

req("repos/$REPO/branches/main" not in text,"beta helper must not resolve main")
req("termuxVirginInstall.sh" not in text,"beta helper must not call tablet installer")
req("rerun" not in text.lower(),"fresh beta CAST must not substitute rerun")
req("DISPATCH_AFTER=" in text and ".createdAt >=" in text,"dispatch window binding missing")

print(json.dumps({
  "schema":"luhmOs.s24FeBetaCastInstallAudit.v1",
  "status":"greenS24FeBetaCastInstall" if not errors else "redS24FeBetaCastInstall",
  "errors":errors,
  "physicalInstall":"pendingPhone",
  "crownStatus":"stop"
},indent=2))
sys.exit(1 if errors else 0)
