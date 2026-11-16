#!/usr/bin/env python3
"""Read-only MCP capability for 60s GPU video review planning."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def register_gpu_video_planner(server: Any, *, root: Path, annotations: Any) -> None:
    path = root / "host" / "api" / "luhmGpuVideoPlanner.py"
    if not path.is_file():
        raise RuntimeError("RED_GPU_VIDEO_PLANNER_MISSING")
    spec = importlib.util.spec_from_file_location("luhmGpuVideoPlanner", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_GPU_VIDEO_PLANNER_IMPORT")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    @server.tool(
        name="luhm_gpu_video_status",
        title="LuHm GPU video pipeline readiness",
        description=(
            "Inspect the planned localhost→private host→remote GPU→enterprise "
            "security profiles, one-minute delivery contract and hard spend gates. "
            "Does not discover or allocate actual GPUs."
        ),
        annotations=annotations,
    )
    def luhm_gpu_video_status() -> dict[str, Any]:
        return module.status()

    @server.tool(
        name="luhm_gpu_video_plan",
        title="LuHm AI video one-minute chunk dry-run",
        description=(
            "Prepare an offline 60-second-delivery shot plan for taskId, exact Git "
            "sourceRef and scopeId. Include bounded prompt, total duration, frames "
            "and requested VRAM mode. It returns no raw prompt and never starts a "
            "worker, pays a model, schedules GPU memory or renders media."
        ),
        annotations=annotations,
    )
    def luhm_gpu_video_plan(
        taskId: str,
        sourceRef: str,
        scopeId: str,
        seconds: int,
        prompt: str,
        width: int = 1280,
        height: int = 720,
        fps: int = 24,
        modelShotSeconds: int = 6,
        vramMode: str = "balanced",
        modelVramEstimateMiB: int = 8192,
    ) -> dict[str, Any]:
        return module.plan(
            task_id=taskId, source_ref=sourceRef, scope_id=scopeId,
            seconds=seconds, prompt=prompt, width=width, height=height,
            fps=fps, model_shot_seconds=modelShotSeconds,
            vram_mode=vramMode, model_vram_estimate_mib=modelVramEstimateMiB,
        )
