#!/usr/bin/env python3
"""Verify only the safe in-chat cast is released, not autonomous execution."""
import json
import subprocess
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
def read(path):
    return json.loads((root/path).read_text(encoding="utf-8"))
cast=read("doctrine/supervisedChatCastReleaseV1.json")
company=read("doctrine/companyWideOperationalQuarantineV1.json")
belldandy=read("doctrine/belldandyOperationalQuarantineV1.json")
assert cast["schema"]=="luhmOs.supervisedChatCastRelease.v1"
assert cast["state"]=="RELEASED" and cast["scope"]=="chatPresentationOnly"
assert cast["authority"]=="Professor"
assert cast["noAgentExecution"] and cast["noHiddenWorkers"] and cast["noAutomaticCalls"]
assert cast["companyRuntimeQuarantineStillEffective"] and cast["roleSpecificQuarantineStillEffective"]
assert not cast["promotionAuthority"] and not cast["signingAuthority"]
assert not cast["providerSecretAccess"] and not cast["costAuthority"]
assert company["state"]=="QUARANTINED"
assert belldandy["state"]=="QUARANTINED"
assert company["registeredCount"]==15
for route in ("direct","read","records","proof","patch","build","external","diagnose","research","monitor","release","art","media","mediaFactory","dictation","asset"):
    result=subprocess.run([sys.executable,str(root/"tools/lumTaskRouter.py"),route],check=True,capture_output=True,text=True,cwd=root)
    packet=json.loads(result.stdout)
    assert packet["workers"]==[],route
    assert packet["sourceMutationLanes"]==0,route
    assert packet["activeResidentCabinet"]==[],route
    assert packet["greenAuthority"] is False,route
print("GREEN_SUPERVISED_CHAT_CAST_RELEASE_ONLY_RUNTIME_QUARANTINED")
