#!/usr/bin/env python3
"""Four-track cross-surface source truth audit. Scope stays source-only until observed."""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((ROOT/name).read_text(encoding="utf-8"))


def review(closure,truth,android,release,company):
    issues=[]
    def need(test,problem):
        if not test:issues.append(problem)
    need(closure.get("schema")=="luhmOs.fourTrackReleaseClosure.v1","four track schema")
    need(truth.get("releaseExecution",{}).get("contract")=="doctrine/fourTrackReleaseClosureV1.json","source truth pointer")
    need(truth.get("releaseExecution",{}).get("status")=="STAGED_EXACT_SOURCE_PROOF_GATES","false release status")
    need(closure.get("sourceTruth")=="doctrine/currentSourceTruthV3.json","source truth drift")
    need(closure.get("baselineSourceRef")=="12aef02b9763b5c0e1d1f0a47bbaf97fb44031b0","entry baseline changed")
    need(set(closure.get("tracks",{}))=={"androidRuntime","chatGptCockpit","godotWeb","stableDistribution"},"release track inventory")
    a=closure.get("tracks",{}).get("androidRuntime",{})
    need(a.get("debugApkSha256")==android.get("proof",{}).get("proposedBuildApkSha256"),"Android artifact drift")
    need(a.get("expectedPackageName")=="art.eggiebagelface.luhmos.testing","package identity drift")
    need(a.get("video",{}).get("installedPackageBound") is False,"device screen was promoted without package hash")
    need(a.get("claimFirstLaunch") is False,"first launch falsely claimed")
    need(android.get("proof",{}).get("physicalDeviceInstall")=="PENDING","device proof incorrectly promoted")
    c=closure.get("tracks",{}).get("chatGptCockpit",{})
    need(c.get("cannotBeProvedByExternalMcpProbe") is True,"endpoint mistaken for ChatGPT host")
    need(c.get("tools")==["luhm_open_cockpit","luhm_open_godot_player"],"MCP tools drift")
    g=closure.get("tracks",{}).get("godotWeb",{})
    need(g.get("exactCastWorkflow")==".github/workflows/godot-web-harness.yml","CAST compile boundary drift")
    d=closure.get("tracks",{}).get("stableDistribution",{})
    need(d.get("debugApkExcluded") is True and d.get("publish") is False,"debug or silent publication")
    need(d.get("fdroidIndexPrivateKeyInGit") is False,"repo private key in git")
    need(release.get("fullPublicReleasePublished") is False,"source final-form release already published")
    need(company.get("state")=="QUARANTINED","agent quarantine drift")
    guard=closure.get("immutableGate",{})
    for key in ("sourceCiDoesNotProvePhysicalDevice","mcpEndpointDoesNotProvePluginInstall",
                "godotLoaderDoesNotProveInput","debugSignerCannotPublish",
                "releaseKeysStayOffRepo","rawPrivateMediaStaysOffRepo",
                "companyOniQuarantineUnchanged","oneMutableSourceLane",
                "fullGreenRequiresIndependentReceipts","noAutoRelease"):
        need(guard.get(key) is True,"missing guard:"+key)
    need(closure.get("crownStatus")=="STOP","Crown drift")
    for tool in (a.get("tool"),c.get("externalProbe"),g.get("smoke"),d.get("preflight")):
        need(isinstance(tool,str) and (ROOT/tool).is_file(),"missing implementation:"+str(tool))
    return issues


def self_test(closure,truth,android,release,company):
    assert not review(closure,truth,android,release,company),"original four-track source failed"
    for key in ("fullGreenRequiresIndependentReceipts","noAutoRelease","mcpEndpointDoesNotProvePluginInstall"):
        bad=copy.deepcopy(closure)
        bad["immutableGate"][key]=False
        assert review(bad,truth,android,release,company),"negative gate failed:"+key
    bad=copy.deepcopy(closure)
    bad["tracks"]["androidRuntime"]["claimFirstLaunch"]=True
    assert review(bad,truth,android,release,company),"forged Samsung proof accepted"
    bad=copy.deepcopy(closure)
    bad["tracks"]["stableDistribution"]["publish"]=True
    assert review(bad,truth,android,release,company),"forged F-Droid publication accepted"
    print("GREEN_FOUR_TRACK_SOURCE_NEGATIVE_CONTROLS")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    c=read("doctrine/fourTrackReleaseClosureV1.json")
    t=read("doctrine/currentSourceTruthV3.json")
    a=read("doctrine/androidDeliveryLanesV1.json")
    r=read("doctrine/finalFormPublicReleaseGateV1.json")
    q=read("doctrine/companyWideOperationalQuarantineV1.json")
    errors=review(c,t,a,r,q)
    if args.self_test:
        self_test(c,t,a,r,q)
    print(json.dumps({"schema":"luhmOs.fourTrackReleaseAudit.v1",
        "status":"RED_SOURCE_CONTRACT" if errors else "GREEN_FOUR_TRACK_EXECUTION_STAGED",
        "androidExactInstalledProof":False,"chatGptHostProof":False,"godotInteractivePlayProof":False,
        "publicReleaseProof":False,"issues":errors,"crownStatus":"STOP"},indent=2))
    raise SystemExit(1 if errors else 0)

if __name__=="__main__":
    main()
