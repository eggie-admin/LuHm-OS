"""Read-only final 3x4x4 CAST proof plan, no firmware or agent execution."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def register_final_three_machine(server:Any, *, root:Path, annotations:Any)->None:
    def load(name:str)->Any:
        path=root/"tools"/name
        spec=importlib.util.spec_from_file_location("luhm_"+name.replace(".","_"),path)
        if spec is None or spec.loader is None:
            raise RuntimeError("RED_FINAL_SOURCE_IMPORT")
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    @server.tool(
       name="luhm_final_three_machine_status",
       title="LuHm three-machine-mutation source status",
       description="Read-only source receipt for original retro tiles, portable Linux/Android recipes and bounded synthetic R. Does not flash, install, tune a real kernel or spawn agents.",
       annotations=annotations)
    def luhm_final_three_machine_status()->dict[str,Any]:
        return load("finalThreeMachineGate.py").audit()

    @server.tool(
       name="luhm_synthetic_r_tuning_plan",
       title="LuHm constrained synthetic R/Python mathematical candidate",
       description="Read-only Python preview of at most sixteen safe integer parameter candidates. Does not execute R, scan credentials or tune hardware.",
       annotations=annotations)
    def luhm_synthetic_r_tuning_plan(target:int,candidates:list[int])->dict[str,Any]:
        return load("rSyntheticTuningGate.py").plan(target=target,candidates=candidates)
