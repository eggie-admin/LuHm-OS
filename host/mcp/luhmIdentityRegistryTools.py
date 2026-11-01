#!/usr/bin/env python3
"""Read-only identity help source for LuHm-OS CAST Bridge."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def register_cast_identity_registry(server: Any, *, root: Path, annotations: Any) -> None:
    path = root / "host" / "api" / "luhmIdentityRegistry.py"
    if not path.is_file():
        raise RuntimeError("RED_CAST_IDENTITY_MODULE_MISSING")
    spec = importlib.util.spec_from_file_location("luhmIdentityRegistry", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_CAST_IDENTITY_IMPORT")
    identity = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(identity)

    @server.tool(
        name="luhm_cast_identity_status",
        title="LuHm four-layer CAST name, hex and SQL identity status",
        description=(
            "Read the source-only 25-name registry and sixteen identity/data "
            "cells with exact hex, canonical names and untrusted aliases. "
            "No OS environment, database, device or private provider is accessed."
        ),
        annotations=annotations,
    )
    def luhm_cast_identity_status() -> dict[str, Any]:
        return identity.cast_projection()

    @server.tool(
        name="luhm_cast_identity_help",
        title="Resolve a compact or hexadecimal LuHm role or data-lane name",
        description=(
            "Look up an explicitly registered camelHump, vowel-ripped, short, "
            "legacy or lowercase byte-hex alias. Return only the canonical "
            "identity and human meaning; never execute an alias, route a "
            "worker, enable USB/Bluetooth or confer authority."
        ),
        annotations=annotations,
    )
    def luhm_cast_identity_help(alias: str) -> dict[str, Any]:
        return identity.resolve(alias)
