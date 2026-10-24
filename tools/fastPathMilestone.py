#!/usr/bin/env python3
"""LuHm fast-path continuity: one verified next step, no self-authorization.

Reconciles GitHub branch/rules/PR/check-run reads with local quarantined Canon.
The result is a status checkpoint, not a release approval or AI executor.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = "eggie-admin/LuHm-OS"
EXPECTED_PR = 386
RULESET_ID = 25699963
SHA = re.compile(r"^[0-9a-f]{40}$")
RULE_TYPES = {"pull_request", "non_fast_forward", "deletion"}


def reconcile(snapshot: dict, hold: dict, *, source_ref: str) -> dict:
    """Fail closed on missing/stale GitHub readings and any agent claim."""
    if not SHA.fullmatch(source_ref):
        raise ValueError("exact sourceRef required")
    main = snapshot.get("main") or {}
    rules = snapshot.get("ruleset") or {}
    pr = snapshot.get("pr") or {}
    checks = snapshot.get("checks") or {}
    seen_rules = {
        item.get("type") for item in rules.get("rules", []) if isinstance(item, dict)
    }
    ref_scope = (rules.get("conditions") or {}).get("ref_name") or {}
    protected = (
        main.get("protected") is True
        and rules.get("id") == RULESET_ID
        and rules.get("enforcement") == "active"
        and "refs/heads/main" in ref_scope.get("include", [])
        and RULE_TYPES.issubset(seen_rules)
    )
    source_match = (
        pr.get("number") == EXPECTED_PR
        and (pr.get("head") or {}).get("sha") == source_ref
        and (pr.get("base") or {}).get("ref") == "main"
    )
    runs = checks.get("check_runs")
    runs = runs if isinstance(runs, list) else []
    gh_actions = [x for x in runs if (x.get("app") or {}).get("slug") == "github-actions"]
    source_ci_green = (
        checks.get("verifiedCommit") == source_ref
        and bool(gh_actions)
        and all(x.get("status") == "completed"
                and x.get("conclusion") in ("success", "skipped")
                for x in gh_actions)
        and any(x.get("conclusion") == "success" for x in gh_actions)
        and not any(x.get("conclusion") == "failure" for x in gh_actions)
    )
    # This external status is not a source-CI failure, but may gate a real deploy.
    externals = [x for x in runs if (x.get("app") or {}).get("slug") != "github-actions"]
    external_red = any(x.get("conclusion") == "failure" for x in externals)
    held = (
        hold.get("schema") == "luhmOs.companyWideOperationalQuarantine.v1"
        and hold.get("state") == "QUARANTINED"
        and hold.get("activeTaskWorkersAllowed") is False
        and hold.get("registeredCount") == 15
        and hold.get("crownStatus") == "STOP"
    )
    merged = (
        pr.get("state") == "closed" and pr.get("merged") is True
        and bool(SHA.fullmatch(pr.get("merge_commit_sha") or ""))
    )
    admin_observed = (
        isinstance(main.get("protected"), bool)
        and rules.get("id") == RULESET_ID
        and isinstance(rules.get("rules"), list)
    )
    if not held:
        stage, action = "POLICY_DRIFT_STOP", "RECONCILE_QUARANTINE_CONTRACT"
    elif not admin_observed:
        stage, action = "P0_ADMIN_VERIFY", "RETRY_MAIN_PROTECTION_EVIDENCE_READ"
    elif not protected:
        stage, action = "P0_ADMIN_GATE", "RESTORE_MAIN_PROTECTION_RULESET_25699963"
    elif not source_match:
        stage, action = "P1_SOURCE_GATE", "RECONCILE_EXACT_PR386_SOURCE"
    elif not source_ci_green:
        stage, action = "P1_CI_GATE", "FINISH_OR_REPAIR_EXACT_HEAD_GITHUB_CI"
    elif not merged:
        stage, action = "P1_MERGE_GATE", "PROTECTED_REVIEW_AND_MERGE_PR386"
    else:
        # The workflow has no live Site/host connector or model-executor proof.
        stage, action = "P2_HOST_GATE", "INSTALL_AND_VERIFY_CHATGPT_MCP_RUNTIME"
    return {
        "schema": "luhmOs.fastPathMilestoneCheckpoint.v1",
        "repository": REPO,
        "sourceRef": source_ref,
        "observedAt": datetime.now(timezone.utc).isoformat(),
        "continuityIssue": f"https://github.com/{REPO}/issues/310",
        "integrationPr": f"https://github.com/{REPO}/pull/386",
        "stage": stage,
        "oneNextAction": action,
        "topology": {
            "compatibilityLayers": [
                {"priority": 1, "id": "chatGptOpenAi",
                 "role": "interactiveChatGptMcpHarness"},
                {"priority": 2, "id": "github",
                 "role": "canonicalSourceReviewAndCi"},
            ],
            "heavyWorkhorse": {"providerId": "googleAi", "adapterId": "bigBrother",
                               "liveEntitlement": "UNVERIFIED",
                               "automaticBillableExecution": False},
            "edge": {"providerId": "cloudflare",
                     "role": "authoritativeDnsOptionalProxyTunnelTrafficPolicy",
                     "aiProvider": False, "ownsRuntime": False,
                     "currentDirectMcpProxyUnchanged": True},
            "modelExecutionNotInferredFromCompatibilityOrder": True,
            "references": [
                "doctrine/studioCompatibilityFastMeshV1.json",
                "doctrine/providerEconomyV1.json",
                "doctrine/cloudflareAirTrafficControllerV1.json",
                "doctrine/apiSpineV1.json",
            ],
        },
        "facts": {
            "mainHead": (main.get("commit") or {}).get("sha", "UNKNOWN"),
            "mainProtectionVerified": protected,
            "exactCandidateMatched": source_match,
            "sourceChecksVerified": source_ci_green,
            "externalBuildRed": external_red,
            "companyQuarantineVerifiedHeld": held,
            "hostInstalled": "UNKNOWN_NOT_READ_FROM_CI",
            "agentModelExecution": "NOT_PROVEN",
            "agentActivation": "NOT_AUTHORIZED",
        },
        "executionAuthorized": False,
        "modelWorkersStarted": 0,
        "agentReleaseAuthorized": False,
        "crownStatus": "STOP",
        "evidence": ["github-api-read-only", "committed-quarantine-contract"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        policy = json.loads((args.root / "doctrine/companyWideOperationalQuarantineV1.json").read_text(encoding="utf-8"))
        receipt = reconcile(snapshot, policy, source_ref=args.source_ref)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        receipt = {"schema": "luhmOs.fastPathMilestoneCheckpoint.v1",
                   "sourceRef": args.source_ref,
                   "stage": "UNKNOWN_FAIL_CLOSED", "oneNextAction": "VERIFY_SOURCE_AND_GITHUB_API",
                   "errorType": type(exc).__name__, "executionAuthorized": False,
                   "agentReleaseAuthorized": False, "crownStatus": "STOP"}
    output = json.dumps(receipt, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output)
    return 0 if receipt["stage"] != "UNKNOWN_FAIL_CLOSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
