#!/usr/bin/env python3
"""Hex64 Insanus 2048: deterministic, source-only CAST escalation matrix.

16 distinct guardrail families x 128 (evidence, tier, authority) scenarios.
A pass means the model honors the tested source policy, NOT a runtime audit.
No external calls, real SQL mutations, root escalation, agents or deployment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
STAGES = (
    "sanityCheck", "audit", "ingest", "mutation",
    "test", "apply", "continue", "deploy",
    "sourceIdentity", "sandboxPrivilege", "sqliteIsolation",
    "binaryStorage", "vendorBudget", "agentQuarantine",
    "rollback", "crownGate",
)
EVIDENCE = (
    "exactSourceGreen", "red", "unknown", "conflict",
    "stale", "missing", "sourceOnlyGreen", "sourceMismatch",
)
AUTHORITY = ("none", "scopedProposal", "sandboxAdmin", "releaseClaim")
# 4-byte magic + four 1-byte fields + two 2-byte fields + two 4-byte
# fields + 32-byte SHA-256 + 12 reserved bytes = exactly 0x40 bytes.
RECORD = struct.Struct("<4sBBBBHHII32s12s")
assert RECORD.size == 0x40
DECISIONS = {"HOLD": 0, "READ_ONLY": 1, "PROPOSED_ONLY": 2, "SANDBOX_ONLY": 3}


def source_requirements(root):
    def read(path):
        return json.loads((root / path).read_text(encoding="utf-8"))

    project = read("doctrine/projectChatCanonV1.json")
    truth = read("doctrine/currentSourceTruthV3.json")
    covenant = read("doctrine/everlastingCovenantV1.json")
    kernel = read("doctrine/escalationKernelV1.json")
    quarantine = read("doctrine/companyWideOperationalQuarantineV1.json")
    solo = read("doctrine/soloStudioOperatingProfileV1.json")
    checks = {
        "canonicalIdentity": project["developmentIdentity"]["productName"] == "LuHm-OS",
        "sourceTruthStop": truth["crownStatus"] == "STOP" and truth["promotion"] is False,
        "guardRail": covenant["guardRail"]["orderedStates"] == list(STAGES[:8]),
        "fourTiers": [item["tier"] for item in kernel["tierSemantics"]] == list(range(4)),
        "tierNotAuthority": "tierIncreaseChangesFocusAndMaturityNotAuthority" in kernel["commonLaws"],
        "companyQuarantined": quarantine["state"] == "QUARANTINED"
            and quarantine["activeTaskWorkersAllowed"] is False,
        "soloNoImplicitAdmin": solo["privacyAndSafety"]["access"].startswith("Least privilege"),
        "soloNoAutoDeploy": "No automatic production" in solo["deployPolicy"],
        "titan500Present": (root / "tools/premonitionTitan500Audit.py").is_file(),
        "currentSourceTracked": (root / "doctrine/crownCathedralWebglCastV1.json").is_file(),
    }
    return checks


def expected_decision(stage, evidence, authority):
    # Independent compact policy table, derived from existing Canon.
    if evidence in (1, 2, 3, 4, 5, 7):
        return "HOLD"
    if stage in (11, 12, 13, 15):
        return "HOLD"  # No live binary, vendor, worker or Crown proof here.
    if stage == 9:
        return "SANDBOX_ONLY" if authority == 2 else "HOLD"
    if stage == 10:
        return "READ_ONLY"  # Actual work is an in-memory rolled-back SQL probe.
    if stage in (0, 1, 2, 4, 8):
        return "READ_ONLY"
    if stage in (3, 5, 6, 7, 14):
        return "PROPOSED_ONLY" if evidence == 0 and authority == 1 else "HOLD"
    raise AssertionError("unknown stage")


def gate_decision(stage, evidence, authority, tier):
    """Implementation under test. Tier must never increase authority."""
    if not 0 <= tier < 4 or not 0 <= evidence < 8 or not 0 <= authority < 4:
        return "HOLD"
    if evidence not in (0, 6):
        return "HOLD"
    if stage in (11, 12, 13, 15):
        return "HOLD"
    if stage == 9:
        if authority == 2:
            return "SANDBOX_ONLY"
        return "HOLD"
    if stage == 10:
        return "READ_ONLY"
    if stage in (0, 1, 2, 4, 8):
        return "READ_ONLY"
    if stage in (3, 5, 6, 7, 14):
        if evidence == 0 and authority == 1:
            return "PROPOSED_ONLY"
        return "HOLD"
    return "HOLD"


def sqlite_probe(connection, case):
    # Savepoint rollback guarantees no retained row. Bound parameters only.
    payload = "audit-' OR 1=1 -- " + str(case)
    connection.execute("SAVEPOINT case_probe")
    connection.execute("INSERT INTO evidence(case_id, value) VALUES (?, ?)", (case, payload))
    row = connection.execute(
        "SELECT value FROM evidence WHERE case_id = ?", (case,)
    ).fetchone()
    ok = row == (payload,)
    connection.execute("ROLLBACK TO case_probe")
    connection.execute("RELEASE case_probe")
    return ok and connection.execute("SELECT COUNT(*) FROM evidence").fetchone()[0] == 0


def matrix(source_ref):
    """Yield verifiable 64-byte receipts and scenario summaries."""
    sql = sqlite3.connect(":memory:")
    sql.execute("CREATE TABLE evidence(case_id INTEGER, value TEXT NOT NULL)")
    try:
        for stage, name in enumerate(STAGES):
            for case in range(0x80):
                evidence = case & 7
                tier = (case >> 3) & 3
                authority = (case >> 5) & 3
                actual = gate_decision(stage, evidence, authority, tier)
                expected = expected_decision(stage, evidence, authority)
                passed = actual == expected
                if stage == 10:
                    passed = passed and sqlite_probe(sql, case)
                # Deliberately adversarial evidence never authorizes anything.
                if evidence in (1, 2, 3, 4, 5, 7) and actual != "HOLD":
                    passed = False
                # No model state authorizes actual publication or worker release.
                if stage in (11, 12, 13, 15) and actual != "HOLD":
                    passed = False
                # Root/admin sandbox is NEVER equivalent to a repo mutation grant.
                if authority == 2 and actual == "PROPOSED_ONLY":
                    passed = False
                sequence = stage * 0x80 + case
                row = {
                    "id": f"0x{sequence:03X}",
                    "stage": name, "tier": tier,
                    "evidence": EVIDENCE[evidence],
                    "authority": AUTHORITY[authority],
                    "decision": actual,
                    "pass": passed,
                }
                digest = hashlib.sha256(
                    json.dumps({"sourceRef": source_ref, **row}, sort_keys=True,
                               separators=(",", ":")).encode("utf-8")
                ).digest()
                flags = evidence | (authority << 3)
                record = RECORD.pack(
                    b"LH64", 1, stage, tier, DECISIONS[actual],
                    case, flags, sequence, 1 if passed else 0,
                    digest, b"\x00" * 12,
                )
                yield row, record
    finally:
        sql.close()


def run(root, source_ref, output_dir):
    anchors = source_requirements(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = []
    binary = bytearray()
    for row, record in matrix(source_ref):
        cases.append(row)
        binary.extend(record)
    passed = sum(item["pass"] for item in cases)
    distinct = len({item["id"] for item in cases})
    shape_ok = (
        len(cases) == 0x800 and distinct == 0x800
        and len(binary) == 0x800 * 0x40
        and all(binary[i:i + 4] == b"LH64" for i in range(0, len(binary), 0x40))
    )
    complete = shape_ok and passed == 0x800 and all(anchors.values())
    report = {
        "schema": "luhmOs.hex64Insanus2048Receipt.v1",
        "sourceRef": source_ref, "stageFamilies": 0x10,
        "scenariosPerFamily": 0x80, "scenarioAssertions": len(cases),
        "passedScenarioAssertions": passed,
        "binaryRecordBytes": 0x40, "binaryBytes": len(binary),
        "sourceAnchors": anchors,
        "verdict": "SOURCE_MODEL_PASS" if complete else "SOURCE_MODEL_RED",
        "auditClass": "policyScenarioMatrixNot2048IndependentRuntimeAudits",
        "realSqlWork": "inMemoryParameterizedRolledBackOnly",
        "buildExecuted": False, "runtimeProven": False,
        "physicalDeviceProven": False, "signingProven": False,
        "autoAgentsActivated": False, "productionReleased": False,
        "crownStatus": "STOP", "cases": cases,
    }
    (output_dir / "hex64-insanus2048.bin").write_bytes(binary)
    (output_dir / "hex64-insanus2048.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report, complete


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="build/hex64Insanus2048")
    args = parser.parse_args()
    root = ROOT
    source_ref = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    report, ok = run(root, source_ref, root / args.output_dir)
    print(json.dumps({
        key: report[key] for key in (
            "sourceRef", "stageFamilies", "scenarioAssertions",
            "passedScenarioAssertions", "binaryRecordBytes",
            "binaryBytes", "sourceAnchors", "verdict", "crownStatus"
        )
    }, indent=2))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
