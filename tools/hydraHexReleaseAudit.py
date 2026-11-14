#!/usr/bin/env python3
"""Source-only HEX 256/512/1024 package evidence inventory.

Counts are *assessed slots*, not successful CI tests, installed apps or releases.
Any missing source evidence stays AMBER; release gate stays BLOCKED_CROWN.
No remote network, provider calls, package installs or artifact publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = "doctrine/hydraHexReleaseMatrixV1.json"
ALLOWED_SLOTS = (256, 512, 1024)
FAMILY_IDS = ("deb", "dmg", "apk", "npm")
STAGES = ("source", "build", "verify", "release")
CONTROL_IDS = (
    "exactSource", "canonAuthority", "workerQuarantine", "packageInputFiles",
    "artifactDescriptor", "toolchainAvailability", "dependencyLock",
    "browserRuntime", "typedSqlJsonManifest", "googleCompatibility",
    "storageBoundary", "rightsAndLicenses", "artifactDigest",
    "installAndRollback", "deviceOrHostSmoke", "professorRelease",
)


def load_json(relative: str) -> dict:
    p = ROOT / relative
    if not p.is_file() or p.is_symlink():
        raise ValueError("RED_MISSING_CANON:" + relative)
    obj = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("RED_CANON_JSON:" + relative)
    return obj


def exact_git_sha() -> str:
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                  text=True, timeout=10).strip().lower()
    if not re.fullmatch("[0-9a-f]{40}", sha):
        raise ValueError("RED_BAD_SOURCE_REF")
    return sha


def source_evidence(family: dict, control: str, context: dict) -> tuple[str, list[str]]:
    """Only static, independently inspectable source facts can pass this gate."""
    truth, q, storage, google, manifest, pkg = (
        context[k] for k in ("truth", "quarantine", "storage", "google", "manifest", "policy")
    )
    known_paths = {
        "packageInputFiles": family["source"],
        "artifactDescriptor": family["contracts"],
        "toolchainAvailability": [family["buildLane"]],
        "dependencyLock": (["androidWeb3Plugin/build.gradle.kts",
                            "androidWeb3Plugin/plugin/build.gradle.kts"]
                           if family["id"] == "apk" else ["frontEnd/package-lock.json"]),
        "browserRuntime": (["androidWeb3Plugin/plugin/src/main/java/art/eggiebagelface/luhmos/web3/AndroidWeb3CockpitPlugin.kt"]
                           if family["id"] == "apk" else ["frontEnd/index.html","frontEnd/app.js"]),
        "typedSqlJsonManifest": ["doctrine/aiTaskManifestV2.template.json",
                                 "host/api/typedLanesV1.sql"],
        "googleCompatibility": ["doctrine/googleAiProxyDeploymentV1.json",
                                "doctrine/googleAiDeveloperEntitlementsV1.json"],
        "storageBoundary": ["doctrine/storageTopologyV1.json"],
        "rightsAndLicenses": ["frontEnd/tools/stage-jquery.mjs"],
        "artifactDigest": family["source"][:1],
        "installAndRollback": ["doctrine/selfHostedRemoteUpdatesV1.json"],
    }
    if control == "exactSource":
        return ("GREEN_SOURCE", ["git:HEAD"])
    if control == "canonAuthority":
        ok = (truth.get("status") == "AMBER_PROPOSED_SEAL_OF_TRUTH"
              and truth.get("crownStatus") == "STOP"
              and truth.get("promotion") is False
              and pkg["sourceLaw"] == truth.get("sourceLaw"))
        if not ok:
            raise ValueError("RED_CANON_AUTHORITY_CHANGED")
        return ("GREEN_SOURCE", ["doctrine/currentSourceTruthV3.json"])
    if control == "workerQuarantine":
        if not(q.get("state") == "QUARANTINED" and
               q.get("registeredCount") == 15 and
               q.get("activeTaskWorkersAllowed") is False):
            raise ValueError("RED_WORKER_AUTHORITY_CHANGED")
        return ("GREEN_SOURCE", ["doctrine/companyWideOperationalQuarantineV1.json"])
    if control == "professorRelease":
        if not(pkg.get("crownStatus") == "STOP" and
               pkg.get("authority", {}).get("externalRelease") is False):
            raise ValueError("RED_CROWN_SCOPE")
        return ("GREEN_SOURCE", [POLICY_PATH])
    if control == "deviceOrHostSmoke":
        return ("AMBER_EXTERNAL_RECEIPT_REQUIRED", ["physical device or host proof pending"])
    if control == "rightsAndLicenses":
        # A script that stages a license is not a completed rights review.
        return ("AMBER_REVIEW_REQUIRED", known_paths[control])
    if control == "installAndRollback":
        # An update doctrine is not a successful system install/upgrade.
        return ("AMBER_EXTERNAL_RECEIPT_REQUIRED", known_paths[control])
    if control == "googleCompatibility":
        if not(google.get("networkEgress") == "DISABLED" and
               google.get("automaticProviderCalls") is False):
            raise ValueError("RED_GOOGLE_PROVIDER_UNEXPECTEDLY_ACTIVE")
    if control == "storageBoundary":
        if not (storage.get("roles", {}).get("github", {}).get("canonicalSourceAuthority")
                and storage.get("roles", {}).get("googleDrive", {}).get("canonicalBinaryStorage")
                and storage.get("rules", {}).get("databaseMayStoreCanonicalBinary") is False):
            raise ValueError("RED_SOURCE_STORAGE_AUTHORITY")
    if control == "typedSqlJsonManifest":
        if manifest.get("schema") != "luhmOs.aiTaskManifest.v2":
            raise ValueError("RED_AI_MANIFEST_SCHEMA")
    paths = known_paths.get(control, [])
    bad = [p for p in paths if not (ROOT / p).is_file()]
    return ("AMBER_SOURCE_GAP" if bad else "GREEN_SOURCE", paths)


def assess(slots: int, source_ref: str | None = None) -> dict:
    if slots not in ALLOWED_SLOTS:
        raise ValueError("RED_UNAPPROVED_SCALE")
    actual = exact_git_sha()
    if source_ref is not None and source_ref != actual:
        raise ValueError("RED_SOURCE_REF_MISMATCH")
    policy = load_json(POLICY_PATH)
    if (policy.get("status") != "PROPOSED_SOURCE_ONLY"
            or policy.get("crownStatus") != "STOP"
            or policy.get("slots", {}).get("scale") != list(ALLOWED_SLOTS)
            or policy.get("lifecycleGates") != list(STAGES)
            or policy.get("evidenceControls") != list(CONTROL_IDS)
            or [x.get("id") for x in policy.get("families", [])] != list(FAMILY_IDS)):
        raise ValueError("RED_MATRIX_CANON_DRIFT")
    if any(len(f["profiles"]) != 4 or len({p["id"] for p in f["profiles"]}) != 4
           for f in policy["families"]):
        raise ValueError("RED_NON_DISTINCT_VARIANTS")
    context = {
        "policy":policy,
        "truth":load_json("doctrine/currentSourceTruthV3.json"),
        "quarantine":load_json("doctrine/companyWideOperationalQuarantineV1.json"),
        "storage":load_json("doctrine/storageTopologyV1.json"),
        "google":load_json("doctrine/googleAiProxyDeploymentV1.json"),
        "manifest":load_json("doctrine/aiTaskManifestV2.template.json"),
    }
    variants = slots // (len(FAMILY_IDS)*len(STAGES)*len(CONTROL_IDS))
    cells = []
    for family in policy["families"]:
        for profile in family["profiles"][:variants]:
            for stage in STAGES:
                for control in CONTROL_IDS:
                    if stage == "source":
                        status, refs = source_evidence(family,control,context)
                    elif stage == "release":
                        status, refs = ("BLOCKED_CROWN", [POLICY_PATH])
                    else:
                        status, refs = ("AMBER_EXTERNAL_RECEIPT_REQUIRED",
                                        [family["buildLane"] if stage=="build" else
                                         "artifact hash, package/install & device proof"])
                    cells.append({
                        "hex": f"0x{len(cells):03x}",
                        "family":family["id"], "profile":profile["id"],
                        "stage":stage, "control":control, "status":status,
                        "evidenceRefs":refs,
                    })
    if len(cells) != slots or len({c["hex"] for c in cells}) != slots:
        raise ValueError("RED_MATRIX_SIZE")
    if any(c["status"] == "GREEN_SOURCE" and c["stage"] != "source" for c in cells):
        raise ValueError("RED_FALSE_GREEN")
    if any(c["status"] != "BLOCKED_CROWN" for c in cells if c["stage"]=="release"):
        raise ValueError("RED_RELEASE_ESCALATION")
    counts={k:sum(c["status"] == k for c in cells)
            for k in ("GREEN_SOURCE","AMBER_SOURCE_GAP","AMBER_REVIEW_REQUIRED",
                      "AMBER_EXTERNAL_RECEIPT_REQUIRED","BLOCKED_CROWN")}
    if sum(counts.values()) != slots:
        raise ValueError("RED_UNACCOUNTED_SLOT")
    return {
        "schema":"luhmOs.hydraHexReleaseReceipt.v1",
        "sourceRef":actual,"scale":slots,"hexFirst":cells[0]["hex"],
        "hexLast":cells[-1]["hex"], "profilesAssessed":variants*len(FAMILY_IDS),
        "cellCount":len(cells),"counts":counts,"cells":cells,
        "verdict":"SOURCE_MATRIX_RECONCILED_RELEASE_UNVERIFIED",
        "legacy200StillSeparate":True,
        "googleAiExecuted":False,"googleDriveWrite":False,
        "debInstalled":False,"dmgNotarized":False,"apkInstalled":False,
        "npmPublished":False,"agentWorkersUnquarantined":False,
        "authority":{"mutation":False,"green":False,"crown":False},
        "crownStatus":"STOP",
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--slots",type=int,choices=ALLOWED_SLOTS,default=256)
    parser.add_argument("--source-ref")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    data=assess(args.slots,args.source_ref)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in data.items() if k!="cells"},sort_keys=True))


if __name__=="__main__":
    main()
