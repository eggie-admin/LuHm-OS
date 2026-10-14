#!/usr/bin/env python3
"""Evidence-only FINAL_FORM public-release audit. No publication side effects."""
import argparse
import copy
import json
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
def read(name):
    return json.loads((root / "doctrine" / name).read_text(encoding="utf-8"))

def check(gate, truth, delivery, art, plugin, debug, head):
    artifact = gate["releaseArtifact"]
    manifest = read("androidApkManifestInspectionV1.json")
    valid_hash = lambda value: isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None
    checks = {
        "exactBuiltRelease": artifact["type"] == "signedStableReleaseApk" and artifact["sourceRef"] == head and valid_hash(artifact["sha256"]) and artifact["sha256"] != debug["artifact"]["sha256"] and artifact["independentVerification"] == "PROVEN" and artifact["stableBuildRequired"] is True and artifact["provenanceRunId"] != "PENDING",
        "physicalSamsung": truth["androidLayer"]["physicalSamsungProof"] == "GREEN" and gate["requiredProofs"]["androidPhysicalFirstLaunch"] == "PROVEN",
        "releaseSigning": gate["requiredProofs"]["androidStableReleaseSignerLineage"] == "PROVEN" and valid_hash(artifact["signingCertificateSha256"]) and artifact["signingKeyContinuityProven"] is True and artifact["signingKeyStoredInGit"] is False,
        "targetSdk36": gate["requiredProofs"]["androidEndApplicationTargetSdk36"] == "PROVEN" and artifact["targetSdkVerified"] == 36 and artifact["targetSdkManifestReceipt"] != "PENDING",
        "updates": gate["requiredProofs"]["androidUpgradeRollbackPath"] == "PROVEN" and artifact["deviceRuntimeReceipt"] != "PENDING",
        "publicArt": art["publicCharacterFamilies"]["currentEvidenceState"] == "APPROVED_HASHED_PUBLIC_ART" and gate["requiredProofs"]["publicArtRightsAndProvenance"] == "PROVEN",
        "publicHttps": gate["requiredProofs"]["publicHttpsInstallAndUpdateRoute"] == "PROVEN",
        "fdroidIndex": gate["requiredProofs"]["fdroidRepositorySigningAndIndex"] == "PROVEN",
        "chatGptHost": plugin["externalGates"]["currentOpenAiToolScan"] == "PROVEN" and gate["requiredProofs"]["chatGptHostInstallAndCurrentChatInvocation"] == "PROVEN",
        "package": gate["requiredProofs"]["releasePackageExactCurrentSource"] == "PROVEN" and artifact["sourceRef"] == head,
        "professorReview": gate["professorAuthority"]["exactStableSignedArtifactReviewed"] is True and gate["requiredProofs"]["finalReleaseAssetReview"] == "PROVEN",
    }
    errors = []
    if gate["schema"] != "luhmOs.finalFormPublicReleaseGate.v1":
        errors.append("schema drift")
    if gate["crownStatus"] != "STOP" or gate["authority"] != "Professor":
        errors.append("Crown authority drift")
    if debug["artifact"]["sha256"] != truth["androidLayer"]["proposedDebugBuild"]["artifactSha256"]:
        errors.append("debug source truth/hash mismatch")
    if not delivery["lanes"]["release"]["prohibitDebugCertificate"]:
        errors.append("release signer boundary drift")
    if manifest.get("sha256") != debug["artifact"]["sha256"] or manifest.get("sourceRef") != debug["builtSourceRef"]:
        errors.append("binary APK proof differs from immutable debug CAST receipt")
    if manifest.get("targetSdk") != 36 or manifest.get("debuggable") is not True:
        errors.append("binary debug APK manifest target/debug drift")
    if delivery["platform"]["endApplicationTargetSdkCurrentEvidence"] != "VERIFIED_DEBUG_APK_TARGET_36":
        errors.append("debug APK targetSdk proof was not reconciled")
    if gate["offlineStaticAuditMayGrantPublication"] is not False or gate["verifiedExternalPublicationProofRequired"] is not True:
        errors.append("static CI cannot grant actual publication")
    if artifact["signingKeyStoredInGit"] is not False:
        errors.append("release signing credentials cannot be in source")
    if gate["releaseArtifactMayNotReuseDebugSigner"] is not True:
        errors.append("release may not reuse disposable debug signer")
    green = all(checks.values()) and not errors
    if gate["fullPublicReleaseGreen"] and not green:
        errors.append("forged GREEN")
    if gate["fullPublicReleasePublished"] and not green:
        errors.append("forged PUBLISHED")
    return {
        "schema":"luhmOs.finalFormPublicReleaseAudit.v1",
        "status":"RED_CONTRACT" if errors else "GREEN_FULL_RELEASE" if green else "AMBER_RELEASE_HOLD",
        "sourceRef":head, "debugSourceRef":debug["builtSourceRef"],
        "observedDebugApkTargetSdk":manifest.get("targetSdk"),
        "observedDebugApkDebuggable":manifest.get("debuggable"),
        "checks":checks, "blocked":sorted(k for k,v in checks.items() if not v),
        "fullPublicReleaseGreen":green, "errors":errors,
        "publicationAuthorized":green and gate["fullPublicReleasePublished"]
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    opts = parser.parse_args()
    g=read("finalFormPublicReleaseGateV1.json")
    t=read("currentSourceTruthV3.json")
    a=read("androidDeliveryLanesV1.json")
    art=read("publicArtReleaseReadinessV1.json")
    p=read("pluginPublicationV2.json")
    d=read("proposedAndroidCastEvidenceV1.json")
    sha=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
    result=check(g,t,a,art,p,d,sha)
    if opts.self_test:
        for key in ("fullPublicReleaseGreen","fullPublicReleasePublished"):
            forged=copy.deepcopy(g);forged[key]=True
            if check(forged,t,a,art,p,d,sha)["status"] != "RED_CONTRACT":
                result["errors"].append("negative control failed: "+key)
    if result["errors"]:result["status"]="RED_CONTRACT"
    out=root / "build/final-form/release-audit.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    raise SystemExit(1 if result["errors"] else 0)
if __name__=="__main__":main()
