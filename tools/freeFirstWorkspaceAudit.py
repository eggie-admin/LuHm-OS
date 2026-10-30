#!/usr/bin/env python3
"""Free-first 4 sources x 4 tiers x 6 gates: source checks, not provider/runtime proof."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"doctrine/freeFirstFourSourceWorkspaceV1.json"
SHA=re.compile(r"^[a-f0-9]{40}$")
GATES=("inventory","normalize","sandbox","zeroCost","proof","approve")
STATES=("PASS_SOURCE","UNVERIFIED","BLOCKED","FAIL_SOURCE")

def check(policy):
    errors=[]
    def ok(condition,code):
        if not condition: errors.append(code)
    ok(policy.get("schema")=="luhmOs.freeFirstFourSourceWorkspace.v1","SCHEMA")
    ok(policy.get("status")=="SOURCE_ONLY_SECURITY_HOLD" and policy.get("crown")=="STOP","CROWN_FALSE_GREEN")
    ok(policy.get("sourceLaw")=="AI proposes. Policy authorizes. CI proves. Human promotes.","DOCTRINE")
    streams=policy.get("sources",[])
    ok([x.get("id") for x in streams]==["openAi","github","googleAi","sidecars"],"FOUR_FEEDS")
    ok(sum(x.get("codeAuthority") is True for x in streams)==1 and streams[1].get("codeAuthority") is True,"GITHUB_AUTHORITY")
    ok(all(x.get("liveTokenOrApiAuthority") is False for x in streams),"PROVIDER_IMPERSONATION")
    tiers=policy.get("tiers",[])
    ok([x.get("id") for x in tiers]==["thinClient","localStudio","githubWorkspace","remoteSidecar"],"FOUR_TIERS")
    ok(policy.get("gates")==list(GATES),"SIX_GATES")
    ok(all(x.get("canReceiveSigningMaterial") is False for x in tiers),"SIGNER_EXPOSURE")
    drive=policy.get("drive",{})
    ok(drive.get("securityFinding")=="PRIVATE_CONTROL_PLANE_CURRENTLY_ANYONE_WRITER","PRIVATE_ACL_GAP_HIDDEN")
    for key in ("formerlyPrivateControlAclVerifiedSafe","globalPrivateAclSafe","protectedReadEnabled",
                "protectedWriteEnabled","publicWriteWorkspaceAuthority","githubActionsDriveAccess"):
        ok(drive.get(key) is False,"DRIVE_LANE_UNSAFE_"+key)
    ok(drive.get("prohibitSecretOrMediaCopy") is True,"SECRET_MOVE")
    proxy=policy.get("proxies",{})
    local=proxy.get("local",{}); remote=proxy.get("remote",{}); trust=proxy.get("trust",{})
    ok(local.get("networkBind") is None and local.get("authority")=="localLoopback127_0_0_1","LOCAL_LOOPBACK")
    ok(all(local.get(key) is False for key in ("allowLanPublicBind","allowAdbRoot","allowDirectPhoneToPrivateVault")),"LOCAL_EXPOSURE")
    ok(remote.get("authority")=="existingRenderManagedTls" and
       all(remote.get(k) is False for k in ("exposeNewPublicPort","enableCloudflareTunnel","allowMutableMcp","oidcReady")),"REMOTE_EXPOSURE")
    ok(all(trust.get(k) is True for k in ("requireIndependentAuth","requireShortLivedIdentityForWrites",
             "doNotTrustForwardedHeaders","denyRawSql","denyUntrustedCustomNodes","denyOpenProxy")),"TRUST_BOUNDARY")
    free=policy.get("freeFirst",{})
    ok(free.get("policy")=="ZERO_UNAPPROVED_SPEND" and free.get("requestedSpendUsdDefault")==0,"SPEND_FLOOR")
    for k in ("providerEligibleFreeTierIsAccountEntitlement","autoUpgradeToPaid","autoBuyCredits"):
        ok(free.get(k) is False,"BILLING_ELEVATION_"+k)
    ok(free.get("approvalBeforeBillableCall")=="PROFESSOR_EXPLICIT_PER_ACTION_AND_PROVIDER_BUDGET","APPROVAL_GATE")
    ok(free.get("overage")=="DENY_AND_DEGRADE_TO_OFFLINE","OVERAGE")
    for k in ("autoCreate",):
        ok(free.get("githubCodespaces",{}).get(k) is False,"CODESPACES_AUTO_CREATE")
    ok(free.get("googleAiStudioGemini",{}).get("autoCall") is False and
       free.get("googleAiStudioGemini",{}).get("sendPrivateMasters") is False,"GOOGLE_AUTO_CALL")
    ok(free.get("googleComputeVm",{}).get("autoProvision") is False,"VM_AUTO_PROVISION")
    daily=policy.get("dailyBuild",{})
    ok(daily.get("source")=="protected-main-only" and
       daily.get("scheduledWorkflow")==".github/workflows/free-first-workspace-daily.yml","DAILY_SOURCE")
    ok(daily.get("npmIgnoreScripts") is True and daily.get("receiptRetentionDays")==7,"DAILY_SUPPLY_CHAIN")
    for k in ("noPaidApi","noDeployment","noProviderSecrets","noDriveSync"):
        ok(daily.get(k) is True,"DAILY_SIDE_EFFECT_"+k)
    safety=policy.get("safety",{})
    ok(safety.get("sourceOnly") is True,"SOURCE_ONLY")
    for k in ("allowAutoMerge","allowAutoDeploy","allowPaidInference","allowSecretsInSource",
              "allowDriveExport","allowDeviceControl"):
        ok(safety.get(k) is False,"UNSAFE_"+k)
    studio=policy.get("studio",{})
    ok(studio.get("resolutionProfiles")==["540p","720p","1080p","nativeMeasuredOnly"],"RESOLUTION_ORDER")
    ok(studio.get("sixWebcamCapture")=="UNVERIFIED" and
       studio.get("godotDeviceLaunch")=="UNVERIFIED","FAKE_DEVICE_PROOF")
    return sorted(set(errors))

def assess(policy):
    errors=check(policy)
    feed=policy["sources"]; tiers=policy["tiers"]; gates=policy["gates"]
    if len(feed)!=4 or len(tiers)!=4 or len(gates)!=6:raise ValueError("MATRIX_CARDINALITY")
    cells=[]
    for src in feed:
        for tier in tiers:
            for gate in gates:
                state="UNVERIFIED"
                if gate=="inventory":
                    state="PASS_SOURCE"
                elif gate=="normalize" and src["id"]=="github":
                    state="PASS_SOURCE"
                elif gate=="sandbox" and tier["id"]=="thinClient":
                    state="PASS_SOURCE" if tier["canReceiveSigningMaterial"] is False else "FAIL_SOURCE"
                elif gate=="zeroCost":
                    state="PASS_SOURCE" if policy["freeFirst"]["requestedSpendUsdDefault"]==0 else "FAIL_SOURCE"
                elif gate=="approve":
                    state="BLOCKED"
                cells.append({"id":src["id"]+"/"+tier["id"]+"/"+gate,"state":state,
                              "proofClass":"policySource" if state=="PASS_SOURCE" else "independentProofRequired"})
    if len(cells)!=96 or len({c["id"] for c in cells})!=96:raise ValueError("MATRIX_IDENTITY")
    counts={k:sum(c["state"]==k for c in cells) for k in STATES}
    return {"schema":"luhmOs.freeFirstWorkspaceSnapshot.v1",
       "sourceSha":None,"status":"RED_SOURCE" if errors else "PASS_SOURCE_ONLY_SECURITY_HOLD",
       "policyErrors":errors,"cells":cells,"counts":counts,"total":96,
       "driveAclOwnerOnly":False,"currentGoogleAiProjectEntitlement":"UNVERIFIED",
       "renderProxyDeployedByThisWorkflow":False,"driveAssetsMoved":False,
       "realSamsungVerified":False,"spendApproved":False,"crown":"STOP"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-ref",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    if not SHA.fullmatch(args.source_ref):raise SystemExit("EXACT_SOURCE_REF_REQUIRED")
    result=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True)
    if result.returncode!=0 or result.stdout.strip()!=args.source_ref:
        raise SystemExit("EXACT_CHECKOUT_SHA_MISMATCH")
    policy=json.loads(POLICY.read_text(encoding="utf8"))
    receipt=assess(policy)
    receipt["sourceSha"]=args.source_ref
    receipt["policySha256"]=hashlib.sha256(POLICY.read_bytes()).hexdigest()
    target=Path(args.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"sourceSha":args.source_ref,"status":receipt["status"],
                      "cells":96,"counts":receipt["counts"],"securityHold":True},sort_keys=True))
    if receipt["policyErrors"]:raise SystemExit(2)

if __name__=="__main__":main()
