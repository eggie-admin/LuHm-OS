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

import html
import json
import mimetypes
import os
from pathlib import Path
from typing import Any, Callable

from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response

UI_RESOURCE_URI = "ui://luhm-os/cockpit-v2.html"
GODOT_PLAYER_RESOURCE_URI = "ui://luhm-os/godot-player-v1.html"
APP_MIME_TYPE = "text/html;profile=mcp-app"
PET_ASSET_IDS = {"lum","urdDoctorGoddess","belldandySecretary","skuldResearch","kiri","momo","shiori","kugi","tetsu","kaji","fumi","sumi","koe","yume","mediaAssetFactory"}


def _origin() -> str:
    value = os.environ.get("LUHM_HARNESS_PUBLIC_ORIGIN", "").strip().rstrip("/")
    if not value:
        return ""
    if not value.startswith("https://") or "/" in value[8:]:
        raise ValueError("LUHM_HARNESS_PUBLIC_ORIGIN must be one HTTPS origin")
    return value


def _headers(*, html: bool = False, production: bool = False, godot_embed: bool = False) -> dict[str, str]:
    headers = {
        "Cache-Control": "no-store" if html else "public, max-age=300",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
        "Cross-Origin-Resource-Policy": "same-origin",
    }
    if html:
        # Godot's generated Web boot page uses inline startup code and WebAssembly.
        # This narrower exception applies only to the immutable export HTML route.
        script_policy = "script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'; " if godot_embed else "script-src 'self'; "
        style_policy = "style-src 'self' 'unsafe-inline'; " if godot_embed else "style-src 'self'; "
        ancestors = (
            "frame-ancestors 'self' https://*.web-sandbox.oaiusercontent.com"
            if godot_embed else "frame-ancestors 'self'"
        )
        headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            + script_policy
            + style_policy
            + "img-src 'self' data: blob:; "
            + "media-src 'self' blob:; "
            + "connect-src 'self'; "
            + "frame-src 'self'; "
            + "object-src 'none'; "
            + "base-uri 'none'; "
            + "form-action 'none'; "
            + ancestors
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
    godot_player_path = harness_root / "godotPlayerWidget.html"
    experience_path = root / "doctrine" / "inChatExperienceV1.json"
    crown_flow_path = root / "doctrine" / "chatGptPluginCrownFlowV1.json"
    runtime_receipt_path = root / "doctrine" / "chatGptPluginRuntimeReceiptV1.json"
    opening_day_path = root / "doctrine" / "openingDayStaffTrainingV1.json"
    api_spine_path = root / "doctrine" / "apiSpineV1.json"
    traffic_controller_path = root / "doctrine" / "cloudflareAirTrafficControllerV1.json"
    precision_command_path = root / "doctrine" / "chatPrecisionCommandV1.json"
    after_hours_path = root / "doctrine" / "afterHoursExperienceV1.json"

    if not all(path.is_file() for path in (widget_path, godot_player_path, index_path, pets_path, libraries_path, loading_sprites_path, loading_atlas_path, experience_path, crown_flow_path, runtime_receipt_path, opening_day_path, api_spine_path, traffic_controller_path, precision_command_path, after_hours_path)):
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
        "openai/widgetDescription": "LuHm OS in-chat cockpit for Lum/Oni activity, roleplay, pet status, source truth, and the bounded Godot handoff.",
    }
    public_origin = _origin()
    experience = json.loads(experience_path.read_text(encoding="utf-8"))
    crown_flow = json.loads(crown_flow_path.read_text(encoding="utf-8"))
    runtime_receipt = json.loads(runtime_receipt_path.read_text(encoding="utf-8"))
    opening_day = json.loads(opening_day_path.read_text(encoding="utf-8"))
    api_spine = json.loads(api_spine_path.read_text(encoding="utf-8"))
    traffic_controller = json.loads(traffic_controller_path.read_text(encoding="utf-8"))
    precision_command = json.loads(precision_command_path.read_text(encoding="utf-8"))
    after_hours = json.loads(after_hours_path.read_text(encoding="utf-8"))
    if experience.get("schema") != "luhmOs.inChatExperience.v1":
        raise RuntimeError("RED_IN_CHAT_EXPERIENCE_SCHEMA")
    if experience.get("runtime", {}).get("resourceUri") != UI_RESOURCE_URI:
        raise RuntimeError("RED_IN_CHAT_RESOURCE_DRIFT")
    if crown_flow.get("schema") != "luhmOs.chatGptPluginCrownFlow.v1":
        raise RuntimeError("RED_CROWN_FLOW_SCHEMA")
    if opening_day.get("schema") != "luhmOs.openingDayStaffTraining.v1":
        raise RuntimeError("RED_OPENING_DAY_TRAINING_SCHEMA")
    if api_spine.get("schema") != "luhmOs.apiSpine.v1":
        raise RuntimeError("RED_API_SPINE_SCHEMA")
    if traffic_controller.get("schema") != "luhmOs.cloudflareAirTrafficController.v1":
        raise RuntimeError("RED_TRAFFIC_CONTROLLER_SCHEMA")
    if precision_command.get("schema") != "luhmOs.chatPrecisionCommand.v1":
        raise RuntimeError("RED_PRECISION_COMMAND_SCHEMA")
    if after_hours.get("schema") != "luhmOs.afterHoursExperience.v1":
        raise RuntimeError("RED_AFTER_HOURS_SCHEMA")
    if after_hours.get("modeBoundary", {}).get("defaultMode") != "normalChat" or not after_hours.get("modeBoundary", {}).get("explicitEntryRequired"):
        raise RuntimeError("RED_AFTER_HOURS_BOUNDARY")
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

    @server.resource(
        GODOT_PLAYER_RESOURCE_URI,
        name="luhm-os-godot-player",
        title="LuHm OS Godot 4 Player",
        description="Dedicated in-chat viewer for the verified LuHm Godot 4 Web export.",
        mime_type=APP_MIME_TYPE,
        meta={
            "ui": {
                "prefersBorder": False,
                "csp": {
                    "connectDomains": [],
                    "resourceDomains": [],
                    "frameDomains": [public_origin] if public_origin else [],
                },
                **({"domain": public_origin} if public_origin else {}),
            },
            "openai/ui": {"availableDisplayModes": ["inline", "fullscreen"]},
            "openai/widgetDescription": "LuHm Godot 4 gameplay viewer; no builds or privileged actions.",
        },
    )
    def luhm_godot_player_resource() -> str:
        page = godot_player_path.read_text(encoding="utf-8")
        staged = (
            (godot_root / "index.html").is_file()
            and any(godot_root.glob("*.wasm"))
            and any(godot_root.glob("*.pck"))
        )
        if not public_origin or not staged:
            frame = '<p class="pending">Godot Web export not staged on this HTTPS origin. Player is waiting for exact-source CAST proof.</p>'
        else:
            url = html.escape(public_origin + "/harness/godot-export/index.html", quote=True)
            frame = (
                '<iframe title="LuHm OS Godot 4 playable viewport" src="' + url + '"'
                ' sandbox="allow-scripts allow-same-origin allow-pointer-lock"'
                ' allow="fullscreen; gamepad" allowfullscreen loading="eager" referrerpolicy="no-referrer"></iframe>'
            )
        return page.replace("<!-- LUHM_GODOT_FRAME -->", frame)

    @server.tool(
        name="luhm_open_godot_player",
        title="Play LuHm OS Godot 4 in chat",
        description="Open the bounded in-chat Godot Web viewer when a real WebAssembly/PCK export is staged. Read-only; no CAST, deployment, or Crown.",
        annotations=annotations,
        meta={
            "ui": {"resourceUri": GODOT_PLAYER_RESOURCE_URI, "visibility": ["model", "app"]},
            "openai/outputTemplate": GODOT_PLAYER_RESOURCE_URI,
            "openai/toolInvocation/invoking": "Checking Godot 4 Web player…",
            "openai/toolInvocation/invoked": "Godot 4 viewer opened.",
        },
    )
    def luhm_open_godot_player() -> dict[str, Any]:
        staged = (
            (godot_root / "index.html").is_file()
            and any(godot_root.glob("*.wasm"))
            and any(godot_root.glob("*.pck"))
        )
        return {
            "schema": "luhmOs.inChatGodotPlayer.v1",
            "resourceUri": GODOT_PLAYER_RESOURCE_URI,
            "state": "WEB_EXPORT_FILES_STAGED" if staged and public_origin else "PENDING_EXPORT_OR_HTTPS_ORIGIN",
            "runtimeVerifiedInChat": False,
            "sourceRef": "EXACT_BUILD_RECEIPT_REQUIRED",
            "readOnly": True,
            "buildAuthority": False,
            "crownStatus": "STOP",
        }

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
            "schema": "luhmOs.inChatExperiencePayload.v1",
            "surface": "mcp-app",
            "experience": experience,
            "crownFlow": crown_flow,
            "runtimeReceipt": runtime_receipt,
            "openingDay": opening_day,
            "apiSpine": api_spine,
            "trafficController": traffic_controller,
            "precisionCommands": precision_command,
            "afterHours": after_hours,
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
        parts = Path(relative).parts
        pet_asset = (
            len(parts) == 4
            and parts[0] == "pets"
            and parts[1] in PET_ASSET_IDS
            and len(parts[2]) == 64
            and all(c in "0123456789abcdef" for c in parts[2].lower())
            and parts[3] in {"sequence.webp", "sequence.png", "sequence.json"}
        )
        if relative not in allowed and not pet_asset:
            return PlainTextResponse("not found", status_code=404, headers=_headers())
        target = _safe_file(harness_root, relative)
        if target is None:
            return PlainTextResponse("not found", status_code=404, headers=_headers())
        media_type = {".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".json": "application/json", ".png": "image/png", ".webp": "image/webp"}.get(target.suffix, "application/octet-stream")
        return FileResponse(target, media_type=media_type, headers=_headers())

    @server.custom_route("/harness/config.json", methods=["GET"])
    async def harness_config(_: Request) -> Response:
        libraries = json.loads(libraries_path.read_text(encoding="utf-8"))
        pets = json.loads(pets_path.read_text(encoding="utf-8"))
        return JSONResponse(
            {
                "schema": "luhmOs.harnessConfig.v2",
                "experience": experience,
                "crownFlow": crown_flow,
                "runtimeReceipt": runtime_receipt,
                "openingDay": opening_day,
                "apiSpine": api_spine,
                "trafficController": traffic_controller,
                "precisionCommands": precision_command,
                "afterHours": after_hours,
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
            headers=_headers(html=html, production=profile_provider() == "production", godot_embed=html),
        )
