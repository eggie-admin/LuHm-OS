#!/usr/bin/env python3
"""Source-only operational freeze regression; never a ChatGPT host receipt."""
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
policy=json.loads((ROOT/"doctrine/companyWideOperationalQuarantineV1.json").read_text())
registry=json.loads((ROOT/"doctrine/agentSystemDeploymentV1.json").read_text())
assert policy["schema"]=="luhmOs.companyWideOperationalQuarantine.v1"
assert policy["state"]=="QUARANTINED"
assert policy["registeredCount"]==15
assert policy["registeredAgents"]==registry["requiredAgents"]
assert policy["supervisedProbe"]["hostInvocationReceipt"] is None
assert policy["crownStatus"]=="STOP"
for kind in ("direct","read","records","proof","patch","build","external","diagnose","research","monitor","release","art","media","mediaFactory","dictation","asset"):
    cmd=[sys.executable,str(ROOT/"tools/lumTaskRouter.py"),kind]
    run=subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True)
    report=json.loads(run.stdout)
    assert report["workers"]==[],kind
    assert report["activeResidentCabinet"]==[],kind
    assert report["sourceMutationLanes"]==0,kind
    assert report["greenAuthority"] is False,kind
    assert report["companyQuarantine"]["hostInvocationProven"] is False,kind
assert "def luhm_belldandy_supervised_probe(" in (ROOT/"host/mcp/luhmMcpServer.py").read_text()
assert "MCP_TOOL_RESPONSE_ONLY_NOT_AGENT_EXECUTION" in (ROOT/"host/mcp/luhmMcpServer.py").read_text()
print("GREEN_COMPANY_WIDE_QUARANTINE_SOURCE_ONLY_16_ROUTE_CHECKS")
