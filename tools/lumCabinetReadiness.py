#!/usr/bin/env python3
"""Run the five LuHm cabinet source audits with exact-source receipts.

This is REAL bounded Python audit execution, not five provider agents.
No agent is activated, no model weights change, no vendor calls, no private
health data, no documents get silently rewritten, and no deploy occurs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "lum", "urdDoctorGoddess", "belldandySecretary", "skuldResearch",
    "kiri", "momo", "shiori", "kugi", "tetsu", "kaji", "fumi",
    "sumi", "koe", "yume", "mediaAssetFactory",
)
PROFILES = {
    "lum": {
        "work": "training, task routing, workflow logistics and evidence integration",
        "checks": ("tools/agentSystemDeploymentAudit.py",
                   "tools/openingDayStaffTrainingAudit.py"),
        "helpers": (),
    },
    "urdDoctorGoddess": {
        "work": "system-health, security risk and evidence integrity; no human clinical monitoring",
        "checks": ("tools/urdClinicalSecurityPracticeAudit.py",
                   "tools/companyWideQuarantineAudit.py"),
        "helpers": (),
    },
    "belldandySecretary": {
        "work": "documentation, provenance, licensing and authorship intake; writing stays draft until approved",
        "checks": ("tools/belldandyHousekeepingAudit.py",
                   "tools/belldandyOniDeploymentGate.py"),
        "helpers": ("fumi", "koe"),
    },
    "skuldResearch": {
        "work": "architecture drift, network compatibility and vendor-doc research backlog",
        "checks": ("tools/worldHeadquartersAudit.py",
                   "tools/networkSpineAudit.py"),
        "helpers": ("momo", "shiori"),
    },
    "yume": {
        "work": "brand, visual asset rights, video and CSS/image production readiness",
        "checks": ("tools/yumeArtCabinetAudit.py",
                   "tools/yumeCreativePipelineAudit.py"),
        "helpers": ("sumi", "mediaAssetFactory"),
    },
}
SOURCE_SHA = re.compile(r"^[a-f0-9]{40}$")


def readDoc(root: Path, relative: str) -> dict:
    path = root / relative
    if not path.is_file() or path.is_symlink():
        raise ValueError("missing/symlink doctrine: " + relative)
    return json.loads(path.read_text(encoding="utf-8"))


def checkContract(deployment: dict, plane: dict, hold: dict) -> list[str]:
    errors = []
    def need(ok: bool, why: str) -> None:
        if not ok:
            errors.append(why)
    need(deployment.get("requiredAgents") == list(REQUIRED), "registered roster drift")
    need(deployment.get("requiredAgentCount") == 15, "agent count drift")
    need(plane.get("boss") == "lum", "Lum boss drift")
    need(set(plane.get("agents", {})) == set(REQUIRED), "control-plane roster drift")
    need(plane.get("invariants", {}).get("maxParallelSupportWorkers") == 3,
         "support concurrency drift")
    need(plane.get("invariants", {}).get("oneMutableSourceLane") is True,
         "source mutation-lane drift")
    need(hold.get("registeredAgents") == list(REQUIRED), "quarantine roster drift")
    need(hold.get("registeredCount") == 15, "quarantine size drift")
    need(hold.get("state") == "QUARANTINED", "quarantine policy unexpectedly changed")
    need(hold.get("activeTaskWorkersAllowed") is False, "quarantine bypass")
    need(hold.get("hiddenAsyncAgents") is False, "covert background-agent drift")
    need(hold.get("crownStatus") == "STOP", "Crown leak")
    need(tuple(PROFILES) == ("lum", "urdDoctorGoddess", "belldandySecretary", "skuldResearch", "yume"),
         "cabinet roster drift")
    for person, record in PROFILES.items():
        need(person in REQUIRED and all(helper in REQUIRED for helper in record["helpers"]),
             "unknown helper under " + person)
    return errors


def runChecks(root: Path, sourceRef: str, *, run: bool = False) -> dict:
    errors = []
    try:
        deployment = readDoc(root, "doctrine/agentSystemDeploymentV1.json")
        plane = readDoc(root, "doctrine/luhmAiControlPlaneV1.json")
        hold = readDoc(root, "doctrine/companyWideOperationalQuarantineV1.json")
        errors.extend(checkContract(deployment, plane, hold))
        observed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                                  capture_output=True, text=True, timeout=10, check=True).stdout.strip()
        if not SOURCE_SHA.fullmatch(sourceRef) or observed != sourceRef:
            errors.append("exact source mismatch")
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as exc:
        observed = "UNVERIFIED"
        errors.append("source read failure:" + type(exc).__name__ + ":" + str(exc)[:150])
    output = {
        "schema": "luhmOs.cabinetReadinessReceipt.v1",
        "sourceRef": observed,
        "expectedSourceRef": sourceRef,
        "mode": "sourceAudits" if run else "sourceInventory",
        "roles": [],
        "contractErrors": errors,
        "supervisedProviderAgentExecuted": False,
        "clinicalPatientMonitoring": False,
        "modelTrainingExecuted": False,
        "vendorDocsFetched": False,
        "documentOrMediaCreated": False,
        "activeAgents": 0,
        "companyQuarantine": "QUARANTINED",
        "crownStatus": "STOP",
    }
    for agent, item in PROFILES.items():
        row = {"agentId": agent, "responsibility": item["work"],
               "registeredHelpers": list(item["helpers"]), "checks": [],
               "executionKind": "deterministicRepoAuditsNotModelAgents"}
        for script in item["checks"]:
            path = root / script
            if not path.is_file() or path.is_symlink():
                errors.append("missing audit script:" + script)
                row["checks"].append({"script": script, "status": "MISSING"})
                continue
            if not run or errors:
                row["checks"].append({"script": script, "status": "NOT_EXECUTED"})
                continue
            try:
                # Existing source audits run one at a time under the CI budget.
                cmd = subprocess.run([sys.executable, str(path)],
                                     cwd=root, timeout=90,
                                     capture_output=True, text=True, check=False)
                combined = (cmd.stdout + "\n" + cmd.stderr)[-4000:]
                receiptHash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
                state = "PASS_SOURCE_ONLY" if cmd.returncode == 0 else "RED_SOURCE_AUDIT"
                row["checks"].append({"script": script, "status": state,
                                      "exitCode": cmd.returncode,
                                      "outputSha256": receiptHash,
                                      "outputTail": combined[-380:]})
                if cmd.returncode:
                    errors.append("audit failed:" + script)
            except (OSError, subprocess.TimeoutExpired) as exc:
                errors.append("audit timeout/execution failure:" + script)
                row["checks"].append({"script": script, "status": "RED_EXECUTION",
                                      "error": type(exc).__name__})
        output["roles"].append(row)
    output["contractErrors"] = errors
    output["auditsExecuted"] = sum(c["status"] in ("PASS_SOURCE_ONLY", "RED_SOURCE_AUDIT")
                                    for r in output["roles"] for c in r["checks"])
    output["auditsPassed"] = sum(c["status"] == "PASS_SOURCE_ONLY"
                                  for r in output["roles"] for c in r["checks"])
    output["status"] = ("RED_SOURCE" if errors else
                        "GREEN_SOURCE_AUDITS_WORKERS_QUARANTINED" if run else
                        "SOURCE_INVENTORY_WORKERS_QUARANTINED")
    return output


def main() -> int:
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--source-ref", required=True)
    arg.add_argument("--run-source-checks", action="store_true")
    arg.add_argument("--output", type=Path)
    cfg = arg.parse_args()
    receipt = runChecks(ROOT, cfg.source_ref, run=cfg.run_source_checks)
    data = json.dumps(receipt, indent=2) + "\n"
    if cfg.output:
        cfg.output.parent.mkdir(parents=True, exist_ok=True)
        cfg.output.write_text(data, encoding="utf-8")
    print(data)
    return int(receipt["status"] == "RED_SOURCE")


if __name__ == "__main__":
    raise SystemExit(main())
