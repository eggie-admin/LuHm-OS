#!/usr/bin/env python3
"""Read-only CAST Bridge dual-timeline projection for LuHm MCP."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def register_cast_two_thread(server: Any, *, root: Path, annotations: Any) -> None:
    path = root / "host" / "api" / "luhmCastTwoThreadBridge.py"
    if not path.is_file():
        raise RuntimeError("RED_CAST_TWO_THREAD_SOURCE_MISSING")
    spec = importlib.util.spec_from_file_location("luhmCastTwoThreadBridge", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_CAST_TWO_THREAD_IMPORT")
    control = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(control)

    @server.tool(
        name="luhm_cast_two_thread_status",
        title="LuHm CAST Bridge two-thread source and 4x4 mesh status",
        description=(
            "Read-only source verification for the Professor/Lum and "
            "Lum/orchestration two-thread projection, four typed SQL lanes, "
            "four escalation tiers and eight canonical stages. "
            "Does not create a second ChatGPT conversation or spawn agents."
        ),
        annotations=annotations,
    )
    def luhm_cast_two_thread_status() -> dict[str, Any]:
        return control.source_audit()

    @server.tool(
        name="luhm_cast_two_thread_plan",
        title="LuHm CAST Bridge two visible timelines and staged handoff plan",
        description=(
            "Plan an exact taskId/sourceRef/scopeId and bounded goal at tier "
            "0 through 3 using a named canonical stage. Returns two separate "
            "view models and a 4x4 data/evidence matrix. Does not write SQL, "
            "execute mini-agents, build, deploy, CAST, or create chat threads."
        ),
        annotations=annotations,
    )
    def luhm_cast_two_thread_plan(
        taskId: str, sourceRef: str, scopeId: str,
        goal: str, tier: int = 0, requestedStage: str = "sanityCheck",
    ) -> dict[str, Any]:
        return control.plan(taskId, sourceRef, scopeId, goal, tier, requestedStage)
