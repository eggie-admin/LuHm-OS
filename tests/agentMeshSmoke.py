#!/usr/bin/env python3
import os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.agentMeshRuntime import *

assert [x.name for x in ONI] == ["Kiri","Tetsu","Momo"]
assert MAX_PARALLEL == 3
validate_dispatch(ONI)
try:
    validate_dispatch((*ONI, SHIORI))
    raise AssertionError("parallel cap failed")
except ValueError:
    pass
assert authorize("publish") == Verdict.CROWN_REQUIRED
assert authorize("publish", crown_approved=True) == Verdict.ALLOW
assert authorize("embed_provider_secret", crown_approved=True) == Verdict.DENY
assert authorize("recursive_recruit") == Verdict.DENY
assert provider_ready({}) is False
assert provider_ready({"OPENAI_API_KEY":"test-only-presence"}) is True
assert deployment_state(exact_head_ci=True,provider_receipt=False,apk_receipt=True,device_receipt=False,human_promoted=False) == "RED_OPENAI_LIVE_RECEIPT_MISSING"
print("LUM_ONI_AGENT_MESH_SMOKE=PASS")
