#!/usr/bin/env python3
"""Typed 4×4×4 CAST candidate receipts. Never dispatch jobs, sign or grant Crown."""
from __future__ import annotations
import hashlib
import json
import re

SHA40 = re.compile(r"^[a-f0-9]{40}$")
TASK_ID = re.compile(r"^[a-z][A-Za-z0-9]{0,79}$")
SCOPE_ID = re.compile(r"^[a-z][A-Za-z0-9]{0,79}$")


def compileMatrixIntent(contract: dict, *, stage: str, beat: str, tier: str,
                        fromStage: str | None = None, taskId: str, scopeId: str,
                        requestedSourceRef: str, checkedOutSourceRef: str,
                        voiceAccepted: bool = False) -> dict:
    """Validate coordinate and monotonic stage transition, then return intent only."""
    config = contract["castMatrix"]
    if len(config["stages"]) != 4 or len(config["beats"]) != 4 or len(config["tiers"]) != 4:
        raise ValueError("CAST matrix must be four by four by four")
    aliases = config["legacyStageAliases"]
    canonical = aliases.get(stage, stage)
    previous = aliases.get(fromStage, fromStage) if fromStage else None
    if canonical not in config["stages"]:
        raise ValueError("Unknown CAST stage")
    if beat not in config["beats"] or tier not in config["tiers"]:
        raise ValueError("Unknown CAST beat or audit tier")
    if previous is not None and previous not in config["stages"]:
        raise ValueError("Unknown previous CAST stage")
    if not isinstance(taskId, str) or not TASK_ID.fullmatch(taskId):
        raise ValueError("Invalid taskId")
    if not isinstance(scopeId, str) or not SCOPE_ID.fullmatch(scopeId):
        raise ValueError("Invalid scopeId")
    stageIndex = config["stages"].index(canonical)
    previousIndex = -1 if previous is None else config["stages"].index(previous)
    validTransition = (
        (previousIndex == -1 and stageIndex == 0) or
        (previousIndex >= 0 and stageIndex in (previousIndex, previousIndex + 1))
    )
    refsValid = (isinstance(requestedSourceRef, str) and
                 bool(SHA40.fullmatch(requestedSourceRef)) and
                 requestedSourceRef == checkedOutSourceRef)
    accepted = bool(voiceAccepted) and validTransition and refsValid
    coordinate = {
        "stage": canonical, "beat": beat, "tier": tier,
        "stageIndex": stageIndex, "beatIndex": config["beats"].index(beat),
        "tierIndex": config["tiers"].index(tier)
    }
    identity = {
        "coordinate": coordinate, "fromStage": previous,
        "taskId": taskId, "scopeId": scopeId,
        "sourceRef": requestedSourceRef,
    }
    return {
        "schema": "luhmOs.castMatrixReceipt.v1",
        "product": "LuHm-OS", "project": "Project Premonition",
        "function": "LuHmOS.fn.cast", "matrixSize": 64,
        "coordinate": coordinate, "fromStage": previous,
        "taskId": taskId, "scopeId": scopeId,
        "requestedSourceRef": requestedSourceRef,
        "checkedOutSourceRef": checkedOutSourceRef,
        "voiceAccepted": bool(voiceAccepted),
        "stageTransitionValid": validTransition,
        "sourceBound": bool(refsValid),
        "status": (
            "INTENT_ACCEPTED_CANDIDATE_ONLY" if accepted
            else "HOLD_UNARMED_OR_UNSCOPED" if not voiceAccepted
            else "HOLD_ILLEGAL_STAGE_TRANSITION" if not validTransition
            else "HOLD_EXACT_SOURCE_REQUIRED"
        ),
        "fingerprintSha256": hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest(),
        "buildDispatched": False, "releasePublished": False, "crownGranted": False,
        "authorityEffect": "none"
    }
