#!/usr/bin/env python3
"""Fail-closed evidence gate for LuHm in-chat source/MCP/host claims.

This is a deterministic audit helper, not a live MCP endpoint or Oni executor.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

GATES = ("sourceCi", "renderExactDeploy", "mcpToolDiscovery",
         "mcpResourceContract", "chatGptHostMount", "godotWebInput",
         "samsungTouch")
ALLOWED = {"GREEN", "AMBER", "RED", "UNKNOWN"}

@dataclass(frozen=True)
class Verdict:
    state: str
    gate: str
    reason: str

def adjudicate(packet: dict[str, Any], *, taskId: str,
               sourceRef: str, scopeId: str) -> Verdict:
    if not all(isinstance(s, str) and s.strip() for s in (taskId, sourceRef, scopeId)):
        return Verdict("RED", "identity", "empty expected identity")
    if not isinstance(packet, dict) or packet.get("schema") != "luhmOs.inChatOniReceipt.v1":
        return Verdict("RED", "schema", "wrong or absent schema")
    if any(packet.get(k) != v for k, v in
           (("taskId", taskId), ("sourceRef", sourceRef), ("scopeId", scopeId))):
        return Verdict("RED", "identity", "source/task/scope mismatch")
    if packet.get("authority") != "readOnlyEvidence":
        return Verdict("RED", "authority", "receipt cannot grant action")
    claims = packet.get("gates")
    if not isinstance(claims, dict) or set(claims) != set(GATES):
        return Verdict("RED", "gates", "exact complete gate set required")
    for gate in GATES:
        claim = claims[gate]
        if not isinstance(claim, dict) or claim.get("state") not in ALLOWED:
            return Verdict("RED", gate, "malformed gate")
        if claim["state"] == "GREEN":
            if not all(isinstance(claim.get(k), str) and claim[k].strip()
                       for k in ("sourceRef", "evidenceRef", "observedAt", "proofKind")):
                return Verdict("RED", gate, "GREEN lacks exact receipt")
            if claim["sourceRef"] != sourceRef or claim["proofKind"] != gate:
                return Verdict("RED", gate, "receipt provenance mismatch")
            if claim["evidenceRef"].startswith(("DEMO:", "INFERRED:", "CONFIGURED:")):
                return Verdict("RED", gate, "inferred/demo/config is not runtime evidence")
        if claim["state"] == "RED":
            return Verdict("RED", gate, "reported failed gate")
        if claim["state"] != "GREEN":
            return Verdict("AMBER", gate, "missing or unproven gate")
    return Verdict("GREEN", "all", "all distinct scoped receipts present")
