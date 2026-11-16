"""LuHm CAST hardware seal: read-only composite source evidence MCP tool.

The current ChatGPT plugin is not updated by this Git source registration.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def register_hardware_cast_seal(server: Any, *, root: Path,
                                annotations: Any) -> None:
    path = root / "tools" / "hardwareCastSeal.py"
    if not path.is_file():
        raise RuntimeError("RED_CAST_HARDWARE_SOURCE_FILE")
    spec = importlib.util.spec_from_file_location("hardwareCastSeal", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_CAST_HARDWARE_SOURCE_IMPORT")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    @server.tool(
        name="luhm_hardware_cast_seal",
        title="LuHm CAST hardware source seal",
        description=(
            "Read-only four-lane composite hardware/VM source audit. Returns "
            "exact file bundle SHA256 and explicit unmet real-host proof "
            "requirements. Source-only green does not mean a guest or kernel "
            "has booted. No device probing, VM creation, kernel changes or "
            "proprietary cloud actions."
        ),
        annotations=annotations,
    )
    def luhm_hardware_cast_seal(sourceRef: str) -> dict[str, Any]:
        return mod.source_seal(source_ref=sourceRef)
