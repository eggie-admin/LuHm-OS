#!/usr/bin/env python3
"""Deterministic Cloudflare/Lum routing plan. No network, provider, or agent actions."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = re.compile(r"^[0-9a-f]{40}$")
LANES = ("publicMcp", "privatePortal", "staticAssets", "llmProvider")
FORBIDDEN = ("execute", "publish", "writeDns", "enableProxy", "enableTunnel", "startAgent",
             "recruit", "shareSecrets", "changeFirewall", "exposeLan", "grantCrown")


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def validate_manifest(task, policy):
    errors = []
    def need(ok, reason):
        if not ok: errors.append(reason)
    required = policy["taskEnvelope"]["required"]
    for key in required:
        need(key in task, "missing:" + key)
    for field in ("taskId", "scopeId", "intent"):
        need(isinstance(task.get(field), str) and bool(task.get(field, "").strip()), "empty:" + field)
    need(isinstance(task.get("sourceRef"), str) and SOURCE.fullmatch(task.get("sourceRef", "")) is not None,
         "sourceRefMustBeExact40CharacterSha")
    need(task.get("routeLane") in LANES, "unknownTrafficLane")
    need(task.get("authorityClass") in ("READ_ONLY", "PLAN_ONLY"), "cannotAuthorizeConsequentialAction")
    need(isinstance(task.get("evidenceRefs"), list), "evidenceRefsMustBeArray")
    need(isinstance(task.get("stopConditions"), list) and bool(task.get("stopConditions")),
         "missingStopConditions")
    budget = task.get("budget")
    need(isinstance(budget, dict) and isinstance(budget.get("maxSteps"), int) and
         not isinstance(budget.get("maxSteps"), bool) and 1 <= budget.get("maxSteps", -1) <= 12,
         "invalidMaxSteps")
    need(isinstance(budget, dict) and budget.get("providerUsdMax") == 0,
         "providerSpendingNotAuthorizedInSourcePlanning")
    for key in FORBIDDEN:
        need(task.get(key) is not True, "consequentialActionDenied:" + key)
    need(task.get("providerId") in (None, "none", "deterministicLocal", "existingReceipts",
                                  "googleAi", "openAi"), "unrecognizedProvider")
    return errors


def make_plan(task, policy):
    errors = validate_manifest(task, policy)
    if errors:
        return {"schema":"luhmOs.cloudflareLumRoute.v1","status":"REJECTED","errors":errors,
                "trafficMutation":False,"agentsStarted":0,"crownStatus":"STOP"}
    lane = task["routeLane"]
    conf = policy["trafficLanes"][lane]
    options = {
        "publicMcp": ("readExactRenderMcpAndTls", "DNS-only custom FQDN is not active proof"),
        "privatePortal": ("checkPrivateAccessOriginAndTunnelReceipts", "Tunnel and Access are UNVERIFIED"),
        "staticAssets": ("checkSameOriginStaticAssetRightsAndHashes", "CDN activation not proved"),
        "llmProvider": ("classifyCapabilityAndProviderEntitlement", "No provider runtime invocation")
    }
    operation, disclaimer = options[lane]
    return {
        "schema":"luhmOs.cloudflareLumRoute.v1",
        "status":"READ_ONLY_PLAN_STAGED",
        "taskId":task["taskId"],"sourceRef":task["sourceRef"],"scopeId":task["scopeId"],
        "routeLane":lane, "nextOperation":operation,"networkRoute":conf["route"],
        "notes":disclaimer, "providerRequested":task.get("providerId", "none"),
        "providerExecuted":False,"modelExecuted":False,"privateMcpWrite":False,
        "trafficMutation":False,"agentsStarted":0, "sourceTruth":"doctrine/currentSourceTruthV3.json",
        "evidenceRefs":task["evidenceRefs"],"requestedAuthority":task["authorityClass"],
        "provenRuntime":False,"crownStatus":"STOP",
    }


def test():
    config=load("doctrine/cloudflareLumOrchestrationV1.json")
    base={"taskId":"auditOne","scopeId":"dnsEdge","sourceRef":"a"*40,
          "intent":"look","routeLane":"publicMcp","authorityClass":"READ_ONLY",
          "stopConditions":["onUnknown"],"budget":{"maxSteps":3,"providerUsdMax":0},
          "evidenceRefs":[]}
    for lane in LANES:
        packet={**base,"routeLane":lane}
        decision=make_plan(packet, config)
        assert decision["status"]=="READ_ONLY_PLAN_STAGED",decision
        assert decision["agentsStarted"]==0 and decision["trafficMutation"] is False
    for field,value in (("sourceRef","main"),("routeLane","newOrigin"),
                        ("authorityClass","PUBLIC_EXPOSURE"),
                        ("writeDns",True),("startAgent",True),("publish",True),
                        ("grantCrown",True),("budget",{"maxSteps":1,"providerUsdMax":5})):
        attempt={**base,field:value}
        assert make_plan(attempt,config)["status"]=="REJECTED",field
    print("GREEN_CLOUDFLARE_LUM_ROUTE_NEGATIVE_TESTS")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--task",type=Path)
    args=parser.parse_args()
    if args.self_test:test()
    if args.task:
        plan=make_plan(json.loads(args.task.read_text(encoding="utf-8")),
                       load("doctrine/cloudflareLumOrchestrationV1.json"))
        print(json.dumps(plan,indent=2))
        if plan["status"]=="REJECTED":raise SystemExit(2)


if __name__=="__main__":
    main()
