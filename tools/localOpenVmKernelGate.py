#!/usr/bin/env python3
"""LuHm open-source-first local kernel/VM gate.

No kernel writes, firmware, provider API, VM launch, package installation,
subprocess execution or remote I/O. Optional --local-probe checks *this*
machine's non-identifying capabilities, never the user's Samsung remotely.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/localOpenVmKernelProfileV1.json"
QUARANTINE = ROOT / "doctrine/companyWideOperationalQuarantineV1.json"
TRUTH = ROOT / "doctrine/currentSourceTruthV3.json"
LANES = ("hostKernel", "isolatedGuest", "offlineStudio", "optionalRemote")
PHASES = ("source", "capability", "isolatedFixture", "runtimeOwnerProof")
HEX_SHA = re.compile(r"[0-9a-f]{40}\Z")
ARCH = ("x86_64", "aarch64")
OFF = ("network", "remoteInference", "remoteRendering", "providerPaidCompute",
       "vendorTelemetry", "usbBluetoothPassthrough", "gpuPassthrough",
       "remoteDesktop", "sshPortForward")
REQUIRED_EXCEPTIONS = ("github", "chatgpt", "render")


def _load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf8"))
    if type(obj) is not dict:
        raise ValueError("RED_LOCAL_VM_JSON")
    return obj


def source_audit() -> dict[str, Any]:
    d = _load(POLICY)
    q = _load(QUARANTINE)
    truth = _load(TRUTH)
    issues = []
    if d.get("schema") != "luhmOs.localOpenVmKernelProfile.v1" or d.get(
            "canonicalRepo") != "eggie-admin/LuHm-OS":
        issues.append("RED_LOCAL_VM_SCHEMA")
    if d.get("status") != "SOURCE_ONLY_UNDEPLOYED" or d.get("crownStatus") != "STOP":
        issues.append("RED_LOCAL_VM_PROMOTION")
    if [x.get("id") for x in d.get("fourLanes", [])] != list(LANES) or d.get(
            "phases") != list(PHASES):
        issues.append("RED_LOCAL_VM_4X4_AXES")
    matrix = d.get("matrix4x4", [])
    count = 0
    if len(matrix) != 4:
        issues.append("RED_LOCAL_VM_4X4_ROWS")
    else:
        for i, row in enumerate(matrix):
            cells = row.get("cells", [])
            if row.get("lane") != LANES[i] or len(cells) != 4:
                issues.append("RED_LOCAL_VM_4X4_ROW")
                continue
            for j, cell in enumerate(cells):
                count += 1
                if (cell.get("id") != LANES[i] + "." + PHASES[j] or
                        cell.get("state") != "HOLD_NO_HOST_RECEIPT" or
                        any(cell.get(k) is not False for k in (
                            "proofTrusted", "hostModified", "ownerApproved"))):
                    issues.append("RED_LOCAL_VM_FAKE_PROOF")
    if count != 16:
        issues.append("RED_LOCAL_VM_4X4_COUNT")
    anchors = d.get("sourceAnchors", [])
    if (type(anchors) is not list or len(anchors) != 8 or any(
            type(p) is not str or Path(p).is_absolute() or ".." in Path(p).parts
            or not (ROOT / p).is_file() for p in anchors)):
        issues.append("RED_LOCAL_VM_ANCHORS")
    defaults = d.get("default", {})
    if (defaults.get("executionLocation") != "ON_PREMISE" or
            defaults.get("vmStrategy") != "UNPRIVILEGED_LIBVIRT_SESSION_WHEN_SUPPORTED"
            or any(defaults.get(k) != "DISABLED" if k != "network"
                   else defaults.get(k) != "OFF_BY_DEFAULT" for k in OFF)):
        issues.append("RED_LOCAL_VM_REMOTE_DEFAULT")
    if (defaults.get("kernelPatch") != "NONE" or
            defaults.get("kernelImageBuild") != "NONE" or
            defaults.get("biosFlash") != "NONE" or
            defaults.get("newCloudAccounts") != "NONE"):
        issues.append("RED_LOCAL_VM_KERNEL_NO_MUTATION")
    limits = d.get("limits", {})
    if (defaults.get("guestMemoryMiB") != 2048 or
            defaults.get("guestVcpus") != 2 or
            defaults.get("guestDiskGiB") != 16 or
            limits.get("maxGuestMemoryMiB") != 8192 or
            limits.get("maxGuestVcpus") != 4 or
            limits.get("maxGuestDiskGiB") != 64):
        issues.append("RED_LOCAL_VM_RESOURCE_BUDGET")
    kernel = d.get("kernel", {})
    for key in ("noUserKernelConfigMutation", "noSysctlChanges", "noKernelBuild",
                "noBootLoaderUpdates", "noRoot", "noSudo", "noGuestStartFromCI",
                "noPhysicalAndroidProbe", "noTrustInHypervisorAvailabilityUntilOwnerDeviceProbe"):
        if kernel.get(key) is not True:
            issues.append("RED_LOCAL_VM_KERNEL_PRIVILEGE")
            break
    vm = d.get("vm", {})
    for key in ("explicitOwnerOptInToBoot", "guestDiskImageRightsMustBeVerified",
                "sourceOnlyConfigHasNoExecutionAuthority", "noAutoOpenPorts",
                "noAutoPackageInstallation", "creationIsFutureStage"):
        if vm.get(key) is not True:
            issues.append("RED_LOCAL_VM_BOOT_AUTHORITY")
            break
    if (vm.get("networkAccessDefault") is not False or
            vm.get("hostDevicePassthroughDefault") is not False or
            vm.get("guestDiskImageRightsMustBeVerified") is not True):
        issues.append("RED_LOCAL_VM_ISOLATION")
    deps = d.get("dependencies", {})
    names = [x.get("id") for x in deps.get("existingRemoteExceptions", [])]
    if (names != list(REQUIRED_EXCEPTIONS) or
            any(x.get("proprietaryService") is not True for x in
                deps.get("existingRemoteExceptions", [])) or
            deps.get("noImplicitCloudFallback") is not True or
            deps.get("noNewPaidPlans") is not True or
            deps.get("noCredentialsInRepo") is not True):
        issues.append("RED_LOCAL_VM_VENDOR_POLICY")
    promo = d.get("promotion", {})
    if any(promo.get(k) is not True for k in (
            "originalMainUnmodified", "proposalOnly", "noReleaseMerge",
            "noRealVmBootProven", "noLocalKernelProbePerformed",
            "noAppOnSamsungProven", "noAgentActivation")):
        issues.append("RED_LOCAL_VM_RUNTIME_CLAIM")
    if (q.get("state") != "QUARANTINED" or
            q.get("activeTaskWorkersAllowed") is not False or
            truth.get("promotion") is not False):
        issues.append("RED_LOCAL_VM_CANON_AUTHORITY")
    return {
        "schema": "luhmOs.localVmKernelSourceAudit.v1",
        "state": "SOURCE_PLAN_ONLY" if not issues else "RED_SOURCE_DRIFT",
        "issues": sorted(set(issues)), "evidenceCells": count,
        "guestStarted": False, "kernelModified": False,
        "liveHostProbePerformed": False, "cloudApiCalls": 0,
        "proprietaryRemoteComputeRequired": False, "renderUsedForCompute": False,
        "androidVmVerified": False, "crownAuthority": False,
    }


def plan_guest(*, source_ref: str, host_arch: str, host_memory_mib: int,
               host_cpu_count: int, host_kvm_access: bool,
               guest_memory_mib: int = 2048, guest_vcpus: int = 2,
               guest_disk_gib: int = 16) -> dict[str, Any]:
    """CPU/RAM-bound proposed guest profile, not a QEMU launch command."""
    if type(source_ref) is not str or HEX_SHA.fullmatch(source_ref) is None:
        raise ValueError("RED_LOCAL_VM_GIT_SHA")
    if type(host_arch) is not str or host_arch not in ARCH:
        raise ValueError("RED_LOCAL_VM_ARCH")
    if type(host_kvm_access) is not bool:
        raise ValueError("RED_LOCAL_VM_KVM_PROOF_SHAPE")
    for name, value, limit in (
        ("hostMemoryMiB", host_memory_mib, 1 << 20),
        ("hostCpuCount", host_cpu_count, 256),
        ("guestMemoryMiB", guest_memory_mib, 8192),
        ("guestVcpus", guest_vcpus, 4),
        ("guestDiskGiB", guest_disk_gib, 64),
    ):
        if type(value) is not int or not 1 <= value <= limit:
            raise ValueError("RED_LOCAL_VM_RESOURCE_" + name)
    if (guest_memory_mib > max(0, host_memory_mib - 1024) or
            guest_vcpus > host_cpu_count or guest_disk_gib < 8):
        raise ValueError("RED_LOCAL_VM_RESOURCE_EXCEEDS_HOST")
    a = source_audit()
    if a["issues"]:
        return {"state": "STOP_SOURCE_DRIFT", "issues": a["issues"]}
    return {
        "schema": "luhmOs.localVmGuestPlan.v1",
        "sourceRef": source_ref, "hostArchitectureClaim": host_arch,
        "vcpu": guest_vcpus, "memoryMiB": guest_memory_mib,
        "diskGiB": guest_disk_gib,
        "acceleratorCandidate": "KVM_IF_HOST_PERMISSION_VERIFIED"
                                if host_kvm_access else "QEMU_TCG_SLOW_OR_NO_GUEST",
        "hostCapabilityClaimUntrusted": True,
        "guestConfiguration": {"network": "none", "usb": "none",
                               "bluetooth": "none", "gpuPassthrough": "none",
                               "hostPorts": [], "remoteCloudProvider": None,
                               "libvirtUriCandidate": "qemu:///session"},
        "signedOrRightsClearedGuestImageProvided": False,
        "qemuVmCreated": False, "kernelBuilt": False,
        "hostModified": False, "realGuestBootProven": False,
        "sourceExecuted": False, "ownerApprovalRequired": True,
        "state": "HOLD_IMAGE_PROVENANCE_HOST_AND_OWNER_BOOT_PROOF",
    }


def local_probe(*, explicit_user_opt_in: bool) -> dict[str, Any]:
    """Optional local-only nonidentifying probe, no VM process or sensitive IDs."""
    if explicit_user_opt_in is not True:
        raise ValueError("RED_LOCAL_VM_PROBE_NOT_AUTHORIZED")
    system = platform.system()
    arch_aliases = {"x86_64": "x86_64", "AMD64": "x86_64",
                    "aarch64": "aarch64", "arm64": "aarch64"}
    arch = arch_aliases.get(platform.machine(), "unsupported")
    android_python = callable(getattr(sys, "getandroidapilevel", None))
    if system != "Linux" or android_python:
        return {
            "status": "NO_LINUX_VM_HOST_PROBE_ON_THIS_PLATFORM",
            "linuxHost": False, "architecture": arch,
            "deviceVmSupported": None, "cloudCalls": 0,
            "kernelWrites": 0, "sensitiveMachineIdentifiers": False,
        }
    kvm_path = Path("/dev/kvm")
    name = ("qemu-system-x86_64" if arch == "x86_64"
            else "qemu-system-aarch64" if arch == "aarch64" else None)
    exists = kvm_path.exists()
    return {
        "status": "LOCAL_CAPABILITY_OBSERVATION_UNATTESTED",
        "linuxHost": True, "architecture": arch,
        "kernelVersion": re.sub(r"[^A-Za-z0-9._+\-]", "", platform.release())[:120],
        "devKvmExists": exists,
        "devKvmReadWriteAccessible": bool(exists and os.access(kvm_path, os.R_OK | os.W_OK)),
        "qemuBinaryFound": bool(name and shutil.which(name)),
        "libvirtUserSessionSocketPresent":
            Path("/run/user/" + str(os.getuid()) + "/libvirt/libvirt-sock").exists(),
        "deviceVmSupported": None, "cloudCalls": 0,
        "kernelWrites": 0, "sensitiveMachineIdentifiers": False,
        "hypervisorBootEvidence": False, "ownerValidated": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Local-first LuHm source gate; does not start a guest")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("audit")
    probe = sub.add_parser("probe")
    probe.add_argument("--local-only", action="store_true", required=True)
    guest = sub.add_parser("plan")
    guest.add_argument("--source-ref", required=True)
    guest.add_argument("--arch", choices=ARCH, required=True)
    guest.add_argument("--host-ram-mib", type=int, required=True)
    guest.add_argument("--host-cpus", type=int, required=True)
    guest.add_argument("--kvm-claimed", choices=("yes", "no"), default="no")
    opts = parser.parse_args()
    if opts.action == "audit":
        result = source_audit()
    elif opts.action == "probe":
        result = local_probe(explicit_user_opt_in=opts.local_only)
    else:
        result = plan_guest(source_ref=opts.source_ref, host_arch=opts.arch,
                            host_memory_mib=opts.host_ram_mib,
                            host_cpu_count=opts.host_cpus,
                            host_kvm_access=opts.kvm_claimed == "yes")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
