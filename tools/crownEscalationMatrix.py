#!/usr/bin/env python3
"""Crown Cathedral 4x4 -> 8x8 -> 16x16. Evidence-slot assessments, NOT runtime tests."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PROFILE="doctrine/crownEscalationMatrixV1.json"
SHA=re.compile(r"^[0-9a-f]{40}$")
ALLOWED={"PASS_SOURCE","UNVERIFIED","BLOCKED","FAIL_SOURCE"}

def read_json(root,path):
    return json.loads((root/path).read_text(encoding="utf-8"))

def safe_file(root,relative):
    if not isinstance(relative,str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        return False
    target=root/relative
    try:
        return target.is_file() and not target.is_symlink() and target.resolve().is_relative_to(root.resolve())
    except OSError:
        return False

def digest(root,relative):
    if not safe_file(root,relative):
        return None
    return hashlib.sha256((root/relative).read_bytes()).hexdigest()

def source_checks(root,profile):
    truth=read_json(root,"doctrine/currentSourceTruthV3.json")
    release=read_json(root,"doctrine/finalFormPublicReleaseGateV1.json")
    quarantine=read_json(root,"doctrine/companyWideOperationalQuarantineV1.json")
    fork=read_json(root,"doctrine/communityForkChannelsV1.json")
    lock=read_json(root,"frontEnd/package-lock.json")
    jquery=lock.get("packages",{}).get("node_modules/jquery",{})
    checks={
        "identity/source":truth.get("canonicalRepository")=="eggie-admin/LuHm-OS",
        "identity/lock":fork.get("repository")=="eggie-admin/LuHm-OS" and profile.get("product")=="LuHm-OS: Project Premonition",
        "identity/boundary":fork.get("officialNameDoesNotAuthorizeImpersonation") is True,
        "identity/proof":fork.get("sourceIsNotInstallableBinary") is True,
        "vendor/source":len(fork.get("vendorPins",[]))==8,
        "vendor/lock":lock.get("lockfileVersion")==3 and jquery.get("version")=="3.7.1" and bool(jquery.get("integrity")),
        "vendor/boundary":fork.get("vendorForksCreated")==0 and fork.get("autoForkVendors") is False,
        "vendor/proof":fork.get("upstreamLicensesIndividuallyVerified") is False,
        "security/source":"Security Advisories" in (root/"SECURITY.md").read_text(encoding="utf-8"),
        "security/lock":quarantine.get("state")=="QUARANTINED" and quarantine.get("activeTaskWorkersAllowed") is False,
        "security/boundary":fork.get("noPrivateAssetsInPublicForks") is True,
        "security/proof":fork.get("securitySettingsLiveVerified") is False,
        "release/source":release.get("fullPublicReleaseGreen") is False and release.get("fullPublicReleasePublished") is False,
        "release/lock":all(c.get("signerVerified") is False for c in fork.get("channels",[])),
        "release/boundary":all(fork.get(k) is False for k in ("autoRelease","autoDeploy","autoMerge","autoSign")),
        "release/proof":"rollback" in (root/"manual/pluginReleaseHub.md").read_text(encoding="utf-8").lower()
    }
    rows=profile["fourByFour"]["rows"];cols=profile["fourByFour"]["columns"]
    expected={row+"/"+col for row in rows for col in cols}
    if len(rows)!=4 or len(cols)!=4 or set(checks)!=expected:
        raise ValueError("FOUR_BY_FOUR_SCHEMA_DRIFT")
    return [{"id":name,"status":"PASS_SOURCE" if checks[name] else "FAIL_SOURCE","proofScope":"offlineSource"}
            for name in sorted(expected)]

def probe_dependency(root, component):
    if component=="npmShell":
        p=read_json(root,"frontEnd/package.json")
        return p.get("dependencies",{}).get("jquery")=="3.7.1"
    if component=="glassWorld":
        p=read_json(root,"frontEnd/prototypes/glassWorld/package.json")
        return p.get("dependencies",{})=={"@babylonjs/core":"9.32.0","jquery":"3.7.1","vue":"3.5.44"}
    if component=="mcpHost":
        return "mcp==2.2.0" in (root/"host/mcp/requirements.txt").read_text(encoding="utf-8")
    return None

def eight_assessment(root, profile, sha):
    out=[]
    group=profile["eightByEight"]
    if len(group["components"])!=8 or len(group["contracts"])!=8:
        raise ValueError("EIGHT_BY_EIGHT_SCHEMA_DRIFT")
    for component in group["components"]:
        name=component["id"];rel=component["path"]
        exists=safe_file(root,rel)
        for contract in group["contracts"]:
            state="UNVERIFIED"
            if contract=="exists": state="PASS_SOURCE" if exists else "FAIL_SOURCE"
            elif contract=="sourceBound": state="PASS_SOURCE" if exists and SHA.fullmatch(sha) else "FAIL_SOURCE"
            elif contract=="manifest":
                if not exists:state="FAIL_SOURCE"
                else:
                    try:
                        data=(root/rel).read_bytes()
                        if rel.endswith(".json"):json.loads(data)
                        state="PASS_SOURCE" if data else "FAIL_SOURCE"
                    except (ValueError,UnicodeError,OSError):
                        state="FAIL_SOURCE"
            elif contract=="dependencyPin":
                value=probe_dependency(root,name)
                if value is not None:state="PASS_SOURCE" if value else "FAIL_SOURCE"
            # Other evidence must be actual independent results, not inferred from file existence.
            out.append({"id":name+"/"+contract,"status":state,"sourcePath":rel,
                        "evidence":"sourceSnapshot" if state=="PASS_SOURCE" else "separateIndependentProofRequired"})
    return out

def sixteen_assessment(root,profile):
    out=[]
    group=profile["sixteenBySixteen"]
    if len(group["surfaces"])!=16 or len(group["proofs"])!=16:
        raise ValueError("SIXTEEN_BY_SIXTEEN_SCHEMA_DRIFT")
    for surface in group["surfaces"]:
        rel=surface.get("path")
        for proof in group["proofs"]:
            state="UNVERIFIED"; evidence=None
            if proof=="crownApproval":
                state="BLOCKED";evidence="unmetProductionAndReleaseProofs"
            elif proof in ("sourceAnchor","contentDigest"):
                if rel is not None:
                    value=digest(root,rel)
                    state="PASS_SOURCE" if value else "FAIL_SOURCE"
                    evidence=rel if proof=="sourceAnchor" else value
            elif proof=="syntaxOrSchema" and isinstance(rel,str) and rel.endswith(".json"):
                try:
                    read_json(root,rel)
                    state="PASS_SOURCE"
                    evidence=rel
                except (ValueError,OSError):
                    state="FAIL_SOURCE"
            out.append({"id":surface["id"]+"/"+proof,"status":state,
                        "evidence":evidence,"proofClass":"source" if state=="PASS_SOURCE" else "notYetAccepted"})
    return out

def assess(root,profile,sha):
    if not SHA.fullmatch(sha):raise ValueError("EXACT_SHA_REQUIRED")
    invariants=profile.get("invariants",{})
    required={"readOnly":True,"blockCrown":True,"autoMerge":False,"autoDeploy":False,
              "autoSign":False,"autoPublish":False,"vendorSourceExecuted":False,
              "deviceObserved":False,"externalReceiptsAssumed":False}
    if profile.get("schema")!="luhmOs.crownEscalationMatrix.v1" or any(invariants.get(k) is not v for k,v in required.items()):
        raise ValueError("UNSAFE_POLICY")
    four=source_checks(root,profile)
    eight=eight_assessment(root,profile,sha)
    sixteen=sixteen_assessment(root,profile)
    all_rows=four+eight+sixteen
    if len(four)!=16 or len(eight)!=64 or len(sixteen)!=256 or len({row["id"] for row in all_rows})!=len(all_rows):
        raise ValueError("MATRIX_CARDINALITY_DRIFT")
    if any(row["status"] not in ALLOWED for row in all_rows):
        raise ValueError("INVALID_STATUS")
    if any(row["status"]!="BLOCKED" for row in sixteen if row["id"].endswith("/crownApproval")):
        raise ValueError("CROWN_UNSAFE")
    hard_fail=[row["id"] for row in all_rows if row["status"]=="FAIL_SOURCE"]
    def count(rows):
        return {key:sum(r["status"]==key for r in rows) for key in ("PASS_SOURCE","UNVERIFIED","BLOCKED","FAIL_SOURCE")}
    return {"schema":"luhmOs.crownEscalationReceipt.v1","sourceRef":sha,
            "level4x4":{"evaluated":16,"counts":count(four),"cells":four},
            "level8x8":{"evaluated":64,"counts":count(eight),"cells":eight},
            "level16x16":{"evaluated":256,"counts":count(sixteen),"cells":sixteen},
            "totalEvidenceSlots":336,"sourceErrors":hard_fail,
            "sourceGuard":"PASS_SOURCE_ONLY" if not hard_fail else "RED_SOURCE",
            "realDeviceVerified":False,"cloudflareBuildVerified":False,"vendorForksCreated":0,
            "signerVerified":False,"workflowReductionExecuted":False,"publicReleaseAuthorized":False,
            "productionDeployed":False,"crown":"STOP"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-ref",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    actual=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,text=True,capture_output=True,check=False)
    if actual.returncode!=0 or actual.stdout.strip()!=args.source_ref:
        raise SystemExit("EXACT_GIT_HEAD_MISMATCH")
    profile=read_json(ROOT,PROFILE)
    result=assess(ROOT,profile,args.source_ref)
    target=Path(args.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"sourceRef":result["sourceRef"],"sourceGuard":result["sourceGuard"],
        "level4x4":result["level4x4"]["counts"],
        "level8x8":result["level8x8"]["counts"],
        "level16x16":result["level16x16"]["counts"],
        "crown":result["crown"]},indent=2))
    if result["sourceErrors"]:raise SystemExit(1)

if __name__=="__main__":
    main()
