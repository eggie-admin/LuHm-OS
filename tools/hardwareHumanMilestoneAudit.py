#!/usr/bin/env python3
"""Read-only source-contract audit. This is NOT hardware, GUI, device, or APK proof."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
FAILURES: list[str] = []
PASSES: list[str] = []

def need(name: str, condition: bool) -> None:
    (PASSES if condition else FAILURES).append(name)

def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def check() -> None:
    source = load("doctrine/hardwareHumanMilestonesV1.json")
    canon = load("doctrine/currentSourceTruthV3.json")
    quarantine = load("doctrine/companyWideOperationalQuarantineV1.json")
    need("schema", source.get("schema") == "luhmOs.hardwareHumanMilestones.v1")
    need("proposalOnly", source.get("status") == "PROPOSED_SOURCE_ONLY")
    need("sourceOfTruth", source.get("canonicalRepository") == canon.get("canonicalRepository") == "eggie-admin/LuHm-OS")
    need("noIndependentWorkerRelease", quarantine.get("state") == "QUARANTINED")
    need("noCrownPromotion", source.get("crownStatus") == "STOP" and source.get("promotion") is False)
    need("noPublicationOrSigning", source.get("publicationAuthority") is False and source.get("signingAuthority") is False)
    envelope = source.get("taskEnvelope", {})
    need("taskIdentity", envelope.get("taskId") == "hardwareHumanProgression" and isinstance(envelope.get("scopeId"), str))
    sha = envelope.get("sourceRef", "")
    need("pinnedBaseline", isinstance(sha, str) and len(sha) == 40 and all(c in "0123456789abcdef" for c in sha))
    need("humanAuthority", envelope.get("executionAuthorized") is False)
    need("rollbackIdentified", envelope.get("rollbackRef") == sha)
    ids = ["hardwareLayer", "hardwareHumanLayer", "humanSortaLayer", "fullHumanLayer"]
    stages = source.get("stages", [])
    need("stageCountAndOrder", [item.get("id") for item in stages] == ids and [item.get("order") for item in stages] == list(range(4)))
    need("laneOrder", source.get("laneOrder") == ids)
    need("noDuplicateStages", len({item.get("id") for item in stages}) == len(stages))
    expectedDependencies = [[], ids[:1], ids[1:2], ids[2:3]]
    for idx, item in enumerate(stages):
        name = item.get("id", str(idx))
        need("dependencies:" + name, item.get("dependsOn") == expectedDependencies[idx])
        need("proofsRequired:" + name, isinstance(item.get("requiredProof"), list) and len(item["requiredProof"]) >= 3)
        need("notLiveClaim:" + name, item.get("status") in {"SOURCE_PRESENT_RUNTIME_UNVERIFIED", "SIGNED_ARTIFACT_AND_DEVICE_PENDING", "SOURCE_CANDIDATE_HUMAN_TEST_PENDING", "CONSENT_RIGHTS_AND_RELEASE_PENDING"} and item.get("currentlyObserved", {}).get("device") != "DEVICE_PROVEN")
        need("sourceReferences:" + name, all((ROOT / p).is_file() for p in item.get("sourcePaths", [])) and len(item.get("sourcePaths", [])) >= 3)
        need("humanMeaning:" + name, bool(item.get("humanMeaning")) and bool(item.get("next")))
    axes = source.get("separateAxes", {})
    for k in ("sourceModules", "packageComposition", "visualCompositor", "escalation"):
        need("axis:" + k, (ROOT / axes.get(k, "!missing!")).is_file())
    refs = source.get("portableHelp", {})
    for k in ("skill", "guide", "audit", "ci"):
        need("help:" + k, (ROOT / refs.get(k, "!missing!")).is_file())
    restricted = source.get("releaseBoundaries", {})
    for key in ("newKeys", "automaticPublication", "automaticSocialPosts", "paidServices", "unquarantineAgents",
                "deviceFlash", "merge", "sign", "publicAssetDisclosure", "siteChanges"):
        need("restriction:" + key, restricted.get(key) is False)
    need("currentCanonStillStop", canon.get("publicationAuthority") is False and canon.get("crownStatus") == "STOP")
    need("existingSignerMustPersist", source.get("continuation", {}).get("existingSignerMustNotRotate") is True)
    need("distinctAxes", "DO NOT rename" in axes.get("warning", ""))

if __name__ == "__main__":
    try:
        check()
    except (ValueError, OSError, KeyError, TypeError) as error:
        FAILURES.append("invalidSourceContract:" + type(error).__name__)
    if "--json" in sys.argv[1:]:
        print(json.dumps({"schema": "luhmOs.hardwareHumanSourceAudit.v1", "status": "SOURCE_AUDIT_PASS" if not FAILURES else "SOURCE_AUDIT_FAIL",
                          "sourceOnly": True, "passed": PASSES, "failed": FAILURES}, indent=2))
    else:
        for item in PASSES: print("PASS", item)
        for item in FAILURES: print("FAIL", item)
        print("SOURCE_AUDIT_PASS_NOT_RUNTIME_PROOF" if not FAILURES else "SOURCE_AUDIT_FAIL")
    raise SystemExit(1 if FAILURES else 0)
