#!/usr/bin/env python3
"""LuHmOS.fn.cast: voice-transcript CAST intent and FINAL_FORM evidence preflight.

This is not a microphone service, SQL interpreter, workflow dispatcher, or Crown grant.
A separate exact-source, owner-authored GitHub CAST remains mandatory for builds.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifestPath = root / "doctrine/fnCastV1.yaml"
releaseGatePath = root / "doctrine/finalFormPublicReleaseGateV1.json"
sha40 = re.compile(r"[0-9a-f]{40}\Z")
sha64 = re.compile(r"[0-9a-f]{64}\Z")


def loadContract(path: Path = manifestPath) -> dict:
    # JSON is a compatible YAML 1.2 subset. Do not execute tags or arbitrary YAML.
    contract = json.loads(path.read_text(encoding="utf-8"))
    assert contract["schema"] == "luhmOs.fnCast.v1"
    assert contract["entryPoint"] == "LuHmOS.fn.cast"
    assert contract["voiceTrigger"]["aliases"] == ["cast", "cst", "c"]
    assert contract["crownCondition"]["mode"] == "ALL"
    assert contract["finalCast"]["voiceNeverDispatchesGitHubActions"] is True
    return contract


def voiceIntent(
    transcript: str,
    contract: dict,
    *,
    armed: bool = False,
    context: str = "global",
    confirmSingleLetter: bool = False,
) -> dict:
    """Strict whole-command speech recognition, not a generic substring grep."""
    rule = contract["voiceTrigger"]
    wrappers = re.escape(rule["punctuationWrapper"])
    match = re.fullmatch(
        rf"[{wrappers}\s]*(cast|cst|c)[{wrappers}\s]*",
        transcript,
        flags=re.IGNORECASE | re.ASCII,
    )
    alias = match.group(1).lower() if match else None
    if alias is None:
        state = "NO_EXACT_CAST_TOKEN"
    elif context != "fnCast":
        # Global 'cst' already resolves to currentSourceTruth; 'c' to continue.
        state = "NOT_IN_FN_CAST_CONTEXT"
    elif not armed:
        state = "VOICE_TRIGGER_NOT_ARMED"
    elif alias == "c" and not confirmSingleLetter:
        state = "SINGLE_LETTER_REQUIRES_CONFIRMATION"
    else:
        state = "INTENT_ACCEPTED"
    return {
        "alias": alias,
        "castBoolean": state == "INTENT_ACCEPTED",
        "state": state,
        "context": context,
        "armed": bool(armed),
        "dispatchAuthorized": False,
    }


def inspectFinalForm(
    gate: dict, *, requestedSourceRef: str, checkedOutSourceRef: str
) -> dict:
    """Conjunction only: missing, false, stale, or unknown inputs cannot Crown."""
    required = gate.get("requiredProofs", {})
    pending = sorted(
        key for key, value in required.items()
        if not isinstance(value, str) or value != "PROVEN"
    )
    artifact = gate.get("releaseArtifact", {})
    authority = gate.get("professorAuthority", {})
    checks = {
        "validSourceRef": bool(sha40.fullmatch(requestedSourceRef)),
        "exactCheckout": requestedSourceRef == checkedOutSourceRef,
        "releaseSourceBound": artifact.get("sourceRef") == requestedSourceRef,
        "releaseArtifactHasHash": bool(
            sha64.fullmatch(str(artifact.get("sha256", "")))
        ),
        "stableSignerHasHash": bool(
            sha64.fullmatch(str(artifact.get("signingCertificateSha256", "")))
        ),
        "independentVerification": artifact.get("independentVerification") == "PROVEN",
        "stableSignerContinuity": artifact.get("signingKeyContinuityProven") is True,
        "stableBuildRequired": artifact.get("stableBuildRequired") is True,
        "exactArtifactProfessorReviewed": authority.get("exactStableSignedArtifactReviewed") is True,
        "allExternalProofs": bool(required) and not pending,
        "canonicalReleaseGateGreen": gate.get("fullPublicReleaseGreen") is True,
        "externalPublicationProofRequired": gate.get("verifiedExternalPublicationProofRequired") is True,
        "notUsingDebugSigner": gate.get("releaseArtifactMayNotReuseDebugSigner") is True,
        "noSigningKeyInGit": artifact.get("signingKeyStoredInGit") is False,
    }
    missing = sorted(name for name, satisfied in checks.items() if not satisfied)
    evidence_ready = not missing
    return {
        "schema": "luhmOs.fnCastCrownCondition.v1",
        "operator": "ALL",
        "evidenceReadyForIndependentReview": evidence_ready,
        "missingConditions": missing,
        "pendingProofs": pending,
        "checks": checks,
        "crownGranted": False,
        "publicationAuthorized": False,
        "reason": (
            "Evidence candidate requires independent release audit and separate exact Professor promotion"
            if evidence_ready else
            "FINAL_FORM evidence incomplete; this function never substitutes OR for ALL"
        ),
    }


def buildReceipt(
    transcript: str,
    *,
    armed: bool = False,
    context: str = "global",
    confirmSingleLetter: bool = False,
    requestedSourceRef: str = "",
    checkedOutSourceRef: str = "",
    contract: dict | None = None,
    releaseGate: dict | None = None,
) -> dict:
    contract = contract if contract is not None else loadContract()
    gate = releaseGate if releaseGate is not None else json.loads(
        releaseGatePath.read_text(encoding="utf-8")
    )
    voice = voiceIntent(
        transcript, contract, armed=armed, context=context,
        confirmSingleLetter=confirmSingleLetter,
    )
    crown = inspectFinalForm(
        gate, requestedSourceRef=requestedSourceRef,
        checkedOutSourceRef=checkedOutSourceRef,
    )
    identity = json.dumps(
        {"voice": voice["alias"], "sourceRef": requestedSourceRef,
         "tier": "forFuckSake", "milestone": "finalForm"},
        sort_keys=True,
    )
    return {
        "schema": "luhmOs.fnCastReceipt.v1",
        "project": "Project Premonition",
        "function": "LuHmOS.fn.cast",
        "voiceTrigger": voice,
        "tier": {"id": "forFuckSake", "display": "FFS!", "auditPassTarget": 25},
        "milestone": {"id": "finalForm", "display": "FINAL_FORM"},
        "requestedSourceRef": requestedSourceRef or None,
        "checkedOutSourceRef": checkedOutSourceRef or None,
        "requestFingerprintSha256": hashlib.sha256(identity.encode("utf-8")).hexdigest(),
        "crownCondition": crown,
        "finalCast": {
            "intentRecognized": voice["castBoolean"],
            "state": (
                "HOLD_UNRECOGNIZED_OR_UNARMED" if not voice["castBoolean"]
                else "HOLD_FINAL_FORM_EVIDENCE" if not crown["evidenceReadyForIndependentReview"]
                else "REQUIRES_INDEPENDENT_AUDIT_AND_SEPARATE_PROFESSOR_CROWN"
            ),
            "buildDispatched": False,
            "releasePublished": False,
            "crownGranted": False,
        },
    }


def localHead() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "head"],
        cwd=root, text=True, capture_output=True, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Scoped voice CAST intent, read-only FINAL_FORM gate")
    parser.add_argument("--voice", required=True, help="Already transcribed single command")
    parser.add_argument("--armed", action="store_true", help="Explicit CAST context was armed by user")
    parser.add_argument("--context", default="global", choices=["global", "fnCast"])
    parser.add_argument("--confirm-single-letter", action="store_true", dest="confirmSingleLetter")
    parser.add_argument("--source-ref", default="", dest="sourceRef", help="Exact candidate commit (40 lowercase hex)")
    args = parser.parse_args()
    receipt = buildReceipt(
        args.voice, armed=args.armed, context=args.context,
        confirmSingleLetter=args.confirmSingleLetter,
        requestedSourceRef=args.sourceRef, checkedOutSourceRef=localHead(),
    )
    print(json.dumps(receipt, indent=2))
    # Not a build gate or deploy program. Safe read-only refusal is a normal result.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
