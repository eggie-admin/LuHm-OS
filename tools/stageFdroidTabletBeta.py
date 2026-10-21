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
RECEIPT_SCHEMA = Path(__file__).resolve().parents[1] / "doctrine/schemas/signedSamsungBetaV1.schema.json"

def validateReceiptSchema(receipt):
    """Enforce the deliberately small scalar schema; unknown constraints fail closed."""
    schema = json.loads(RECEIPT_SCHEMA.read_text(encoding="utf8"))
    if set(schema) - {"$schema", "title", "type", "additionalProperties", "required", "properties"}:
        raise ValueError("UNSUPPORTED_RECEIPT_SCHEMA")
    if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
        raise ValueError("UNSUPPORTED_RECEIPT_SCHEMA")
    if type(receipt) is not dict:
        return ["receiptObject"]
    props = schema["properties"]
    errors = ["missing:" + key for key in schema["required"] if key not in receipt]
    errors += ["unknown:" + key for key in receipt if key not in props]
    for key, rule in props.items():
        if set(rule) - {"const", "type", "pattern", "minimum"}:
            raise ValueError("UNSUPPORTED_RECEIPT_CONSTRAINT")
        if key not in receipt:
            continue
        value = receipt[key]
        if "const" in rule and (type(value) is not type(rule["const"]) or value != rule["const"]):
            errors.append("const:" + key)
        if "type" in rule:
            expected = {"string": str, "integer": int}.get(rule["type"])
            if expected is None:
                raise ValueError("UNSUPPORTED_RECEIPT_TYPE")
            if type(value) is not expected:
                errors.append("type:" + key)
                continue
        if "pattern" in rule and (type(value) is not str or re.fullmatch(rule["pattern"], value) is None):
            errors.append("pattern:" + key)
        if "minimum" in rule and (type(value) is not int or value < rule["minimum"]):
            errors.append("minimum:" + key)
    return errors

def validate(receipt: dict, sha: str, signer: str, package: str, version: int, sdk: int, expectedSource: str | None = None):
    errors = validateReceiptSchema(receipt)
    if type(receipt) is not dict:
        return errors
    if expectedSource is not None and (type(expectedSource) is not str or SHA.fullmatch(expectedSource) is None or receipt.get("sourceRef") != expectedSource):
        errors.append("expectedSource")
    def need(ok, label):
        if not ok: errors.append(label)
    need(receipt.get("schema") == "luhmOs.signedSamsungBeta.v1", "receiptSchema")
    need(SHA.fullmatch(str(receipt.get("sourceRef",""))) is not None, "sourceSHA")
    need(receipt.get("applicationId") == PACKAGE == package, "applicationIdentity")
    need(receipt.get("apkSha256") == sha and HEX.fullmatch(sha) is not None, "apkSHA")
    need(receipt.get("appSignerCertificateSha256") == signer
         and HEX.fullmatch(signer) is not None, "ownerSigner")
    need(receipt.get("versionCode") == version and isinstance(version,int) and
         version > 200000, "versionFloor")
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
    r=dict(schema="luhmOs.signedSamsungBeta.v1",sourceRef="f"*40,runId="123",
           applicationId=PACKAGE,apkSha256="a"*64,appSignerCertificateSha256="b"*64,
           versionCode=200010,targetSdk=36,abi="arm64-v8a",
           assetProfile="sourceOnlyProceduralLum",releaseMode=True,
           debuggable=False,deviceProof=False,betaUpgradeProof=False,
           publicPublished=False,crownStatus="STOP")
    assert not validate(r,"a"*64,"b"*64,PACKAGE,200010,36)
    root = RECEIPT_SCHEMA.parents[2]
    contract = json.loads((root / "doctrine/samsungTabletInstallV1.json").read_text())
    beta = contract["lanes"]["ownerSignedBeta"]
    assert beta["receiptSchema"] == str(RECEIPT_SCHEMA.relative_to(root))
    assert beta["applicationId"] == PACKAGE
    assert beta["expectedSourceRequired"] is True and beta["expectedSignerRequired"] is True
    assert contract["promotion"] is False and contract["publicationAuthority"] is False
    assert contract["releaseAuthority"] is False and contract["productionSigningAuthority"] is False
    assert contract["crownStatus"] == "STOP"
    truth = json.loads((root / "doctrine/currentSourceTruthV3.json").read_text())
    cockpit = json.loads((root / "doctrine/androidWeb3CockpitV2.json").read_text())
    assert truth["androidLayer"]["tabletInstallContract"] == "doctrine/samsungTabletInstallV1.json"
    assert cockpit["tabletInstallContract"] == truth["androidLayer"]["tabletInstallContract"]
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
    for bad in [None, [], "receipt", {**r, "unexpected": True}, {**r, "runId": "0"},
                {**r, "sourceRef": "F"*40}, {**r, "versionCode": True},
                {**r, "releaseMode": 1}, {k:v for k,v in r.items() if k != "runId"}]:
        assert validate(bad,"a"*64,"b"*64,PACKAGE,200010,36), "schemaFalseGreen"
    assert validate(r,"a"*64,"b"*64,PACKAGE,200010,36,expectedSource="e"*40), "sourceMismatch"
    assert not validate(r,"a"*64,"b"*64,PACKAGE,200010,36,expectedSource="f"*40)
    print("GREEN_FDROID_SIGNED_BETA_STAGE_17_NEGATIVE_CONTROLS")
    print("NO_ACTUAL_SIGNING_OR_FDROID_INDEX_FROM_SELFTEST")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--apk",type=Path)
    ap.add_argument("--receipt",type=Path)
    ap.add_argument("--expected-source", help="Independently selected full source commit SHA")
    ap.add_argument("--expected-signer",help="Public certificate SHA-256, not a key")
    ap.add_argument("--out",type=Path,default=Path("build/fdroid-beta-stage"))
    ap.add_argument("--aapt",default="aapt")
    ap.add_argument("--apksigner",default="apksigner")
    args=ap.parse_args()
    if args.self_test:
        selftest()
        if not args.apk and not args.receipt: return
    if not args.apk or not args.receipt or not args.expected_signer or not args.expected_source:
        ap.error("--apk, --receipt, --expected-signer and --expected-source required for real staging")
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
    errors=validate(data,digest,cert,app,version,sdk,expectedSource=args.expected_source)
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
