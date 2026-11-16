#!/usr/bin/env python3
"""Read-only cryptographic and optional MariaDB capability status for ChatGPT."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def _module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_CRYPTO_PLUGIN_IMPORT")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def register_crypto_breathing_tools(server: Any, *, root: Path,
                                    annotations: Any) -> None:
    crypto = _module("luhmCryptoBreathing", root / "host/api/luhmCryptoBreathing.py")
    sql = _module("luhmMariaDbReceipt", root / "host/api/luhmMariaDbReceipt.py")

    @server.tool(
        name="luhm_crypto_breathing_status",
        title="LuHm R1-R4 cryptographic breathing ladder",
        description="Read Canon stage names and readiness only; no keys, files, remote calls or release permissions.",
        annotations=annotations,
    )
    def luhm_crypto_breathing_status() -> dict[str, Any]:
        return crypto.status()

    @server.tool(
        name="luhm_mariadb_receipt_status",
        title="LuHm optional MariaDB receipt sink",
        description="Inspect the default-disabled MariaDB receipt adapter without connecting or executing SQL.",
        annotations=annotations,
    )
    def luhm_mariadb_receipt_status() -> dict[str, Any]:
        return sql.connection_plan()
