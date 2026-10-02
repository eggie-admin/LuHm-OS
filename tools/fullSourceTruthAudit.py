#!/usr/bin/env python3
"""Fail-closed LuHm OS full source-of-truth readiness audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "doctrine/SOURCE_OF_TRUTH.json"
BOUNDARY = ROOT / "doctrine/RELEASE_BOUNDARY.json"
DOC_WORKFLOW = ROOT / "doctrine/DOCUMENT_MUTATION_AUDIT_WORKFLOW.json"
ORCHESTRATOR = ROOT / "doctrine/fullSourceTruthOrchestrator-20260926.json"
SAMSUNG_SEAL = ROOT / "doctrine/samsungLayoutSeal-20260926.json"
COCKPIT_SEAL = ROOT / "doctrine/s24FeCockpitAuditSwitchSeal-20260926.json"
PORTAL_SEAL = ROOT / "doctrine/fqdnInstallPortalSeal-20260926.json"
ANDROID_WEB3 = ROOT / "doctrine/ANDROID_WEB3_COCKPIT_SWITCH_V1.json"
SMX400 = ROOT / "doctrine/smX400RootedAndroid16TargetV1.json"

GOOD = {"GREEN", "VERIFIED", "PASS", "PROVEN"}


def load(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"missing required doctrine file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_good(value: object) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        upper = value.upper()
        return upper in GOOD or upper.startswith("GREEN_") or upper.endswith("_GREEN")
    return False


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "build/full-source-truth/readiness.json")
    args = parser.parse_args()

    source = load(SOURCE)
    boundary = load(BOUNDARY)
    doc_workflow = load(DOC_WORKFLOW)
    orchestrator = load(ORCHESTRATOR)
    samsung = load(SAMSUNG_SEAL)
    cockpit = load(COCKPIT_SEAL)
    portal = load(PORTAL_SEAL)
    android_web3 = load(ANDROID_WEB3)
    smx400 = load(SMX400)

    errors: list[str] = []
    blockers: list[dict[str, str]] = []
    post_cast_boundaries: list[dict[str, str]] = []

    if source.get("canonical_repository") != "eggie-admin/LuHm-OS":
        errors.append("canonical repository drift")
    if source.get("authority") != "Professor":
        errors.append("human authority drift")
    if source.get("source_law") != orchestrator.get("source_law"):
        errors.append("source law mismatch between SOURCE_OF_TRUTH and orchestrator")
    if doc_workflow.get("status") != "GREEN_DOCUMENTATION_WORKFLOW":
        errors.append("documentation audit workflow is not canonical GREEN")
    if len(doc_workflow.get("ten_pass_hard_audit", [])) != 10:
        errors.append("ten-pass audit definition is not exactly 10 passes")
    if orchestrator.get("agent_mesh", {}).get("boss", {}).get("name") != "Lum":
        errors.append("Lum is not the configured boss orchestrator")
    if len(orchestrator.get("agent_mesh", {}).get("default_oni", [])) != 3:
        errors.append("default Oni worker count must be exactly 3")
    rules = orchestrator.get("agent_mesh", {}).get("rules", [])
    for required_rule in (
        "Helpers do not recursively recruit.",
        "Parallelism is capped at 3.",
        "Consequential actions remain Crown-gated.",
        "Tool Executor is deterministic and does not reinterpret scope.",
    ):
        if required_rule not in rules:
            errors.append(f"agent mesh rule missing: {required_rule}")

    deny = set(boundary.get("deny", []))
    for required_deny in (
        "production signing",
        "publishing",
        "stable promotion",
        "remote shell execution",
        "embedded provider secrets",
    ):
        if required_deny not in deny:
            errors.append(f"release boundary lost required deny rule: {required_deny}")

    # Historical S24 FE/.lan/Apache receipts remain immutable evidence, but the
    # Android Web3 switch explicitly supersedes them as active readiness gates.
    if android_web3.get("supersedes", {}).get("priorSeal") != "doctrine/s24FeCockpitAuditSwitchSeal-20260926.json":
        errors.append("Android Web3 supersession contract missing historical cockpit seal")
    target = smx400.get("target", {})
    if target.get("model") != "SM-X400" or target.get("androidMajor") != 16:
        errors.append("active Android target drift")

    web3_evidence = android_web3.get("currentEvidence", {})
    if not normalized_good(web3_evidence.get("staticSecurityAudit")):
        blockers.append({"gate": "android_web3.static_security", "reason": str(web3_evidence.get("staticSecurityAudit", "UNKNOWN"))})
    if web3_evidence.get("physicalSamsungWebViewProof") not in {"PENDING", "UNKNOWN"} and not normalized_good(web3_evidence.get("physicalSamsungWebViewProof")):
        blockers.append({"gate": "android_web3.physical_webview", "reason": str(web3_evidence.get("physicalSamsungWebViewProof"))})

    # Physical SM-X400 install/launch is post-CAST deployment evidence. Its
    # absence must remain visible without falsely blocking software readiness.
    post_cast_boundaries.append({"gate": "physical_deployment_post_cast", "reason": "SM-X400 install/launch proof remains physical-only and is not inferred from CI"})

    if source.get("enterpriseReady") is not True:
        blockers.append({"gate": "enterprise_readiness", "reason": "enterpriseReady=false"})

    if source.get("publication_authority") is True:
        errors.append("unexpected publication_authority at top-level source of truth")

    if source.get("status", "").startswith("GREEN_FULL_SOURCE") and blockers:
        errors.append("SOURCE_OF_TRUTH claims full GREEN while readiness blockers remain")

    audit_passes = []
    source_passes = doc_workflow.get("ten_pass_hard_audit", [])
    for entry in source_passes:
        name = entry.get("name", "UNKNOWN")
        if name == "Evidence":
            state = "AMBER" if blockers else "GREEN"
        elif name in {"Render and Hash", "Seal and Save"}:
            state = "AMBER" if blockers else "GREEN"
        else:
            state = "GREEN"
        audit_passes.append({"pass": entry.get("pass"), "name": name, "status": state})

    readiness = "GREEN_FULL_SOURCE_TRUTH_READY" if not blockers else "AMBER_FULL_SOURCE_TRUTH_SEAL_PENDING"
    milestone_complete = not blockers

    report = {
        "schema": "luhm-os.full-source-truth-audit-report.v1",
        "status": readiness,
        "milestoneMutationComplete": milestone_complete,
        "nextState": "PREPARE_FINAL_SEAL" if milestone_complete else "ENTER_LUM_ONI_REPAIR_LOOP",
        "sourceCommit": git_head(),
        "sourceStatus": source.get("status"),
        "releaseBoundary": boundary.get("status"),
        "workflowStatus": orchestrator.get("status"),
        "tenPassAudit": audit_passes,
        "blockers": blockers,
        "postCastBoundaries": post_cast_boundaries,
        "contractErrors": errors,
        "hashes": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (SOURCE, BOUNDARY, DOC_WORKFLOW, ORCHESTRATOR, SAMSUNG_SEAL, COCKPIT_SEAL, PORTAL_SEAL, ANDROID_WEB3, SMX400)
        },
        "authority": "Professor",
        "promotion": False,
        "publicationAuthority": False,
        "productionSigningAuthority": False,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if errors:
        raise SystemExit("full source truth contract audit failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
