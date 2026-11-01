#!/usr/bin/env python3
"""Read-only 4-architecture ISA/firmware/memory/AI machine Forge MCP."""
from __future__ import annotations
import importlib.util
from pathlib import Path
from typing import Any


def register_machine_architecture_forge(server: Any, *, root: Path, annotations: Any) -> None:
    path = root / "tools/machineFourArchitectureAudit.py"
    if not path.is_file():
        raise RuntimeError("RED_MACHINE_ARCH_SOURCE_MISSING")
    spec = importlib.util.spec_from_file_location("machineFourArchitectureAudit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_MACHINE_ARCH_IMPORT")
    machine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(machine)

    @server.tool(
        name="luhm_machine_architecture_status",
        title="LuHm machine 4x4 architecture, firmware and AI source audit",
        description=(
            "Audit x86-64, Arm64, RISC-V and POWER four-by-four staged source "
            "matrix, typed hex widths, BIOS rights, synthetic IPS-only gates "
            "and existing Canon. Does not discover hardware, download OEM "
            "firmware, launch AI inference, create a VM, or flash devices."
        ),
        annotations=annotations,
    )
    def luhm_machine_architecture_status() -> dict[str, Any]:
        return machine.source_audit()

    @server.tool(
        name="luhm_machine_architecture_plan",
        title="LuHm fixed-width hex sorted machine source candidate",
        description=(
            "Create a source-only plan for one declared architecture, machine "
            "layer, decimal RAM byte count and USB/PCI bus identifier. "
            "Device presence, firmware rights, memory size and acceleration "
            "are not physically verified. Never executes an adapter."
        ),
        annotations=annotations,
    )
    def luhm_machine_architecture_plan(
        taskId: str, sourceRef: str, scopeId: str, architecture: str,
        machineLayer: str, ramBytes: int,
        busKind: str = "usbVendorId", busHex: str = "0000"
    ) -> dict[str, Any]:
        return machine.machine_plan(taskId, sourceRef, scopeId,
                                    architecture, machineLayer, ramBytes,
                                    busKind, busHex)
