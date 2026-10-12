#!/usr/bin/env python3
"""Read-only, fail-closed sanity gate for current LuHm AI task manifests.

This gate validates candidate input. A passing result never authorizes execution,
publication, promotion, GREEN status, or changes to user/network files.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_FILES = {
    "truth": "doctrine/currentSourceTruthV3.json",
    "control": "doctrine/luhmAiControlPlaneV1.json",
    "formats": "doctrine/aiManifestFormatV1.json",
    "template": "doctrine/aiTaskManifestV2.template.json",
    "escalation": "doctrine/escalationKernelV1.json",
}


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("RED_DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def decode_json(text):
    return json.loads(text, object_pairs_hook=no_duplicate_keys)


def load_policy(root=ROOT):
    return {
        name: decode_json((root / relative).read_text(encoding="utf-8"))
        for name, relative in POLICY_FILES.items()
    }


def policy_errors(policy):
    truth = policy["truth"]
    control = policy["control"]
    formats = policy["formats"]
    template = policy["template"]
    escalation = policy["escalation"]
    errors = []
    current = "luhmOs.aiTaskManifest.v2"
    manifest_law = truth.get("manifestLaw", {})
    active = control.get("aiTaskManifest", {})
    legacy = control.get("taskManifest", {})
    if not (
        manifest_law.get("currentAiTaskSchema") == current
        and manifest_law.get("taskTemplate") == POLICY_FILES["template"]
        and formats.get("currentSchemas", []).count(current) == 1
        and active.get("schema") == current
        and active.get("template") == POLICY_FILES["template"]
        and template.get("schema") == current
    ):
        errors.append("RED_CURRENT_MANIFEST_CONFLICT")
    if not (
        legacy.get("schema") == "luhmOs.aiTaskManifest.v1"
        and legacy.get("status") == "LEGACY_PROVENANCE_ONLY"
        and legacy.get("mayAuthorizeExecution") is False
        and manifest_law.get("legacyNonCurrentAiManifests") is True
    ):
        errors.append("RED_LEGACY_MANIFEST_AUTHORITY")
    if not (
        truth.get("crownStatus") == "STOP"
        and truth.get("publicationAuthority") is False
        and truth.get("releaseAuthority") is False
        and truth.get("productionSigningAuthority") is False
        and control.get("crownStatus") == "STOP"
        and control.get("invariants", {}).get("professorFinalAuthority") is True
        and control.get("invariants", {}).get("escalationTierDoesNotExpandAuthority") is True
        and control.get("invariants", {}).get("escalationPreservesTaskSourceScope") is True
        and active.get("responseAuthority") is False
    ):
        errors.append("RED_CROWN_OR_AUTHORITY_DRIFT")
    if not (
        truth.get("escalationSystem", {}).get("tierCount") == 4
        and truth.get("escalationSystem", {}).get("zeroBased") is True
        and truth.get("escalationSystem", {}).get("authorityEffect") == "NONE"
        and [row.get("tier") for row in escalation.get("tierSemantics", [])] == [0, 1, 2, 3]
    ):
        errors.append("RED_ESCALATION_CONTRACT_DRIFT")
    return errors


def validate_manifest(manifest, policy, task_id, source_ref, scope_id):
    errors = policy_errors(policy)
    if not isinstance(manifest, dict):
        return errors + ["RED_MANIFEST_NOT_OBJECT"]
    template = policy["template"]
    active = policy["control"].get("aiTaskManifest", {})
    allowed_keys = set(template)
    missing = set(active.get("required", [])) - set(manifest)
    if missing:
        errors.append("RED_MISSING_REQUIRED_FIELDS")
    if set(manifest) - allowed_keys:
        errors.append("RED_UNKNOWN_MANIFEST_FIELDS")
    if manifest.get("schema") != policy["truth"].get("manifestLaw", {}).get("currentAiTaskSchema"):
        errors.append("RED_LEGACY_OR_UNKNOWN_SCHEMA")
    for name, expected in (("taskId", task_id), ("sourceRef", source_ref), ("scopeId", scope_id)):
        if not isinstance(expected, str) or not expected.strip() or expected == "UNKNOWN":
            errors.append("RED_EXPLICIT_IDENTITY_REQUIRED")
        elif manifest.get(name) != expected:
            errors.append("RED_IDENTITY_MISMATCH")
    for key in ("providerId", "capabilityId", "requiredOutputSchema"):
        val = manifest.get(key)
        if not isinstance(val, str) or not val.strip() or val == "UNKNOWN":
            errors.append("RED_UNRESOLVED_CAPABILITY")
    refs = manifest.get("inputRefs")
    if not isinstance(refs, list) or not all(isinstance(r, str) and r.strip() for r in refs):
        errors.append("RED_INPUT_REFS")
    budget = manifest.get("budget")
    if not isinstance(budget, dict) or set(budget) != {"maxRequests", "maxParallel", "maxPasses"}:
        errors.append("RED_BUDGET_SHAPE")
    else:
        maximums = {
            "maxRequests": 10,
            "maxParallel": min(3, policy["control"].get("invariants", {}).get("maxParallelSupportWorkers", 0)),
            "maxPasses": 10,
        }
        for key, upper in maximums.items():
            amount = budget.get(key)
            if type(amount) is not int or not 1 <= amount <= upper:
                errors.append("RED_BUDGET_EXCEEDED")
                break
    stops = manifest.get("stopConditions")
    required_stops = {"sourceMismatch", "evidenceConflict", "budgetExhausted"}
    allowed_stops = set(template.get("stopConditions", []))
    if not (isinstance(stops, list) and len(stops) == len(set(map(str, stops)))
            and all(isinstance(item, str) for item in stops)
            and required_stops.issubset(stops) and set(stops).issubset(allowed_stops)):
        errors.append("RED_STOP_CONDITIONS")
    if manifest.get("authority") != {"mutation": False, "green": False, "crown": False}:
        errors.append("RED_PRIVILEGE_ESCALATION")
    return sorted(set(errors))


def candidate(task_id="sanityTest", source_ref="0123456789abcdef0123456789abcdef01234567", scope_id="readOnly"):
    return {
        "schema": "luhmOs.aiTaskManifest.v2",
        "status": "CANDIDATE",
        "providerId": "local",
        "capabilityId": "research",
        "taskId": task_id,
        "sourceRef": source_ref,
        "scopeId": scope_id,
        "inputRefs": [],
        "requiredOutputSchema": "luhmOs.candidateEvidence.v1",
        "budget": {"maxRequests": 1, "maxParallel": 1, "maxPasses": 1},
        "stopConditions": ["scopeComplete", "evidenceConflict", "sourceMismatch", "budgetExhausted"],
        "authority": {"mutation": False, "green": False, "crown": False},
        "responseRequired": ["providerId", "taskId", "sourceRef", "scopeId", "responseId", "outputRefs", "claims", "timestamp"],
    }


def self_test(policy):
    import copy
    base = candidate()
    identity = ("sanityTest", base["sourceRef"], "readOnly")
    cases = [
        ("currentV2", base, True),
        ("legacyV1", {**base, "schema": "luhmOs.aiTaskManifest.v1"}, False),
        ("unknownOverride", {**base, "functionOverrides": {}}, False),
        ("crownGrant", {**base, "authority": {"mutation": False, "green": False, "crown": True}}, False),
        ("wrongSource", {**base, "sourceRef": "wrong"}, False),
        ("unsafeParallel", {**base, "budget": {"maxRequests": 1, "maxParallel": 4, "maxPasses": 1}}, False),
        ("missingStop", {**base, "stopConditions": ["scopeComplete"]}, False),
    ]
    results = []
    for name, item, expected in cases:
        actual = not validate_manifest(copy.deepcopy(item), policy, *identity)
        results.append({"case": name, "pass": actual == expected})
    try:
        decode_json('{"schema": "a", "schema": "b"}')
        results.append({"case": "duplicateKey", "pass": False})
    except ValueError:
        results.append({"case": "duplicateKey", "pass": True})
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--task-id", default="")
    parser.add_argument("--source-ref", default="")
    parser.add_argument("--scope-id", default="")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        policy = load_policy()
        if args.self_test:
            results = self_test(policy)
            errors = policy_errors(policy)
            ok = not errors and all(row["pass"] for row in results)
            print(json.dumps({"status": "GREEN_STATIC_CANDIDATE" if ok else "RED", "tests": results,
                              "errors": errors, "executionAuthority": False, "crownStatus": "STOP"}, indent=2))
            return 0 if ok else 1
        if not args.manifest:
            parser.error("--manifest required unless --self-test is used")
        manifest = decode_json(args.manifest.read_text(encoding="utf-8"))
        errors = validate_manifest(manifest, policy, args.task_id, args.source_ref, args.scope_id)
        print(json.dumps({"status": "VALID_CANDIDATE_ONLY" if not errors else "RED",
                          "errors": errors, "executionAuthority": False, "crownStatus": "STOP"}, indent=2))
        return 0 if not errors else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "RED", "errors": [type(exc).__name__],
                          "executionAuthority": False, "crownStatus": "STOP"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
