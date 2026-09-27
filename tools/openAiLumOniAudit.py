#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/"doctrine/openAiLumOniDeployment-20260927.json").read_text())
errors=[]
if d["authority"]!="Professor": errors.append("authority drift")
a=d["architecture"]
if a["boss"]!="Lum" or a["parallelism_max"]!=3: errors.append("mesh drift")
if a["android_provider_secrets"] or a["android_remote_shell"]: errors.append("Android boundary violated")
o=d["openai"]
if o["credential_in_git"] or o["credential_in_apk"]: errors.append("credential boundary violated")
if "allowlist" not in o["tool_policy"]: errors.append("tool allowlist missing")
if d["agent_contract"]["consequential_actions_crown_gated"] is not True: errors.append("Crown gate missing")
if errors: raise SystemExit("RED: "+"; ".join(errors))
print("OPENAI_LUM_ONI_DOCTRINE_AUDIT=PASS")
