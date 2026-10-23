#!/usr/bin/env python3
"""One-shot deterministic source inspection. No model, network or agent activation."""
import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "doctrine/agentSystemDeploymentV1.json",
    "doctrine/luhmAiControlPlaneV1.json",
    "doctrine/companyWideOperationalQuarantineV1.json",
)


def inspect(root, expected_source, task_id):
    receipt = {"schema": "luhmOs.supervisedSourceTask.v1", "taskId": task_id,
               "scopeId": "sourceRosterInspection", "expectedSource": expected_source,
               "observedAt": datetime.now(timezone.utc).isoformat(),
               "executionKind": "deterministicSourceInspection", "status": "FAILED",
               "inferenceExecuted": False, "agentsActivated": [], "errors": []}
    try:
        if not re.fullmatch(r"[0-9a-f]{40}", expected_source):
            raise ValueError("exact source SHA required")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]{0,79}", task_id):
            raise ValueError("invalid task identity")
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                       text=True, timeout=5).strip()
        receipt["sourceRef"] = head
        if head != expected_source:
            raise ValueError("source mismatch")
        if subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"],
                                   cwd=root, text=True, timeout=5).strip():
            raise ValueError("tracked source has uncommitted changes")
        docs, hashes = [], {}
        for name in FILES:
            path = (root / name).resolve()
            if not path.is_relative_to(root.resolve()) or path.stat().st_size > 262144:
                raise ValueError("unsafe or oversized contract")
            raw = path.read_bytes()
            # Bind bytes to Git, including rejection of untracked replacements.
            committed = subprocess.check_output(["git", "show", f"HEAD:{name}"],
                                                cwd=root, timeout=5)
            if raw != committed:
                raise ValueError("contract does not match commit")
            hashes[name] = hashlib.sha256(raw).hexdigest()
            docs.append(json.loads(raw))
        registry, control, hold = docs
        roster = registry["requiredAgents"]
        if (len(roster) != 15 or len(set(roster)) != 15 or
                set(roster) != set(control["agents"]) or
                set(roster) != set(hold["registeredAgents"])):
            raise ValueError("roster mismatch")
        if hold["state"] != "QUARANTINED" or hold["activeTaskWorkersAllowed"] is not False:
            raise ValueError("activation policy changed; review executor scope")
        receipt.update(status="COMPLETED", contractHashes=hashes,
                       registeredAgents=roster, runtimeState="HELD_UNVERIFIED",
                       meaning="Source inspection completed; no provider worker was executed")
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as exc:
        receipt["errors"].append(type(exc).__name__ + ": " + str(exc)[:200])
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--task-id", required=True)
    args = parser.parse_args()
    receipt = inspect(ROOT, args.source, args.task_id)
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
