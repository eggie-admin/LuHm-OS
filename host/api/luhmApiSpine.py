#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SPINE_PATH = ROOT / "doctrine" / "apiSpineV1.json"
TRAFFIC_PATH = ROOT / "doctrine" / "cloudflareAirTrafficControllerV1.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain an object")
    return value


def load_contracts() -> tuple[dict[str, Any], dict[str, Any]]:
    spine = load_json(SPINE_PATH)
    traffic = load_json(TRAFFIC_PATH)
    if spine.get("schema") != "luhmOs.apiSpine.v1":
        raise RuntimeError("RED_API_SPINE_SCHEMA")
    if traffic.get("schema") != "luhmOs.cloudflareAirTrafficController.v1":
        raise RuntimeError("RED_TRAFFIC_CONTROLLER_SCHEMA")
    if spine.get("routing", {}).get("principle") != "capabilityFirstProviderSecond":
        raise RuntimeError("RED_PROVIDER_FIRST_ROUTING")
    if traffic.get("authorityBoundary", {}).get("aiProvider") is not False:
        raise RuntimeError("RED_CLOUDFLARE_AI_PROVIDER_DRIFT")
    return spine, traffic


def resolve_capability(capability_id: str, provider_hint: str = "") -> dict[str, Any]:
    capability = capability_id.strip()
    if not capability:
        raise ValueError("capabilityId is required")
    spine, traffic = load_contracts()
    providers = spine.get("providers", {})
    eligible = []
    for provider_id, adapter in providers.items():
        if capability in adapter.get("capabilityClasses", []):
            eligible.append({
                "providerId": provider_id,
                "adapterId": adapter.get("adapterId", "UNKNOWN"),
                "readiness": adapter.get("readiness", "UNKNOWN"),
                "entitlementState": adapter.get("entitlementState", "UNKNOWN"),
                "modelIdentityState": adapter.get("modelIdentityState", "UNKNOWN"),
                "fallbackAdapters": adapter.get("fallbackAdapters", []),
                "receiptSchema": adapter.get("receiptSchema", "UNKNOWN"),
            })
    if provider_hint:
        hinted = [x for x in eligible if x["providerId"] == provider_hint or x["adapterId"] == provider_hint]
        if not hinted:
            raise ValueError("provider hint is not eligible for requested capability")
        eligible = hinted + [x for x in eligible if x not in hinted]
    return {
        "schema": "luhmOs.apiRoutePlan.v1",
        "capabilityId": capability,
        "routingPrinciple": spine.get("routing", {}).get("principle"),
        "eligibleAdapters": eligible,
        "providerExecutionProven": False,
        "degradedMode": False if eligible else True,
        "trafficController": {
            "provider": traffic.get("provider"),
            "role": traffic.get("role"),
            "aiProvider": traffic.get("authorityBoundary", {}).get("aiProvider"),
        },
        "authority": {
            "greenAuthority": False,
            "crownAuthority": False,
            "mutationAuthority": False,
        },
    }


def validate_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    spine, _ = load_contracts()
    required = spine.get("observability", {}).get("requiredReceiptFields", [])
    missing = [key for key in required if receipt.get(key) in (None, "")]
    schema_ok = receipt.get("schema") == spine.get("adapterContract", {}).get("stableReceiptSchema")
    return {
        "schema": "luhmOs.providerReceiptValidation.v1",
        "valid": schema_ok and not missing,
        "schemaValid": schema_ok,
        "missing": missing,
        "projectGreen": False,
        "requiresUrdAdjudication": True,
        "requiresLumReconciliation": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--capability", default="")
    parser.add_argument("--provider", default="")
    args = parser.parse_args()

    if args.check:
        spine, traffic = load_contracts()
        print(json.dumps({
            "status": "LUHM_API_SPINE_SOURCE_GREEN",
            "schema": spine.get("schema"),
            "providers": len(spine.get("providers", {})),
            "trafficController": traffic.get("role"),
            "cloudflareAiProvider": traffic.get("authorityBoundary", {}).get("aiProvider"),
            "crownStatus": "STOP",
        }, indent=2))
        return 0

    if args.capability:
        print(json.dumps(resolve_capability(args.capability, args.provider), indent=2))
        return 0

    parser.error("use --check or --capability")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
