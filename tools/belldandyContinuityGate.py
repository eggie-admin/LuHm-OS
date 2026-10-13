#!/usr/bin/env python3
"""Read-only Belldandy handoff contract. Source/CI proof, never live agent proof."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/belldandyOperationalQuarantineV1.json"
SHA = re.compile(r"[0-9a-f]{40}\Z")
STATUSES = {"GREEN", "AMBER", "RED", "UNKNOWN", "CONFLICT"}
SAFE_ACTIONS = {"readOnly", "hold", "professorUi", "escalateToUrd"}
PROTECTED_SCOPES = {"chatGptHostInstalled": "hostRuntime", "publicDirectoryPublished": "publicDirectory"}


def review(packet: dict, policy: dict) -> list[str]:
    errors: list[str] = []
    for key in ("taskId", "sourceRef", "scopeId", "currentMilestone", "pendingGate"):
        if not isinstance(packet.get(key), str) or not packet[key].strip():
            errors.append(f"missing:{key}")
    source = packet.get("sourceRef", "")
    if not isinstance(source, str) or not SHA.fullmatch(source):
        errors.append("exactSourceRefRequired")
    status = packet.get("claimedStatus")
    if status not in STATUSES:
        errors.append("invalidStatus")
    if packet.get("claimedAuthority") != "READ_ONLY":
        errors.append("authorityCeilingExceeded")
    next_action = packet.get("nextAction")
    if not isinstance(next_action, dict) or next_action.get("kind") not in SAFE_ACTIONS:
        errors.append("unboundedNextAction")
    if isinstance(next_action, dict) and next_action.get("executed") is not False:
        errors.append("cannotClaimExecution")
    if packet.get("uiActionCount", 0) not in (0, 1):
        errors.append("oneUiActionBoundary")
    evidence = packet.get("verifiedEvidenceRefs")
    if not isinstance(evidence, list):
        errors.append("evidenceListRequired")
        evidence = []
    for idx, item in enumerate(evidence):
        if not isinstance(item, dict) or item.get("taskId") != packet.get("taskId") or item.get("sourceRef") != source or item.get("scopeId") != packet.get("scopeId"):
            errors.append(f"evidenceIdentityDrift:{idx}")
        elif item.get("verified") is not True or not item.get("ref"):
            errors.append(f"unverifiedEvidence:{idx}")
    if status == "GREEN":
        if not evidence or packet.get("conflicts") or packet.get("knownUnknowns"):
            errors.append("greenWithoutCompleteUncontestedEvidence")
        kinds = {x.get("kind") for x in evidence if isinstance(x, dict)}
        if "sourceProof" not in kinds and "hostRuntime" not in kinds and "publicDirectory" not in kinds:
            errors.append("greenWithoutProvingEvidenceClass")
        protected = PROTECTED_SCOPES.get(packet.get("claimScope"))
        if protected and protected not in kinds:
            errors.append("hostOrDirectoryClaimWithoutHostProof")
    corrections = packet.get("explicitProfessorCorrections", [])
    if not isinstance(corrections, list):
        errors.append("invalidCorrectionLedger")
    elif corrections:
        if not all(isinstance(x, dict) and isinstance(x.get("sequence"), int) and isinstance(x.get("text"), str) for x in corrections):
            errors.append("invalidCorrectionLedger")
        else:
            latest = max(corrections, key=lambda x: x["sequence"])
            if packet.get("normalizedIntent") != latest["text"]:
                errors.append("latestProfessorCorrectionLost")
    if policy.get("schema") != "luhmOs.belldandyOperationalQuarantine.v1":
        errors.append("quarantinePolicyDrift")
    if policy.get("state") == "QUARANTINED":
        if packet.get("actingSecretary") is not False:
            errors.append("quarantinedSecretaryActing")
        if packet.get("producer") != "lumFallback":
            errors.append("quarantineBypass")
    elif policy.get("state") != "CLEARED":
        errors.append("unknownQuarantineState")
    if packet.get("grantsCrown") is not False or packet.get("grantsPromotion") is not False:
        errors.append("selfPromotionForbidden")
    return errors


def self_test(policy: dict) -> None:
    base = {
        "taskId": "audit-001", "sourceRef": "a" * 40, "scopeId": "publicPlugin",
        "currentMilestone": "pluginHost", "pendingGate": "upload",
        "claimedStatus": "AMBER", "claimedAuthority": "READ_ONLY",
        "nextAction": {"kind": "professorUi", "executed": False},
        "uiActionCount": 1, "verifiedEvidenceRefs": [],
        "knownUnknowns": ["hostInstall"], "conflicts": [],
        "explicitProfessorCorrections": [
            {"sequence": 1, "text": "old instruction"},
            {"sequence": 2, "text": "fix the secretary"}
        ],
        "normalizedIntent": "fix the secretary",
        "actingSecretary": False, "producer": "lumFallback",
        "grantsCrown": False, "grantsPromotion": False
    }
    assert not review(base, policy), review(base, policy)
    def denied(modifier):
        changed = json.loads(json.dumps(base))
        modifier(changed)
        assert review(changed, policy), changed
    denied(lambda p: p.update({"actingSecretary": True}))
    denied(lambda p: p.update({"normalizedIntent": "old instruction"}))
    denied(lambda p: p.update({"claimedAuthority": "MERGE"}))
    denied(lambda p: p.update({"uiActionCount": 2}))
    denied(lambda p: p.update({"claimedStatus": "GREEN", "knownUnknowns": []}))
    denied(lambda p: p.update({"claimedStatus": "GREEN", "knownUnknowns": [], "claimScope": "chatGptHostInstalled",
                 "verifiedEvidenceRefs": [{"taskId": "audit-001", "sourceRef": "a"*40,
                 "scopeId": "publicPlugin", "kind": "sourceProof", "ref": "ci-123", "verified": True}]}))
    denied(lambda p: p.update({"claimedStatus": "GREEN", "knownUnknowns": [], "claimScope": "publicDirectoryPublished",
                 "verifiedEvidenceRefs": [{"taskId": "audit-001", "sourceRef": "b"*40,
                 "scopeId": "publicPlugin", "kind": "publicDirectory", "ref": "host", "verified": True}]}))
    print("GREEN_BELLDANDY_CONTINUITY_CONTRACT_8_CASES_SOURCE_ONLY")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--packet", type=Path)
    args = parser.parse_args()
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if args.self_test:
        self_test(policy)
        return 0
    if args.packet is None:
        parser.error("--packet required unless --self-test")
    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    errors = review(packet, policy)
    print(json.dumps({"status": "RED_PACKET" if errors else "SOURCE_PACKET_ACCEPTED_ONLY",
                      "errors": errors, "mutationAuthority": False,
                      "hostExecutionProof": False, "crownStatus": "STOP"}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
