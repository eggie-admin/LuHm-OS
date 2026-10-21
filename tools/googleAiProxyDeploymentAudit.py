#!/usr/bin/env python3
"""Source safety gate for GitHub-green automatic deploy and Google AI status tool."""
from pathlib import Path
import json
import ast
ROOT=Path(__file__).resolve().parents[1]
def load(path):return json.loads((ROOT/path).read_text())
deploy=load("doctrine/githubGatedDeploymentV1.json")
google=load("doctrine/googleAiProxyDeploymentV1.json")
quarantine=load("doctrine/companyWideOperationalQuarantineV1.json")
other=load("doctrine/googleAiDeveloperEntitlementsV1.json")
cabinet=load("doctrine/goddessCabinetLiveChatV1.json")
assert deploy["renderNativeAutoDeploy"]=="OFF_PRESERVED"
assert deploy["state"].startswith("SOURCE_CONFIGURED")
assert len(deploy["renderTargets"])==2
assert all(t["existing"] and t["plan"]=="free" for t in deploy["renderTargets"])
assert deploy["staticPublicationAutomatic"] is False
assert quarantine["state"]=="QUARANTINED" and not quarantine["activeTaskWorkersAllowed"]
assert len(quarantine["registeredAgents"])==15
assert cabinet["status"]=="PROFESSOR_AUTHORIZED_SUPERVISED_CHAT_CAST"
assert google["runtimeMode"]=="READ_ONLY_STATUS_ONLY"
assert google["automaticDeploy"] is False
assert google["networkEgress"]=="DISABLED" and google["billingApproval"]=="NOT_GRANTED"
assert not google["automaticProviderCalls"] and not google["runtimeAgentWorkerActivation"]
assert other["executionLaw"]["defaultAction"]=="DENY"
assert other["executionLaw"]["noAutomaticDeploy"] is True
mcp=(ROOT/"host/mcp/luhmMcpServer.py").read_text()
node=ast.parse(mcp)
fns={n.name:n for n in node.body if isinstance(n,ast.FunctionDef)}
assert "luhm_google_ai_proxy_status" in fns
f=fns["luhm_google_ai_proxy_status"]
assert not any(isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and
               x.func.id in {"subprocess","urlopen","requests"} for x in ast.walk(f))
assert "READ_ONLY_STATUS_ONLY" in mcp and '"providerCalled": False' in mcp
script=(ROOT/"tools/autoDeployRenderSidecar.py").read_text()
assert 'commitId' in script and 'MAIN_SOURCE_DRIFT_STOP' in script
assert 'api.render.com/v1/services/' in script
assert "RENDER_API_KEY" in script
assert (ROOT/"render.yaml").read_text().count("autoDeployTrigger: off")>=3
print("GREEN_LUM_SUPERVISED_GODDESSES_GITHUB_RENDER_AUTO_PIPELINE_GOOGLE_AI_FAIL_CLOSED")
