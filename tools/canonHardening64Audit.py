#!/usr/bin/env python3
"""64 exact-source LuHm-OS Canon assertions, 4 domains x 4 lanes x 4 beats.

All checks are offline, read-only and scoped to committed repository source.
A passing 64/64 is AMBER_SOURCE_ONLY, not live service, API or device proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "doctrine/canonHardening64V1.json"
DOMAINS = ("governance", "security", "integration", "delivery")
BEATS = ("inventory", "scope", "verify", "propose")
DOCS = (
    "doctrine/currentSourceTruthV3.json",
    "doctrine/projectChatCanonV1.json",
    "doctrine/escalationKernelV1.json",
    "doctrine/proposedWorkingLaneV1.json",
    "doctrine/companyWideOperationalQuarantineV1.json",
    "doctrine/storageTopologyV1.json",
    "doctrine/typedFourLaneSqlV1.json",
    "doctrine/cloudflareAirTrafficControllerV1.json",
    "doctrine/apiSpineV1.json",
    "doctrine/googleAiDeveloperEntitlementsV1.json",
    "doctrine/googleAiProxyDeploymentV1.json",
    "doctrine/cloudflareLumOrchestrationV1.json",
    "doctrine/androidDeliveryLanesV1.json",
    "doctrine/publicArtReleaseReadinessV1.json",
    "doctrine/releaseBoundaryV2.json",
    "doctrine/fourTierOperatingModelV1.json",
)
SHA = re.compile(r"^[0-9a-f]{40}$")
KEY = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")
OPERATORS = ("eq", "contains", "length")


def path_value(data, route):
    if not isinstance(route, str) or not route or len(route) > 200:
        raise ValueError("unbounded or empty JSON selector")
    current = data
    for key in route.split("."):
        if not KEY.fullmatch(key) or not isinstance(current, dict) or key not in current:
            raise KeyError(route)
        current = current[key]
    return current


def match(value, op, expected):
    # A Python bool must never impersonate numeric zero or one.
    if op == "eq":
        return type(value) is type(expected) and value == expected
    if op == "length":
        return isinstance(value, (list, dict)) and type(expected) is int and len(value) == expected
    if op == "contains":
        return isinstance(value, list) and expected in value
    raise ValueError("unsupported assertion")


def verify_manifest(m):
    if not isinstance(m, dict) or m.get("schema") != "luhmOs.canonHardening64.v1" or m.get("status") != "SOURCE_CANDIDATE_ONLY":
        raise ValueError("invalid or promoted matrix")
    if m.get("taskId") != "canonHardening64_20261104" or m.get("scopeId") != "wholeSystemSourceAuthorityAudit":
        raise ValueError("task identity drift")
    if m.get("sourceLaw") != "AI proposes. Policy authorizes. CI proves. Human promotes.":
        raise ValueError("source law drift")
    if m.get("authority") != "Professor" or m.get("boss") != "lum" or m.get("promotion") is not False:
        raise ValueError("authority drift")
    g = m.get("geometry", {})
    if g.get("domains") != list(DOMAINS) or g.get("lanesPerDomain") != 4 or g.get("beats") != list(BEATS) or g.get("slots") != 64 or g.get("hexRange") != "0x00..0x3f":
        raise ValueError("not 4x4x4")
    esc = m.get("escalation", {})
    if esc.get("startTier") != 0 or esc.get("highestTier") != 3 or esc.get("maxSameSourceRetries") != 3:
        raise ValueError("unsafe tier shape")
    if not all(esc.get(k) is True for k in ("failureEscalatesWithinScope", "unknownHolds", "noAuthorityIncrease", "passDeescalates", "eachTickReverifies")):
        raise ValueError("unsafe escalation law")
    gates = m.get("gates", {})
    if gates.get("githubPermissions") != "contents:read" or gates.get("crown") != "STOP" or gates.get("oneMutableSourceLane") is not True or gates.get("publicPrUntrusted") is not True:
        raise ValueError("unsafe gate")
    if not all(gates.get(k) is False for k in ("cloudSecrets", "providerApiCalls", "paidCredits", "productionSql", "cloudflareMutation", "liveDeviceProof", "agentRelease", "mainMerge", "productionDeploy", "publication")):
        raise ValueError("escalated privileges")
    rows = m.get("matrix")
    if not isinstance(rows, list) or len(rows) != 64:
        raise ValueError("not 64 assertions")
    if len(set((r.get("cell") for r in rows if isinstance(r, dict)))) != 64:
        raise ValueError("duplicate hex cells")
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {"cell", "domain", "lane", "beat", "source", "jsonPath", "operator", "expected"}:
            raise ValueError("unrecognized matrix fields")
        if row["cell"] != f"0x{i:02x}" or row["domain"] != DOMAINS[i // 16] or type(row["lane"]) is not int or row["lane"] != i % 16 // 4 or row["beat"] != BEATS[i % 4]:
            raise ValueError("matrix order drift")
        if row["source"] != DOCS[i // 4] or row["operator"] not in OPERATORS:
            raise ValueError("unapproved check/source")
        if not isinstance(row["jsonPath"], str) or not all(KEY.fullmatch(x) for x in row["jsonPath"].split(".")):
            raise ValueError("invalid selector")
        if row["operator"] == "length" and type(row["expected"]) is not int:
            raise ValueError("length must be exact integer")
    return rows


def read_sources(root=ROOT):
    docs, digests = {}, {}
    for rel in DOCS:
        src = root / rel
        if not src.is_file() or src.is_symlink():
            raise ValueError("missing or aliased Canon file: " + rel)
        content = src.read_bytes()
        docs[rel] = json.loads(content)
        digests[rel] = hashlib.sha256(content).hexdigest()
    return docs, digests


def independent_authority_stop(docs):
    # Untrusted edits to a matrix's expected values cannot grant a release.
    truth, hold, ent, proxy, edge, mobile, release, art = (docs[DOCS[i]] for i in (0, 4, 9, 10, 7, 12, 14, 13))
    return (
        truth.get("promotion") is False and truth.get("crownStatus") == "STOP"
        and truth.get("publicationAuthority") is False
        and hold.get("state") == "QUARANTINED" and hold.get("activeTaskWorkersAllowed") is False
        and ent.get("executionLaw", {}).get("defaultAction") == "DENY"
        and ent.get("entitlementAxes", {}).get("cloudBilling", {}).get("paidCallsAllowed") is False
        and proxy.get("automaticProviderCalls") is False
        and proxy.get("networkEgress") == "DISABLED"
        and edge.get("authorityBoundary", {}).get("crownAuthority") is False
        and mobile.get("proof", {}).get("physicalDeviceInstall") == "PENDING"
        and mobile.get("proof", {}).get("binaryManifestReleaseEligible") is False
        and "productionSigning" in release.get("deniedActions", [])
        and art.get("publicationAuthority") is False
    )


def receipt(m, docs, digests, expected_ref, actual_ref, prior=None):
    rows = verify_manifest(m)
    if not isinstance(expected_ref, str) or not SHA.fullmatch(expected_ref) or actual_ref != expected_ref:
        raise ValueError("immutable sourceRef mismatch")
    if not independent_authority_stop(docs):
        raise ValueError("critical authority breach")
    prior = prior or {}
    if not isinstance(prior, dict):
        raise ValueError("prior receipt must be object")
    # Prior state is never evidence. It is used only for bounded diagnosis tiers.
    prior_lanes = {}
    if prior.get("sourceRef") == expected_ref and prior.get("canonSha256") == digests:
        previous_lanes = prior.get("lanes", [])
        if not isinstance(previous_lanes, list):
            raise ValueError("malformed prior lanes")
        for lane in previous_lanes:
            if not isinstance(lane, dict) or lane.get("id") in prior_lanes:
                raise ValueError("duplicate/bad prior lane")
            prior_lanes[lane.get("id")] = lane
    results, lane_results = [], []
    for i in range(16):
        name = f"{DOMAINS[i//4]}/{i%4}"
        prior_row = prior_lanes.get(name, {})
        tier = prior_row.get("tier", 0)
        retries = prior_row.get("retries", 0)
        if type(tier) is not int or not 0 <= tier <= 3 or type(retries) is not int or not 0 <= retries <= 3:
            raise ValueError("invalid escalation receipt")
        blocked = retries >= 3
        local_results = []
        for row in rows[i * 4:i * 4 + 4]:
            # Reverify even a previously blocked lane. Do not trust a stale GREEN.
            try:
                value = path_value(docs[row["source"]], row["jsonPath"])
                ok = match(value, row["operator"], row["expected"])
            except (KeyError, TypeError, ValueError):
                ok = False
            local_results.append(ok)
            results.append({"cell": row["cell"], "domain": row["domain"],
                            "lane": row["lane"], "beat": row["beat"], "source": row["source"],
                            "selector": row["jsonPath"], "result": "PASS" if ok else "RED"})
        if all(local_results):
            next_tier = max(tier - 1, 0)
            state, next_retries = "SOURCE_PASS", 0
        else:
            next_retries = min(retries + 1, 3)
            next_tier = min(tier + 1, 3)
            state = "HOLD_SPECIALIST" if blocked or next_retries >= 3 else "REPAIR_REQUIRED"
        lane_results.append({"id": name, "tier": next_tier, "retries": next_retries,
                             "state": state, "passed": sum(local_results)})
    passed = sum(r["result"] == "PASS" for r in results)
    return {
        "schema": "luhmOs.canonHardening64Receipt.v1", "taskId": m["taskId"], "scopeId": m["scopeId"],
        "sourceRef": expected_ref, "canonSha256": digests,
        "sourceStatus": "PASS_64_SOURCE_CHECKS" if passed == 64 else "RED_SOURCE_CHECKS",
        "overallVerdict": "AMBER_EXTERNAL_PROOF_REQUIRED" if passed == 64 else "RED_SOURCE_BLOCKER",
        "checked": 64, "passed": passed, "failed": 64-passed, "cells": results, "lanes": lane_results,
        "liveExternalProof": False, "googleAiExecution": False, "physicalDeviceProof": False,
        "merge": False, "deployment": False, "agentActivation": False,
        "spending": False, "publication": False, "crownStatus": "STOP",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=8).strip()
        m = json.loads(MATRIX.read_text(encoding="utf-8"))
        docs, digests = read_sources()
        prior = json.loads(args.previous.read_text(encoding="utf-8")) if args.previous else None
        data = receipt(m, docs, digests, args.source_ref, actual, prior)
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError, subprocess.SubprocessError):
        data = {"schema": "luhmOs.canonHardening64Receipt.v1", "sourceStatus": "RED_INVALID_AUDIT",
                "overallVerdict": "RED_SOURCE_BLOCKER", "crownStatus": "STOP",
                "liveExternalProof": False, "merge": False, "deployment": False}
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if data["sourceStatus"] == "PASS_64_SOURCE_CHECKS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
