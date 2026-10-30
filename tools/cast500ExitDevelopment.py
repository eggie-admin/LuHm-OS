#!/usr/bin/env python3
"""500-slot release-exit reconciliation. Read-only, no deploy or authorization."""
from __future__ import annotations
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import samsungCast500Audit as samsung
from unifiedGoddessOrchestraAudit import inspect as inspect_orchestra, sql_smoke

CANDIDATE = "doctrine/cast500ExitDevelopmentGateV1.json"

def read(path: str, root: Path = ROOT) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))

def inventory(rows: list[dict], *, runner: bool) -> dict:
    """500 per-slot integrity assertions; PASS requires narrow real runner evidence."""
    failures: list[str] = []
    allowed = {
        "osAndDrivers/osRelease": "runner_os_release_exists",
        "osAndDrivers/kernelRelease": "runner_kernel_release",
        "osAndDrivers/cpuArchitecture": "runner_platform_machine",
        "forgeAndRelease/sourceShaPresent": "git_rev_parse_HEAD",
        "forgeAndRelease/SqliteJson1Bridge": "in_memory_sqlite_strict_json1",
    }
    canonical = {f"{target}/{domain}/{control}"
                 for target in samsung.TARGETS
                 for domain, controls in samsung.DOMAINS.items()
                 for control in controls}
    if len(canonical) != 500:
        failures.append("MATRIX_500_CANONICAL_IDS")
    seen = set()
    for row in rows:
        key = row.get("id")
        if not isinstance(key, str) or key not in canonical or key in seen:
            failures.append("NONCANONICAL_OR_DUPLICATE_SLOT")
            continue
        seen.add(key)
        target, domain, control = key.split("/")
        if (row.get("target"), row.get("domain"), row.get("control")) != (target, domain, control):
            failures.append("SLOT_ID_FIELDS_MISMATCH")
        verdict = row.get("verdict")
        evidence = row.get("evidence")
        if verdict not in ("PASS", "GAP", "UNVERIFIED") or not isinstance(evidence, str):
            failures.append("INVALID_VERDICT_OR_EVIDENCE")
        elif verdict == "PASS":
            if not runner or target != "githubRunner" or allowed.get(domain+"/"+control) != evidence:
                failures.append("UNSUPPORTED_PASS_CLAIM")
        elif target != "githubRunner" and verdict != "UNVERIFIED":
            failures.append("REMOTE_OR_DEVICE_UNOBSERVED")
    if len(rows) != 500 or seen != canonical:
        failures.append("MISSING_OR_EXTRANEOUS_SLOTS")
    return {"evaluated": len(seen), "expected": 500,
            "counts": dict(Counter(r.get("verdict") for r in rows)),
            "errors": sorted(set(failures)),
            "physicalOrRemoteDeviceProven": False}

def audit(config_override=None, rows_override=None, *, runner=False, root=ROOT) -> dict:
    p = config_override if config_override is not None else read(CANDIDATE, root)
    source = read("doctrine/samsungCast500V1.json", root)
    release = read("doctrine/finalFormPublicReleaseGateV1.json", root)
    quarantine = read("doctrine/companyWideOperationalQuarantineV1.json", root)
    cast = read("doctrine/PROFESSOR_CAST_BRIDGE_V1.json", root)
    stage = read("doctrine/castBridgeStageGateV1.json", root)
    privacy = read("doctrine/dataProtectionLadderV1.json", root)
    checks = {}
    def ck(key, valid): checks[key] = bool(valid)

    ck("schema", p.get("schema") == "luhmOs.cast500ExitDevelopmentGate.v1")
    ck("sourceStatus", p.get("status") == "CAST_PRE_RELEASE_RECONCILIATION_SOURCE_ONLY")
    ck("law", p.get("sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes.")
    entry = p["entry"]
    ck("repository", entry["canonicalRepo"] == "eggie-admin/LuHm-OS")
    ck("baselineMainSha", entry["baselineMainSha"] == "f0cb6ee54066b490c0e80efc2c96200fec76ee2d")
    ck("ancestorSha", entry["previousGoddessHeadSha"] == "4d405a1d8c3525f446fa1f2a82a3928936a358c7")
    ck("stack", entry["previousPr"] == 457 and entry["reconciledStackStart"] == 448 and entry["reconciledStackEnd"] == 457)
    ck("mainNotMerged", entry["mergeIntoMainCompleted"] is False)
    matrix = p["assessment"]
    ck("matrixDimensions", (matrix["targets"], matrix["domains"], matrix["controlsPerDomain"], matrix["slots"]) == (5,4,25,500))
    ck("sourceMatrixStillCanonical", source["assessmentSlots"] == 500 and source["distinctControls"] == 100)
    ck("runnerNotHardware", all(matrix[k] for k in ("runnerCannotProveSamsung","runnerCannotProveLinuxStudio"))
       and matrix["cameraStreamsVerified"] == 0)
    ck("noFalseEvidence", matrix["metadataChecksAreRuntimeSuccess"] is False and matrix["sourceCiIsProductionProof"] is False)
    ck("canonicalRefs", all((root / ref).is_file() for ref in p["dependencyGates"].values()))
    ck("sourceQuarantine", quarantine["state"] == "QUARANTINED" and quarantine["activeTaskWorkersAllowed"] is False)
    ck("castOwnerLaw", cast["trigger"]["requiredActor"] == "github.repository_owner" and cast["trigger"]["exactMainMatch"] is True)
    ck("castStillIdle", stage["ownerCast"]["dispatchTriggered"] is False)
    ck("privateSharingUnresolved", privacy["privacy"]["permissionMutationAuthorized"] is False)
    ck("releaseGateStop", release["fullPublicReleaseGreen"] is False and release["crownStatus"] == "STOP")
    ck("proofPending", all(value is False for value in p["promotionProof"].values()))
    ck("promotionDisabled", all(x["ready"] is False for k,x in p["releasePhases"].items() if k != "sourceIntegration"))
    ck("sourceOnlyIntegration", p["releasePhases"]["sourceIntegration"]["readyForReview"] is True and p["releasePhases"]["sourceIntegration"]["automaticMerge"] is False)
    ck("noSideEffects", all(value is False for value in p["actions"].values()))
    ck("crownStop", p["crownStatus"] == "STOP")
    si = samsung.checks(source, root)
    ck("samsungSourceChecks", not si)
    orchestra = inspect_orchestra(root=root)
    ck("orchestraStillQuarantined", not orchestra["failures"] and orchestra["activeAgents"] == 0)
    sql = sql_smoke(root=root)
    ck("sqlInMemoryConstraints", sql["negativeCasesRejected"] == 4 and sql["productionDatabaseTouched"] is False)
    rows = rows_override if rows_override is not None else samsung.assess(source, run_runner=runner)
    matrix_receipt = inventory(rows, runner=runner)
    ck("everySlotIntegrityChecked", matrix_receipt["evaluated"] == 500 and not matrix_receipt["errors"])
    failed = sorted(k for k,value in checks.items() if not value)
    return {
        "schema": "luhmOs.cast500ExitDevelopmentAudit.v1",
        "sourceRef": os.getenv("LUHM_SOURCE_REF", "LOCAL_AUDIT_UNBOUND"),
        "sourceChecks": len(checks),
        "sourcePassed": len(checks)-len(failed),
        "sourceErrors": failed,
        "slotInventory": matrix_receipt,
        "sourceVerdict": "GREEN_MATRIX_INTEGRITY_ONLY" if not failed else "RED_SOURCE",
        "productionGo": False,
        "castAuthorized": False,
        "publicReleaseAuthorized": False,
        "promotionBlockedBy": sorted(p["promotionProof"].keys()),
        "deviceInstallVerified": False,
        "castDispatchRun": False,
        "crown": "STOP",
    }

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--runner", action="store_true")
    ap.add_argument("--assert-production-ready", action="store_true")
    ap.add_argument("--report",type=Path)
    args=ap.parse_args()
    result=audit(runner=args.runner)
    output=json.dumps(result, sort_keys=True, indent=2)+"\n"
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(output,encoding="utf8")
    print(output,end="")
    # A source audit cannot mint production proof, even on 500 valid rows.
    return 1 if result["sourceErrors"] or args.assert_production_ready else 0

if __name__ == "__main__":
    raise SystemExit(main())
