#!/usr/bin/env python3
"""Read-only ChatGPT MCP planning projection for the LuHm two-lane FastAPI spine."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def register_lum_orchestration(server: Any, *, root: Path, annotations: Any) -> None:
    module_path = root / "host" / "api" / "luhmCanonOrchestration.py"
    if not module_path.is_file():
        raise RuntimeError("RED_ORCHESTRATION_MODULE_MISSING")
    spec = importlib.util.spec_from_file_location("luhmCanonOrchestration", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_ORCHESTRATION_MODULE_IMPORT")
    control = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(control)

    @server.tool(
        name="luhm_orchestration_plan",
        title="Lum and mini-agent two-lane Canon plan",
        description=(
            "Dry-run the 4/4 + eight-note orchestration roles using an explicit taskId, "
            "40-digit Git sourceRef, scopeId and bounded goal. Returns hashes, logical "
            "lane labels and current blockers. It does NOT spawn agents, record SQL, "
            "execute FastAPI requests, perform remote actions or authorize spending."
        ),
        annotations=annotations,
    )
    def luhm_orchestration_plan(
        taskId: str,
        sourceRef: str,
        scopeId: str,
        goal: str,
        tier: int = 0,
    ) -> dict[str, Any]:
        return control.plan(taskId, sourceRef, scopeId, goal, tier)

    @server.tool(
        name="luhm_orchestration_status",
        title="LuHm Canon orchestration state",
        description=(
            "Read the two logical lanes, current company quarantine, and offline "
            "evidence proof boundaries. This is not a live FastAPI process or agent run."
        ),
        annotations=annotations,
    )
    def luhm_orchestration_status() -> dict[str, Any]:
        contract, _, hold = control._assert_contract()
        return {
            "schema": "luhmOs.lumTwoLaneStatus.v1",
            "status": contract["status"],
            "logicalLanes": contract["logicalLanes"],
            "agentRuntimeQuarantined": (
                hold.get("state") != "RELEASED" or
                hold.get("activeTaskWorkersAllowed") is not True
            ),
            "typedSqlSchema": contract["baseline"]["sqlSchema"],
            "fastApiPrivateHostOnly": True,
            "activeAgentThreads": 0,
            "providerExecutionProven": False,
            "hostMountProven": False,
            "greenAuthority": False,
            "crownAuthority": False,
        }
