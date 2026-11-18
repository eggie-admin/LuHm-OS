#!/usr/bin/env python3
"""Read-only audit of the proposed layered orchestration doctrine. No provider calls."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT / path).read_text(encoding="utf-8"))

doc = load("doctrine/lumOsLayeredOrchestrationV1.json")
roster = load("doctrine/agentSystemDeploymentV1.json")
hardening = load("doctrine/lumOrchestraHardeningV1.json")
orch = doc["orchestration"]
lanes = doc["escalationLanes"]

checks = {
    "proposedOnly": doc["status"] == "PROPOSED_CANDIDATE_ONLY",
    "professorAuthority": doc["authority"] == "Professor",
    "crownStop": doc["crownStatus"] == "STOP",
    "rosterIs15": orch["rosterSize"] == 15 == len(hardening["canonicalAgents"]),
    "singleBossLum": orch["frontEnd"]["agent"] == hardening["boss"] == "lum",
    "googleApiDenyDefault": orch["workhorse"]["apiInvocationDefault"] == "DENY",
    "googleEntitlementUnknown": orch["workhorse"]["entitlement"].startswith("UNKNOWN"),
    "noConsumerApiGrant": orch["workhorse"]["consumerPlanGrantsApiAccess"] is False,
    "rolesNotWorkers": orch["agentsAreRegisteredRolesNotWorkers"] is True,
    "parallelCapMatches": orch["maxParallelSupportWorkers"] == hardening["maxParallelSupportWorkers"],
    "hex64": doc["hexChunkEscalation"]["chunkBits"] == 64,
    "failClosed": "UNKNOWN" in doc["hexChunkEscalation"]["failClosedOn"],
    "privateLanes": lanes["privateLanes"] == ["testingLane", "proposedLane"],
    "deployProposedOnly": lanes["deploy"].startswith("proposedCandidateOnly"),
    "botNotEnabled": doc["nightlyBuildBot"]["status"] == "PROPOSED_NOT_ENABLED",
    "rosterFileResolves": bool(roster),
}
for name, ok in checks.items():
    print(("PASS " if ok else "FAIL ") + name)
print(f"LAYERED_ORCHESTRATION_AUDIT={sum(checks.values())}/{len(checks)}")
print("PROVIDER_EXECUTION=UNVERIFIED; CROWN=STOP")
sys.exit(0 if all(checks.values()) else 1)
