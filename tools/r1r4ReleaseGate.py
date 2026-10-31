#!/usr/bin/env python3
"""R1→R4 evidence ladder. Strict source truth, no automatic release/promotion."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"doctrine/r1r4GothPreviewV1.json"
SHA=re.compile(r"^[a-f0-9]{40}$")
def verify(doc):
    errors=[]
    def need(ok,code):
        if not ok:errors.append(code)
    need(doc.get("schema")=="luhmOs.r1r4GothPreviewV1" and doc.get("state")=="SOURCE_CANDIDATE"
         and doc.get("authority")=="Professor" and doc.get("crown")=="STOP","RUNG_SCHEMA")
    r=doc.get("rungs",[])
    need([x.get("id") for x in r]==["R1","R2","R3","R4"] and
         [x.get("name") for x in r]==["PROPOSED","TESTING","SIGNED_BETA","PUBLIC_RELEASE"] and
         all(x.get("automaticProtectedMutation") is False for x in r),"RUNG_SEQUENCE")
    need(len(doc.get("source",[]))==5 and all((ROOT/x.get("path","")).is_file() for x in doc.get("source",[])),
         "RUNG_SOURCE_ARTIFACTS")
    evidence=doc.get("independentProof",{})
    need(len(evidence)==9 and all(v is False for v in evidence.values()),"RUNG_FAKE_EXTERNAL_PROOF")
    render=doc.get("render",{})
    need(render.get("source")=="ORIGINAL_PROCEDURAL_GEOMETRY" and render.get("adultCharacterOnly") is True and
         render.get("WebGl2Primary") is True and render.get("SVG2dFallback") is True and
         render.get("externalRendererDependencies")==0 and render.get("adaptiveDprMax")==1.5,"RENDER_BUDGET")
    for k in ("riggedAsset","topologyReadyForRetarget","autoDownloadModels","nativeAPKShipped","deviceFPSMeasured"):
        need(render.get(k) is False,"RUNG_FAKE_RENDER_"+k)
    release=doc.get("release",{})
    for k in ("protectedMainMayBeMergedAutomatically","publicDeploymentAllowed","signingSecretsFromGit"):
        need(release.get(k) is False,"RUNG_RELEASE_"+k)
    need(release.get("doNotInventCrown") is True,"RUNG_CROWN_INVARIANT")
    need(release.get("ownerPromotionRequired") is True and release.get("unrealLicenseHold") is True
         and release.get("CIIsNotDeviceProof") is True,"RUNG_OWNER")
    return sorted(set(errors))
def ladder(doc,source_green=False):
    if verify(doc):raise ValueError("RUNG_POLICY_FAIL")
    has_source=bool(source_green)
    return {
      "schema":"luhmOs.r1r4ReleaseAssessment.v1",
      "rungs":[
        {"id":"R1","status":"SOURCE_CHECKED" if has_source else "BLOCKED_SOURCE","promoted":False,
         "scope":"candidate only"},
        {"id":"R2","status":"CI_AND_REAL_DEVICE_EVIDENCE_PENDING" if has_source else "BLOCKED_R1",
         "promoted":False,"scope":"testing only"},
        {"id":"R3","status":"HOLD_OWNER_SIGNING_AND_SAMSUNG_PROOF","promoted":False,"scope":"private signed beta"},
        {"id":"R4","status":"HOLD_PUBLIC_RELEASE_AND_OWNER_CAST","promoted":False,"scope":"public"},
      ],
      "nativeApkAvailable":False,"fullyRigged3dAssetProven":False,
      "realSamsungWebgl2Tested":False,"publicReleaseAuthorized":False,"crown":"STOP"
    }
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--source-ref",required=True);parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if not SHA.fullmatch(args.source_ref):raise SystemExit("EXACT_SOURCE_SHA_REQUIRED")
    head=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True)
    if head.returncode or head.stdout.strip()!=args.source_ref:raise SystemExit("EXACT_CHECKOUT_MISMATCH")
    doc=json.loads(POLICY.read_text(encoding="utf-8"))
    errors=verify(doc)
    report=ladder(doc,source_green=not errors) if not errors else {"status":"RED_SOURCE","errors":errors,"crown":"STOP"}
    report["sourceRef"]=args.source_ref
    report["policySha256"]=hashlib.sha256(POLICY.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    if errors:raise SystemExit(2)
if __name__=="__main__":main()
