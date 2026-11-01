#!/usr/bin/env python3
"""Source-only LuHm CAST hardware seal: four axes x four guarded proof stages.

Composes prior *read-only* auditors. Does not touch firmware/kernel, probe the
host, start a VM, launch a game, write a database, or connect to any provider.
The source SHA is an untrusted caller value until a CI runner checks it
against the exact Git checkout; a source digest is not a signature.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/hardwareCastSealV1.json"
TRUTH = ROOT / "doctrine/currentSourceTruthV3.json"
QUARANTINE = ROOT / "doctrine/companyWideOperationalQuarantineV1.json"
HEADLESS = ROOT / "doctrine/headlessUniversalVmMatrixV1.json"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
LANES = ("hardwareIdentity", "kernelBoundary", "guestIsolation", "proofAndRelease")
PHASES = ("R0", "R1", "R2", "R3")
AUDITORS = (
    ("tools/localOpenVmKernelGate.py", "source_audit", "state", "SOURCE_PLAN_ONLY"),
    ("tools/machineFourArchitectureAudit.py", "source_audit", "state", "SOURCE_CANDIDATE_ONLY"),
    ("tools/hostileModForgeAudit.py", "audit", "status", "SOURCE_CANDIDATE_ONLY"),
    ("tools/brandVmSealAudit.py", "audit", "status", "SOURCE_SEALED_CANDIDATE_ONLY"),
)
BLOCKERS = (
    "OWNER_HOST_KERNEL_ARCH_BUILD_RECEIPT",
    "VERIFIED_KVM_OR_TCG_EXECUTION_RECEIPT",
    "LICENSED_GUEST_IMAGE_AND_RESOURCE_BOUND",
    "ACTUAL_ISOLATED_GUEST_BOOT_AND_ROLLBACK_RECEIPT",
    "OWNER_APPROVAL_EXACT_SCOPE_SOURCE",
)
BOUNDARIES = (
    "noFirmwareFlash", "noBiosReplacement", "noBootloaderMutation",
    "noKernelPatch", "noRootElevation", "noProprietaryRemoteComputeRequired",
    "noPaidProviderFallback", "noAutomaticLiveGuestStart", "noRemotePortExposure",
    "noUsbBluetoothGpuPassthrough", "noUnsignedImageImport",
    "noMainMerge", "noPluginDeployment", "noAgentResumption",
    "companyQuarantinePreserved",
)
SOURCES = (
    "AGENTS.md", "LICENSE",
    "doctrine/currentSourceTruthV3.json",
    "doctrine/companyWideOperationalQuarantineV1.json",
    "doctrine/machineFourArchitectureForgeV1.json",
    "doctrine/hostileModForge4x4V1.json",
    "doctrine/localOpenVmKernelProfileV1.json",
    "doctrine/headlessUniversalVmMatrixV1.json",
    "doctrine/leanVmForgeAlignmentV1.json",
    "doctrine/brandVmArchitectureSealV1.json",
    "doctrine/castTwoThreadBridgeV1.json",
)


def _read(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf8"))
    if not isinstance(obj, dict):
        raise ValueError("RED_HARDWARE_CAST_JSON")
    return obj


def _auditor(name: str, entry: str) -> dict[str, Any]:
    """Load only known source entrypoints, never names from an untrusted file."""
    if (name, entry) not in ((p, e) for p, e, _, _ in AUDITORS):
        raise ValueError("RED_HARDWARE_CAST_AUDITOR_ALLOWLIST")
    file = ROOT / name
    spec = importlib.util.spec_from_file_location(
        "luhm_hardware_" + file.stem, file)
    if spec is None or spec.loader is None:
        raise ValueError("RED_HARDWARE_CAST_IMPORT")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fn = getattr(module, entry, None)
    if not callable(fn):
        raise ValueError("RED_HARDWARE_CAST_MISSING_AUDITOR")
    report = fn()
    if not isinstance(report, dict):
        raise ValueError("RED_HARDWARE_CAST_BAD_AUDIT")
    return report


def _source_digest() -> str:
    """Hash path + length + bytes to make deterministic cross-file source receipt."""
    h = hashlib.sha256()
    for name in ("doctrine/hardwareCastSealV1.json", *SOURCES,
                 *(x[0] for x in AUDITORS)):
        path = ROOT / name
        data = path.read_bytes()
        b = name.encode("utf8")
        h.update(len(b).to_bytes(4, "big"))
        h.update(b)
        h.update(len(data).to_bytes(8, "big"))
        h.update(data)
    return h.hexdigest()


def source_seal(*, source_ref: str | None = None) -> dict[str, Any]:
    if source_ref is not None and (type(source_ref) is not str or
                                   SHA40.fullmatch(source_ref) is None):
        raise ValueError("RED_HARDWARE_CAST_SOURCE_SHA")
    p = _read(CONTRACT)
    t = _read(TRUTH)
    q = _read(QUARANTINE)
    v = _read(HEADLESS)
    issues: list[str] = []
    if (p.get("schema") != "luhmOs.hardwareCastSeal.v1"
        or p.get("source") != "eggie-admin/LuHm-OS"
        or p.get("scope") != "hardwareLayerOnlyDoNotModifyFirmware"):
        issues.append("RED_HARDWARE_CAST_CANON")
    if ([x.get("id") for x in p.get("lanes", [])] != list(LANES)
        or [x.get("id") for x in p.get("phases", [])] != list(PHASES)):
        issues.append("RED_HARDWARE_CAST_4X4_AXES")
    cells = p.get("cells", [])
    if len(cells) != 16 or len({x.get("key") for x in cells}) != 16:
        issues.append("RED_HARDWARE_CAST_CELL_COUNT")
    else:
        for i, row in enumerate(cells):
            if (row.get("key") != LANES[i // 4] + "." + PHASES[i % 4]
                or row.get("lane") != LANES[i // 4]
                or row.get("phase") != PHASES[i % 4]
                or row.get("stage") != "CANDIDATE_ONLY"
                or any(row.get(k) is not False for k in (
                    "realHostProven", "runtimeVmBootProven",
                    "firmwareRightsVerified", "ownerPromoted"))):
                issues.append("RED_HARDWARE_CAST_FALSE_PROOF")
                break
    if p.get("refCanon") != list(SOURCES) or any(
            not (ROOT / name).is_file() for name in SOURCES):
        issues.append("RED_HARDWARE_CAST_SOURCE_ANCHORS")
    auditors = p.get("sourceAuditors", [])
    if ([(x.get("path"), x.get("entry"), x.get("expectedField"),
          x.get("expectedValue")) for x in auditors] != list(AUDITORS)):
        issues.append("RED_HARDWARE_CAST_AUDIT_SOURCE_DRIFT")
    if p.get("runtimeBlockers") != list(BLOCKERS):
        issues.append("RED_HARDWARE_CAST_MISSING_RUNTIME_PROOF")
    bounds = p.get("mandatoryBoundaries", {})
    if any(bounds.get(key) is not True for key in BOUNDARIES):
        issues.append("RED_HARDWARE_CAST_PRIVILEGE")
    identity = p.get("typedIdentity", {})
    if (identity.get("hexNeverPermission") is not True
        or identity.get("canonicalNameNeverDiscarded") is not True):
        issues.append("RED_HARDWARE_CAST_HEX_AUTHORITY")
    rel = p.get("release", {})
    if (p.get("state") != "SOURCE_CANDIDATE_HARDWARE_RUNTIME_HOLD"
        or rel.get("sourceStatus") != "HOLD_UNTIL_EXACT_CI"
        or rel.get("crownStatus") != "STOP"
        or any(rel.get(k) is not False for k in (
            "liveKernelAccepted", "realVmBooted", "realSamsungInstallProven",
            "publicReleaseAllowed", "mainMerged"))):
        issues.append("RED_HARDWARE_CAST_RELEASE")
    if (q.get("state") != "QUARANTINED"
        or q.get("activeTaskWorkersAllowed") is not False
        or t.get("promotion") is not False
        or v.get("runtimeStatus") != "UNCONNECTED_SOURCE_ONLY"
        or v.get("security", {}).get("VMProvisionAllowed") is not False
        or v.get("security", {}).get("kernelMutationAllowed") is not False):
        issues.append("RED_HARDWARE_CAST_QUARANTINE")
    checks: list[dict[str, Any]] = []
    # Do not execute a path supplied by registry input.
    for path, fn, field, expected in AUDITORS:
        try:
            result = _auditor(path, fn)
            okay = (result.get(field) == expected and
                    result.get("issues") == [] and
                    result.get("crownAuthority") is False)
        except (ValueError, RuntimeError, OSError, KeyError, TypeError,
                json.JSONDecodeError):
            okay = False
        checks.append({"auditor": path, "sourceOk": okay, "runtimeProof": False})
        if not okay:
            issues.append("RED_HARDWARE_CAST_PARENT_AUDIT:" + path)
    issues = sorted(set(issues))
    return {
        "schema": "luhmOs.hardwareCastSourceSealReceipt.v1",
        "state": "SOURCE_READY_RUNTIME_HOLD" if not issues else "STOP_SOURCE_DRIFT",
        "issues": issues,
        "sourceRefClaim": source_ref,
        "sourceRefIndependentlyVerified": False,
        "sourceBundleSha256": _source_digest(),
        "sourceBundleDigestIsSignature": False,
        "fourByFourCells": len(cells),
        "sourceAuditors": checks,
        "castStages": ["sanityCheck", "audit", "ingest", "mutation",
                       "test", "apply", "continue", "deploy"],
        "sourceReadiness": not issues,
        "runtimeBlockers": list(BLOCKERS),
        "realHostKernelProven": False,
        "realKvmOrTcgGuestProven": False,
        "realHardwareFlashed": False,
        "realVmBooted": False,
        "guestNetworkOpened": False,
        "paidRemoteComputeUsed": False,
        "mainMerged": False,
        "humanApprovalRecorded": False,
        "ownerRuntimeSeal": False,
        "crownAuthority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="LuHm hardware CAST source-only seal")
    parser.add_argument("--source-ref", help="40 lowercase Git object ID from checked-out CI source")
    args = parser.parse_args()
    print(json.dumps(source_seal(source_ref=args.source_ref), indent=2))


if __name__ == "__main__":
    main()
