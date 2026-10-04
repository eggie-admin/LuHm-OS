#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
LAW="AI proposes. Policy authorizes. CI proves. Human promotes."
BASE="cb0f53c9dfc8aedf6852a77e60f41634f8d18bab"
errors=[]

def req(ok, code):
    if not ok:
        errors.append(code)

def load(path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        errors.append(f"RED_JSON_{path.name}:{exc}")
        return {}

contract=load(ROOT/"doctrine/TERMUX_SECURE_FOLDER_SHIZUKU_EXPERIMENT_V1.json")
installer=(ROOT/"scripts/termux/install-luhm-dev.sh").read_text()
probe=(ROOT/"scripts/termux/luhm-secure-folder-shizuku-probe.sh").read_text()
bootstrap=(ROOT/"scripts/termux/bootstrap-secure-folder.sh").read_text()

req(contract.get("sourceLaw")==LAW, "RED_SOURCE_LAW")
req(contract.get("baseCandidate")==BASE, "RED_BASE_CANDIDATE")
req(contract.get("promotion") is False, "RED_PROMOTION")
req(contract.get("crownStatus")=="STOP", "RED_CROWN")
req('LUHM_SECURE_FOLDER_EXPERIMENT' in installer, "RED_EXPLICIT_OPT_IN_MISSING")
req('SECONDARY_OR_CONTAINER_USER' in installer, "RED_PROFILE_CLASS_MISSING")
req('secureFolderConfirmed":False' in installer, "RED_NO_FALSE_SECURE_FOLDER_PROOF")
req('RISH_PRESERVE_ENV=0' in probe, "RED_RISH_ENV_BOUNDARY")
req("rish -c" not in installer, "RED_INSTALLER_DIRECT_RISH_EXECUTION")
req("cmd user list" in probe, "RED_USER_DIAGNOSTIC")
req("termuxHomeProbe" in probe, "RED_HOME_BOUNDARY_DIAGNOSTIC")
req('rootClaim":False' in installer, "RED_ROOT_CLAIM")
req('knoxBypassClaim":False' in installer, "RED_KNOX_CLAIM")
req('crossProfileAccessClaim":False' in installer, "RED_CROSS_PROFILE_CLAIM")
req('exec bash "$INSTALLER"' in bootstrap, "RED_BOOTSTRAP_HANDOFF")
req("EXPECTED_BASE" in bootstrap, "RED_BOOTSTRAP_BASE_PIN")

status="GREEN_SECURE_FOLDER_SHIZUKU_SOURCE" if not errors else "RED_SECURE_FOLDER_SHIZUKU_SOURCE"
print(json.dumps({
  "schema":"luhm-os.termux-secure-folder-shizuku-audit.v1",
  "status":status,
  "errors":errors,
  "baseCandidate":BASE,
  "secureFolderRuntimeAuthority":False,
  "shizukuAuthority":"BOUNDED_DIAGNOSTIC_ONLY",
  "crownStatus":"STOP"
}, indent=2))
raise SystemExit(1 if errors else 0)
