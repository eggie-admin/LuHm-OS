#!/usr/bin/env python3
"""Additive LuHm OS presentation harness.

This module registers:
- a read-only ChatGPT/MCP Apps cockpit resource and render tool;
- a standalone same-origin HTML harness for local IPv4 development and Render HTTPS;
- a bounded same-origin Godot 4 Web export viewer;
- pet and JavaScript-library policy manifests.

It does not grant merge, release, signing, publication, or source-truth authority.
"""
from __future__ import annotations

import json
import mimetypes
import os
from pathlib import Path
from typing import Any, Callable

from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response

UI_RESOURCE_URI = "ui://luhm-os/cockpit-v1.html"
APP_MIME_TYPE = "text/html;profile=mcp-app"


def _origin() -> str:
    value = os.environ.get("LUHM_HARNESS_PUBLIC_ORIGIN", "").strip().rstrip("/")
    if not value:
        return ""
    if not value.startswith("https://") or "/" in value[8:]:
        raise ValueError("LUHM_HARNESS_PUBLIC_ORIGIN must be one HTTPS origin")
    return value


def _headers(*, html: bool = False, production: bool = False) -> dict[str, str]:
    headers = {
        "Cache-Control": "no-store" if html else "public, max-age=300",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
        "Cross-Origin-Resource-Policy": "same-origin",
    }
    if html:
        headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data: blob:; "
            "media-src 'self' blob:; "
            "connect-src 'self'; "
            "frame-src 'self'; "
            "object-src 'none'; "
            "base-uri 'none'; "
            "form-action 'none'; "
            "frame-ancestors 'self'"
        )
    if production:
        headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return headers


def _safe_file(root: Path, relative: str) -> Path | None:
    root = root.resolve()
    candidate = (root / relative).resolve()
    if candidate != root and root not in candidate.parents:
        return None
    if not candidate.is_file():
        return None
    return candidate


def register_harness(
    server: Any,
    *,
    root: Path,
    annotations: Any,
    status_provider: Callable[[], dict[str, Any]],
    roster_provider: Callable[[], dict[str, Any]],
    profile_provider: Callable[[], str],
) -> None:
    harness_root = root / "host" / "harness"
    widget_path = harness_root / "widget.html"
    index_path = harness_root / "index.html"
    pets_path = harness_root / "pets.json"
    loading_sprites_path = harness_root / "agent-loading-sprites.json"
    loading_atlas_path = harness_root / "agent-roster-v1.png"
    libraries_path = harness_root / "libraryPolicy.json"
    godot_root = harness_root / "godot-export"

    if not all(path.is_file() for path in (widget_path, index_path, pets_path, libraries_path, loading_sprites_path, loading_atlas_path)):
        raise RuntimeError("RED_HARNESS_SOURCE_MISSING")

    resource_meta: dict[str, Any] = {
        "ui": {
            "prefersBorder": True,
            "csp": {
                "connectDomains": [],
                "resourceDomains": [],
            },
        },
        "openai/ui": {
            "availableDisplayModes": ["inline", "fullscreen"],
        },
        "openai/widgetDescription": "LuHm OS read-only cockpit with Lum/Oni pet status and a full-harness handoff.",
    }
    public_origin = _origin()
    if public_origin:
        resource_meta["ui"]["domain"] = public_origin

    @server.resource(
        UI_RESOURCE_URI,
        name="luhm-os-cockpit",
        title="LuHm OS Cockpit",
        description="Read-only LuHm status and Lum/Oni cockpit rendered inside MCP Apps hosts.",
        mime_type=APP_MIME_TYPE,
        meta=resource_meta,
    )
    def luhm_cockpit_resource() -> str:
        return widget_path.read_text(encoding="utf-8")

    @server.tool(
        name="luhm_open_cockpit",
        title="Open LuHm OS cockpit",
        description="Render the read-only LuHm OS cockpit. This never mutates source, deploys, signs, publishes, or grants GREEN authority.",
        annotations=annotations,
        meta={
            "ui": {"resourceUri": UI_RESOURCE_URI, "visibility": ["model", "app"]},
            "openai/outputTemplate": UI_RESOURCE_URI,
            "openai/toolInvocation/invoking": "Opening LuHm cockpit…",
            "openai/toolInvocation/invoked": "LuHm cockpit ready.",
        },
    )
    def luhm_open_cockpit() -> dict[str, Any]:
        return {
            "schema": "luhm-os.cockpit.v1",
            "surface": "mcp-app",
            "status": status_provider(),
            "roster": roster_provider(),
            "harness": {
                "publicOrigin": public_origin or "LOCAL_ONLY",
                "standalonePath": "/harness/",
                "godotPath": "/harness/godot-export/index.html",
                "godotEmbeddingInChat": False,
                "reason": "Nested Godot iframe is kept out of the chat widget by default; the full same-origin harness owns it.",
            },
            "authority": {
                "readOnly": True,
                "mutationAuthority": False,
                "publicationAuthority": False,
                "greenAuthority": False,
            },
        }

    @server.custom_route("/", methods=["GET"])
    async def harness_root_redirect(_: Request) -> Response:
        return RedirectResponse("/harness/", status_code=307)

    @server.custom_route("/harness/", methods=["GET", "HEAD"])
    async def harness_index(_: Request) -> Response:
        return FileResponse(
            index_path,
            media_type="text/html; charset=utf-8",
            headers=_headers(html=True, production=profile_provider() == "production"),
        )

    @server.custom_route("/harness/assets/{asset_path:path}", methods=["GET", "HEAD"])
    async def harness_asset(request: Request) -> Response:
        relative = request.path_params.get("asset_path", "")
        allowed = {"cockpit.css", "cockpit.js", "agent-loading-sprites.json", "agent-roster-v1.png"}
        if relative not in allowed:
            return PlainTextResponse("not found", status_code=404, headers=_headers())
        target = _safe_file(harness_root, relative)
        if target is None:
            return PlainTextResponse("not found", status_code=404, headers=_headers())
        media_type = {".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".json": "application/json", ".png": "image/png"}.get(target.suffix, "application/octet-stream")
        return FileResponse(target, media_type=media_type, headers=_headers())

    @server.custom_route("/harness/config.json", methods=["GET"])
    async def harness_config(_: Request) -> Response:
        libraries = json.loads(libraries_path.read_text(encoding="utf-8"))
        pets = json.loads(pets_path.read_text(encoding="utf-8"))
        return JSONResponse(
            {
                "schema": "luhm-os.harness-config.v1",
                "network": {
                    "localDevelopment": "http://127.0.0.1:8788/harness/",
                    "publicHttpsRequired": True,
                    "renderOriginIpv6": False,
                    "renderIpv6Note": "Render origin is IPv4-only; do not publish AAAA records for the Render origin.",
                },
                "chatUi": {
                    "resourceUri": UI_RESOURCE_URI,
                    "availableDisplayModes": ["inline", "fullscreen"],
                    "nestedFramesByDefault": False,
                },
                "godot": {
                    "viewer": "/harness/godot-export/index.html",
                    "webExportTarget": "host/harness/godot-export/index.html",
                    "threadSupport": False,
                    "requiredRuntime": ["WebAssembly", "WebGL2", "HTTPS outside localhost"],
                },
                "libraries": libraries,
                "pets": pets,
                "authority": {
                    "readOnly": True,
                    "mutationAuthority": False,
                    "publicationAuthority": False,
                    "greenAuthority": False,
                },
            },
            headers=_headers(),
        )

    @server.custom_route("/harness/pets.json", methods=["GET"])
    async def harness_pets(_: Request) -> Response:
        return JSONResponse(json.loads(pets_path.read_text(encoding="utf-8")), headers=_headers())

    @server.custom_route("/harness/godot-export/{asset_path:path}", methods=["GET", "HEAD"])
    async def godot_asset(request: Request) -> Response:
        relative = request.path_params.get("asset_path", "")
        target = _safe_file(godot_root, relative)
        if target is None:
            return PlainTextResponse(
                "Godot 4 Web export is not staged in this build.",
                status_code=404,
                headers=_headers(),
            )
        media_type, _ = mimetypes.guess_type(target.name)
        if target.suffix == ".wasm":
            media_type = "application/wasm"
        elif target.suffix in {".pck", ".zip"}:
            media_type = "application/octet-stream"
        html = target.suffix == ".html"
        return FileResponse(
            target,
            media_type=media_type or "application/octet-stream",
            headers=_headers(html=html, production=profile_provider() == "production"),
        )
