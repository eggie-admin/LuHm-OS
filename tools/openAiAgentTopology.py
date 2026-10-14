#!/usr/bin/env python3
"""OpenAI Agents SDK topology proposal; creates no agents, calls, or credentials."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))


def model_topology(registry, control, guard, hold):
    expected = registry.get("requiredAgents", [])
    agents = control.get("agents", {})
    if (registry.get("requiredAgentCount") != 15 or len(expected) != 15 or
        len(set(expected)) != 15 or set(expected) != set(agents)):
        raise ValueError("ROSTER_DRIFT")
    if control.get("boss") != "lum" or guard["aiOrchestration"]["boss"] != "lum":
        raise ValueError("BOSS_DRIFT")
    if guard["aiOrchestration"]["maxParallelSupportWorkers"] != 3:
        raise ValueError("SUPPORT_BUDGET_DRIFT")
    if (hold.get("state") != "QUARANTINED" or
        hold.get("activeTaskWorkersAllowed") is not False or
        guard["aiOrchestration"]["activeWorkerCount"] != 0):
        raise ValueError("QUARANTINE_FAIL_CLOSED")
    profiles = control.get("routeProfiles", {})
    for name, crew in profiles.items():
        if "lum" not in crew or any(x not in expected and x != "professorCrown" for x in crew):
            raise ValueError("INVALID_WORKER_PROFILE:" + name)
    return {
        "schema":"luhmOs.openAiManagerTopology.v1",
        "status":"SDK_TOPOLOGY_DRAFT_NO_RUNTIME",
        "manager":"lum",
        "roster":expected,
        "futureDelegationMode":"agentsAsToolsUnderLumManager",
        "futureProvider":"openAiAgentsSdkOptional",
        "currentProviderInvocations":0,
        "activeAgents":0,
        "availableRuntimeTools":[],
        "handoffs":[],
        "maxParallelSupportWorkers":3,
        "routeProfilesAudited":len(profiles),
        "execution":"DENIED_WHILE_COMPANY_QUARANTINED",
        "agentInstructionsSource":"agent skills and source truth, not synthesized model permission",
        "sdkInstalledOrModelEntitled":False,
        "tracePayloadPolicy":"NO_PRIVATE_MODEL_REASONING_OR_RAW_SECRETS",
        "sourceLaw":"AI proposes. Policy authorizes. CI proves. Human promotes.",
        "crownStatus":"STOP",
    }


def self_test(registry,control,guard,hold):
    base=model_topology(registry,control,guard,hold)
    assert base["activeAgents"]==0 and base["availableRuntimeTools"]==[]
    clone=json.loads(json.dumps(hold))
    clone["activeTaskWorkersAllowed"]=True
    try:model_topology(registry,control,guard,clone)
    except ValueError:pass
    else:raise AssertionError("quarantine bypass")
    clone=json.loads(json.dumps(control))
    clone["boss"]="belldandySecretary"
    try:model_topology(registry,clone,guard,hold)
    except ValueError:pass
    else:raise AssertionError("boss spoof")
    clone=json.loads(json.dumps(registry))
    clone["requiredAgentCount"]=16
    try:model_topology(clone,control,guard,hold)
    except ValueError:pass
    else:raise AssertionError("phantom helper")
    print("GREEN_OPENAI_MANAGER_TOPOLOGY_NEGATIVE_TESTS")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--output",type=Path)
    opts=ap.parse_args()
    docs=[load("doctrine/"+f) for f in (
        "agentSystemDeploymentV1.json","luhmAiControlPlaneV1.json",
        "cloudflareLumOrchestrationV1.json","companyWideOperationalQuarantineV1.json")]
    if opts.self_test:self_test(*docs)
    result=model_topology(*docs)
    if opts.output:
        opts.output.parent.mkdir(parents=True,exist_ok=True)
        opts.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
