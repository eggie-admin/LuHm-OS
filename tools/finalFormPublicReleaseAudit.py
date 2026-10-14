#!/usr/bin/env python3
"""Evidence-only FINAL_FORM public-release audit. No publication side effects."""
import argparse
import copy
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
def read(name):
    return json.loads((root / "doctrine" / name).read_text(encoding="utf-8"))

def check(gate, truth, delivery, art, plugin, debug, head):
    checks = {
        "exactBuiltRelease": debug["builtSourceRef"] == head and debug["claims"]["stableReleaseCertificateProven"],
        "physicalSamsung": truth["androidLayer"]["physicalSamsungProof"] == "GREEN" and gate["requiredProofs"]["androidPhysicalFirstLaunch"] == "PROVEN",
        "releaseSigning": gate["requiredProofs"]["androidStableReleaseSignerLineage"] == "PROVEN",
        "targetSdk36": delivery["platform"]["endApplicationTargetSdkCurrentEvidence"] == "PROVEN_TARGET_36",
        "updates": gate["requiredProofs"]["androidUpgradeRollbackPath"] == "PROVEN",
        "publicArt": art["publicCharacterFamilies"]["currentEvidenceState"] == "APPROVED_HASHED_PUBLIC_ART",
        "publicHttps": gate["requiredProofs"]["publicHttpsInstallAndUpdateRoute"] == "PROVEN",
        "fdroidIndex": gate["requiredProofs"]["fdroidRepositorySigningAndIndex"] == "PROVEN",
        "chatGptHost": plugin["externalGates"]["currentOpenAiToolScan"] == "PROVEN",
        "package": gate["requiredProofs"]["releasePackageExactCurrentSource"] == "PROVEN",
        "professorReview": gate["professorAuthority"]["exactStableSignedArtifactReviewed"] is True,
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
    green = all(checks.values()) and not errors
    if gate["fullPublicReleaseGreen"] and not green:
        errors.append("forged GREEN")
    if gate["fullPublicReleasePublished"] and not green:
        errors.append("forged PUBLISHED")
    return {
        "schema":"luhmOs.finalFormPublicReleaseAudit.v1",
        "status":"RED_CONTRACT" if errors else "GREEN_FULL_RELEASE" if green else "AMBER_RELEASE_HOLD",
        "sourceRef":head, "debugSourceRef":debug["builtSourceRef"],
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
