#!/usr/bin/env python3
"""Read-only MCP planning tools for remote WMS/VM management."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def register_wms_vm_tools(server: Any, *, root: Path, annotations: Any) -> None:
    path = root / "host" / "remote" / "luhmWmsVmManager.py"
    if not path.is_file():
        raise RuntimeError("RED_WMS_MANAGER_MISSING")
    spec = importlib.util.spec_from_file_location("luhmWmsVmManager", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_WMS_MANAGER_IMPORT")
    manager = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(manager)

    matrix_path = root / "tools" / "headlessMachineMatrixAudit.py"
    matrix_spec = importlib.util.spec_from_file_location("headlessMachineMatrixAudit", matrix_path)
    if matrix_spec is None or matrix_spec.loader is None:
        raise RuntimeError("RED_MACHINE_MATRIX_AUDITOR_MISSING")
    matrix = importlib.util.module_from_spec(matrix_spec)
    matrix_spec.loader.exec_module(matrix)

    @server.tool(
        name="luhm_machine_matrix_status",
        title="LuHm 4x4 headless VM source audit",
        description=(
            "Audit 16 canonical headless Pi, VM, emulation/media and capture cells for "
            "source consistency. No real device, hypervisor, camera, or content is accessed."
        ),
        annotations=annotations,
    )
    def luhm_machine_matrix_status() -> dict[str, Any]:
        return matrix.audit_schema()

    @server.tool(
        name="luhm_machine_matrix_plan",
        title="LuHm R1-R4 isolated machine lane plan",
        description=(
            "For explicit taskId, full sourceRef, scopeId and one allowlisted lane "
            "(foundation, virtualization, emulationMedia, captureMotion), return "
            "a 4-gate read-only proof plan. No install, SSH, JIT, ROM/BIOS, VM, or capture action."
        ),
        annotations=annotations,
    )
    def luhm_machine_matrix_plan(
        taskId: str,
        sourceRef: str,
        scopeId: str,
        lane: str,
    ) -> dict[str, Any]:
        return matrix.plan(taskId, sourceRef, scopeId, lane)

    @server.tool(
        name="luhm_wms_status",
        title="LuHm remote WMS status",
        description=(
            "Read the candidate remote virtual-manager contract and current proof gates. "
            "Does not inspect real hosts, disclose URLs or connect to a VM."
        ),
        annotations=annotations,
    )
    def luhm_wms_status() -> dict[str, Any]:
        return manager.status()

    @server.tool(
        name="luhm_wms_plan",
        title="LuHm remote WMS machine dry-run",
        description=(
            "Plan an allowlisted remote virtual-machine operation without executing it. "
            "Requires explicit taskId, exact sourceRef, scopeId, machineId and operation. "
            "Use machineId='manager' for inventory or capabilities planning only. "
            "Never runs shell commands, logs in, creates VMs, or changes machine state."
        ),
        annotations=annotations,
    )
    def luhm_wms_plan(
        taskId: str,
        sourceRef: str,
        scopeId: str,
        machineId: str,
        operation: str = "status",
    ) -> dict[str, Any]:
        return manager.plan(taskId, sourceRef, scopeId, machineId, operation)
