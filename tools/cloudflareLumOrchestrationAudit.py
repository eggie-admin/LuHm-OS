#!/usr/bin/env python3
"""Cloudflare air traffic and Lum model-provider source truth audit; no external mutation."""
from __future__ import annotations
import copy
import json
from pathlib import Path
from cloudflareLumRoute import test as route_test

ROOT=Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))


def audit(policy, cloud, truth, ai, network, registry, hold):
    errors=[]
    def require(yes,why):
        if not yes:errors.append(why)
    require(policy.get("schema")=="luhmOs.cloudflareLumOrchestration.v1","orchestration schema")
    require(policy.get("authority")=="Professor" and policy.get("sourceAnchor")==
            "7b0c6b5e730d2a77b71223c0cf6b55d1cc4c1121","authority/source anchor")
    require(policy.get("canonicalSource")=="doctrine/currentSourceTruthV3.json","canonical pointer")
    require(cloud.get("aiOrchestrationBoundary",{}).get("contract")==
            "doctrine/cloudflareLumOrchestrationV1.json","Cloudflare policy link")
    require(truth.get("networkLayer",{}).get("airTrafficOrchestration",{}).get("contract")==
            "doctrine/cloudflareLumOrchestrationV1.json","source truth link")
    require(truth.get("agentLayer",{}).get("cloudflareOrchestration")==
            "doctrine/cloudflareLumOrchestrationV1.json","agent truth link")
    require(ai.get("cloudflareLumOrchestration",{}).get("contract")==
            "doctrine/cloudflareLumOrchestrationV1.json","AI control plane link")
    require(ai.get("boss")=="lum" and policy.get("aiOrchestration",{}).get("boss")=="lum",
            "boss delegation drift")
    require(registry.get("requiredAgentCount")==15,"registered roster drift")
    require(hold.get("state")=="QUARANTINED" and hold.get("activeTaskWorkersAllowed") is False,
            "agent quarantine lifted without proof")
    require(policy.get("aiOrchestration",{}).get("activeWorkerCount")==0 and
            policy.get("aiOrchestration",{}).get("recursiveRecruitment") is False and
            policy.get("aiOrchestration",{}).get("handoffsEnabled") is False,
            "recursive/executing Oni leak")
    require(policy.get("aiOrchestration",{}).get("maxParallelSupportWorkers")==3,
            "parallel staff budget drift")
    lanes=policy.get("trafficLanes",{})
    require(set(lanes)=={"publicMcp","privatePortal","staticAssets","llmProvider"},
            "traffic lane count")
    mcp=lanes.get("publicMcp",{})
    cloud_mcp=cloud.get("lanes",{}).get("publicChatPluginMcp",{})
    require(mcp.get("origin")+"/mcp"==cloud_mcp.get("currentEndpoint"),
            "MCP direct origin drift")
    require(mcp.get("route")=="directRenderManagedTls" and
            cloud_mcp.get("cloudflareDependencyForCurrentEndpoint") is False and
            mcp.get("cloudflareTunnel") is False and
            mcp.get("cloudflareProxy")=="OFF_UNTIL_COMPAT_PROOF",
            "MCP tunnel/proxy activated without compatibility proof")
    require(mcp.get("cacheMcpRequests") is False and mcp.get("writePermission") is False,
            "anonymous MCP allowed cache or writes")
    require(lanes.get("privatePortal",{}).get("tunnelState")=="UNVERIFIED" and
            lanes.get("privatePortal",{}).get("edgeAccessState")=="UNVERIFIED",
            "unproved private tunnel/Access")
    require(lanes.get("staticAssets",{}).get("route")=="renderSameOrigin" and
            lanes.get("staticAssets",{}).get("cdnState")=="UNVERIFIED",
            "unproved external CDN")
    require(lanes.get("llmProvider",{}).get("route")=="NOT_CLOUDFLARE_AI" and
            lanes.get("llmProvider",{}).get("providerGatewayState")=="NOT_DEPLOYED",
            "Cloudflare AI provider promoted")
    require(network.get("identityChain",{}).get("runtimeState")=="UNVERIFIED",
            "DNS identity chain promoted")
    require(policy.get("taskEnvelope",{}).get("sourceRefExact40Sha") is True,
            "unbounded source identity")
    for field, allowed in policy.get("writeControls",{}).items():
        require(allowed is False,"unexpected mutation allowed:"+field)
    require(policy.get("statusSeal",{}).get("crownStatus")=="STOP","Crown drift")
    return errors


def self_test(items):
    policy, cloud, truth, ai, network, registry, hold = items
    assert not audit(*items)
    for field,value in [("mayChangeCloudflareDns",True),("mayActivateAiAgents",True),
                        ("mayExposePrivateLan",True),("mayUseProductionSigningKey",True)]:
        corrupt=copy.deepcopy(policy)
        corrupt["writeControls"][field]=value
        assert audit(corrupt,cloud,truth,ai,network,registry,hold),"negative:"+field
    for lane,change in [("publicMcp",("cloudflareTunnel",True)),
                        ("llmProvider",("providerGatewayState","LIVE")),
                        ("privatePortal",("tunnelState","ACTIVE"))]:
        corrupt=copy.deepcopy(policy)
        corrupt["trafficLanes"][lane][change[0]]=change[1]
        assert audit(corrupt,cloud,truth,ai,network,registry,hold),"negative:"+lane
    changed=copy.deepcopy(hold)
    changed["activeTaskWorkersAllowed"]=True
    assert audit(policy,cloud,truth,ai,network,registry,changed)
    route_test()
    print("GREEN_CLOUDFLARE_LUM_ORCHESTRATION_NEGATIVE_CONTROLS")


def main():
    items=(read("doctrine/cloudflareLumOrchestrationV1.json"),
           read("doctrine/cloudflareAirTrafficControllerV1.json"),
           read("doctrine/currentSourceTruthV3.json"),
           read("doctrine/luhmAiControlPlaneV1.json"),
           read("doctrine/networkSpineV1.json"),
           read("doctrine/agentSystemDeploymentV1.json"),
           read("doctrine/companyWideOperationalQuarantineV1.json"))
    errors=audit(*items)
    if not errors:self_test(items)
    print(json.dumps({"schema":"luhmOs.cloudflareLumOrchestrationAudit.v1",
        "status":"RED_SOURCE_CONTRACT" if errors else "GREEN_SOURCE_ORCHESTRATION_ONLY",
        "cloudflareDnsChanged":False,"openAiAgentRunProven":False,
        "chatGptHostProven":False,"agentRuntimeProven":False,"issues":errors,
        "crownStatus":"STOP"},indent=2))
    raise SystemExit(1 if errors else 0)


if __name__=="__main__":
    main()
