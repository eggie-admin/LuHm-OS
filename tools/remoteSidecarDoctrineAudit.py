#!/usr/bin/env python3
"""Deterministic, offline remote sidecar doctrine denial tests."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "doctrine/remoteSidecarHardeningV1.json").read_text())
KNOWN = {s["id"] for s in D["sidecars"]}
READS = {("github", "inspect"), ("render", "publicReadOnly")}

def decision(sidecar: str, action: str) -> str:
    if sidecar not in KNOWN:
        return "DENY"
    if D["invariants"]["companyQuarantine"] != "QUARANTINED":
        return "DENY"
    if (sidecar, action) in READS:
        return "ALLOW"
    return "DENY"

def main() -> int:
    assert D["invariants"]["activeAgentsAllowed"] is False
    assert D["invariants"]["defaultRemoteWrite"] is False
    assert D["invariants"]["defaultExternalAiExecution"] is False
    assert D["invariants"]["denyUnknown"] is True
    assert D["productionChanged"] is False
    assert len(KNOWN) == len(D["sidecars"])
    for test in D["testCases"]:
        actual = decision(test["sidecar"], test.get("action", ""))
        assert actual == test["expected"], (test["id"], actual)
    print(f"GREEN_REMOTE_SIDECAR_SOURCE_DENIAL_TESTS:{len(D['testCases'])}")
    print("NOTE: source contract test only; not runtime/provider authentication proof")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
