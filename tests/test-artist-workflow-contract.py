#!/usr/bin/env python3
"""Source-contract checks for the artist-first production workflow; no runtime claims."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "doctrine/artistFirstProductionWorkflowV1.json").read_text())

assert contract["schema"] == "luhm.artistFirstProductionWorkflow.v1"
assert contract["status"] == "PROPOSED_ONLY"
assert contract["authority"] == "Professor"
assert contract["sourceLaw"] == "AI proposes. Policy authorizes. Deterministic evidence proves. Professor promotes."
assert contract["taskEnvelope"]["oneMutableSourceLane"] is True
assert contract["taskEnvelope"]["unknownOrMissingRightsFailClosed"] is True
assert contract["taskEnvelope"]["evidenceMustBindToSameTaskSourceAndScope"] is True

stages = [stage["id"] for stage in contract["stages"]]
assert stages == [
    "brief", "register", "inspect-and-demux", "storyboard-and-task-cards",
    "candidate-generation", "continuity-review", "deterministic-assembly",
    "professor-review", "export"
]
by_id = {stage["id"]: stage for stage in contract["stages"]}
assert "demuxingCreatesAWorkingCopyNotRightsOrApproval" in by_id["inspect-and-demux"]["law"]
assert "neverOverwriteProtectedMaster" in by_id["candidate-generation"]["law"]
assert "llmTextNeverBecomesACommand" in by_id["deterministic-assembly"]["law"]
assert "approvalHashMismatch" in by_id["professor-review"]["stopIf"]
assert "publicationRequiresSeparatePolicyAndHumanAction" in by_id["export"]["law"]

mesh = contract["mesh"]
assert mesh["boss"] == "lum"
assert mesh["recursiveRecruitment"] is False
assert mesh["hiddenAsyncExecution"] is False
assert mesh["maxMutableSourceLanes"] == 1
assert 1 <= mesh["maxParallelSupportWorkers"] <= 3
assert mesh["allChangesIntegratedAndVerifiedByLum"] is True

gates = contract["releaseGates"]
assert gates["candidateReviewRequired"] is True
assert gates["professorApprovalRequired"] is True
assert gates["publicPublicationAutomatic"] is False
assert gates["serviceDeploymentAutomatic"] is False
assert gates["canonicalPromotionAutomatic"] is False
assert gates["crownStatus"] == "STOP"

print("ARTIST_FIRST_WORKFLOW_SOURCE_CONTRACT_PASS")
