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

# Additive remote-update metadata. V1 routes and plugin identities remain unchanged.
V2_MANIFEST_ROUTE = "/harness/updates/v2/manifest.json"
V2_ASSET_ROUTE = "/harness/updates/v2/assets/{digest}/{filename}"
V2_POLICY_PATH = "doctrine/selfHostedRemoteUpdatesV1.json"
V2_PUBLIC_ASSETS = (
    "cockpit.css", "cockpit.js", "studioDeck.css", "studioDeck.js",
    "titan7Cockpit.js", "jquery-3.7.1.min.js", "jquery-ui-1.14.2.min.js",
    "agent-loading-sprites.json", "agent-roster-v1.png",
    "fontStack.css", "luhmSigil.svg",
)
V2_MEDIA_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json",
    ".png": "image/png",
    ".svg": "image/svg+xml",
}
V2_MAX_ASSET_BYTES = 2_000_000


def _read_v2_asset(root: Path, name: str) -> bytes:
    if name not in V2_PUBLIC_ASSETS or "/" in name or chr(92) in name:
        raise ValueError("RED_UPDATE_V2_NOT_ALLOWLISTED")
    directory = (root / "host/harness").resolve(strict=True)
    asset = directory / name
    if asset.is_symlink() or asset.parent != directory or not asset.is_file():
        raise ValueError("RED_UPDATE_V2_UNSAFE_ASSET")
    data = asset.read_bytes()
    if not data or len(data) > V2_MAX_ASSET_BYTES:
        raise ValueError("RED_UPDATE_V2_ASSET_SIZE")
    if name.endswith(".svg"):
        # SVG used as image only; no scripting, remote references or active DOM.
        lower = data.lower()
        if (not lower.lstrip().startswith(b"<svg") or
            any(token in lower for token in (
                b"<script", b"foreignobject", b"onload=", b"onerror=",
                b"javascript:", b"<iframe", b"href=", b"@import", b"<style",
                b"<!entity", b"<!doctype",
            ))):
            raise ValueError("RED_UPDATE_V2_SVG_ACTIVE_CONTENT")
    if name.endswith(".css"):
        lower = data.lower().replace(b" ", b"")
        if b"@import" in lower or b"url(https://" in lower or b"url(http://" in lower:
            raise ValueError("RED_UPDATE_V2_CSS_REMOTE_IMPORT")
    return data


def build_remote_update_manifest(root: Path, *, deployed_sha: str | None = None) -> dict[str, Any]:
    """Read-only version check for approved same-origin files, not an installer."""
    base = root.resolve(strict=True)
    policy = json.loads((base / V2_POLICY_PATH).read_text(encoding="utf-8"))
    if policy.get("schema") != "luhmOs.selfHostedRemoteUpdates.v1":
        raise ValueError("RED_UPDATE_V2_DOCTRINE")
    if tuple(policy.get("publicAssets", [])) != V2_PUBLIC_ASSETS:
        raise ValueError("RED_UPDATE_V2_ALLOWLIST_DRIFT")
    if (policy.get("remoteScriptExecution") is not False or
        policy.get("automaticApkInstall") is not False or
        policy.get("runtimeCdnScripts") is not False or
        policy.get("crownStatus") != "STOP"):
        raise ValueError("RED_UPDATE_V2_AUTHORITY")
    # Preserve V1 source/tool/package identity and apply its existing guards.
    old = build_update_manifest(base, deployed_sha=deployed_sha)
    assets = []
    for name in V2_PUBLIC_ASSETS:
        data = _read_v2_asset(base, name)
        digest = hashlib.sha256(data).hexdigest()
        assets.append({
            "id": name,
            "sha256": digest,
            "bytes": len(data),
            "mime": V2_MEDIA_TYPES[Path(name).suffix],
            "path": "/harness/updates/v2/assets/" + digest + "/" + name,
            "cache": "bounded-revalidation",
        })
    rev = old["deployedSourceRef"]
    digest = hashlib.sha256(_canonical_json(assets)).hexdigest()
    return {
        "schema": "luhmOs.remoteUpdateManifest.v2",
        "status": "CHECK_ONLY_NOT_RELEASE_AUTHORITY",
        "sourceAuthority": "eggie-admin/LuHm-OS#main",
        "sourceRef": rev,
        "sourceRefVerified": rev != "UNVERIFIED",
        "assetSetDigest": digest,
        "assets": assets,
        "fontPolicy": "self-hosted-approved-woff2-or-system-fallback; none bundled in this candidate",
        "svgPolicy": "inert-original-vector-no-active-content",
        "cdnStatus": "NOT_ACTIVATED_SAME_ORIGIN_ONLY",
        "plugin": {
            "shellVersion": old["shellVersion"],
            "mcpEndpoint": old["compatibleMcpOrigin"],
            "resourceUri": old["stableResourceUri"],
            "hostReinstall": "NOT_REQUIRED_FOR_COMPATIBLE_ASSET_CONTENT_UPDATES",
            "hostUiMountVerified": False,
        },
        "android": {
            "updateMode": "SIGNED_REPOSITORY_ONLY_AFTER_SEPARATE_PROOF",
            "fdroidRepository": "NOT_PUBLISHED",
            "apkUrl": None,
            "applicationId": None,
            "releaseCertFingerprint": None,
            "installedUpgradeVerified": False,
            "autoInstall": False,
        },
        "metadataOnly": True,
        "sameOriginOnly": True,
        "immutableDurableAssetArchiveProven": False,
        "remoteScriptExecution": False,
        "autoInstall": False,
        "autoPublish": False,
        "crownStatus": "STOP",
    }


def register_remote_update_routes(server: Any, *, root: Path) -> None:
    """Supplement V1 with v2 GET/HEAD only; no upload, apply, install or redirect."""
    base_headers = {
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
        "Cross-Origin-Resource-Policy": "same-origin",
        "Vary": "Accept-Encoding",
    }

    @server.custom_route(V2_MANIFEST_ROUTE, methods=["GET", "HEAD"])
    async def remote_manifest(request: Request) -> Response:
        try:
            body = _canonical_json(build_remote_update_manifest(
                root, deployed_sha=os.environ.get("RENDER_GIT_COMMIT")))
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            return Response(status_code=503, content=b"update unavailable", media_type="text/plain",
                            headers={**base_headers, "Cache-Control": "no-store"})
        etag = '"' + hashlib.sha256(body).hexdigest() + '"'
        headers = {**base_headers, "Cache-Control": "no-cache, must-revalidate", "ETag": etag}
        if request.headers.get("if-none-match") == etag:
            return Response(status_code=304, headers=headers)
        if request.method == "HEAD":
            return Response(status_code=200, headers=headers, media_type="application/json")
        return Response(content=body, media_type="application/json", headers=headers)

    @server.custom_route(V2_ASSET_ROUTE, methods=["GET", "HEAD"])
    async def remote_asset(request: Request) -> Response:
        name = request.path_params.get("filename", "")
        requested = request.path_params.get("digest", "")
        if not isinstance(requested, str) or not re.fullmatch(r"[0-9a-f]{64}", requested):
            return Response(status_code=404, headers={**base_headers, "Cache-Control": "no-store"})
        try:
            # Reject a drifted policy, even for apparently known filenames.
            manifest = build_remote_update_manifest(
                root, deployed_sha=os.environ.get("RENDER_GIT_COMMIT"))
            record = next((x for x in manifest["assets"]
                           if x["id"] == name and x["sha256"] == requested), None)
            if record is None:
                return Response(status_code=404, headers={**base_headers, "Cache-Control": "no-store"})
            body = _read_v2_asset(root.resolve(strict=True), name)
            if hashlib.sha256(body).hexdigest() != requested:
                raise ValueError("RED_UPDATE_V2_HASH_CHANGED")
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            return Response(status_code=503, headers={**base_headers, "Cache-Control": "no-store"})
        # Cache stays bounded until durable old digest URLs are retained across deploys.
        headers = {**base_headers, "ETag": '"' + requested + '"',
                   "Cache-Control": "public, max-age=300"}
        if name.endswith(".svg"):
            headers["Content-Security-Policy"] = "default-src 'none'; sandbox"
        if request.headers.get("if-none-match") == headers["ETag"]:
            return Response(status_code=304, headers=headers)
        if request.method == "HEAD":
            return Response(status_code=200, headers=headers, media_type=record["mime"])
        return Response(content=body, media_type=record["mime"], headers=headers)
