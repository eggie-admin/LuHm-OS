#!/usr/bin/env python3
"""Read-only, fail-closed vendor provenance boundary and portable ZIP source receipt."""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import subprocess
try:
    from tools import vendorApacheAudit, zipInteropAudit
except ImportError:
    import vendorApacheAudit
    import zipInteropAudit

ROOT=Path(__file__).resolve().parents[1]
VENDORS=(
    "raspberryPiOs","debianUbuntu","firefoxGeckoView","chromium",
    "samsungInternet","safariWebkit","chromiumOs","chromeOs",
    "samsungAndroid","appleIosMacos","pythonZipfile","javaGradleAndroid",
    "ffmpeg","blender","godot4","aiModelsProviders"
)
FIRST_PARTY=("portableZipPolicy","vendorLedger","studioAdapterBoundary")
NO_ACTIONS=("deviceInstall","cloudProvision","keysUsed","publicPublish",
            "merge","crownPromote","agentActivate")

def load(root=ROOT):
    return json.loads((root/"doctrine/vendorProvenanceBoundaryV1.json").read_text(encoding="utf8"))

def source_ref(root=ROOT):
    p=subprocess.run(["git","rev-parse","HEAD"],cwd=root,text=True,capture_output=True,check=False)
    sha=p.stdout.strip()
    if p.returncode or not re.fullmatch("[a-f0-9]{40}",sha):
        raise ValueError("NO_EXACT_SOURCE_SHA")
    if os.getenv("LUHM_SOURCE_REF") and os.environ["LUHM_SOURCE_REF"]!=sha:
        raise ValueError("EXACT_SHA_MISMATCH")
    return sha

def check(p,root=ROOT):
    errors=[]
    def need(value,label):
        if not value:errors.append(label)
    need(p.get("schema")=="luhmOs.vendorProvenanceBoundary.v1","SCHEMA")
    repo=p.get("repository",{})
    need(repo.get("license")=="GPL-3.0-only" and repo.get("rootLicense")=="LICENSE","ROOT_GPL")
    need(all(repo.get(k) is False for k in ("replaceExistingNotices","relicenseThirdParty","publicShip")),"LICENSE_HOLD")
    need("GNU GENERAL PUBLIC LICENSE" in (root/"LICENSE").read_text(encoding="utf8"),"LICENSE_FILE")
    need(p.get("baseReview",{}).get("mainUnchangedRequired") is True,"MAIN_PROTECTED")
    rows=p.get("vendorRows",[])
    need(len(rows)==len(VENDORS) and [r.get("id") for r in rows]==list(VENDORS),"EXACT_VENDOR_CENSUS")
    for row in rows:
        id_=str(row.get("id","unknown"))
        need(row.get("installedVersion")=="UNVERIFIED" and row.get("fileLevelProvenance")=="UNVERIFIED",
             "VENDOR_PROOF_NOT_OBSERVED:"+id_)
        need(all(row.get(k) is False for k in ("sourceFilesCopied","bundledInMutation")),
             "NO_THIRD_PARTY_COPY:"+id_)
        need(row.get("licenseClassIsNotRelicensing") is True and
             isinstance(row.get("licenseClass"),str) and row["licenseClass"]!="Apache-2.0",
             "NO_VENDOR_RELICENSE:"+id_)
        need(str(row.get("upstreamLicenseSource","")).startswith("https://"),"UPSTREAM_REFERENCE:"+id_)
    fp=p.get("firstPartyCandidates",[])
    need([x.get("id") for x in fp]==list(FIRST_PARTY),"FIRST_PARTY_CANDIDATES")
    for row in fp:
        id_=str(row.get("id","unknown"))
        need(row.get("currentDistribution")=="GPL-3.0-only" and
             row.get("apacheCompatibleNewModule")=="CANDIDATE_ONLY","FIRST_PARTY_LICENSE:"+id_)
        need(all(row.get(k) is False for k in
             ("ownershipProof","contributionClearance","derivativeAudit","apacheReleaseEligible")),
             "NO_UNPROVEN_APACHE_ELIGIBILITY:"+id_)
        need((root/row["path"]).is_file(),"FIRST_PARTY_PATH:"+id_)
    z=p.get("artifactContract",{})
    need(z.get("compression")=="ZIP_DEFLATED" and z.get("maxEntries")==96 and
         z.get("maxEntryBytes")==2_000_000 and z.get("maxArchiveBytes")==6_000_000,
         "ZIP_INTEROP_BOUNDS")
    need(all(z.get(k) is True for k in
         ("sortedAllowlist","archiveSha256","perFileSha256InPythonReceipt","javaArchiveSha256",
          "pythonAuthoritativeArchivePolicy","portableAsciiNames","windowsDeviceNamesRejected",
          "casefoldCollisionsRejected")),"ZIP_SAFETY")
    need(all(z.get(k) is False for k in
         ("javaPerFileSha256Verification","untrustedExtractAllAllowed","aarOrApkInstalled","apkSigned")),
         "NO_FALSE_JAVA_APK_PROOF")
    need(not zipInteropAudit.portable_name("luhmos-dev/CON.txt") and
         not zipInteropAudit.portable_name("luhmos-dev/a.txt:ads") and
         zipInteropAudit.portable_name("luhmos-dev/README.md"),"PORTABLE_PATH_IMPLEMENTED")
    devices=p.get("devices",{})
    need(all(devices.get(k)=="UNVERIFIED" for k in
         ("samsungLiteOs","samsungS24FeAntennaProxy","piModel","piHeadlessRuntime",
          "remoteVmHealth","appleRuntime")),"DEVICE_RUNTIME_NOT_PROVEN")
    need(devices.get("samsungLiteNativeDex") is False and
         devices.get("noRootNoFirmwareChanges") is True,"DEVICE_SAFETY")
    transport=p.get("transport",{})
    need(transport.get("base64urlJsonEncoding") is True and
         transport.get("maxDecodedBytes")==45056 and
         all(transport.get(k) is False for k in
             ("base64urlIsEncryption","base44IsEncoding","base44ExternalProviderConnected",
              "openProxy","cloudflareDnsChanged","certbotExecuted")),"ENCODING_AND_EDGE")
    ai=p.get("ai",{})
    need(ai.get("coordinator")=="Lum" and ai.get("proposalOnly") is True and
         ai.get("activeAgents")==0 and ai.get("quarantinedAgents")==15 and
         len(ai.get("roles",[]))==6 and
         all(ai.get(k) is False for k in
             ("modelWeightsBundled","paidProviderCalls","remoteCodeExecution")),"LUM_QUARANTINE")
    need(all(p.get("approvals",{}).get(k) is False for k in NO_ACTIONS),"NO_UNATTENDED_ACTION")
    need(p.get("crownStatus")=="STOP","CROWN_STOP")
    return sorted(set(errors))

def receipt(root=ROOT):
    policy=load(root)
    errors=check(policy,root)
    prior=vendorApacheAudit.check(root)
    errors+=["PREVIOUS_VENDOR_AUDIT:"+e for e in prior["errors"]]
    return {
      "schema":"luhmOs.vendorProvenanceReceipt.v1",
      "exactSourceSha":source_ref(root),
      "sourceChecks":"PASS" if not errors else "FAIL",
      "errors":errors,
      "vendorsAudited":len(policy["vendorRows"]),
      "firstPartyApacheEligible":sum(1 for x in policy["firstPartyCandidates"] if x["apacheReleaseEligible"]),
      "npmTransitivePackages":prior["npmTransitivePackages"],
      "npmMissingLicenseMetadata":prior["npmMissingLicenseMetadata"],
      "npmMetadataLicenseCoverageOnly":len(prior["npmMissingLicenseMetadata"])==0,
      "npmLicenseFilesAndRightsVerified":False,
      "sourceLicense":"GPL-3.0-only",
      "unresolvedGates":[
         "COPYRIGHT_AND_CONTRIBUTION_PROOF",
         "THIRD_PARTY_FILE_LEVEL_LICENSE_SBOM",
         "NPM_PACKAGE_LICENSE_FILES_AND_RIGHTS_REVIEW",
         "JAVA_ZIP_ENTRY_SHA256_NOT_INDEPENDENTLY_CHECKED",
         "SAMSUNG_LITE_AND_ANTENNA_PROXY_PHYSICAL_PROOF",
         "RASPBERRY_PI_AND_REMOTE_VM_HEALTH_PROOF",
         "APPLE_AND_BROWSER_RUNTIME_COMPATIBILITY_PROOF",
         "OWNER_CAST_AND_PUBLICATION_AUTHORITY"
      ],
      "deviceProof":"UNVERIFIED","vmProof":"UNVERIFIED","agentWorkersActive":0,
      "firmwareChanged":False,"networkChanged":False,"keysUsed":False,
      "releaseAllowed":False,"crownStatus":"STOP"
    }

if __name__=="__main__":
    print(json.dumps(receipt(),indent=2))
    raise SystemExit(1 if receipt()["errors"] else 0)
