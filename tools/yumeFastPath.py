#!/usr/bin/env python3
"""Yume low-risk fast-path classifier. Read-only, no agent or provider execution."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine" / "yumeFastPathCanonV1.json"
SHA = re.compile(r"^[0-9a-f]{40}$")
IDENTITY = re.compile(r"^[a-z][A-Za-z0-9]{0,79}$")


def evaluate(packet: object, policy: dict) -> dict:
    """A strict PASS only accelerates planning; it never authorizes publication."""
    blockers = []
    if not isinstance(packet, dict):
        packet = {}
        blockers.append("packetMustBeObject")
    missing = [k for k in policy["requiredPacketFields"] if k not in packet]
    blockers.extend("missing:" + key for key in missing)
    for key in ("taskId", "scopeId"):
        val = packet.get(key)
        if not isinstance(val, str) or not IDENTITY.fullmatch(val):
            blockers.append("invalidIdentity:" + key)
    source = packet.get("sourceRef")
    if not isinstance(source, str) or not SHA.fullmatch(source):
        blockers.append("invalidExactSourceRef")
    if packet.get("projectLane") != policy["privateProjectLane"]:
        blockers.append("notPersonalWorkspace")
    if packet.get("workType") not in policy["eligibleWorkTypes"]:
        blockers.append("nonFastPathWorkType")
    if packet.get("contentLane") != policy["privateContentLane"]:
        blockers.append("nonPrivateContentLane")
    if type(packet.get("publicAllowed")) is not bool or packet["publicAllowed"] is not False:
        blockers.append("publicDistributionNotPermitted")
    if packet.get("provenanceState") not in policy["allowedProvenanceStates"]:
        blockers.append("unknownOrUnsafeProvenance")
    if packet.get("rightsState") not in policy["allowedRightsStates"]:
        blockers.append("missingOrUnsafeRights")
    for flag in ("sourceProtected", "privateOnly", "reversible", "localOnly"):
        if packet.get(flag) is not True:
            blockers.append("mustBeTrue:" + flag)
    for flag in ("externalProviderCall", "usesCredentials", "changesProduction",
                 "writesOutsideScratch", "agentExecution"):
        if packet.get(flag) is not False:
            blockers.append("mustBeFalse:" + flag)
    cost = packet.get("estimatedNewCostUsd")
    if type(cost) not in (float, int) or cost != 0:
        blockers.append("requiresZeroNewSpend")

    allowed = not blockers
    return {
        "schema": "luhmOs.yumeFastPathReceipt.v1",
        "status": policy["fastPathToken"] if allowed else policy["escalationToken"],
        "mode": "privateTier0" if allowed else "riskReview",
        "taskId": packet.get("taskId"),
        "sourceRef": packet.get("sourceRef"),
        "scopeId": packet.get("scopeId"),
        "errors": blockers,
        "steps": policy["fastPathSteps"] if allowed else
                 ["review blockers; use existing canonical full gate"],
        "owner": "yume",
        "coordinator": "lum",
        "publicationAuthority": False,
        "autonomousWorkerExecution": False,
        "providerCalled": False,
        "changesPerformed": False,
        "quarantineLifted": False,
        "crownStatus": "STOP"
    }


def sample_packet() -> dict:
    return {
        "taskId": "artDraft01", "scopeId": "rebelPrivate",
        "sourceRef": "a" * 40, "projectLane": "personal",
        "workType": "concept", "contentLane": "privateMutation",
        "publicAllowed": False, "sourceProtected": True,
        "provenanceState": "verifiedOwnerOriginal", "rightsState": "owned",
        "privateOnly": True, "reversible": True, "localOnly": True,
        "externalProviderCall": False, "usesCredentials": False,
        "changesProduction": False, "writesOutsideScratch": False,
        "agentExecution": False, "estimatedNewCostUsd": 0
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("packet", nargs="?", help="Path to one task packet JSON")
    ap.add_argument("--example", action="store_true", help="Show a sample private task packet")
    args = ap.parse_args()
    if args.example:
        print(json.dumps(sample_packet(), indent=2))
        return 0
    if not args.packet:
        ap.error("packet is required unless --example is used")
    try:
        packet = json.loads(Path(args.packet).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "FULL_GATE_REQUIRED",
                          "errors": ["unreadableOrInvalidPacket"], "detail": type(exc).__name__}))
        return 1
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    outcome = evaluate(packet, policy)
    print(json.dumps(outcome, indent=2))
    return 0 if outcome["status"] == policy["fastPathToken"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
