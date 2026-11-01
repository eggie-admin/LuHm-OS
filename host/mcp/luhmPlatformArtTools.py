#!/usr/bin/env python3
"""Read-only Premonition platform and art-data separation MCP routes."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def register_platform_art_tools(server: Any, *, root: Path, annotations: Any) -> None:
    path = root / "tools" / "premonitionPlatformArtAudit.py"
    if not path.is_file():
        raise RuntimeError("RED_PLATFORM_ART_AUDITOR_MISSING")
    spec = importlib.util.spec_from_file_location("premonitionPlatformArtAudit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_PLATFORM_ART_AUDITOR_IMPORT")
    impl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(impl)

    @server.tool(
        name="luhm_platform_art_status",
        title="LuHm Premonition Android, Samsung, iOS and 3D source audit",
        description=(
            "Audit the 16 proposed Android/Samsung/iOS/Linux source-art cells, "
            "Project Premonition identity, source-only platform exports and the "
            "SQLite STRICT metadata schema. No devices, kernels, art uploads, "
            "workers or live SQL servers are touched."
        ),
        annotations=annotations,
    )
    def luhm_platform_art_status() -> dict[str, Any]:
        return impl.audit_source()

    @server.tool(
        name="luhm_platform_asset_route",
        title="LuHm vector, 3D, media and SQL metadata route",
        description=(
            "Return a source-only capability plan for a known asset format and "
            "target platform. No user art bytes, private pointers, vendor "
            "entitlements, signing, kernel patches or remote tools are involved."
        ),
        annotations=annotations,
    )
    def luhm_platform_asset_route(assetFormat: str, platform: str) -> dict[str, Any]:
        if assetFormat not in impl.EXTENSIONS or platform not in impl.PLATFORMS:
            raise ValueError("UNKNOWN_PLATFORM_OR_ASSET_FORMAT")
        kind = impl.EXTENSIONS[assetFormat]
        return {
            "schema": "luhmOs.premonitionAssetRoute.v1",
            "platform": platform, "format": assetFormat, "assetClass": kind,
            "pythonRole": "boundedOfflineInspectAndHash",
            "sqlRole": "PrivateSqliteStrictMetadataPointerOnly",
            "sourceOfTruth": "eggie-admin/LuHm-OS",
            "brand": "LuHm-OS: Project Premonition",
            "state": "HOLD_ACTUAL_ART_RIGHTS_AND_DEVICE_RECEIPT",
            "actualDeviceConnected": False, "assetBytesInspected": False,
            "publicRelease": False, "greenAuthority": False, "crownAuthority": False,
        }
