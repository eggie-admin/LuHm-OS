#!/usr/bin/env python3
"""Prepare a private F-Droid repository workspace from an independently verified APK.

No signing keys, no invocation of fdroidserver, no publication, no network.
Only the repo/ directory is eligible for later public hosting AFTER fdroid
update signs the index and owner approval. metadata/ and config.yml are private.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path
from zipfile import ZipFile

APP="art.eggiebagelface.luhmos.beta"
HEX40=re.compile(r"[0-9a-f]{40}\Z")
HEX64=re.compile(r"[0-9a-f]{64}\Z")
NAME="LuHm-OS: Project Premonition Beta"

def review(folder: Path, *, source: str, signer: str, version: int, digest: str) -> tuple[list[str], Path]:
    errors=[]
    def need(value: bool, label: str):
        if not value: errors.append(label)
    folder=folder.resolve()
    path=folder/"stagingReceipt.json"
    record={}
    try: record=json.loads(path.read_text(encoding="utf8"))
    except (OSError,ValueError): errors.append("missingOrInvalidReceipt")
    filename=f"{APP}_{version}.apk"
    apk=folder/"repo"/filename
    need(HEX40.fullmatch(source) is not None,"independentSourceSHA")
    need(HEX64.fullmatch(signer) is not None,"independentSignerFingerprint")
    need(HEX64.fullmatch(digest) is not None,"independentAPKDigest")
    need(isinstance(version,int) and not isinstance(version,bool) and version>200000,"independentVersionCode")
    need(record.get("schema")=="luhmOs.fdroidStagingReceipt.v1","schema")
    need(record.get("status")=="STAGED_UNSIGNED_INDEX_NOT_PUBLISHED","unsignedIndexState")
    need(record.get("applicationId")==APP,"applicationId")
    need(record.get("sourceRef")==source,"sourceRef")
    need(record.get("versionCode")==version,"version")
    need(record.get("signerCertificateSha256")==signer,"signer")
    need(record.get("apkSha256")==digest,"sha256")
    need(record.get("fdroidRepoIndexSigned") is False,"noIndexClaim")
    need(record.get("repoHosted") is False and record.get("publicPublished") is False,"notPublished")
    need(record.get("deviceTested") is False and record.get("crownStatus")=="STOP","deviceAndCrown")
    need(Path(str(record.get("apkPath",""))).resolve()==apk.resolve(),"exactAPKBinder")
    need(apk.is_file() and not apk.is_symlink(),"apkPresentRegularFile")
    if apk.is_file():
        need(apk.stat().st_size>100,"nonemptyAPK")
        need(hashlib.sha256(apk.read_bytes()).hexdigest()==digest,"actualByteDigest")
        try:
            with ZipFile(apk) as data:
                need("AndroidManifest.xml" in data.namelist(),"androidManifestPresent")
        except (OSError,ValueError): errors.append("notAnArchive")
    others=[p for p in (folder/"repo").glob("*.apk") if p.name!=filename]
    need(not others,"unexpectedAPK")
    # A staging directory is NOT a signed F-Droid repository. Allow only the
    # independently verified APK, including no hidden files, legacy index.jar,
    # private artwork, config, symlinks, or nested directories.
    repoDir=folder/"repo"
    if not repoDir.is_dir() or repoDir.is_symlink():
        errors.append("unsafeRepoDirectory")
    else:
        entries=list(repoDir.iterdir())
        need(len(entries)==1 and entries[0].name==filename
             and entries[0].is_file() and not entries[0].is_symlink(),
             "unexpectedRepoContents")
    forbidden=[
        folder/"repo"/"config.yml",
        folder/"repo"/"config.py",
        folder/"repo"/"keystore.jks",
        folder/"repo"/"index-v2.json",
        folder/"repo"/"index-v2.jar"
    ]
    need(not any(x.exists() for x in forbidden),"unsignedOrSecretPublicIndex")
    return errors,apk

def build(folder: Path, *, source: str, signer: str, version: int, digest: str):
    errors,apk=review(folder,source=source,signer=signer,version=version,digest=digest)
    if errors: raise SystemExit("RED_FDROID_REPO_CANDIDATE:"+",".join(errors))
    metadata=folder/"metadata"/f"{APP}.yml"
    metadata.parent.mkdir(parents=True,exist_ok=True)
    content=(
        "Categories:\n  - Games\n"
        "Name: "+NAME+"\n"
        "Summary: Original 3D and interactive art prototype\n"
        "Description: |-\n"
        "  LuHm-OS: Project Premonition is an artist-first Android game and creative studio beta.\n"
        "  This build uses approved local assets and procedural Lum, without\n"
        "  publishing private Rebel character or film master files.\n"
        "SourceCode: https://github.com/eggie-admin/LuHm-OS\n"
        "CurrentVersionCode: "+str(version)+"\n"
    )
    if metadata.is_file() and metadata.read_text(encoding="utf8")!=content:
        raise SystemExit("RED_METADATA_CONFLICT_NOT_OVERWRITTEN")
    metadata.write_text(content,encoding="utf8")
    receipt={
        "schema":"luhmOs.fdroidRepoCandidate.v1",
        "state":"OWNER_SIGNING_AND_REPO_HOSTING_PENDING",
        "sourceRef":source,
        "applicationId":APP,
        "versionCode":version,
        "apkSha256":digest,
        "apkSignerCertificateSha256":signer,
        "candidateApk":apk.name,
        "metadataFile":metadata.name,
        "publicFilesReady":False,
        "repoIndexSigned":False,
        "repoSignerFingerprint":"NOT_CONFIGURED",
        "url":"NOT_VERIFIED",
        "tabletInstalled":False,
        "tabletUpgradeProven":False,
        "publicPublicationApproved":False,
        "crownStatus":"STOP"
    }
    outfile=folder/"fdroidCandidateReceipt.json"
    outfile.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf8")
    print(json.dumps(receipt,indent=2))

def test():
    import zipfile
    with tempfile.TemporaryDirectory() as tmp:
        folder=Path(tmp)
        source="a"*40
        signer="b"*64
        version=200501
        repo=folder/"repo"
        repo.mkdir()
        apk=repo/f"{APP}_{version}.apk"
        with zipfile.ZipFile(apk,"w") as z:
            z.writestr("AndroidManifest.xml",b"x"*140)
        digest=hashlib.sha256(apk.read_bytes()).hexdigest()
        state={"schema":"luhmOs.fdroidStagingReceipt.v1",
          "status":"STAGED_UNSIGNED_INDEX_NOT_PUBLISHED",
          "apkPath":str(apk),"apkSha256":digest,
          "applicationId":APP,"sourceRef":source,"versionCode":version,
          "signerCertificateSha256":signer,"deviceTested":False,
          "fdroidRepoIndexSigned":False,"repoHosted":False,"publicPublished":False,
          "crownStatus":"STOP"}
        receipt=folder/"stagingReceipt.json"
        receipt.write_text(json.dumps(state))
        assert not review(folder,source=source,signer=signer,version=version,digest=digest)[0]
        build(folder,source=source,signer=signer,version=version,digest=digest)
        assert (folder/"metadata"/f"{APP}.yml").is_file()
        # These would be unsafe to upload even if the expected APK is valid.
        for name in ("index.jar", "index-v2.json", ".hidden-key", "private-master.glb"):
            extra=repo/name
            extra.write_bytes(b"UNAPPROVED")
            assert review(folder,source=source,signer=signer,version=version,digest=digest)[0], "unexpectedRepoFile:"+name
            extra.unlink()
        extraDir=repo/"private-art"
        extraDir.mkdir()
        assert review(folder,source=source,signer=signer,version=version,digest=digest)[0], "unexpectedRepoDirectory"
        extraDir.rmdir()
        checks=[
          ("badSource",dict(source="c"*40)),
          ("badSigner",dict(signer="c"*64)),
          ("badHash",dict(digest="c"*64)),
          ("badVersion",dict(version=200502)),
        ]
        for label,kw in checks:
            params=dict(source=source,signer=signer,version=version,digest=digest)
            params.update(kw)
            assert review(folder,**params)[0],"NEGATIVE_FALSE_GREEN:"+label
        state["publicPublished"]=True
        receipt.write_text(json.dumps(state))
        assert review(folder,source=source,signer=signer,version=version,digest=digest)[0],"publishedReceipt"
        state["publicPublished"]=False
        receipt.write_text(json.dumps(state))
        with apk.open("ab") as output:output.write(b"TAMPER")
        assert review(folder,source=source,signer=signer,version=version,digest=digest)[0],"corruptedAPK"
        apk.write_bytes(apk.read_bytes()[:-6])
        (repo/"config.yml").write_text("SHOULD_NOT_BE_PUBLIC")
        assert review(folder,source=source,signer=signer,version=version,digest=digest)[0],"secretInPublicRepo"
    print("GREEN_FDROID_OFFLINE_WORKSPACE_7_NEGATIVE_CONTROLS")
    print("NO_SIGNING_KEYS_NO_PUBLIC_INDEX_NO_TABLET_INSTALL")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--stage",type=Path,default=Path("build/fdroid-beta-stage"))
    ap.add_argument("--expected-source")
    ap.add_argument("--expected-signer")
    ap.add_argument("--expected-version",type=int)
    ap.add_argument("--expected-apk-sha256")
    args=ap.parse_args()
    if args.self_test:test()
    if args.self_test and not args.expected_source:return
    if not all((args.expected_source,args.expected_signer,args.expected_version,args.expected_apk_sha256)):
        ap.error("require independently selected --expected-source, --expected-signer, --expected-version, --expected-apk-sha256")
    build(args.stage,source=args.expected_source,signer=args.expected_signer.lower(),version=args.expected_version,digest=args.expected_apk_sha256.lower())

if __name__=="__main__":main()
