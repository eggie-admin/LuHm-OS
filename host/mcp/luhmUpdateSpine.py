#!/usr/bin/env python3
"""Read-only same-origin update metadata for the stable installed LuHm-OS shell.

Never executes code, mutates assets, fetches Drive, or infers host/CDN health.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import Response

PUBLIC_ASSETS = ("cockpit.css", "cockpit.js", "agent-loading-sprites.json", "agent-roster-v1.png")
MEDIA_TYPES = {".css": "text/css", ".js": "text/javascript", ".json": "application/json", ".png": "image/png"}
MANIFEST_ROUTE = "/harness/update-manifest.json"


def _canonical_json(data: Any) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def build_update_manifest(root: Path, *, deployed_sha: str | None = None) -> dict[str, Any]:
    """Read only statically allowlisted public assets and the pinned update contract."""
    base = root.resolve(strict=True)
    doctrine = json.loads((base / "doctrine/stablePluginUpdateSpineV1.json").read_text(encoding="utf-8"))
    if doctrine.get("schema") != "luhmOs.stablePluginUpdateSpine.v1":
        raise ValueError("RED_UPDATE_DOCTRINE_SCHEMA")
    policy = doctrine.get("updateManifest", {})
    if sorted(policy.get("publicAllowlist", [])) != sorted(PUBLIC_ASSETS):
        raise ValueError("RED_UPDATE_ASSET_ALLOWLIST_DRIFT")
    shell = doctrine.get("singleInstallShell", {})
    plugin = json.loads((base / shell["canonicalPlugin"]).read_text(encoding="utf-8"))
    mcp = json.loads((base / shell["stableMcpConfig"]).read_text(encoding="utf-8"))
    if plugin.get("name") != "luhm-os" or plugin.get("version") != shell.get("baselineVersion"):
        raise ValueError("RED_HOST_PLUGIN_VERSION_DRIFT")
    if mcp.get("mcpServers", {}).get("luhm", {}).get("url") != shell.get("stableMcpUrl"):
        raise ValueError("RED_STABLE_MCP_ENDPOINT_DRIFT")
    asset_root = (base / "host/harness").resolve(strict=True)
    assets = []
    for name in PUBLIC_ASSETS:
        candidate = asset_root / name
        if candidate.is_symlink():
            raise ValueError("RED_UNSAFE_UPDATE_ASSET_SYMLINK")
        path = candidate.resolve(strict=True)
        if path.parent != asset_root or not path.is_file():
            raise ValueError("RED_UNSAFE_UPDATE_ASSET")
        data = path.read_bytes()
        assets.append({
            "id": name,
            "path": "/harness/assets/" + name,
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
            "mime": MEDIA_TYPES[path.suffix],
            "cache": "revalidate-unversioned",
        })
    digest = hashlib.sha256(_canonical_json(assets)).hexdigest()
    verified_sha = deployed_sha if isinstance(deployed_sha, str) and re.fullmatch(r"[0-9a-f]{40}", deployed_sha) else "UNVERIFIED"
    return {
        "schema": "luhmOs.updateManifest.v1",
        "package": "LuHmOS",
        "shellVersion": plugin["version"],
        "compatibleMcpOrigin": shell["stableMcpUrl"],
        "stableToolNames": shell["stableToolNames"],
        "stableResourceUri": shell["stableResourceUri"],
        "deployedSourceRef": verified_sha,
        "assetSetDigest": digest,
        "assets": assets,
        "metadataOnly": True,
        "hostInstallationProven": False,
        "cloudflareCdnProven": False,
        "autoInstall": False,
        "autoPublish": False,
        "crownStatus": "STOP",
    }


def register_update_spine(server: Any, *, root: Path) -> None:
    @server.custom_route(MANIFEST_ROUTE, methods=["GET", "HEAD"])
    async def update_manifest(request: Request) -> Response:
        try:
            body = _canonical_json(build_update_manifest(root, deployed_sha=os.environ.get("RENDER_GIT_COMMIT")))
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            return Response(status_code=503, content=b"manifest unavailable", media_type="text/plain", headers={
                "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer"})
        etag = '"' + hashlib.sha256(body).hexdigest() + '"'
        headers = {"Cache-Control": "no-cache, must-revalidate", "ETag": etag,
                   "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer"}
        if request.headers.get("if-none-match") == etag:
            return Response(status_code=304, headers=headers)
        if request.method == "HEAD":
            return Response(status_code=200, headers=headers, media_type="application/json")
        return Response(content=body, media_type="application/json", headers=headers)
