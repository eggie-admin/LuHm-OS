#!/usr/bin/env python3
"""LuHm 4x4 source-only escalation planner. No execution or promotion authority."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from tools.escalationKernel import plan
except ImportError:
    from escalationKernel import plan

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/escalationFourByFourPolishV1.json"
SHA = re.compile(r"[0-9a-f]{40}\Z")
IDENTITY = re.compile(r"[a-zA-Z][a-zA-Z0-9_.-]{2,99}\Z")
BEATS = ("hear", "resolve", "act", "verify")
OUTCOMES = ("working", "green", "blocked", "red", "unknown", "conflict")
DOMAINS = ("default", "corporate", "magic", "art", "technology")


def load_policy() -> dict:
    data = json.loads(POLICY.read_text(encoding="utf-8"))
    if data.get("schema") != "luhmOs.escalationFourByFourPolish.v1":
        raise ValueError("RED_4X4_SCHEMA")
    if data.get("status") != "PROPOSED_SOURCE_ONLY" or data.get("crownStatus") != "STOP":
        raise ValueError("RED_4X4_CROWN")
    if data.get("kernel") != "doctrine/escalationKernelV1.json":
        raise ValueError("RED_4X4_KERNEL_POINTER")
    if data.get("interactionRhythm") != "doctrine/fourBeatInteractionRhythmV1.json":
        raise ValueError("RED_4X4_RHYTHM_POINTER")
    if data.get("beats") != list(BEATS):
        raise ValueError("RED_4X4_BEATS")
    if [x.get("tier") for x in data.get("tiers", [])] != [0, 1, 2, 3]:
        raise ValueError("RED_4X4_TIERS")
    cells = data.get("cells", [])
    if len(cells) != 16:
        raise ValueError("RED_4X4_CELLS")
    for index, cell in enumerate(cells):
        tier, beat_index = divmod(index, 4)
        if cell.get("cell") != ("T" + str(tier) + "_" + BEATS[beat_index].upper()):
            raise ValueError("RED_4X4_CELL_ORDER")
        if cell.get("tier") != tier or cell.get("beat") != BEATS[beat_index]:
            raise ValueError("RED_4X4_CELL_IDENTITY")
        if not isinstance(cell.get("receiptKind"), str) or not cell["receiptKind"]:
            raise ValueError("RED_4X4_RECEIPT")
    if "autoSign" not in data.get("denied", []) or "selfCrown" not in data.get("denied", []):
        raise ValueError("RED_4X4_AUTHORITY")
    return data


def evaluate(measure: dict, previous: dict | None = None) -> dict:
    policy = load_policy()
    if not isinstance(measure, dict):
        raise ValueError("measure must be a JSON object")
    task = measure.get("taskId")
    source = measure.get("sourceRef")
    scope = measure.get("scopeId")
    domain = measure.get("domain")
    tier = measure.get("tier")
    beat = measure.get("beat")
    outcome = measure.get("outcome", "working")
    for label, value in (("taskId", task), ("scopeId", scope)):
        if not isinstance(value, str) or not IDENTITY.fullmatch(value):
            raise ValueError("RED_4X4_" + label)
    if not isinstance(source, str) or not SHA.fullmatch(source):
        raise ValueError("RED_4X4_SOURCE")
    if domain not in DOMAINS or type(tier) is not int or tier not in range(4):
        raise ValueError("RED_4X4_DOMAIN_TIER")
    if beat not in BEATS or outcome not in OUTCOMES:
        raise ValueError("RED_4X4_BEAT_OUTCOME")
    receipts = measure.get("evidenceRefs", [])
    if not isinstance(receipts, list) or len(receipts) > 24:
        raise ValueError("RED_4X4_EVIDENCE_ARRAY")
    if any(not isinstance(x, str) or not 4 <= len(x) <= 256 for x in receipts):
        raise ValueError("RED_4X4_EVIDENCE_REF")
    blocker = measure.get("blocker", "")
    if not isinstance(blocker, str) or len(blocker) > 500:
        raise ValueError("RED_4X4_BLOCKER")
    current_id = {"taskId": task, "sourceRef": source, "scopeId": scope}
    if previous is not None:
        if not isinstance(previous, dict):
            raise ValueError("RED_4X4_PREVIOUS")
        # A previous receipt is advisory state, NEVER inherited proof.
        if any(previous.get(key) != value for key, value in current_id.items()):
            return _receipt(current_id, domain, tier, beat, outcome,
                            "HOLD_IDENTITY_DRIFT", tier, "hear", 0)
    if beat != "verify":
        if outcome != "working":
            raise ValueError("RED_4X4_ONLY_VERIFY_DECIDES")
        return _receipt(current_id, domain, tier, beat, outcome, "NEXT_BEAT",
                        tier, BEATS[BEATS.index(beat) + 1], len(receipts))
    if outcome == "red":
        return _receipt(current_id, domain, tier, beat, outcome, "STOP_RED",
                        tier, "hear", len(receipts))
    if outcome in ("unknown", "conflict"):
        return _receipt(current_id, domain, tier, beat, outcome,
                        "HOLD_" + outcome.upper(), tier, "hear", len(receipts))
    if outcome == "working":
        return _receipt(current_id, domain, tier, beat, outcome, "REPEAT_TIER",
                        tier, "hear", len(receipts))
    if not receipts or (outcome == "blocked" and not blocker.strip()):
        return _receipt(current_id, domain, tier, beat, outcome,
                        "HOLD_UNPROVEN_" + outcome.upper(), tier, "hear", len(receipts))
    canonical = plan(domain, tier, outcome)
    if outcome == "blocked":
        decision = ("ESCALATE_ONE_TIER" if tier < 3 else "HOLD_TIER_3_BLOCKER")
    else:
        decision = "CLOSE_OR_DEESCALATE"
    if canonical.get("nextTier") != (min(3, tier + 1) if outcome == "blocked" else max(0, tier - 1)):
        raise ValueError("RED_4X4_KERNEL_DRIFT")
    return _receipt(current_id, domain, tier, beat, outcome, decision,
                    canonical["nextTier"], "hear", len(receipts))


def _receipt(identity, domain, tier, beat, outcome, decision, next_tier, next_beat, count):
    return {
        "schema": "luhmOs.escalationFourByFourDecision.v1",
        **identity, "domain": domain, "tier": tier, "beat": beat,
        "outcome": outcome.upper(), "decision": decision,
        "nextTier": next_tier, "nextBeat": next_beat, "evidenceRefCount": count,
        "evidenceAttestation": "UNVERIFIED_INPUT_NOT_INDEPENDENT_PROOF",
        "mayAutoExecute": False, "mayMerge": False, "maySign": False,
        "mayPublish": False, "mayReleaseQuarantinedAgents": False,
        "physicalDeviceProof": False, "crownStatus": "STOP",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan one source-bound 4x4 escalation measure")
    parser.add_argument("--measure", type=Path, required=True, help="JSON file; no credentials or secrets")
    parser.add_argument("--previous", type=Path, help="Optional previous source/scope receipt")
    args = parser.parse_args()
    data = json.loads(args.measure.read_text(encoding="utf-8"))
    previous = json.loads(args.previous.read_text(encoding="utf-8")) if args.previous else None
    print(json.dumps(evaluate(data, previous), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
