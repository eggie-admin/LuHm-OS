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
