#!/usr/bin/env python3
"""Read-only remote-only consolidation report. No imports beyond Python stdlib."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "doctrine/currentSourceTruthV3.json",
    "doctrine/apiSpineV1.json",
    "frontEnd/package.json",
    "packages/unified-ops/package.json",
)
def audit(root=ROOT):
    missing = [p for p in REQUIRED if not (root / p).is_file()]
    if missing:
        return {"schema":"luhmOs.remoteOnlyAudit.v1","status":"BLOCKED","missing":missing}
    truth = json.loads((root / REQUIRED[0]).read_text())
    spine = json.loads((root / REQUIRED[1]).read_text())
    front = json.loads((root / REQUIRED[2]).read_text())
    ops = json.loads((root / REQUIRED[3]).read_text())
    providers = set(spine.get("providers", {}))
    preferred = {"openAi", "googleAi", "githubCopilot"}
    optional = sorted(providers - preferred)
    return {
        "schema":"luhmOs.remoteOnlyAudit.v1",
        "status":"SOURCE_ONLY_NO_DEPLOY",
        "canonicalRepository":truth.get("canonicalRepository"),
        "promotionAllowed":bool(truth.get("promotion", False)),
        "providerAdaptersPreferred":sorted(providers & preferred),
        "providerAdaptersToReview":optional,
        "frontendDependencies":front.get("dependencies", {}),
        "devBridgeDependencies":ops.get("dependencies", {}),
        "devBridgeDevDependencies":ops.get("devDependencies", {}),
        "sourceLicensesMustBeAudited":True,
        "creativeCommonsIsAssetSpecific":True,
        "fairUseIsNotAnAutomaticLicense":True,
        "githubIsNotMutableFileStorage":True,
        "remoteExecutionVerified":False,
        "oneAppRuntimeVerified":False,
        "recommendation":"REVIEW_ONLY_NO_AUTOMATIC_PRUNE",
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(audit(args.root), indent=2, sort_keys=True))
