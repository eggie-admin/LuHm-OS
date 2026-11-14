"""CAST Bridge / CAST four-lane release mapping, source-only and fail-closed.

This maps the user's release vocabulary onto existing Canon. It does not
change the Forge single-use CAST gate or authorize builds/publication.
"""
from __future__ import annotations
import re

LANES = ("testing", "proposed", "beta", "release")
REQUIRED = {
    "testing": ("sourceRef", "automatedChecks", "failureOrSmokeReceipt"),
    "proposed": ("sourceRef", "candidateBuildOrRun", "failureOrSmokeReceipt"),
    "beta": ("sourceRef", "signedTesterArtifact", "securityReview",
             "physicalDeviceSmoke", "upgradeEvidence"),
    "release": ("sourceRef", "stableSigner", "reproducibleBuild",
                "regressionEvidence", "publicationApproval"),
}
CONTROLLER = {"testing": "castBridge", "proposed": "castBridge",
              "beta": "cast", "release": "cast"}

def plan_transition(current, target, evidence, *, source_ref, approval=False):
    if current not in LANES or target not in LANES:
        return {"status": "BLOCKED", "reason": "UNKNOWN_LANE", "authorized": False}
    if not isinstance(source_ref, str) or not re.fullmatch(r"[a-f0-9]{40}", source_ref):
        return {"status": "BLOCKED", "reason": "EXACT_SOURCE_REQUIRED", "authorized": False}
    if not isinstance(evidence, dict):
        return {"status": "BLOCKED", "reason": "EVIDENCE_MAPPING_REQUIRED", "authorized": False}
    i, j = LANES.index(current), LANES.index(target)
    if j < i or j > i + 1:
        return {"status": "BLOCKED", "reason": "NO_SKIP_OR_DOWNGRADE", "authorized": False}
    missing = [k for k in REQUIRED[target] if evidence.get(k) is not True
               and not (k == "sourceRef" and evidence.get(k) == source_ref)]
    if missing:
        return {"status": "AMBER", "controller": CONTROLLER[target],
                "missing": missing, "authorized": False}
    if j > i and (target in ("beta", "release") or current == "proposed") and not approval:
        return {"status": "BLOCKED", "reason": "PROFESSOR_GATE",
                "controller": CONTROLLER[target], "authorized": False}
    return {"status": "READY_FOR_REVIEW", "controller": CONTROLLER[target],
            "from": current, "to": target, "sourceRef": source_ref,
            "authorized": False, "execution": "NONE", "crownStatus": "STOP"}

def release_map():
    return {"schema": "luhmOs.castLaneMap.v1",
            "lanes": [{"hex": f"0x{i:02x}", "id": name,
                       "controller": CONTROLLER[name],
                       "requiredEvidence": list(REQUIRED[name])}
                      for i, name in enumerate(LANES)],
            "lts": {"status": "PROPOSED_STABILITY_DESIGNATION",
                    "canonicalLane": "release", "separateLtsGateImplemented": False},
            "forgeCastGateUnchanged": True, "automaticPublication": False}
