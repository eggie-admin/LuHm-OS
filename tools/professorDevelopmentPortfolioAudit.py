#!/usr/bin/env python3
"""Candidate consistency audit for Professor's four-lane development portfolio."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))

portfolio = load("doctrine/professorDevelopmentPortfolioV1.json")
truth = load("doctrine/currentSourceTruthV3.json")
control = load("doctrine/luhmAiControlPlaneV1.json")
deployment = load("doctrine/agentSystemDeploymentV1.json")
covenant = load("doctrine/everlastingCovenantV1.json")
errors = []

def require(condition, label):
    if not condition:
        errors.append(label)

expected = ["aiDevelopment", "gameDevelopment", "codingDevelopment", "artDevelopment"]
lanes = portfolio.get("developmentLanes", [])
require(portfolio.get("schema") == "luhmOs.professorDevelopmentPortfolio.v1", "schema")
require(portfolio.get("status") == "PROPOSED_CANDIDATE", "candidate status")
require(portfolio.get("authority") == "Professor" and portfolio.get("boss") == "lum", "authority chain")
require([lane.get("id") for lane in lanes] == expected, "four lane identities and order")
require(len({lane.get("focus") for lane in lanes}) == 4, "distinct lane scopes")
require(control.get("inherits", {}).get("professorDevelopmentPortfolio") == "doctrine/professorDevelopmentPortfolioV1.json", "control plane pointer")
require(truth.get("developmentPortfolio", {}).get("contract") == "doctrine/professorDevelopmentPortfolioV1.json", "source truth pointer")
require(truth.get("developmentPortfolio", {}).get("developmentLanes") == expected, "source truth lane list")
require(portfolio.get("canonicalTaskGuardRail") == "doctrine/everlastingCovenantV1.json", "guard rail pointer")
require(covenant.get("schema") == "luhmOs.everlastingCovenant.v1", "covenant schema loaded")
require(deployment.get("activationLaw", {}).get("maxParallelSupportWorkers") == 3, "parallel worker ceiling")
require(deployment.get("activationLaw", {}).get("oneMutableSourceLane") is True, "single mutable source lane")
require((ROOT / portfolio.get("orchestration", {}).get("providerAndGitHubBudgets", "")).is_file(), "provider and GitHub budget contract exists")
require(portfolio.get("orchestration", {}).get("multipleWorkflowsMayBeTrackedAtOnce") is True, "multiple workflows enabled")
require(portfolio.get("orchestration", {}).get("noHiddenAsyncWorkers") is True, "no hidden workers")
require(portfolio.get("orchestration", {}).get("activeTaskSelectsOnePrimaryLane") is True, "one primary lane per task")
require(portfolio.get("orchestration", {}).get("supportingLanesAreReadOnly") is True, "support lanes remain read-only")
require(portfolio.get("orchestration", {}).get("runtimeExecutor", "").startswith("NOT_ATTACHED"), "registry does not claim a runtime executor")
for lane in lanes:
    for path in lane.get("sourceContracts", []) + lane.get("ciWorkflows", []):
        require((ROOT / path).is_file(), f"missing {lane.get('id')} reference: {path}")
    require(bool(lane.get("acceptanceEvidence")), f"missing acceptance evidence: {lane.get('id')}")
game = next((lane for lane in lanes if lane.get("id") == "gameDevelopment"), {})
require(game.get("vendorEntitlements", {}).get("currentState") == "UNKNOWN_UNTIL_VENDOR_RECEIPT", "game vendor entitlements stay unknown")
income = portfolio.get("incomeCampaign", {})
require(income.get("role") == "sharedPortfolioOutcome_not_a_fifth_developmentLane", "income objective remains cross-lane")
require(income.get("financialTargets") == "UNSET_REQUIRES_PROFESSOR_DECISION", "no invented financial target")
require(income.get("automaticSend") is False and income.get("automaticPublication") is False, "campaign send and publish remain gated")
require(income.get("automaticPayout") is False and income.get("automaticPurchaseOrTierChange") is False, "payout and provider spend remain gated")
require((ROOT / income.get("evidenceLedger", "")).is_file(), "campaign evidence ledger exists")
require(income.get("financialRecord", "").startswith("PRIVATE_SYSTEM_OF_RECORD_REQUIRED"), "private financial record boundary")
require("do not count as cash received" in income.get("sidecarReductionGate", ""), "in-kind support is not cash")
require(portfolio.get("safety", {}).get("promotion") is False and portfolio.get("safety", {}).get("crownStatus") == "STOP", "promotion remains stopped")

print(json.dumps({
    "schema": "luhmOs.professorDevelopmentPortfolioAudit.v1",
    "status": "GREEN_CANDIDATE" if not errors else "RED_CANDIDATE",
    "sourceConfigured": True,
    "liveExecutionProven": False,
    "lanes": expected,
    "errors": errors,
    "promotion": False,
    "crownStatus": "STOP"
}, indent=2))
raise SystemExit(1 if errors else 0)
