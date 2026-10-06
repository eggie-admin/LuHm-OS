#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def need(ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)

debug = load("doctrine/vendorAiDebugV1.json")
magic = load("doctrine/luhmChatMagicTriggerV1.json")
truth = load("doctrine/currentSourceTruthV3.json")
deployment = load("doctrine/agentSystemDeploymentV1.json")
economy = load("doctrine/providerEconomyV1.json")

need(debug.get("status") == "PROPOSED_SOURCE_ONLY", "vendor debug must remain proposed")
need(debug.get("namingLaw", {}).get("machineKeys") == "lowerCamelHump", "machine naming drift")
need(debug.get("namingLaw", {}).get("debugPresentation") == "UPPERCASE", "debug presentation must be uppercase")
need(debug.get("truthLaw", {}).get("providerNativeDefault") == "UNKNOWN_UNTIL_PROVIDER_RECEIPT", "native default truth boundary drift")
need(debug.get("truthLaw", {}).get("observedExecution") == "UNKNOWN_UNTIL_EXACT_EXECUTION_RECEIPT", "observed execution boundary drift")
need(debug.get("promotion") is False and debug.get("crownStatus") == "STOP", "vendor debug may not self-promote")

providers = debug.get("providers", {})
need(set(providers) == {"openAi","googleAi","githubCopilot","huggingFace","edgeGallery"}, "provider set drift")
for provider_id, profile in providers.items():
    need(profile.get("nativeDefaultLogic") == "UNKNOWN_UNTIL_PROVIDER_RECEIPT", f"{provider_id}: native default overclaim")
    need(profile.get("reconcile") == "lum", f"{provider_id}: must reconcile through Lum")
    need("authority" in profile, f"{provider_id}: authority missing")

need(providers.get("googleAi", {}).get("nickname") == "bigBrother", "Big Brother mapping drift")
need(providers.get("openAi", {}).get("nickname") == "openDaddy", "openDaddy mapping drift")
need(providers.get("edgeGallery", {}).get("readiness") == "UNCONFIGURED_EVIDENCE_PENDING", "Edge Gallery readiness overclaim")
need(providers.get("huggingFace", {}).get("readiness") == "CANDIDATE_PROVIDER_UNPROVEN", "Hugging Face readiness overclaim")
need(economy.get("routingOrder") == ["deterministicLocal","existingReceiptsAndCachedEvidence","bigBrother","openDaddyWhenMateriallyJustified"], "provider economy route drift")

trigger = magic.get("trigger", {})
need(trigger.get("operator") == "AND", "magic trigger must remain AND")
need(trigger.get("allOf") == ["I invoke the old magic","so let it be written, so let it be done"], "magic phrases drift")
need(trigger.get("authorityEffect") == "none", "magic trigger may not change authority")
need(magic.get("activation", {}).get("vendorDebug") == "doctrine/vendorAiDebugV1.json", "magic/vendor debug binding missing")
need(magic.get("defaults", {}).get("maximumConcurrentSupportAgents") == 3, "support parallelism drift")
need(magic.get("roleplayLaw", {}).get("mayChangeAuthority") is False, "roleplay authority drift")

need(truth.get("vendorDebugLayer", {}).get("contract") == "doctrine/vendorAiDebugV1.json", "source truth debug pointer drift")
need(truth.get("vendorDebugLayer", {}).get("workingLane") == "PROPOSED_ONLY", "source truth debug lane drift")
need(truth.get("vendorDebugLayer", {}).get("crownStatus") == "STOP", "source truth debug Crown drift")
need(deployment.get("activationLaw", {}).get("maxParallelSupportWorkers") == 3, "deployment parallelism drift")

plugin = (ROOT / "frontEnd/jquery/luhm.cockpit.js").read_text(encoding="utf-8")
for token in [
    "$.fn.mgcCdngRlplay",
    "$.fn.vendorAiDebug",
    "luhm:magic:roleplay:activate",
    "luhm:vendor:debug:request",
    "VENDOR_AI_DEBUG",
    "echoTriggerText: false",
]:
    need(token in plugin, f"frontend missing {token}")

tool = ROOT / "tools/vendorAiDebug.py"
for provider in ("openai","google","copilot","huggingface","edge"):
    run = subprocess.run([sys.executable, str(tool), provider], cwd=ROOT, capture_output=True, text=True)
    need(run.returncode == 0, f"debug tool failed for {provider}")
    need("VENDOR_AI_DEBUG=ON" in run.stdout, f"uppercase debug header missing for {provider}")
    need("PROVIDER_NATIVE_DEFAULT=UNKNOWN_UNTIL_PROVIDER_RECEIPT" in run.stdout, f"native default overclaim for {provider}")
    need("VERDICT=DEBUG_ONLY_NOT_GREEN" in run.stdout, f"debug verdict drift for {provider}")

if errors:
    print(json.dumps({"status":"RED_VENDOR_AI_DEBUG","errors":errors}, indent=2))
    raise SystemExit(1)

print(json.dumps({
    "status":"GREEN_VENDOR_AI_DEBUG_SOURCE_CANDIDATE",
    "providers":5,
    "debugPresentation":"UPPERCASE",
    "machineNaming":"lowerCamelHump",
    "magicRoleplayBound":True,
    "providerNativeDefault":"UNKNOWN_UNTIL_PROVIDER_RECEIPT",
    "observedExecution":"UNKNOWN_UNTIL_EXACT_EXECUTION_RECEIPT",
    "crownStatus":"STOP"
}, indent=2))
