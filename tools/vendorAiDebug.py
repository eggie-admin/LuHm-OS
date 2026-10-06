#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine" / "vendorAiDebugV1.json"

ALIASES = {
    "all": "all",
    "openai": "openAi",
    "opendaddy": "openAi",
    "google": "googleAi",
    "googleai": "googleAi",
    "bigbrother": "googleAi",
    "copilot": "githubCopilot",
    "github": "githubCopilot",
    "githubcopilot": "githubCopilot",
    "huggingface": "huggingFace",
    "hf": "huggingFace",
    "edge": "edgeGallery",
    "edgegallery": "edgeGallery",
}

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def source_ref() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        value = result.stdout.strip()
        return value if value else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def render(provider_id: str, profile: dict, ref: str) -> str:
    lines = [
        "VENDOR_AI_DEBUG=ON",
        f"PROVIDER={provider_id}",
        f"NICKNAME={profile.get('nickname','UNKNOWN')}",
        f"ROLE={profile.get('role','UNKNOWN')}",
        f"LUHM_ROUTE={profile.get('luhmRoute','UNKNOWN')}",
        f"READINESS={profile.get('readiness','UNKNOWN')}",
        f"MODEL_ID={profile.get('modelIdentity','UNKNOWN')}",
        f"ENTITLEMENT={profile.get('entitlement','UNKNOWN')}",
        f"PROVIDER_NATIVE_DEFAULT={profile.get('nativeDefaultLogic','UNKNOWN')}",
        "OBSERVED_EXECUTION=UNKNOWN_UNTIL_EXACT_EXECUTION_RECEIPT",
        f"FALLBACK={profile.get('fallback','UNKNOWN')}",
        f"RECONCILE={profile.get('reconcile','UNKNOWN')}",
        f"AUTHORITY={profile.get('authority','UNKNOWN')}",
        f"SOURCE_REF={ref}",
        "VERDICT=DEBUG_ONLY_NOT_GREEN",
    ]
    return "\n".join(lines)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("provider", nargs="?", default="all")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    contract = load(CONTRACT)
    providers = contract.get("providers", {})
    key = ALIASES.get(str(args.provider).lower())
    if key is None:
        raise SystemExit(f"UNKNOWN_PROVIDER={args.provider}")

    chosen = list(providers) if key == "all" else [key]
    ref = source_ref()
    if args.json_output:
        payload = {
            "schema": "luhmOs.vendorAiDebugSnapshot.v1",
            "sourceRef": ref,
            "debugPresentation": "UPPERCASE",
            "providers": [
                {
                    "providerId": provider_id,
                    **providers[provider_id],
                    "observedExecution": "UNKNOWN_UNTIL_EXACT_EXECUTION_RECEIPT",
                    "verdict": "DEBUG_ONLY_NOT_GREEN",
                }
                for provider_id in chosen
            ],
            "greenAuthority": False,
            "crownAuthority": False,
        }
        print(json.dumps(payload, indent=2))
        return 0

    for index, provider_id in enumerate(chosen):
        if index:
            print("---")
        print(render(provider_id, providers[provider_id], ref))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
