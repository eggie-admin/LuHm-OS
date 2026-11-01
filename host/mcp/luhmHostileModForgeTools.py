#!/usr/bin/env python3
"""Read-only host-neutral 4x4 mod/device environment candidate tools for MCP.

Nothing here reads actual os.environ or enumerates devices, downloads third-party
code, opens an emulator, runs a worker or grants distribution rights.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def register_hostile_mod_forge(server: Any, *, root: Path, annotations: Any) -> None:
    source = root / "tools" / "hostileModForgeAudit.py"
    if not source.is_file():
        raise RuntimeError("RED_HOSTILE_MOD_FORGE_GATE_MISSING")
    spec = importlib.util.spec_from_file_location("hostileModForgeAudit", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_HOSTILE_MOD_FORGE_IMPORT")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)

    @server.tool(
        name="luhm_hostile_mod_forge_status",
        title="LuHm 4x4 hardening, community tool license and device source status",
        description=(
            "Source-only hostile-input audit for Wayland/headless variables, "
            "USB/Bluetooth/debug controls, upstream community component permissions "
            "and ROM-patch metadata boundaries. No host, kernel, device, GitHub fork "
            "or third-party mod is touched; no promotion authority."
        ),
        annotations=annotations,
    )
    def luhm_hostile_mod_forge_status() -> dict[str, Any]:
        return gate.audit()

    @server.tool(
        name="luhm_hostile_mod_environment_plan",
        title="LuHm offline planned headless/Wayland and device permission flags",
        description=(
            "Check only eight explicit LUHM_* configuration values as a proposed "
            "set. Does not read or change the host environment, grant Bluetooth, "
            "USB or display access, or enable privileged execution."
        ),
        annotations=annotations,
    )
    def luhm_hostile_mod_environment_plan(
        displayBackend: str = "headless", usb: str = "off",
        bluetooth: str = "off", debug: str = "off"
    ) -> dict[str, Any]:
        return gate.environment_plan({
            "LUHM_DISPLAY_BACKEND": displayBackend,
            "LUHM_USB_ENABLED": usb,
            "LUHM_BLUETOOTH_ENABLED": bluetooth,
            "LUHM_DEBUG_PROFILE": debug,
        })
