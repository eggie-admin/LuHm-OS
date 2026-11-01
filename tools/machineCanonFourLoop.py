#!/usr/bin/env python3
"""Bounded 4x4 Canon machine audit tick. No privileged operations or CAST."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    from .escalationKernel import plan
except ImportError:
    from escalationKernel import plan

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/machineCanonFourLoopV1.json"
BEATS = ("inventory", "scope", "verify", "propose")
LANES = ("machine", "service", "studio", "interface")
# Literal source-only commands, never received from a prompt, JSON or network.
CHECKS = (
    ("machine", (
        ("machineInventory", (sys.executable, "tools/machineToHumanWizard.py", "--json")),
        ("headlessContract", (sys.executable, "tools/unifiedMachineBaseAudit.py", "--profile", "linuxHeadless", "--source-ref", "@HEAD")),
        ("sourceArchitecture", (sys.executable, "tools/systemArchitectureAudit.py", "--self-test")),
        ("escalationCanon", (sys.executable, "tools/escalationKernelAudit.py")),
    )),
    ("service", (
        ("networkRouting", (sys.executable, "tools/networkSpineAudit.py")),
        ("certbotMetadata", (sys.executable, "tools/certbotWorkspaceSymlinkAudit.py")),
        ("pkiBoundary", (sys.executable, "tools/belldandyPkiCorporateSecretaryAudit.py")),
        ("storageLaw", (sys.executable, "tools/storageTopologyAudit.py")),
    )),
    ("studio", (
        ("garageContract", (sys.executable, "tools/professorGarageContractAudit.py")),
        ("studioContract", (sys.executable, "tools/unifiedMachineBaseAudit.py", "--profile", "linuxStudio", "--source-ref", "@HEAD")),
        ("desktopSafety", (sys.executable, "tools/desktopPythonJsAudit.py")),
        ("machineRegression", (sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "testUnifiedMachineBaseAudit.py")),
    )),
    ("interface", (
        ("staticBrowser", ("node", "frontEnd/tools/check.mjs")),
        ("piDesktopContract", (sys.executable, "tools/unifiedMachineBaseAudit.py", "--profile", "raspberryPiDesktop", "--source-ref", "@HEAD")),
        ("androidBoundary", (sys.executable, "tools/androidWeb3CockpitAudit.py")),
        ("androidThinClient", (sys.executable, "tools/unifiedMachineBaseAudit.py", "--profile", "androidClient", "--source-ref", "@HEAD")),
    )),
)
EXACT_SHA = re.compile(r"^[0-9a-f]{40}$")


def canonical_receipt() -> tuple[str, dict]:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if policy.get("schema") != "luhmOs.machineCanonFourLoop.v1":
        raise ValueError("machine loop schema drift")
    if policy.get("status") != "DRAFT_SOURCE_CHECKLIST_ONLY":
        raise ValueError("machine loop may not self-promote")
    if policy.get("taskId") != "machineCanonFourLoopSourceAudit" or policy.get("scopeId") != "machineLayerFourByFour":
        raise ValueError("task/scope drift")
    if policy.get("sourceLaw") != "AI proposes. Policy authorizes. CI proves. Human promotes.":
        raise ValueError("authority law drift")
    if policy.get("fourBeats") != list(BEATS) or policy.get("lanes") != list(LANES):
        raise ValueError("four-by-four lane shape drift")
    if policy.get("cells") != 16 or policy.get("hexadecimal") != "logicalLabelsOnly":
        raise ValueError("hex labels incorrectly treated as registers")
    if policy.get("retryCeilingPerLane") != 3 or policy.get("tierRange") != [0, 1, 2, 3]:
        raise ValueError("retry/tier drift")
    if policy.get("escalation") != "blockedAdvancesOneTierWithoutExpandingAuthority":
        raise ValueError("escalation authority drift")
    expected = {name: [check for check, _ in rows] for name, rows in CHECKS}
    if policy.get("checks") != expected:
        raise ValueError("allowlisted source check plan changed")
    approvals = policy.get("approvals", {})
    if approvals.get("sourceAudit") is not True or approvals.get("proposeReversibleChanges") is not True:
        raise ValueError("approved source scope missing")
    for key in ("autoBuild", "mergeMain", "productionDeploy", "signAndroid", "partitionDisk",
                "flashFirmware", "certbotIssue", "productionSqlMigration", "cast"):
        if approvals.get(key) is not False:
            raise ValueError("forbidden authority: " + key)
    if approvals.get("crownStatus") != "STOP":
        raise ValueError("crown authority violation")
    paths = [policy["canonicalSource"], *policy["sourceRefs"], "doctrine/machineCanonFourLoopV1.json"]
    if len(paths) != len(set(paths)):
        raise ValueError("duplicate canon paths")
    digests = {}
    for rel in paths:
        if not re.fullmatch(r"doctrine/[A-Za-z0-9_.-]+\.json", rel):
            raise ValueError("unapproved Canon path")
        value = ROOT / rel
        if not value.is_file() or value.is_symlink():
            raise ValueError("missing/aliased Canon source: " + rel)
        raw = value.read_bytes()
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("invalid Canon document: " + rel)
        digests[rel] = hashlib.sha256(raw).hexdigest()
    truth = json.loads((ROOT / "doctrine/currentSourceTruthV3.json").read_text(encoding="utf-8"))
    if truth.get("promotion") is not False:
        raise ValueError("production truth is not in proposed hold")
    base = json.loads((ROOT / "doctrine/unifiedMachineBaseV1.json").read_text(encoding="utf-8"))
    if base.get("status") != "PROPOSED_SOURCE_ONLY" or base.get("authority", {}).get("crownStatus") != "STOP":
        raise ValueError("unified machine source boundary drift")
    deployment = json.loads((ROOT / "doctrine/agentSystemDeploymentV1.json").read_text(encoding="utf-8"))
    if deployment.get("requiredAgentCount") != 15:
        raise ValueError("agent roster count drift")
    quarantine = json.loads((ROOT / "doctrine/companyWideOperationalQuarantineV1.json").read_text(encoding="utf-8"))
    if quarantine.get("state") != "QUARANTINED" or quarantine.get("activeTaskWorkersAllowed") is not False:
        raise ValueError("agent quarantine unexpectedly lifted")
    fingerprint = hashlib.sha256(json.dumps(digests, sort_keys=True).encode("ascii")).hexdigest()
    return fingerprint, digests


def source_head() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True,
                            check=True, timeout=10)
    sha = result.stdout.strip()
    if not EXACT_SHA.fullmatch(sha):
        raise ValueError("invalid Git source SHA")
    return sha


def execute(command: tuple[str, ...], timeout: int = 90) -> dict:
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout,
                                check=False)
        digest = hashlib.sha256((result.stdout + "\n" + result.stderr).encode("utf-8")).hexdigest()
        return {"status": "PASS" if result.returncode == 0 else "FAIL",
                "exitCode": result.returncode, "outputSha256": digest}
    except subprocess.TimeoutExpired:
        return {"status": "FAIL", "failureKind": "timeout"}
    except OSError:
        return {"status": "FAIL", "failureKind": "missingExecutable"}


def tick(source_ref: str, canon_hash: str, previous: dict, runner, source_now) -> dict:
    """One finite pass. Persist retry state externally, never treat it as proof."""
    if not EXACT_SHA.fullmatch(source_ref) or not re.fullmatch(r"[0-9a-f]{64}", canon_hash):
        raise ValueError("exact source and Canon fingerprint required")
    if not isinstance(previous, dict):
        raise ValueError("invalid prior state")
    if previous.get("sourceRef") != source_ref or previous.get("canonFingerprint") != canon_hash:
        previous = {}
    prior_lanes = previous.get("lanes", [])
    if not isinstance(prior_lanes, list):
        raise ValueError("invalid lane state")
    prior = {row["lane"]: row for row in prior_lanes if isinstance(row, dict) and row.get("lane") in LANES}
    if len(prior) != len([x for x in prior_lanes if isinstance(x, dict) and x.get("lane") in LANES]):
        raise ValueError("duplicate lane state")
    rows = []
    observed_change = False
    for lane_index, (lane_name, checks) in enumerate(CHECKS):
        prior_row = prior.get(lane_name, {})
        tier, failures = prior_row.get("tier", 0), prior_row.get("failures", 0)
        if type(tier) is not int or type(failures) is not int or not 0 <= tier <= 3 or not 0 <= failures <= 3:
            raise ValueError("invalid bounded retry state")
        lane = {"lane": lane_name, "tier": tier, "failures": failures, "checks": []}
        rows.append(lane)
        if source_now() != source_ref:
            observed_change = True
            lane.update(status="SOURCE_CHANGED", nextAction="restartWithNewCommit")
            break
        if failures >= 3:
            lane.update(status="BLOCKED", nextAction="exactSourceBoundedRepairRequired")
            continue
        for beat_index, (check_name, command) in enumerate(checks):
            if source_now() != source_ref:
                observed_change = True
                lane.update(status="SOURCE_CHANGED", nextAction="restartWithNewCommit")
                break
            safe_command = tuple(source_ref if item == "@HEAD" else item for item in command)
            result = runner(safe_command)
            if not isinstance(result, dict) or result.get("status") not in ("PASS", "FAIL", "UNKNOWN"):
                raise ValueError("invalid machine audit runner receipt")
            check = {"id": check_name, "beat": BEATS[beat_index],
                     "cell": f"0x{lane_index * 4 + beat_index:02x}", **result}
            lane["checks"].append(check)
            if result["status"] != "PASS":
                failures += 1
                outcome = "blocked" if result["status"] == "FAIL" else "unknown"
                escalation = plan("technology", tier, outcome)
                tier = escalation["nextTier"]
                lane.update(tier=tier, failures=failures, status="RED" if outcome == "blocked" else "UNKNOWN",
                            nextAction="exactSourceBoundedRepairRequired" if failures >= 3 else
                                       "recheckAfterDiagnosis" if outcome == "blocked" else "holdAndDiagnose")
                break  # Do not tick the rest of this lane GREEN.
        else:
            lane.update(tier=plan("technology", tier, "green")["nextTier"], failures=0,
                        status="GREEN_SOURCE_ONLY", nextAction="sourceChecksComplete")
        if observed_change:
            break
        continue  # A failure in one lane never skips the next independent lane.
    stable = not observed_change and source_now() == source_ref
    all_green = stable and len(rows) == 4 and all(
        row["status"] == "GREEN_SOURCE_ONLY" and len(row["checks"]) == 4 for row in rows
    )
    return {
        "schema": "luhmOs.machineCanonFourLoopReceipt.v1", "taskId": "machineCanonFourLoopSourceAudit",
        "scopeId": "machineLayerFourByFour", "sourceRef": source_ref, "canonFingerprint": canon_hash,
        "lanes": rows, "checkedCells": sum(len(row["checks"]) for row in rows),
        "totalCells": 16, "sourceStable": stable,
        "sourceStatus": "GREEN_SOURCE_CHECKS_ONLY" if all_green else "AMBER_OR_RED_SOURCE",
        "physicalDeviceProof": False, "actualKernelBuild": False,
        "productionMutationAuthorized": False, "castAuthorized": False,
        "crownStatus": "STOP",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-ref", required=True, help="exact lower-case 40-char Git SHA")
    parser.add_argument("--state", type=Path, help="optional previous same-source retry state")
    parser.add_argument("--output", type=Path, help="optional output receipt path, outside source checkout in CI")
    args = parser.parse_args()
    try:
        source = source_head()
        if source != args.source_ref or not EXACT_SHA.fullmatch(args.source_ref):
            raise ValueError("source checkout/expected SHA mismatch")
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=normal"],
                               cwd=ROOT, text=True, capture_output=True, check=True, timeout=10)
        if dirty.stdout.strip():
            raise ValueError("source checkout not clean")
        fingerprint, digests = canonical_receipt()
        previous = json.loads(args.state.read_text(encoding="utf-8")) if args.state and args.state.exists() else {}
        receipt = tick(source, fingerprint, previous, execute, source_head)
        receipt["canonSha256"] = digests
        payload = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload, encoding="utf-8")
        print(payload, end="")
        return 0 if receipt["sourceStatus"] == "GREEN_SOURCE_CHECKS_ONLY" else 1
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as err:
        print(json.dumps({"status": "RED_MACHINE_CANON_LOOP", "failureKind": type(err).__name__,
                          "sourceAuthorized": False, "castAuthorized": False, "crownStatus": "STOP"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
