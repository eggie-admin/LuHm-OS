#!/usr/bin/env python3
from pathlib import Path
import json, sys

root = Path(__file__).resolve().parents[1]
errors=[]

def req(ok,msg):
    if not ok: errors.append(msg)

installer=(root/"tools/s24FeBetaInstall.sh").read_text()
contract=json.loads((root/"doctrine/s24FeBetaInstallV1.json").read_text())

req(contract["target"]["model"]=="SM-S721U1","S24 FE model drift")
req(contract["target"]["android"]=="16","Android target drift")
req(contract["target"]["abi"]=="arm64-v8a","ABI drift")
req(contract["package"]=="art.eggiebagelface.luhmos.testing","package drift")
req(contract["safety"]["rootNotAssumed"] is True,"root must not be assumed")
req(contract["safety"]["checksumRequired"] is True,"checksum must be required")
req(contract["safety"]["broadStorageDeletion"] is False,"broad deletion forbidden")

for token in (
    'EXPECTED_MODEL="SM-S721U1"',
    'EXPECTED_ANDROID="16"',
    'EXPECTED_ABI="arm64-v8a"',
    'sha256sum -c "$SHA_NAME"',
    'PACKAGE="art.eggiebagelface.luhmos.testing"',
    'pm uninstall',
    'pm install -t',
    'termux-open --view "$APK"',
    'LUHM_S24FE_BETA_INSTALL=GREEN',
    'LUHM_S24FE_BETA_INSTALL=AMBER_USER_CONFIRM',
):
    req(token in installer, f"installer missing {token}")

req(installer.index('sha256sum -c "$SHA_NAME"') < installer.index('pm uninstall'),"checksum must precede uninstall")
req('"/sdcard/Android/data/$PACKAGE"' in installer,"scoped Android/data cleanup missing")
req('"/sdcard/Android/obb/$PACKAGE"' in installer,"scoped Android/obb cleanup missing")
req("rm -rf /" not in installer,"broad root deletion forbidden")

print(json.dumps({
  "schema":"luhmOs.s24FeBetaInstallAudit.v1",
  "status":"greenS24FeBetaInstallSource" if not errors else "redS24FeBetaInstallSource",
  "errors":errors,
  "physicalInstall":"pendingDevice",
  "crownStatus":"stop"
},indent=2))
sys.exit(1 if errors else 0)
