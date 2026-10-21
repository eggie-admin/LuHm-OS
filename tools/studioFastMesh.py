#!/usr/bin/env python3
"""Read-only, fail-closed route planner for Pirate Daddies Film's dual compatibility layers."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lumTaskRouter import ROUTES

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/studioCompatibilityFastMeshV1.json"


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("contract must be a JSON object")
    return value


def audit() -> list[str]:
    errors: list[str] = []
    contract = load("doctrine/studioCompatibilityFastMeshV1.json")
    source = load("doctrine/currentSourceTruthV3.json")
    economy = load("doctrine/providerEconomyV1.json")
    spine = load("doctrine/apiSpineV1.json")
    agents = load("doctrine/agentSystemDeploymentV1.json")
    quarantine = load("doctrine/companyWideOperationalQuarantineV1.json")
    stream = load("doctrine/chatGptPluginWorkflowStreamV1.json")

    def require(test: bool, issue: str) -> None:
        if not test:
            errors.append(issue)

    studio = contract.get("studio", {})
    compat = contract.get("compatibilityLayers", {})
    openai = compat.get("chatGptOpenAi", {})
    github = compat.get("github", {})
    workhorse = contract.get("workhorse", {}).get("googleAi", {})
    sidecars = contract.get("sidecars", {})
    hf = sidecars.get("huggingFace", {})
    render = sidecars.get("render", {})
    mesh = contract.get("fastMesh", {})
    boundary = contract.get("releaseBoundary", {})

    require(contract.get("schema") == "luhmOs.studioCompatibilityFastMesh.v1", "schema")
    require(contract.get("status") == "CANDIDATE_NOT_DEPLOYED", "candidate status")
    require(contract.get("authority") == "Professor", "authority")
    require(studio.get("canonicalWorkspace") == "github" == economy.get("workspaceLaw", {}).get("officialEntitledWorkspace"), "GitHub workspace law")
    require(studio.get("canonicalRepository") == github.get("repository") == source.get("canonicalRepository") == "eggie-admin/LuHm-OS", "source identity")
    require(github.get("role") == "primaryResearchAndDevelopmentStudio", "GitHub studio role")
    require(openai.get("role") == "interactiveSidecar", "OpenAI sidecar role")
    require(openai.get("sourceAuthority") is False and openai.get("billableExecutionAllowed") is False, "OpenAI cannot grant source authority or spending")
    require(openai.get("billingTierVerified") is False, "unverified OpenAI billing must remain unverified")
    require(workhorse.get("providerId") == economy.get("bigBrother", {}).get("providerId") == "googleAi", "Google workhorse identity")
    require(workhorse.get("adapterId") == spine.get("providers", {}).get("googleAi", {}).get("adapterId") == "bigBrother", "Google adapter")
    require(workhorse.get("permittedBillableCalls") is False and workhorse.get("outputAuthority") == "candidateEvidenceOnly", "Google entitlement boundary")
    require(hf.get("providerId") == "huggingFace" and economy.get("specialistProviders", {}).get("huggingFace", {}).get("role") == "specialistTrainer", "Hugging Face specialist identity")
    require(hf.get("executionRequiresSeparateEntitlementAndCostCheck") is True, "Hugging Face execution gate")
    require(render.get("role") == "freeTierRuntimeSidecar" and render.get("planCeiling") == "free", "Render free-tier sidecar")
    require(render.get("ownsSourceTruth") is False and render.get("automaticPaidUpgrade") is False, "Render authority and billing")
    require(mesh.get("router") == "tools/lumTaskRouter.py" and mesh.get("boss") == "lum", "canonical fast router")
    require(mesh.get("roster") == "doctrine/agentSystemDeploymentV1.json", "roster identity")
    require(agents.get("requiredAgentCount") == len(agents.get("requiredAgents", [])) == 15, "agent roster count")
    require(mesh.get("maxParallelSupportWorkers") == agents.get("activationLaw", {}).get("maxParallelSupportWorkers") == 3, "support worker limit")
    require(mesh.get("maxParallelBuilds") == 2 and mesh.get("singleMutableSourceLane") is True, "build/mutation limits")
    require(mesh.get("recursiveRecruitment") is False and mesh.get("hiddenAsyncAgents") is False, "no recursive/hidden workers")
    require(mesh.get("plannedOnly") is True and mesh.get("neverInferExecutionFromRoute") is True, "routing does not execute")
    require(stream.get("boss") == "lum" and stream.get("agentMesh") == mesh.get("roster"), "workflow mesh binding")
    require(quarantine.get("state") in ("QUARANTINED", "CLEARED"), "quarantine state must be valid")
    require(boundary.get("companyOperationalQuarantineState") == "QUARANTINED", "candidate operational hold")
    require(all(boundary.get(key) is False for key in ("workerActivation", "merge", "deploy", "publish", "spend", "sign")), "no implicit execution authority")
    require(quarantine.get("crownStatus") == "STOP", "Crown stop")
    require(quarantine.get("state") != "CLEARED" or all(quarantine.get("supervisedProbe", {}).get(k) for k in ("hostInvocationReceipt", "urdEvaluationReceipt", "professorResumeReceipt")), "quarantine release evidence")
    require(mesh.get("quarantinePreserved") is True, "quarantine preservation")
    return errors


def plan(kind: str, *, heavy: bool = False, specialist: bool = False) -> dict[str, Any]:
    if kind not in ROUTES:
        raise ValueError("unsupported canonical route kind")
    errors = audit()
    if errors:
        raise RuntimeError("RED_STUDIO_FAST_MESH_CONTRACT: " + ", ".join(errors))
    quarantine = load("doctrine/companyWideOperationalQuarantineV1.json")
    proposed = list(dict.fromkeys(ROUTES[kind]))
    provider = "deterministicLocal"
    if specialist:
        provider = "huggingFace"
    elif heavy:
        provider = "googleAi"
    elif kind in ("research", "external"):
        provider = "googleAi"
    if provider == "googleAi":
        entitlement = "UNKNOWN_ACCOUNT_BOUND_RECEIPT_REQUIRED"
    elif provider == "huggingFace":
        entitlement = "SPECIALIST_SCOPE_AND_COST_CHECK_REQUIRED"
    else:
        entitlement = "NO_EXTERNAL_PROVIDER_REQUIRED"
    return {
        "schema": "luhmOs.studioFastMeshPlan.v1",
        "kind": kind,
        "sourceRepository": "eggie-admin/LuHm-OS",
        "compatibilityLayers": ["chatGptOpenAi", "github"],
        "providerCandidate": provider,
        "entitlementGate": entitlement,
        "proposedWorkers": proposed,
        "activeWorkers": [],
        "companyOperationalHold": quarantine["state"],
        "mayInvokeProvider": False,
        "mayExecuteWorkers": False,
        "mayMutateSource": False,
        "mayDeploy": False,
        "maySpend": False,
        "requiresExactSourceRefBeforeExecution": True,
        "requiresProfessorCrownForPromotion": True,
        "status": "READ_ONLY_CANDIDATE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--kind", choices=sorted(ROUTES))
    parser.add_argument("--heavy", action="store_true")
    parser.add_argument("--specialist", action="store_true")
    args = parser.parse_args()
    try:
        if args.check:
            errors = audit()
            print(json.dumps({"status": "GREEN_SOURCE_ONLY" if not errors else "RED_SOURCE",
                              "errors": errors, "runtimeProven": False, "crownStatus": "STOP"}, indent=2))
            return 1 if errors else 0
        if not args.kind:
            parser.error("provide --check or --kind")
        if args.heavy and args.specialist:
            parser.error("choose at most one of --heavy and --specialist")
        print(json.dumps(plan(args.kind, heavy=args.heavy, specialist=args.specialist), indent=2))
        return 0
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "RED_FAIL_CLOSED", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
