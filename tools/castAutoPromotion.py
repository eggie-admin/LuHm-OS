"""Source-only fast-path gate for CAST Bridge and ChatGPT cockpit defaults.

Only testing->proposed is eligible for automatic candidate promotion.
This module does not push refs, merge PRs, enable connectors or install add-ons.
"""
from __future__ import annotations
import re

REQUIRED = ("sourceRef", "exactHeadCi", "cleanDiff", "noSecrets",
            "noPersonalData", "noProtectedAssets", "noPrivilegedOperations",
            "isolatedCandidate", "sourceAuditGreen")

def evaluate_auto_promotion(from_lane, to_lane, evidence, *, source_ref):
    base = {"schema": "luhmOs.castAutoPromotion.v1",
            "automaticPolicyDefault": True, "executed": False,
            "releaseAuthorized": False, "crownStatus": "STOP"}
    if (from_lane, to_lane) != ("testing", "proposed"):
        return {**base, "status": "BLOCKED", "reason": "RELEASE_OR_OTHER_LANE_GATE"}
    if not isinstance(source_ref, str) or re.fullmatch(r"[0-9a-f]{40}", source_ref) is None:
        return {**base, "status": "BLOCKED", "reason": "EXACT_SHA_REQUIRED"}
    if not isinstance(evidence, dict):
        return {**base, "status": "BLOCKED", "reason": "EVIDENCE_REQUIRED"}
    if evidence.get("sourceRef") != source_ref:
        return {**base, "status": "BLOCKED", "reason": "SOURCE_MISMATCH"}
    if evidence.get("classification") != "PUBLIC_DISPOSABLE":
        return {**base, "status": "BLOCKED", "reason": "UNKNOWN_OR_SENSITIVE_CLASS"}
    missing = [key for key in REQUIRED if key != "sourceRef" and evidence.get(key) is not True]
    if missing:
        return {**base, "status": "AMBER", "missing": missing}
    return {**base, "status": "ELIGIBLE_FOR_BOUNDED_AUTOMATION",
            "nextAction": "candidateBranchOrPROnly", "sourceRef": source_ref}

def cockpit_default(connection_verified, user_authorized):
    return {"schema": "luhmOs.cockpitDefault.v1",
            "desiredEnabled": True,
            "effectiveEnabled": connection_verified is True and user_authorized is True,
            "connectionVerified": connection_verified is True,
            "permissionGranted": user_authorized is True,
            "canForceChatGptInstallation": False,
            "firefoxFocusTransport": "HTTPS_WEB_FALLBACK",
            "browserExtensionRequired": False}
