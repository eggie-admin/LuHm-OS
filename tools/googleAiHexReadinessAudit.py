#!/usr/bin/env python3
"""Offline 0x00..0x0F Google AI Canon readiness. No provider calls or secret access."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = {
    "hex": "doctrine/googleAiHexReadinessV1.json",
    "truth": "doctrine/currentSourceTruthV3.json",
    "spine": "doctrine/apiSpineV1.json",
    "ent": "doctrine/googleAiDeveloperEntitlementsV1.json",
    "proxy": "doctrine/googleAiProxyDeploymentV1.json",
    "orchestra": "doctrine/lumOrchestraHardeningV1.json",
    "mesh": "doctrine/studioCompatibilityFastMeshV1.json",
    "hold": "doctrine/companyWideOperationalQuarantineV1.json",
    "machine": "doctrine/machineCanonFourLoopV1.json",
}
IDS = (
    "exactSource", "canonicalAuthority", "googleAdapterIdentity", "companyHold",
    "consumerNotApi", "developerProofUnknown", "billingProofUnknown", "noPaidCalls",
    "sanitizedReviewOnly", "hostOnlySecrets", "proxyEgressDisabled", "noPrCloudCredentials",
    "localFallback", "identityBoundReceipts", "zeroActiveWorkers", "crownStop",
)
LANES = ("canon", "entitlement", "execution", "promotion")
BEATS = ("inventory", "scope", "verify", "propose")
SHA = re.compile(r"^[0-9a-f]{40}$")


def field(value, *keys):
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def load_docs(root=ROOT):
    return {name: json.loads((root / path).read_text(encoding="utf-8"))
            for name, path in SOURCE.items()}


def build_receipt(docs, source_ref, actual_ref):
    h, truth, spine, ent, proxy = (docs[n] for n in ("hex", "truth", "spine", "ent", "proxy"))
    orchestra, mesh, hold, machine = (docs[n] for n in ("orchestra", "mesh", "hold", "machine"))
    expected = [{"cell": f"0x{i:02x}", "lane": LANES[i // 4],
                 "beat": BEATS[i % 4], "operation": name}
                for i, name in enumerate(IDS)]
    g = field(spine, "providers", "googleAi")
    evidence = field(ent, "entitlementAxes")
    law = field(ent, "executionLaw")
    flags = field(h, "guarantees")
    source_paths = [SOURCE[k] for k in SOURCE if k != "hex"]
    checks = [
        bool(SHA.fullmatch(source_ref)) and source_ref == actual_ref
        and h.get("cells") == expected and h.get("laneOrder") == list(LANES)
        and h.get("beatOrder") == list(BEATS)
        and h.get("sourceRefs") == source_paths
        and h.get("schema") == "luhmOs.googleAiHexReadiness.v1"
        and h.get("status") == "PROPOSED_SOURCE_ONLY"
        and h.get("sixteenCells") == "logicalHexLabelsNotHardwareOperations",
        field(truth, "canonicalRepository") == "eggie-admin/LuHm-OS"
        and field(truth, "promotion") is False
        and field(h, "sourceAuthority") == "github"
        and field(h, "sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes.",
        field(g, "providerId") == field(proxy, "providerId") == "googleAi"
        and field(g, "adapterId") == field(proxy, "adapterId") == "bigBrother"
        and field(h, "providerId") == "googleAi" and field(h, "adapterId") == "bigBrother",
        field(hold, "state") == "QUARANTINED"
        and field(hold, "activeTaskWorkersAllowed") is False
        and field(machine, "hexadecimal") == "logicalLabelsOnly",
        field(evidence, "consumerSubscription", "grantsDeveloperApi") is False
        and field(evidence, "consumerSubscription", "grantsCloudBilling") is False,
        field(evidence, "developerApi", "apiEnabledState") == "UNKNOWN"
        and field(evidence, "developerApi", "authorizedSmokeState") == "UNKNOWN"
        and field(proxy, "googleDeveloperApiEntitlement") == "UNVERIFIED",
        field(evidence, "cloudBilling", "currentResolutionState") == "UNKNOWN"
        and field(proxy, "billingApproval") == "NOT_GRANTED",
        field(law, "defaultAction") == "DENY"
        and field(evidence, "cloudBilling", "paidCallsAllowed") is False
        and field(mesh, "workhorse", "googleAi", "permittedBillableCalls") is False
        and field(flags, "spend") is False,
        field(proxy, "inputScope") == "SANITIZED_GITHUB_DIFF_ONLY_AFTER_HUMAN_APPROVAL"
        and field(proxy, "outputs") == "UNTRUSTED_ADVISORY_PROPOSALS_ONLY",
        field(law, "neverCommitCredentialOrAccountIdentifiers") is True
        and field(spine, "secrets", "sourceControl") is False
        and field(spine, "secrets", "pluginPackage") is False
        and field(flags, "credentialRead") is False,
        field(proxy, "networkEgress") == "DISABLED"
        and field(proxy, "automaticProviderCalls") is False
        and field(flags, "providerCall") is False
        and field(flags, "cloudflareMutation") is False,
        field(law, "noGithubPrOidcOrSecrets") is True
        and field(orchestra, "github", "oidcEnabledByThisWorkflow") is False
        and field(flags, "gitHubOidc") is False,
        field(proxy, "fallback") == field(h, "fallback") == "deterministicLocal"
        and field(orchestra, "googleAi", "fallback") == "deterministicLocal",
        field(spine, "adapterContract", "stableReceiptSchema") == "luhmOs.providerExecutionReceipt.v1"
        and {"taskId", "sourceRef", "scopeId"}.issubset(
            set(field(spine, "observability", "requiredReceiptFields") or []))
        and field(h, "taskId") == "googleAiHexCanonReadiness20261104"
        and field(h, "scopeId") == "googleAiCandidateReviewOnly",
        field(proxy, "runtimeAgentWorkerActivation") is False
        and field(hold, "activeTaskWorkersAllowed") is False
        and field(flags, "agentUnquarantine") is False,
        field(proxy, "crownStatus") == field(h, "crownStatus") == "STOP"
        and field(truth, "crownStatus") == "STOP"
        and field(h, "promotion") is False
        and field(flags, "productionDeploy") is False
        and field(flags, "mainMerge") is False and field(flags, "autoCrown") is False,
    ]
    rows = [{"cell": item["cell"], "lane": item["lane"], "beat": item["beat"],
             "operation": item["operation"], "sourceCheck": "PASS" if ok else "FAIL"}
            for item, ok in zip(expected, checks)]
    all_pass = all(checks) and len(checks) == 16
    return {
        "schema": "luhmOs.googleAiHexReadinessReceipt.v1",
        "taskId": "googleAiHexCanonReadiness20261104",
        "scopeId": "googleAiCandidateReviewOnly",
        "sourceRef": source_ref if isinstance(source_ref, str) and SHA.fullmatch(source_ref) else "INVALID",
        "status": "AMBER_PROVIDER_PROOF_REQUIRED" if all_pass else "RED_SOURCE_POLICY",
        "checkedCells": len(rows), "passedCells": sum(checks), "cells": rows,
        "providerApiInvoked": False, "authenticatedProviderProven": False,
        "billingProven": False, "sourceOnly": True, "agentWorkersActivated": False,
        "canSpend": False, "canMerge": False, "canDeploy": False, "crownStatus": "STOP",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                         text=True, timeout=8).strip()
        receipt = build_receipt(load_docs(), args.source_ref, actual)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, json.JSONDecodeError):
        receipt = {"schema": "luhmOs.googleAiHexReadinessReceipt.v1",
                   "status": "RED_SOURCE_READ_FAILED", "providerApiInvoked": False,
                   "canSpend": False, "canMerge": False, "canDeploy": False, "crownStatus": "STOP"}
    result = json.dumps(receipt, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    print(result, end="")
    return 0 if receipt["status"] == "AMBER_PROVIDER_PROOF_REQUIRED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
