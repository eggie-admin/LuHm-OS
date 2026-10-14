#!/usr/bin/env python3
"""Safe direct-APK distribution preflight. Never creates keys or publishes a release."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

HASH=re.compile(r"^[0-9a-f]{64}$")
EXPECTED_PACKAGE="art.eggiebagelface.luhmos.testing"
DEBUG_APK_SHA="0b0fdfbe25e8937abfe6e647cb23de53838e0189fc545d062aee73f57edd4f0e"


def verify_claims(meta):
    errors=[]
    def need(ok,msg):
        if not ok:errors.append(msg)
    need(meta.get("schema")=="luhmOs.stableAndroidDistributionCandidate.v1","schema")
    need(meta.get("applicationId")==EXPECTED_PACKAGE,"package identity")
    need(isinstance(meta.get("versionCode"),int) and meta.get("versionCode",0)>116,"monotonic version required")
    need(meta.get("targetSdk",0)>=36,"targetSdk for Play handset lane")
    need(meta.get("debuggable") is False,"debuggable APK not releasable")
    need(meta.get("signerClass")=="ownerControlledStableRelease","disposable/debug signer")
    for k in ("apkSha256","appSignerCertificateSha256","fdroidIndexCertificateSha256"):
        need(isinstance(meta.get(k),str) and HASH.fullmatch(meta[k]) is not None,"missing valid hash:"+k)
    need(meta.get("apkSha256")!=DEBUG_APK_SHA,"historical debug artifact cannot publish")
    need(meta.get("appSignerCertificateSha256")!=meta.get("fdroidIndexCertificateSha256"),"distinct signing identities")
    for flag in ("rightsReviewed","privacyReviewed","updateInstallTested","userLaunchProved","professorExactArtifactApproval"):
        need(meta.get(flag) is True,"missing external proof:"+flag)
    evidence=meta.get("evidence",{})
    for field in ("deviceRun","stableSignerLineage","fdroidSignedIndex","publicHttpsAndTls","versionUpgrade","professorReview"):
        need(isinstance(evidence.get(field),str) and len(evidence[field])>=12,"missing referenced receipt:"+field)
    need(meta.get("repositoryPrivateSigningKeysStoredInSource") is False,"signing keys in repository")
    need(meta.get("releasePublicationStatus")=="NOT_PUBLISHED","preflight cannot be a publication receipt")
    return errors


def read_signer_output(text):
    match=re.search(r"Signer #1 certificate SHA-256 digest:\s*([0-9a-fA-F]{64})",text)
    if not match:raise ValueError("apksigner certificate digest missing")
    return match.group(1).lower()


def self_test():
    fake={"schema":"luhmOs.stableAndroidDistributionCandidate.v1",
          "applicationId":EXPECTED_PACKAGE,"versionCode":117,"targetSdk":36,
          "debuggable":False,"signerClass":"ownerControlledStableRelease",
          "apkSha256":"a"*64,"appSignerCertificateSha256":"b"*64,
          "fdroidIndexCertificateSha256":"c"*64,"rightsReviewed":True,
          "privacyReviewed":True,"updateInstallTested":True,"userLaunchProved":True,
          "professorExactArtifactApproval":True,
          "evidence":{k:"external-receipt-"+k for k in ("deviceRun","stableSignerLineage","fdroidSignedIndex","publicHttpsAndTls","versionUpgrade","professorReview")},
          "repositoryPrivateSigningKeysStoredInSource":False,
          "releasePublicationStatus":"NOT_PUBLISHED"}
    assert not verify_claims(fake)
    for key,value in (("debuggable",True),("signerClass","debug"),("apkSha256",DEBUG_APK_SHA),
                      ("professorExactArtifactApproval",False),("versionCode",116),
                      ("releasePublicationStatus","LIVE")):
        original=fake[key]
        fake[key]=value
        assert verify_claims(fake),"negative control failed:"+key
        fake[key]=original
    assert read_signer_output("Signer #1 certificate SHA-256 digest: "+"f"*64)=="f"*64
    print("GREEN_DISTRIBUTION_CONTRACT_NEGATIVE_TESTS")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--apk",type=Path)
    ap.add_argument("--candidate",type=Path)
    ap.add_argument("--output",default="build/distribution/release-preflight.json")
    args=ap.parse_args()
    if args.self_test:self_test()
    if not args.candidate:return
    meta=json.loads(args.candidate.read_text(encoding="utf-8"))
    errors=verify_claims(meta)
    if not args.apk or not args.apk.is_file():
        errors.append("release APK missing")
    else:
        digest=hashlib.sha256(args.apk.read_bytes()).hexdigest()
        if digest!=meta.get("apkSha256"):errors.append("APK bytes differ from signed candidate")
        else:
            try:
                proc=subprocess.run(["apksigner","verify","--verbose","--print-certs",str(args.apk)],
                                    check=True,capture_output=True,text=True,timeout=45)
                cert=read_signer_output(proc.stdout)
                if cert!=meta.get("appSignerCertificateSha256"):errors.append("signer lineage mismatch")
            except (FileNotFoundError,subprocess.SubprocessError,ValueError) as exc:
                errors.append("independent apksigner verify unavailable:"+type(exc).__name__)
    report={"schema":"luhmOs.publicDistributionPreflight.v1",
            "status":"RED_PREPARE" if errors else "SOURCE_AND_APK_PREFLIGHT_ELIGIBLE_EXTERNAL_PROOF_REQUIRED",
            "releasePublished":False,"fdroidIndexLiveProven":False,
            "androidNativeRuntimeProven":False,"errors":errors,"crownStatus":"STOP"}
    target=Path(args.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    raise SystemExit(1 if errors else 0)


if __name__=="__main__":main()
