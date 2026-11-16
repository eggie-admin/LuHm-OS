#!/usr/bin/env python3
"""Read-only MCP status/plan for machine-readable LuHm Forge/VM alignment."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def register_lean_vm_forge(server: Any, *, root: Path, annotations: Any) -> None:
    path = root / "tools" / "leanVmForgeAudit.py"
    if not path.is_file():
        raise RuntimeError("RED_VM_FORGE_AUDITOR_MISSING")
    spec = importlib.util.spec_from_file_location("leanVmForgeAudit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_VM_FORGE_AUDITOR_IMPORT")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    @server.tool(
        name="luhm_forge_alignment_status",
        title="LuHm source/Netplan/VM/SQL/proxy licensing audit",
        description=(
            "Read and validate repository Canon, real Render source, SQL DDL "
            "in temporary in-memory SQLite, uninstalled Netplan example, "
            "proxy freeze, root GPL license and free-tier provider descriptions. "
            "No network, VM, Cloudflare, host config or paid service actions."
        ),
        annotations=annotations,
    )
    def luhm_forge_alignment_status() -> dict[str, Any]:
        return module.audit()

    @server.tool(
        name="luhm_forge_vm_plan",
        title="LuHm provider-scoped free-tier VM hold plan",
        description=(
            "Accept bounded taskId, exact sourceRef, scopeId, vmId and one provider "
            "(oracle/google/azure/aws). Returns known rights/identity/Netplan/network "
            "proof blockers. Never enrolls, provisions, deploys or pays for VMs."
        ),
        annotations=annotations,
    )
    def luhm_forge_vm_plan(
        taskId: str, sourceRef: str, scopeId: str, vmId: str, provider: str,
    ) -> dict[str, Any]:
        return module.plan_vm(taskId, sourceRef, scopeId, vmId, provider)
