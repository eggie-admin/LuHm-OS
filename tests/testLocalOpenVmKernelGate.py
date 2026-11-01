#!/usr/bin/env python3
"""Local open VM source gate, provenance, denial and privacy regression fixtures."""
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("localOpenVmKernelGate",
                                              ROOT / "tools/localOpenVmKernelGate.py")
assert spec and spec.loader
vm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vm)
SHA = "6e93bc0a84ba2d8ae1cb5d026484fdcdd4cdb801"
BASE = dict(source_ref=SHA, host_arch="x86_64",
            host_memory_mib=8192, host_cpu_count=4, host_kvm_access=False)


class TestLocalOpenVmKernel(unittest.TestCase):
    def test_4x4_source_and_zero_new_proprietary_remote_compute(self):
        s = vm.source_audit()
        self.assertEqual(s["state"], "SOURCE_PLAN_ONLY", s["issues"])
        self.assertEqual(s["evidenceCells"], 16)
        self.assertFalse(s["kernelModified"])
        self.assertFalse(s["guestStarted"])
        self.assertFalse(s["liveHostProbePerformed"])
        self.assertEqual(s["cloudApiCalls"], 0)
        self.assertFalse(s["proprietaryRemoteComputeRequired"])

    def test_local_guest_is_private_and_unprivileged_by_default(self):
        s = vm.plan_guest(**BASE)
        self.assertEqual(s["acceleratorCandidate"], "QEMU_TCG_SLOW_OR_NO_GUEST")
        self.assertEqual(s["vcpu"], 2)
        self.assertEqual(s["memoryMiB"], 2048)
        self.assertEqual(s["diskGiB"], 16)
        self.assertEqual(s["guestConfiguration"]["network"], "none")
        self.assertEqual(s["guestConfiguration"]["hostPorts"], [])
        self.assertEqual(s["guestConfiguration"]["libvirtUriCandidate"], "qemu:///session")
        self.assertIsNone(s["guestConfiguration"]["remoteCloudProvider"])
        self.assertTrue(s["hostCapabilityClaimUntrusted"])
        self.assertFalse(s["realGuestBootProven"])
        self.assertFalse(s["sourceExecuted"])

    def test_kvm_claim_never_becomes_actual_hardware_proof(self):
        guest = vm.plan_guest(**{**BASE, "host_kvm_access": True})
        self.assertEqual(guest["acceleratorCandidate"],
                         "KVM_IF_HOST_PERMISSION_VERIFIED")
        self.assertFalse(guest["realGuestBootProven"])
        self.assertTrue(guest["ownerApprovalRequired"])

    def test_minimum_host_ram_budget_and_exact_numeric_types(self):
        updates = (
            {"host_memory_mib": 2200},
            {"host_memory_mib": -1},
            {"host_memory_mib": True},
            {"host_cpu_count": 1},
            {"host_cpu_count": 0},
            {"host_cpu_count": 2.5},
            {"guest_memory_mib": 8193},
            {"guest_memory_mib": 0},
            {"guest_memory_mib": 1024, "guest_disk_gib": 7},
            {"guest_vcpus": 5},
            {"source_ref": "main"},
            {"source_ref": "A" * 40},
            {"host_arch": "windows"},
            {"host_arch": "armv7"},
            {"host_kvm_access": "yes"},
            {"host_kvm_access": 1},
        )
        for update in updates:
            with self.subTest(update=update), self.assertRaises(ValueError):
                vm.plan_guest(**{**BASE, **update})

    def test_probe_is_explicit_and_never_automatically_opened(self):
        with self.assertRaisesRegex(ValueError, "RED_LOCAL_VM_PROBE_NOT_AUTHORIZED"):
            vm.local_probe(explicit_user_opt_in=False)
        with self.assertRaisesRegex(ValueError, "RED_LOCAL_VM_PROBE_NOT_AUTHORIZED"):
            vm.local_probe(explicit_user_opt_in="yes")

    def test_opt_in_probe_is_nonidentifying_and_not_vm_boot(self):
        with patch.object(vm.platform, "system", return_value="Linux"), \
             patch.object(vm.platform, "machine", return_value="x86_64"), \
             patch.object(vm.platform, "release", return_value="6.12.0-test"), \
             patch.object(vm.sys, "getandroidapilevel", None, create=True), \
             patch.object(vm.Path, "exists", return_value=False), \
             patch.object(vm.shutil, "which", return_value=None):
            p = vm.local_probe(explicit_user_opt_in=True)
        self.assertEqual(p["status"], "LOCAL_CAPABILITY_OBSERVATION_UNATTESTED")
        self.assertEqual(p["kernelVersion"], "6.12.0-test")
        self.assertFalse(p["devKvmExists"])
        self.assertFalse(p["qemuBinaryFound"])
        self.assertIsNone(p["deviceVmSupported"])
        self.assertEqual(p["cloudCalls"], 0)
        self.assertEqual(p["kernelWrites"], 0)
        self.assertNotIn("hostname", p)
        self.assertNotIn("serial", p)
        self.assertFalse(p["hypervisorBootEvidence"])

    def test_android_like_client_not_assumed_linux_vm_host(self):
        with patch.object(vm.platform, "system", return_value="Linux"), \
             patch.object(vm.platform, "machine", return_value="aarch64"), \
             patch.object(vm.sys, "getandroidapilevel", lambda: 35, create=True):
            p = vm.local_probe(explicit_user_opt_in=True)
        self.assertEqual(p["status"], "NO_LINUX_VM_HOST_PROBE_ON_THIS_PLATFORM")
        self.assertIsNone(p["deviceVmSupported"])
        self.assertFalse(p["linuxHost"])

    def test_fake_host_green_and_cloud_sprawl_are_red(self):
        original = vm._load

        def changed(path):
            x = original(path)
            if path == vm.POLICY:
                x = copy.deepcopy(x)
                x["default"]["remoteInference"] = "OPENAI_PAID_CLOUD"
                x["default"]["biosFlash"] = "AUTO"
                x["promotion"]["noRealVmBootProven"] = False
                x["matrix4x4"][0]["cells"][0]["proofTrusted"] = True
                x["dependencies"]["noImplicitCloudFallback"] = False
            return x

        with patch.object(vm, "_load", side_effect=changed):
            s = vm.source_audit()
        for key in ("RED_LOCAL_VM_REMOTE_DEFAULT", "RED_LOCAL_VM_KERNEL_NO_MUTATION",
                    "RED_LOCAL_VM_FAKE_PROOF", "RED_LOCAL_VM_VENDOR_POLICY",
                    "RED_LOCAL_VM_RUNTIME_CLAIM"):
            self.assertIn(key, s["issues"])


if __name__ == "__main__":
    unittest.main()
