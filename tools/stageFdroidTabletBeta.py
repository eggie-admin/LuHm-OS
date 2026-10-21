#!/usr/bin/env python3
"""Stage one verified owner-signed Samsung beta APK for an independent F-Droid repo.

No key creation, no fdroid update/sign, no DNS, no uploads or remote calls.
Requires real SDK aapt/apksigner output and a matching exact-build receipt.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

PACKAGE = "art.eggiebagelface.luhmos.beta"
HEX = re.compile(r"^[a-f0-9]{64}$")
SHA = re.compile(r"^[a-f0-9]{40}$")

def validate(receipt: dict, sha: str, signer: str, package: str, version: int, sdk: int):
    errors = []
    def need(ok, label):
        if not ok: errors.append(label)
    need(receipt.get("schema") == "luhmOs.signedSamsungBeta.v1", "receiptSchema")
    need(SHA.fullmatch(str(receipt.get("sourceRef",""))) is not None, "sourceSHA")
    need(receipt.get("applicationId") == PACKAGE == package, "applicationIdentity")
    need(receipt.get("apkSha256") == sha and HEX.fullmatch(sha) is not None, "apkSHA")
    need(receipt.get("appSignerCertificateSha256") == signer
         and HEX.fullmatch(signer) is not None, "ownerSigner")
    need(receipt.get("versionCode") == version and isinstance(version,int) and
         version > 200000, "monotonicVersion")
    need(receipt.get("targetSdk") == sdk == 36, "targetSdk")
    need(receipt.get("abi") == "arm64-v8a", "arm64")
    need(receipt.get("assetProfile") == "sourceOnlyProceduralLum", "publicAssetFirewall")
    need(receipt.get("releaseMode") is True and receipt.get("debuggable") is False,
         "nonDebugRelease")
    need(receipt.get("deviceProof") is False and receipt.get("betaUpgradeProof") is False,
         "noFakedDeviceProof")
    need(receipt.get("publicPublished") is False, "alreadyPublishedClaim")
    need(receipt.get("crownStatus") == "STOP", "notYetPublic")
    return errors

def probe(command, *, timeout=40):
    p = subprocess.run(command, check=True, capture_output=True, text=True,
                       timeout=timeout)
    return p.stdout + p.stderr

def inspect(apk: Path, aapt: str, apksigner: str):
    badging=probe([aapt,"dump","badging",str(apk)])
    signer=probe([apksigner,"verify","--verbose","--print-certs",str(apk)])
    identity=re.search(r"package: name='([^']+)' versionCode='([0-9]+)'",badging)
    sdk=re.search(r"targetSdkVersion:'([0-9]+)'",badging)
    fingerprint=re.search(r"Signer #1 certificate SHA-256 digest:\s*([0-9a-fA-F]{64})",signer)
    if not identity or not sdk or not fingerprint:
        raise ValueError("BAD_APK_MANIFEST_OR_CERTIFICATE")
    if "application-debuggable" in badging:
        raise ValueError("DEBUGGABLE_APK")
    if "native-code: 'arm64-v8a'" not in badging:
        raise ValueError("WRONG_ABI")
    return identity.group(1),int(identity.group(2)),int(sdk.group(1)),fingerprint.group(1).lower()

def selftest():
    r=dict(schema="luhmOs.signedSamsungBeta.v1",sourceRef="f"*40,
           applicationId=PACKAGE,apkSha256="a"*64,appSignerCertificateSha256="b"*64,
           versionCode=200010,targetSdk=36,abi="arm64-v8a",
           assetProfile="sourceOnlyProceduralLum",releaseMode=True,
           debuggable=False,deviceProof=False,betaUpgradeProof=False,
           publicPublished=False,crownStatus="STOP")
    assert not validate(r,"a"*64,"b"*64,PACKAGE,200010,36)
    for label,bad in [
      ("wrongApp",{"applicationId":PACKAGE+".testing"}),
      ("badSigner",{"appSignerCertificateSha256":"c"*64}),
      ("debuggable",{"debuggable":True}),
      ("badAsset",{"assetProfile":"privateDonor"}),
      ("fakeDevice",{"deviceProof":True}),
      ("downgrade",{"versionCode":116}),
      ("selfRelease",{"publicPublished":True}),
    ]:
        trial={**r,**bad}
        assert validate(trial,"a"*64,"b"*64,PACKAGE,200010,36),label
    print("GREEN_FDROID_SIGNED_BETA_STAGE_7_NEGATIVE_CONTROLS")
    print("NO_ACTUAL_SIGNING_OR_FDROID_INDEX_FROM_SELFTEST")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--apk",type=Path)
    ap.add_argument("--receipt",type=Path)
    ap.add_argument("--expected-signer",help="Public certificate SHA-256, not a key")
    ap.add_argument("--out",type=Path,default=Path("build/fdroid-beta-stage"))
    ap.add_argument("--aapt",default="aapt")
    ap.add_argument("--apksigner",default="apksigner")
    args=ap.parse_args()
    if args.self_test:
        selftest()
        if not args.apk and not args.receipt: return
    if not args.apk or not args.receipt or not args.expected_signer:
        ap.error("--apk, --receipt and --expected-signer required for real staging")
    if not HEX.fullmatch(args.expected_signer.lower()):
        raise SystemExit("RED_EXPECTED_SIGNER_FINGERPRINT")
    if not args.apk.is_file() or not args.receipt.is_file():
        raise SystemExit("RED_MISSING_APK_OR_RECEIPT")
    data=json.loads(args.receipt.read_text(encoding="utf8"))
    digest=hashlib.sha256(args.apk.read_bytes()).hexdigest()
    try:
        app,version,sdk,cert=inspect(args.apk,args.aapt,args.apksigner)
    except (subprocess.SubprocessError,FileNotFoundError,ValueError) as exc:
        raise SystemExit("RED_APK_INSPECTION:"+type(exc).__name__) from exc
    errors=validate(data,digest,cert,app,version,sdk)
    if cert != args.expected_signer.lower(): errors.append("expectedOwnerSigner")
    if errors: raise SystemExit("RED_FDROID_CANDIDATE:"+",".join(errors))
    out=args.out.resolve()
    repo=out/"repo"
    dst=repo/f"{PACKAGE}_{version}.apk"
    if dst.exists():
        if hashlib.sha256(dst.read_bytes()).hexdigest()!=digest:
            raise SystemExit("RED_VERSION_FILENAME_CONFLICT")
    else:
        repo.mkdir(parents=True,exist_ok=True)
        shutil.copy2(args.apk,dst)
    report=dict(schema="luhmOs.fdroidStagingReceipt.v1",status="STAGED_UNSIGNED_INDEX_NOT_PUBLISHED",
                apkPath=str(dst),apkSha256=digest,applicationId=PACKAGE,
                sourceRef=data["sourceRef"],versionCode=version,signerCertificateSha256=cert,
                deviceTested=False,fdroidRepoIndexSigned=False,repoHosted=False,
                publicPublished=False,crownStatus="STOP")
    out.mkdir(parents=True,exist_ok=True)
    (out/"stagingReceipt.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
