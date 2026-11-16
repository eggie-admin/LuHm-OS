"""Read-only LuHm local-first kernel/VM candidate tools for MCP cockpit."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def register_local_open_vm_kernel(server: Any, *, root: Path,
                                  annotations: Any) -> None:
    path = root / "tools" / "localOpenVmKernelGate.py"
    spec = importlib.util.spec_from_file_location("localOpenVmKernelGate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_LOCAL_VM_SOURCE_MISSING")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)

    @server.tool(
        name="luhm_local_open_vm_status",
        title="LuHm local open-source kernel and VM source status",
        description=(
            "Check four host/guest/studio/vendor lanes and no-cloud defaults "
            "against GitHub source only. Does not inspect a phone, probe a "
            "host, start KVM, connect to a VM or modify firmware."
        ),
        annotations=annotations,
    )
    def luhm_local_open_vm_status() -> dict[str, Any]:
        return gate.source_audit()

    @server.tool(
        name="luhm_local_open_vm_plan",
        title="LuHm isolated local QEMU guest sizing candidate",
        description=(
            "Size a hypothetical local guest from caller-provided CPU/RAM and "
            "an exact Git source SHA. Submitted host capabilities remain "
            "UNTRUSTED; network and passthrough stay disabled. This tool "
            "never boots a guest or purchases cloud compute."
        ),
        annotations=annotations,
    )
    def luhm_local_open_vm_plan(
        sourceRef: str, hostArch: str, hostMemoryMiB: int,
        hostCpuCount: int, kvmClaimed: bool = False,
        guestMemoryMiB: int = 2048, guestVcpus: int = 2,
        guestDiskGiB: int = 16,
    ) -> dict[str, Any]:
        return gate.plan_guest(
            source_ref=sourceRef, host_arch=hostArch,
            host_memory_mib=hostMemoryMiB,
            host_cpu_count=hostCpuCount, host_kvm_access=kvmClaimed,
            guest_memory_mib=guestMemoryMiB,
            guest_vcpus=guestVcpus, guest_disk_gib=guestDiskGiB,
        )
