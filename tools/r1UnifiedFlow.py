#!/usr/bin/env python3
"""R1: one bounded, zero-network source flow over the existing escalation/Crown code.
No installer, root, GRUB editor, firmware mutator, network scanner, agent or cloud calls.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

from tools.crownEscalationMatrix import assess as crown_assess
from tools.escalationKernel import plan as escalate_plan
from tools.mediaStudioAudit import audit as media_policy_audit
from tools.mediaStudioAudit import inspect_sources as media_source_audit
from tools.rootlessCast36Audit import verify as rootless_policy_audit
from tools.sinisterSpider import POLICY as SPIDER_POLICY, spider as run_spider

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/r1UnifiedFlowV1.json"
SHA = re.compile(r"^[0-9a-f]{40}$")
DEPTHS = (0,2,4,8,16,32,64,128,256)
BEATS = ("hear","resolve","act","verify")


def depth_value(text):
    if not isinstance(text, str) or not re.fullmatch(r"(?:0x[0-9a-fA-F]+|[0-9]+)", text):
        raise ValueError("INVALID_DEPTH")
    value = int(text, 16) if text.lower().startswith("0x") else int(text)
    if value not in DEPTHS:
        raise ValueError("DEPTH_NOT_ALLOWED")
    return value


def sample_256(doc):
    """A deterministic address sample. It never executes the 2,048 conceptual cases."""
    axes=doc["coverage"]["axes"]
    widths=tuple(len(a["values"]) for a in axes)
    if widths!=(4,4,8,16):raise ValueError("MATRIX_AXES")
    # Every dimension participates, including all 16 evidence labels.
    points=tuple((i%4,(i//4)%4,(i//16)%8,8*(i//128)+(i//16)%8) for i in range(256))
    if len(points)!=len(set(points)) or any({x[d] for x in points}!=set(range(widths[d])) for d in range(4)):
        raise ValueError("MATRIX_SAMPLE_COLLISION")
    return points


def validate_policy(doc):
    problems=[]
    def need(ok,reason):
        if not ok:problems.append(reason)
    need(doc.get("schema")=="luhmOs.r1UnifiedFlow.v1" and doc.get("state")=="PROPOSED_SOURCE_ONLY","R1_SCHEMA")
    need(doc.get("authority")=="Professor" and doc.get("crown")=="STOP" and doc.get("sourceRepo")=="eggie-admin/LuHm-OS","R1_AUTHORITY")
    flow=doc.get("flow",{})
    need(flow.get("units")==1 and flow.get("beats")==list(BEATS) and
         flow.get("entrypoint")=="tools/r1UnifiedFlow.py" and flow.get("unattendedProtectedMutations") is False and
         flow.get("sideEffectMode")=="READ_ONLY_AND_OPTIONAL_RECEIPT_FILE" and
         flow.get("maxRuntimeSideEffects")==0,"R1_ONE_UNIT")
    canonical=doc.get("existingCanon",{})
    required={
      "escalation":"doctrine/escalationKernelV1.json",
      "resolver":"tools/escalationKernel.py",
      "crownMatrix":"doctrine/crownEscalationMatrixV1.json",
      "crownCode":"tools/crownEscalationMatrix.py",
      "rootless":"doctrine/rootlessCast36V1.json",
      "rootlessAudit":"tools/rootlessCast36Audit.py",
      "media":"doctrine/mediaStudioFourByFourV1.json",
      "mediaAudit":"tools/mediaStudioAudit.py",
      "androidWorkflow":".github/workflows/samsung-lite-signed-beta.yml",
      "unreal":"doctrine/unrealFinalFormBridgeV1.json",
      "rootlessLauncher":"tools/termuxRootlessCast.sh"}
    need(all(canonical.get(k)==v for k,v in required.items()),"R1_CANON_REUSE")
    coverage=doc.get("coverage",{})
    axes=coverage.get("axes",[])
    need([len(a.get("values",[])) for a in axes]==[4,4,8,16] and
         [a.get("id") for a in axes]==["layer","execution","beat","evidence"],"R1_4X4X8X16")
    need(coverage.get("conceptualMatrixCells")==2048 and coverage.get("sourceSamplesPlanned")==256 and
         coverage.get("fullMatrixExecuted")==0 and coverage.get("physicalTestsExecuted")==0 and
         coverage.get("additionalAuditRunsExecuted")==0,"R1_FALSE_PROOF")
    depths=coverage.get("depths",[])
    need([row.get("decimal") for row in depths]==list(DEPTHS) and
         [row.get("hex") for row in depths]==[f"0x{x:02x}" for x in DEPTHS[:-1]]+["0x100"],"R1_HEX_LADDER")
    need(coverage.get("maxAutomaticSourceDepth")==16 and coverage.get("evidencePromotionFromDepthAlone") is False,"R1_DEPTH_PERMISSIONS")
    arch=doc.get("architecture",{})
    need(arch.get("grub")=="LINUX_ONLY_OPTIONAL_BOOT_PATH_EXISTENCE_NOT_CONFIG_WRITE" and
         arch.get("android")=="UNROOTED_APP_SANDBOX_NO_GRUB_OR_BOOTLOADER_ACCESS" and
         arch.get("sql")=="SQLITE_USERSPACE_NEVER_FIRMWARE" and
         arch.get("python")=="STANDARD_LIBRARY_ONLY","R1_HOST_BOUNDARIES")
    reduction=doc.get("reduction",{})
    for k in ("newWorkflowFilesAllowed","newPackageDependenciesAllowed","newKernelScriptsAllowed",
              "newRootServiceAllowed","newAiAgentsAllowed","duplicateAuthoritiesAllowed"):
        need(reduction.get(k) is False,"R1_VENDOR_"+k)
    for k in ("delegateToExistingEscalationKernel","delegateToExistingCrown336","delegateToExistingRootless36",
              "delegateToExistingMediaFourByFour"):
        need(reduction.get(k) is True,"R1_DELEGATION_"+k)
    guard=doc.get("guardrails",{})
    for k in ("autoMerge","autoDeploy","autoSign","autoPublish","autoInstall","autoModifyFirmware",
              "autoModifyKernel","autoEditGrub","autoReboot","autoRoot","autoChangeSqlFirmware","autoInvokeAgent",
              "autoCallProvider","autoRemotePing","autoConnectPrivateDrive"):
        need(guard.get(k) is False,"R1_UNSAFE_"+k)
    need(type(guard.get("autoSpendUsd")) is int and guard.get("autoSpendUsd")==0 and
         guard.get("ownerApproval")=="UNSATISFIED" and guard.get("unknownDeviceStatus")=="UNVERIFIED","R1_CROWN_HOLD")
    if not problems:
        try:sample_256(doc)
        except (ValueError,KeyError,TypeError):problems.append("R1_SAMPLES")
    return sorted(set(problems))


def inspect_host(system=None, termux=None, filesystem=None):
    """Optional read-only OS metadata; never read GRUB content, boot config or machine identifiers."""
    system=platform.system() if system is None else system
    termux=("/com.termux/" in (os.environ.get("PREFIX","") or "") or
            "/com.termux/" in sys.prefix) if termux is None else termux
    filesystem=Path if filesystem is None else filesystem
    linux=system=="Linux"
    return {
      "hostClass":"ANDROID_TERMUX_USERSPACE" if termux and linux else
                  "LINUX_READONLY_HOST" if linux else "OTHER_USERSPACE",
      "osFamily":system,
      "kernelMetadataInspected":False,
      "androidBootloaderTouched":False,
      "grubApplicable":bool(linux and not termux),
      "grubConfigFilePresent":bool(linux and not termux and filesystem("/etc/default/grub").is_file()),
      "grubDirectoryPresent":bool(linux and not termux and filesystem("/boot/grub").is_dir()),
      "efiDirectoryPresent":bool(linux and not termux and filesystem("/sys/firmware/efi").is_dir()),
      "privilegedMutationPerformed":False,
      "hardwareProven":False,
    }


def source_truth_identity(truth):
    """Fail closed on the authoritative repository and source-law identity."""
    return (truth.get("schema")=="luhmOs.currentSourceTruth.v3" and
            truth.get("canonicalRepository")=="eggie-admin/LuHm-OS" and
            truth.get("authority")=="Professor" and
            truth.get("sourceLaw")=="AI proposes. Policy authorizes. CI proves. Human promotes.")


def source_truth_crown_stop(truth):
    """All independent promotion flags must deny release, not merely one."""
    lane=truth.get("workingDoctrineLane",{})
    return (truth.get("crownStatus")=="STOP" and
            truth.get("promotion") is False and
            truth.get("publicationAuthority") is False and
            truth.get("releaseAuthority") is False and
            truth.get("productionSigningAuthority") is False and
            isinstance(lane,dict) and
            lane.get("status")=="PROPOSED_ONLY" and
            lane.get("crownStatus")=="STOP" and
            lane.get("currentMutationPromotion") is False and
            lane.get("professorPromotionRequired") is True)


def source_checks(root,sha,crown):
    """Sixteen bounded source inspections, not firmware/device tests."""
    read=lambda path: json.loads((root/path).read_text(encoding="utf-8"))
    truth=read("doctrine/currentSourceTruthV3.json")
    ek=read("doctrine/escalationKernelV1.json")
    rootless=read("doctrine/rootlessCast36V1.json")
    media=read("doctrine/mediaStudioFourByFourV1.json")
    unreal=read("doctrine/unrealFinalFormBridgeV1.json")
    checks={
      "source/canonicalRepo":source_truth_identity(truth),
      "source/exactShaShape":bool(SHA.fullmatch(sha)),
      "source/rootlessLauncher":(root/"tools/termuxRootlessCast.sh").is_file(),
      "source/noNewWorkflow":(root/".github/workflows/free-first-workspace-daily.yml").is_file(),
      "policy/escalationTiers":[x.get("tier") for x in ek.get("tierSemantics",[])]==[0,1,2,3],
      "policy/fourBeats":ek.get("fourByFourModel",{}).get("horizontalBeats")==list(BEATS),
      "policy/samsungRootless":rootless_policy_audit(rootless)==[],
      "policy/mediaVendor":media_policy_audit(media)==[] and media_source_audit()==[],
      "evidence/crown336":not crown.get("sourceErrors") and crown.get("totalEvidenceSlots")==336,
      "evidence/guardedSql":(root/"tools/rootlessCastCockpit.py").is_file() and
           "PRAGMA journal_mode=WAL" in (root/"tools/rootlessCastCockpit.py").read_text(encoding="utf-8"),
      "evidence/staticWeb":(root/"frontEnd/rootlessCockpit/index.html").is_file() and
           (root/"frontEnd/prototypes/glassWorld/src/babylon-world.js").is_file(),
      "evidence/godotCandidate":(root/"project.godot").is_file() and
           (root/".github/workflows/samsung-lite-signed-beta.yml").is_file(),
      "decision/grubNoAndroid":rootless.get("storage",{}).get("firmwareWrite") is False,
      "decision/aiNoAutoCall":rootless.get("aiBenchmarkLaw",{}).get("noProviderAutoCalls") is True,
      "decision/unrealLicenseUnproven":unreal.get("status")!="RUNTIME_GREEN",
      "decision/crownStop":source_truth_crown_stop(truth)
    }
    if len(checks)!=16:raise ValueError("R1_16_SOURCE_CHECKS_DRIFT")
    return checks


def assess(policy,sha,depth=16,root=ROOT,host=None):
    if not SHA.fullmatch(sha):raise ValueError("EXACT_SHA_REQUIRED")
    if depth not in DEPTHS:raise ValueError("DEPTH_NOT_ALLOWED")
    errors=validate_policy(policy)
    if errors:
        return {"schema":"luhmOs.r1Receipt.v1","status":"RED_SOURCE",
                "sourceRef":sha,"sourceRefIndependentlyChecked":False,
                "sourceErrors":errors,"sourceChecksExecuted":0,
                "matrixConceptualCells":2048,"matrixCasesExecuted":0,
                "releaseAuthorized":False,"crown":"STOP",
                "escalation":escalate_plan("technology",0,"blocked")["decision"]}
    crown=crown_assess(root,json.loads((root/"doctrine/crownEscalationMatrixV1.json").read_text()),sha)
    checks=source_checks(root,sha,crown)
    errors=[name for name,ok in checks.items() if not ok]
    errors.extend(crown.get("sourceErrors",[]))
    points=sample_256(policy)
    evidence=json.dumps(points,separators=(",",":"),sort_keys=True).encode("utf-8")
    status="RED_SOURCE" if errors else "AMBER_SOURCE_ONLY"
    outcome="blocked" if errors else "working"
    escalation=escalate_plan("technology",0,outcome)
    result={
        "schema":"luhmOs.r1Receipt.v1",
        "status":status,"sourceRef":sha,"sourceRefIndependentlyChecked":False,
        "auditDepthRequested":depth,"auditDepthHex":f"0x{depth:02x}" if depth<256 else "0x100",
        "automaticSourceDepthCap":16,
        "expandedDepthsStatus":"PLANNED_NOT_EXECUTED" if depth>16 else "BASE_SOURCE_ONLY",
        "unitCount":1,"beats":list(BEATS),
        "sourceChecksExecuted":len(checks),"sourceChecksPassed":sum(checks.values()),
        "sourceErrors":sorted(set(errors)),"sourceCheckStatuses":checks,
        "crownEvidenceSlotsAssessed":crown["totalEvidenceSlots"],
        "crownEvidenceCounts":{name:crown[name]["counts"] for name in ("level4x4","level8x8","level16x16")},
        "matrixConceptualCells":2048,"matrixSourceAddressesPlanned":len(points),
        "matrixSourceAddressDigestSha256":hashlib.sha256(evidence).hexdigest(),
        "matrixCasesExecuted":0,"deviceTestsExecuted":0,"aiModelBenchmarksExecuted":0,
        "firmwareWrites":0,"kernelChanges":0,"grubChanges":0,"sqlFirmwareChanges":0,
        "optionalHostInspection":host,
        "escalation":{"domain":"technology","currentTier":0,"nextTier":escalation["nextTier"],
                      "decision":escalation["decision"],"automaticTierTransition":False},
        "ownerApproval":False,"releaseAuthorized":False,"crown":"STOP"}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-ref",required=True)
    parser.add_argument("--depth",default="0x10",help="One of 0,2,4,8,16,32,64,128,256 or hex")
    parser.add_argument("--inspect-host",action="store_true",help="Read only coarse OS/EFI/GRUB path presence")
    parser.add_argument("--spider",action="store_true",help="Bounded read-only source-graph reconciliation")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:depth=depth_value(args.depth)
    except ValueError as exc:parser.error(str(exc))
    if not SHA.fullmatch(args.source_ref):raise SystemExit("EXACT_SHA_REQUIRED")
    head=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True,check=False)
    if head.returncode or head.stdout.strip()!=args.source_ref:raise SystemExit("EXACT_SOURCE_MISMATCH")
    policy=json.loads(POLICY.read_text(encoding="utf-8"))
    result=assess(policy,args.source_ref,depth=depth,host=inspect_host() if args.inspect_host else None)
    result["sourceRefIndependentlyChecked"]=True
    result["policySha256"]=hashlib.sha256(POLICY.read_bytes()).hexdigest()
    if args.spider:
        spider_policy=json.loads(SPIDER_POLICY.read_text(encoding="utf-8"))
        graph=run_spider(ROOT,spider_policy)
        result["localSourceSpider"]=graph
        if graph["errors"]:
            result["sourceErrors"]=sorted(set(result.get("sourceErrors",[])+graph["errors"]))
            result["status"]="RED_SOURCE"
    payload=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.output:
        if args.output.is_symlink():raise SystemExit("REFUSE_SYMLINK_RECEIPT")
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    print(json.dumps({key:result[key] for key in ("sourceRef","status","auditDepthHex","sourceChecksExecuted",
       "sourceChecksPassed","crownEvidenceSlotsAssessed","matrixConceptualCells","matrixCasesExecuted","crown")},indent=2))
    return 0 if result["status"]=="AMBER_SOURCE_ONLY" else 2

if __name__=="__main__":raise SystemExit(main())
