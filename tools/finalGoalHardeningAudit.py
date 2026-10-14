#!/usr/bin/env python3
"""Cross-layer fail-closed LuHm final-goal source audit. No runtime or publication."""
from __future__ import annotations
import argparse
import copy
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=re.compile(r"^[0-9a-f]{40}$")
SHA=re.compile(r"^[0-9a-f]{64}$")


def read(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))


def evaluate(guard,truth,hold,release,cloud):
    errors=[]
    def need(ok,why):
        if not ok:errors.append(why)
    need(guard.get("schema")=="luhmOs.finalGoalHardening.v1","schema")
    need(guard.get("authority")=="Professor","authority")
    need(guard.get("canonicalRepo")==truth.get("canonicalRepository")=="eggie-admin/LuHm-OS","source repo")
    need(truth.get("finalGoalHardening",{}).get("contract")=="doctrine/finalGoalHardeningV1.json","truth pointer")
    need(guard.get("notAnExhaustivePenTest") is True,"overclaim exhaustive review")
    layers=guard.get("layers",{})
    need(set(layers)=={"source","cloudflare","agents","chatGptHost","godotWeb","android","publicDistribution"},"missing layer")
    for name,layer in layers.items():
        target=layer.get("contract")
        need(isinstance(target,str) and target.startswith("doctrine/") and (ROOT/target).is_file(),"unbound layer:"+name)
    need(guard.get("layers",{}).get("cloudflare",{}).get("currentPublicMcp")=="directRenderManagedTls","network redirect")
    need(guard["layers"]["cloudflare"]["liveDnsChanged"] is False,"unverified DNS changed")
    need(cloud.get("trafficLanes",{}).get("publicMcp",{}).get("cloudflareTunnel") is False,"public MCP tunnel unexpectedly enabled")
    need(hold.get("state")=="QUARANTINED" and hold.get("activeTaskWorkersAllowed") is False,"Oni hold")
    need(layers["agents"].get("activeWorkers")==0 and layers["agents"].get("providerSdkExecutionProven") is False,"agent invented")
    need(truth.get("agentLayer",{}).get("companyActiveOniWorkers")==0,"agent truth mismatch")
    need(layers["chatGptHost"].get("hostInvocationProven") is False,"host fabricated")
    need(layers["chatGptHost"].get("packageBuiltIsHostInstall") is False,"plugin package mistaken for invocation")
    need(layers["godotWeb"].get("gameplayAndTouchProven") is False,"gameplay fabricated")
    need(layers["godotWeb"].get("sourceAndRenderIsPlayableProof") is False,"render mistaken for play")
    android=layers["android"]
    need(android.get("requiresExactBuildShaFromCi") is True and android.get("requiresExactSourceRef") is True,"stale Android source proof accepted")
    need(SHA.fullmatch(str(android.get("knownDebugApkSha256",""))) is not None,"debug sha")
    need(SHA.fullmatch(str(android.get("knownDebugSignerSha256",""))) is not None,"debug signer")
    need(SOURCE.fullmatch(str(android.get("knownDebugSourceRef",""))) is not None,"debug source")
    need(android.get("knownArtifactIsProductionSigned") is False and android.get("physicalInstallProof") is False,"debug promoted to release")
    need((ROOT/android.get("collector","missing")).is_file(),"Android collector missing")
    pub=layers["publicDistribution"]
    need(pub.get("publicationAllowed") is False and pub.get("fullPublicReleaseGreen") is False,"public release forged")
    need(release.get("fullPublicReleaseGreen") is False and release.get("fullPublicReleasePublished") is False,"final gate forged")
    need(pub.get("ownerReleaseKeyCustody")=="EXTERNAL_REQUIRED","release signing key mislocated")
    need(pub.get("fdroidSignedIndexProven") is False,"unverified F-Droid index")
    need(truth.get("finalFormRelease",{}).get("publicReleaseGreen") is False,"release source truth mismatch")
    promotion=guard.get("promotion",{})
    for key in ("separateTruthForSourceCiRenderDeviceHostAndPublic","noModelSelfApproval","noAutoSecrets",
                "noAutoOniActivation","noPublicReleaseFromDebug","professorCrownMaintained","buildOnlyAllowed"):
        need(promotion.get(key) is True,"missing promotion control:"+key)
    need(guard.get("crownStatus")=="STOP","Crown drift")
    return errors


def self_test(args):
    guard,truth,hold,release,cloud=args
    assert not evaluate(*args),"original contract broken"
    for layer,key,value in (("agents","activeWorkers",1),
                            ("chatGptHost","hostInvocationProven",True),
                            ("godotWeb","gameplayAndTouchProven",True),
                            ("android","physicalInstallProof",True),
                            ("publicDistribution","publicationAllowed",True),
                            ("cloudflare","liveDnsChanged",True)):
        bad=copy.deepcopy(guard)
        bad["layers"][layer][key]=value
        assert evaluate(bad,truth,hold,release,cloud),"forged proof accepted:"+layer
    bad=copy.deepcopy(guard)
    bad["layers"]["android"]["knownDebugApkSha256"]="yesterday"
    assert evaluate(bad,truth,hold,release,cloud),"stale APK hash accepted"
    print("GREEN_FINAL_GOAL_CROSS_LAYER_NEGATIVE_TESTS")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    opts=ap.parse_args()
    args=(read("doctrine/finalGoalHardeningV1.json"),
          read("doctrine/currentSourceTruthV3.json"),
          read("doctrine/companyWideOperationalQuarantineV1.json"),
          read("doctrine/finalFormPublicReleaseGateV1.json"),
          read("doctrine/cloudflareLumOrchestrationV1.json"))
    errors=evaluate(*args)
    if opts.self_test and not errors:
        self_test(args)
    source=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    report={"schema":"luhmOs.finalGoalHardeningAudit.v1","sourceRef":source,
            "status":"RED_SOURCE_CONTRACT" if errors else "GREEN_SOURCE_GATES_PUBLIC_RELEASE_PENDING",
            "fullSystemRuntimeGreen":False,"signedPublicApkProven":False,
            "chatGptHostInvoked":False,"deviceInstalled":False,"openAiAgentsActive":False,
            "errors":errors,"crownStatus":"STOP"}
    print(json.dumps(report,indent=2))
    raise SystemExit(1 if errors else 0)


if __name__=="__main__":
    main()
