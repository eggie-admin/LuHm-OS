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

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "doctrine/fnCastV1.yaml"
RELEASE_GATE = ROOT / "doctrine/finalFormPublicReleaseGateV1.json"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")


def load_contract(path: Path = MANIFEST) -> dict:
    # JSON is a compatible YAML 1.2 subset. Do not execute tags or arbitrary YAML.
    contract = json.loads(path.read_text(encoding="utf-8"))
    assert contract["schema"] == "luhmOs.fnCast.v1"
    assert contract["entryPoint"] == "LuHmOS.fn.cast"
    assert contract["voiceTrigger"]["aliases"] == ["cast", "cst", "c"]
    assert contract["crownCondition"]["mode"] == "ALL"
    assert contract["finalCast"]["voiceNeverDispatchesGitHubActions"] is True
    return contract


def voice_intent(
    transcript: str,
    contract: dict,
    *,
    armed: bool = False,
    context: str = "global",
    confirm_single_letter: bool = False,
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
    elif alias == "c" and not confirm_single_letter:
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


def inspect_final_form(
    gate: dict, *, requested_source_ref: str, checked_out_source_ref: str
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
        "validSourceRef": bool(SHA40.fullmatch(requested_source_ref)),
        "exactCheckout": requested_source_ref == checked_out_source_ref,
        "releaseSourceBound": artifact.get("sourceRef") == requested_source_ref,
        "releaseArtifactHasHash": bool(
            SHA64.fullmatch(str(artifact.get("sha256", "")))
        ),
        "stableSignerHasHash": bool(
            SHA64.fullmatch(str(artifact.get("signingCertificateSha256", "")))
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


def build_receipt(
    transcript: str,
    *,
    armed: bool = False,
    context: str = "global",
    confirm_single_letter: bool = False,
    requested_source_ref: str = "",
    checked_out_source_ref: str = "",
    contract: dict | None = None,
    release_gate: dict | None = None,
) -> dict:
    contract = contract if contract is not None else load_contract()
    gate = release_gate if release_gate is not None else json.loads(
        RELEASE_GATE.read_text(encoding="utf-8")
    )
    voice = voice_intent(
        transcript, contract, armed=armed, context=context,
        confirm_single_letter=confirm_single_letter,
    )
    crown = inspect_final_form(
        gate, requested_source_ref=requested_source_ref,
        checked_out_source_ref=checked_out_source_ref,
    )
    identity = json.dumps(
        {"voice": voice["alias"], "sourceRef": requested_source_ref,
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
        "requestedSourceRef": requested_source_ref or None,
        "checkedOutSourceRef": checked_out_source_ref or None,
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


def local_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Scoped voice CAST intent, read-only FINAL_FORM gate")
    parser.add_argument("--voice", required=True, help="Already transcribed single command")
    parser.add_argument("--armed", action="store_true", help="Explicit CAST context was armed by user")
    parser.add_argument("--context", default="global", choices=["global", "fnCast"])
    parser.add_argument("--confirm-single-letter", action="store_true")
    parser.add_argument("--source-ref", default="", help="Exact candidate commit (40 lowercase hex)")
    args = parser.parse_args()
    receipt = build_receipt(
        args.voice, armed=args.armed, context=args.context,
        confirm_single_letter=args.confirm_single_letter,
        requested_source_ref=args.source_ref, checked_out_source_ref=local_head(),
    )
    print(json.dumps(receipt, indent=2))
    # Not a build gate or deploy program. Safe read-only refusal is a normal result.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
