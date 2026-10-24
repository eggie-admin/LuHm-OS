#!/usr/bin/env python3
"""Urd-style deterministic review of one GitHub supervised source-task receipt.

This is a separate source-policy verification, NOT an independent Urd model,
in-chat MCP host invocation, worker activation, or Professor release.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = (
    "doctrine/agentSystemDeploymentV1.json",
    "doctrine/luhmAiControlPlaneV1.json",
    "doctrine/companyWideOperationalQuarantineV1.json",
)
SHA = re.compile(r"^[0-9a-f]{40}$")
TASK = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]{0,79}$")


def verify(root: Path, receipt: dict, expected_source: str, expected_task: str) -> dict:
    failures: list[str] = []
    def require(ok: bool, code: str) -> None:
        if not ok:
            failures.append(code)

    require(bool(SHA.fullmatch(expected_source)), "BAD_SOURCE_ID")
    require(bool(TASK.fullmatch(expected_task)), "BAD_TASK_ID")
    require(isinstance(receipt, dict), "INVALID_RECEIPT")
    if not isinstance(receipt, dict):
        receipt = {}

    try:
        observed = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, timeout=5
        ).strip()
    except (OSError, subprocess.SubprocessError):
        observed = "UNKNOWN"
    require(observed == expected_source, "CHECKOUT_MISMATCH")
    require(receipt.get("schema") == "luhmOs.supervisedSourceTask.v1", "SCHEMA_MISMATCH")
    require(receipt.get("sourceRef") == expected_source, "RECEIPT_SOURCE_MISMATCH")
    require(receipt.get("expectedSource") == expected_source, "EXPECTED_SOURCE_MISMATCH")
    require(receipt.get("taskId") == expected_task, "TASK_MISMATCH")
    require(receipt.get("scopeId") == "sourceRosterInspection", "SCOPE_MISMATCH")
    require(receipt.get("status") == "COMPLETED", "INCOMPLETE_TASK")
    require(receipt.get("executionKind") == "deterministicSourceInspection", "EXECUTOR_TYPE_MISMATCH")
    require(receipt.get("inferenceExecuted") is False, "UNPROVEN_MODEL_EXECUTION")
    require(receipt.get("agentsActivated") == [], "AGENT_ACTIVATION_FORBIDDEN")
    require(receipt.get("runtimeState") == "HELD_UNVERIFIED", "RUNTIME_STATE_SPOOF")
    require(receipt.get("errors") == [], "SOURCE_TASK_ERRORS")
    try:
        doc = {
            name: json.loads((root / name).read_text(encoding="utf-8"))
            for name in CONTRACTS
        }
        actual_hashes = {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in CONTRACTS
        }
        require(receipt.get("contractHashes") == actual_hashes, "CONTRACT_HASH_MISMATCH")
        registry, control, policy = (doc[name] for name in CONTRACTS)
        ids = registry.get("requiredAgents")
        require(isinstance(ids, list) and len(ids) == 15
                and len(set(ids)) == 15, "REGISTERED_ROSTER_INVALID")
        require(isinstance(control.get("agents"), dict)
                and set(control["agents"]) == set(ids or []), "CONTROL_ROSTER_DRIFT")
        require(receipt.get("registeredAgents") == ids, "RECEIPT_ROSTER_DRIFT")
        require(policy.get("state") == "QUARANTINED"
                and policy.get("activeTaskWorkersAllowed") is False
                and policy.get("registeredCount") == 15
                and policy.get("crownStatus") == "STOP", "COMPANY_HOLD_DRIFT")
        require(policy.get("supervisedProbe", {}).get("requiresCurrentChatHostInvocation")
                is True, "HOST_INVOCATION_GATE_MISSING")
        require(policy.get("releaseMode") == "twoPhasePerAgentNoAutomaticRelease",
                "RELEASE_POLICY_MISMATCH")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        failures.append("CONTRACT_READ_FAILED_" + type(exc).__name__)

    return {
        "schema": "luhmOs.urdDeterministicSourceReview.v1",
        "taskId": expected_task, "sourceRef": expected_source,
        "observedAt": datetime.now(timezone.utc).isoformat(),
        "reviewerKind": "deterministicPolicyCheckNotIndependentUrdAgent",
        "sourceTaskStatus": "ACCEPTED" if not failures else "REJECTED",
        "errors": failures,
        "chatGptHostInvocationObserved": False,
        "belldandyMcpProbeVerified": False,
        "independentUrdAgentExecuted": False,
        "professorAgentResumeVerified": False,
        "agentsActivated": [],
        "productionPromotionAuthority": False,
        "crownStatus": "STOP",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--task-receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        record = json.loads(args.task_receipt.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        record = {}
    review = verify(ROOT, record, args.source, args.task_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(review, indent=2))
    return 0 if review["sourceTaskStatus"] == "ACCEPTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
