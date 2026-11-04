#!/usr/bin/env python3
"""2048 fail-closed source-policy scenarios for local Firefox TestBridge.

These are 16 * 128 decision-table assertions, NOT 2048 independent
browser/SQL penetration tests or real external TLS/identity proofs.
Emits fixed 64-byte records and a redacted source-only snapshot.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = (
    "explicitConsent", "sameOrigin", "csrfToken", "inputSchema",
    "parameterizedSql", "dataMinimization", "oneHourRetention", "deleteRequest",
    "htmlSafeText", "localTransport", "manifestAccuracy", "workerQuarantine",
    "githubNoPersonalData", "mutationVerb", "exactSource", "crownStop",
)
EVIDENCE = ("valid", "noConsent", "hostileOrigin", "badToken",
            "badSchema", "stale", "unknown", "conflict")
SCOPES = ("loopback", "privateLan", "publicInternet", "crossOrigin")
AUTHORITY = ("anonymous", "userExplicit", "sandboxAdmin", "enterpriseClaim")
RECORD = struct.Struct("<4sBBBBHHII32s12s")
assert RECORD.size == 64
RESULT = {"HOLD": 0, "LOCAL_DEMO_ONLY": 1}


def policy_actual(family, evidence, scope, auth):
    if family in (11, 12, 15):
        return "HOLD"  # agent release, pushing personal data to GitHub, Crown
    if evidence != 0 or scope != 0 or auth != 1:
        return "HOLD"
    return "LOCAL_DEMO_ONLY"


def policy_expected(family, evidence, scope, auth):
    # Separate required control list; no inherited grants through escalation.
    deny = (evidence in (1, 2, 3, 4, 5, 6, 7) or
            scope in (1, 2, 3) or
            auth in (0, 2, 3) or
            FAMILIES[family] in {"workerQuarantine", "githubNoPersonalData", "crownStop"})
    return "HOLD" if deny else "LOCAL_DEMO_ONLY"


def verify_source():
    from host.testBridge import luhmTestBridge
    luhmTestBridge.load_source_policy(ROOT)
    policy = json.loads((ROOT / "doctrine/firefoxTestBridgeV1.json").read_text())
    extension = json.loads((ROOT / "plugins/luhm-firefox-antenna/manifest.json").read_text())
    asserts = {
        "policySchema": policy["schema"] == "luhmOs.firefoxTestBridge.v1",
        "rootSource": policy["parentSource"] == "doctrine/firefoxAntennaV1.json",
        "dataConsent": policy["data"]["requiresExplicitOptIn"] is True,
        "volatileSqlite": policy["data"]["database"] == ":memory:",
        "noRealCredentials": policy["data"]["emailAndPasswords"] is False,
        "localOnly": policy["network"]["bind"] == "127.0.0.1",
        "portIsolated": policy["network"]["port"] == 8766,
        "noGitHubData": policy["data"]["personalRecordsInGitHub"] is False,
        "workerQuarantine": policy["authority"]["agentsReleased"] is False,
        "stop": policy["crownStatus"] == "STOP",
        "firefoxExtensionStillStatusOnly": extension["browser_specific_settings"]["gecko"]["data_collection_permissions"]["required"] == ["none"]
          and extension["host_permissions"] == ["http://127.0.0.1:8765/*"],
        "staticPage": (ROOT / "host/testBridge/index.html").is_file(),
    }
    if luhmTestBridge.MAX_AGE_SECONDS != 3600 or luhmTestBridge.MAX_RECORDS != 32:
        asserts["retentionBudget"] = False
    else:
        asserts["retentionBudget"] = True
    return asserts


def generate(source_ref):
    for family, name in enumerate(FAMILIES):
        for case in range(128):
            evidence = case & 0x7
            scope = (case >> 3) & 3
            auth = (case >> 5) & 3
            actual = policy_actual(family, evidence, scope, auth)
            expected = policy_expected(family, evidence, scope, auth)
            seq = family * 128 + case
            passed = actual == expected
            row = {
                "id": f"0x{seq:03X}", "family": name, "evidence": EVIDENCE[evidence],
                "scope": SCOPES[scope], "authority": AUTHORITY[auth],
                "decision": actual, "pass": passed,
            }
            digest = hashlib.sha256(json.dumps(
                {"sourceRef": source_ref, **row}, sort_keys=True,
                separators=(",", ":")
            ).encode("utf-8")).digest()
            record = RECORD.pack(
                b"LT64", 1, family, scope, RESULT[actual],
                case, evidence | (auth << 3), seq, int(passed),
                digest, b"\x00" * 12,
            )
            yield row, record


def run(source_ref, output_dir):
    anchors = verify_source()
    rows = []
    binary = bytearray()
    for row, rec in generate(source_ref):
        rows.append(row)
        binary.extend(rec)
    ok = (len(rows) == 2048 and len(binary) == 131072
          and len({r["id"] for r in rows}) == 2048
          and all(r["pass"] for r in rows) and all(anchors.values()))
    report = {
        "schema": "luhmOs.firefoxTestBridge2048Snapshot.v1",
        "sourceRef": source_ref, "scope": "LOCAL_TESTBRIDGE_SOURCE_ONLY",
        "scenarioFamilies": 16, "scenariosPerFamily": 128,
        "scenarioAssertions": len(rows),
        "passedScenarioAssertions": sum(r["pass"] for r in rows),
        "binaryRecordBytes": 64, "binaryBytes": len(binary),
        "sourceAnchors": anchors,
        "verdict": "SOURCE_MODEL_PASS" if ok else "SOURCE_MODEL_RED",
        "proofClass": "deterministicPolicyScenariosNotIndependentRealWorldTests",
        "privateRecordsIncluded": False, "sql": "SQLiteMemoryOnly",
        "tlsPublicProof": False, "phpMyAdminRuntime": False,
        "firefoxHostSigningProven": False, "livePublicDeployment": False,
        "currentChatMcpMounted": False, "crownStatus": "STOP",
        "cases": rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "testBridge2048.bin").write_bytes(binary)
    (output_dir / "snapshot.json").write_text(json.dumps(report, indent=2) + "\n")
    return report, ok


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="build/testBridge2048")
    args = parser.parse_args()
    ref = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    snapshot, ok = run(ref, ROOT / args.output_dir)
    print(json.dumps({k: snapshot[k] for k in (
        "sourceRef", "scenarioAssertions", "passedScenarioAssertions",
        "binaryBytes", "sourceAnchors", "verdict", "crownStatus"
    )}, indent=2))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
