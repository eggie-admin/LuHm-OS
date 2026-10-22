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

import hashlib
import html
import json
import mimetypes
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response

UI_RESOURCE_URI = "ui://luhm-os/cockpit-v2.html"
GODOT_PLAYER_RESOURCE_URI = "ui://luhm-os/godot-player-v1.html"
MCP_COCKPIT_PUBLIC_ORIGIN = "https://luhm-os-harness-green.onrender.com"
EXISTING_GODOT_PUBLIC_ORIGIN = "https://luhm-os-godot-harness-green.onrender.com"
APP_MIME_TYPE = "text/html;profile=mcp-app"
PET_ASSET_IDS = {"lum","urdDoctorGoddess","belldandySecretary","skuldResearch","kiri","momo","shiori","kugi","tetsu","kaji","fumi","sumi","koe","yume","mediaAssetFactory"}


def _origin() -> str:
    value = os.environ.get("LUHM_HARNESS_PUBLIC_ORIGIN", "").strip().rstrip("/")
    if not value:
        return ""
    if not value.startswith("https://") or "/" in value[8:]:
        raise ValueError("LUHM_HARNESS_PUBLIC_ORIGIN must be one HTTPS origin")
    return value


def _headers(*, html: bool = False, production: bool = False, godot_embed: bool = False, dynamic: bool = False) -> dict[str, str]:
    headers = {
        "Cache-Control": "no-store" if html or dynamic else "public, max-age=300",
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
            "frame-ancestors 'self' https://*.web-sandbox.oaiusercontent.com https://luhm-os-publication-site.onrender.com"
            if godot_embed else "frame-ancestors 'self'"
        )
        frame_policy = "frame-src 'self'; " if godot_embed else "frame-src 'self' blob: https://www.youtube-nocookie.com; "
        headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            + script_policy
            + style_policy
            + "img-src 'self' data: blob:; "
            + "media-src 'self' blob:; "
            + "connect-src 'self'; "
            + frame_policy
            + "object-src 'none'; "
            + "base-uri 'none'; "
            + "form-action 'none'; "
            + ancestors
        )
    if production:
        headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return headers


def _safe_file(root: Path, relative: str) -> Path | None:
    # Serve only plain files below the allowlisted root; reject path aliases
    # and symlink traversal, even if the link resolves to an internal file.
    if not isinstance(relative, str) or not relative or chr(0) in relative or chr(92) in relative:
        return None
    path = Path(relative)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in relative.split("/")):
        return None
    root = root.resolve()
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            return None
    candidate = current.resolve()
    if root not in candidate.parents or not candidate.is_file():
        return None
    return candidate


@lru_cache(maxsize=4)
def _inspect_godot_bundle(root: Path) -> dict[str, Any]:
    """Verify local Godot HTML, WASM and PCK bytes against build SHA256SUMS."""
    unavailable = {"ready": False, "fileCount": 0, "wasmCount": 0, "pckCount": 0, "integrity": "UNVERIFIED"}
    manifest = root / "SHA256SUMS.txt"
    if not manifest.is_file():
        return unavailable
    try:
        lines = manifest.read_text(encoding="utf-8").splitlines()
        if not lines or len(lines) > 100:
            return unavailable
        names = set()
        for line in lines:
            match = re.fullmatch(r"([0-9a-f]{64})\s+\*?(?:\./)?([A-Za-z0-9][A-Za-z0-9._-]*)", line)
            if match is None:
                return unavailable
            digest, name = match.groups()
            if name in names or name.endswith((".glb", ".gltf", ".rar", ".zip", ".7z")):
                return unavailable
            names.add(name)
            asset = root / name
            if not asset.is_file() or asset.is_symlink() or asset.stat().st_size == 0:
                return unavailable
            if hashlib.sha256(asset.read_bytes()).hexdigest() != digest:
                return unavailable
        wasm = sum(name.endswith(".wasm") for name in names)
        pck = sum(name.endswith(".pck") for name in names)
        if "index.html" not in names or not wasm or not pck:
            return unavailable
        return {"ready": True, "fileCount": len(names), "wasmCount": wasm, "pckCount": pck, "integrity": "SHA256_PASS"}
    except (OSError, UnicodeError, ValueError):
        return unavailable
def _studio_page(harness_root: Path, page: str, *, widget: bool = False) -> str:
    """One set of studio controls for the browser and MCP Apps resource."""
    deck = (harness_root / "studioDeck.html").read_text(encoding="utf-8")
    if widget:
        css = (harness_root / "studioDeck.css").read_text(encoding="utf-8")
        import base64
        atlas = base64.b64encode((harness_root / "agent-roster-v1.png").read_bytes()).decode("ascii")
        css = css.replace("/harness/assets/agent-roster-v1.png", "data:image/png;base64," + atlas)
        script = (harness_root / "studioDeck.js").read_text(encoding="utf-8")
        deck = "<style>" + css + "</style>" + deck + "<script>" + script + "</script>"
    return page.replace("<!-- LUHM_STUDIO_DECK -->", deck)


def _studio_contract(root: Path) -> dict[str, Any]:
    value = json.loads((root / "doctrine" / "embeddedStudioV1.json").read_text(encoding="utf-8"))
    quarantine = json.loads((root / "doctrine" / "companyWideOperationalQuarantineV1.json").read_text(encoding="utf-8"))
    # Contract updates require a source review; a browser switch cannot promote a lane.
    if value.get("schema") != "luhmOs.embeddedStudio.v1" or value.get("lane") != "testing":
        raise RuntimeError("RED_STUDIO_CONTRACT")
    if value.get("serverWrites") is not False or value.get("productionPromotion") is not False:
        raise RuntimeError("RED_STUDIO_AUTHORITY")
    value["quarantine"] = {"state": quarantine.get("state", "UNKNOWN"),
                           "activeTaskWorkersAllowed": quarantine.get("activeTaskWorkersAllowed", False)}
    value["sourceRef"] = os.environ.get("RENDER_GIT_COMMIT", "UNKNOWN")
    return value


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
    artist_studio_path = root / "doctrine" / "artistStudioPluginV1.json"
    rebel_studio_path = root / "doctrine" / "rebelInChatStudioV1.json"
    crown_flow_path = root / "doctrine" / "chatGptPluginCrownFlowV1.json"
    runtime_receipt_path = root / "doctrine" / "chatGptPluginRuntimeReceiptV1.json"
    opening_day_path = root / "doctrine" / "openingDayStaffTrainingV1.json"
    api_spine_path = root / "doctrine" / "apiSpineV1.json"
    traffic_controller_path = root / "doctrine" / "cloudflareAirTrafficControllerV1.json"
    precision_command_path = root / "doctrine" / "chatPrecisionCommandV1.json"
    after_hours_path = root / "doctrine" / "afterHoursExperienceV1.json"
    coding_roleplay_path = root / "doctrine" / "codingRoleplayDirectorV2.json"
    virgin_install_path = root / "doctrine" / "manualPluginVirginInstallV1.json"
    beta_lane_path = root / "doctrine" / "pluginBetaFourLaneV1.json"

    if not all(path.is_file() for path in (widget_path, godot_player_path, index_path, pets_path, libraries_path, loading_sprites_path, loading_atlas_path, experience_path, artist_studio_path, rebel_studio_path, crown_flow_path, runtime_receipt_path, opening_day_path, api_spine_path, traffic_controller_path, precision_command_path, after_hours_path, coding_roleplay_path, virgin_install_path, beta_lane_path)):
        raise RuntimeError("RED_HARNESS_SOURCE_MISSING")

    for name in ("studioDeck.html", "studioDeck.css", "studioDeck.js"):
        if not (harness_root / name).is_file():
            raise RuntimeError("RED_STUDIO_SOURCE_MISSING")
    _studio_contract(root)

    resource_meta: dict[str, Any] = {
        "ui": {
            "prefersBorder": True,
            "csp": {
                "connectDomains": [],
                "resourceDomains": [],
                "frameDomains": ["https://www.youtube-nocookie.com"],
            },
        },
        "openai/ui": {
            "availableDisplayModes": ["inline", "fullscreen"],
        },
        "openai/widgetDescription": "LuHm OS artist-first in-chat storyboard and creative studio candidate, with Lum/Yume continuity, source truth and bounded Godot handoff.",
    }
    public_origin = _origin()
    remote_godot_candidate = public_origin == MCP_COCKPIT_PUBLIC_ORIGIN
    godot_frame_origin = public_origin  # same exact-commit Render build
    experience = json.loads(experience_path.read_text(encoding="utf-8"))
    artist_studio = json.loads(artist_studio_path.read_text(encoding="utf-8"))
    rebel_studio = json.loads(rebel_studio_path.read_text(encoding="utf-8"))
    crown_flow = json.loads(crown_flow_path.read_text(encoding="utf-8"))
    runtime_receipt = json.loads(runtime_receipt_path.read_text(encoding="utf-8"))
    opening_day = json.loads(opening_day_path.read_text(encoding="utf-8"))
    api_spine = json.loads(api_spine_path.read_text(encoding="utf-8"))
    traffic_controller = json.loads(traffic_controller_path.read_text(encoding="utf-8"))
    precision_command = json.loads(precision_command_path.read_text(encoding="utf-8"))
    after_hours = json.loads(after_hours_path.read_text(encoding="utf-8"))
    coding_roleplay = json.loads(coding_roleplay_path.read_text(encoding="utf-8"))
    virgin_install = json.loads(virgin_install_path.read_text(encoding="utf-8"))
    beta_lanes = json.loads(beta_lane_path.read_text(encoding="utf-8"))
    if coding_roleplay.get("schema") != "luhmOs.codingRoleplayDirector.v2":
        raise RuntimeError("RED_CODING_ROLEPLAY_SCHEMA")
    if (beta_lanes.get("schema") != "luhmOs.pluginBetaFourLane.v1" or
        beta_lanes.get("inChatTarget", {}).get("resourceUri") != UI_RESOURCE_URI or
        beta_lanes.get("inChatTarget", {}).get("primarySurface") != "CHATGPT_APP_IN_CONVERSATION" or
        beta_lanes.get("release", {}).get("betaInviteSent") is not False or
        beta_lanes.get("release", {}).get("betaReleased") is not False):
        raise RuntimeError("RED_IN_CHAT_BETA_AUTHORITY_DRIFT")
    if virgin_install.get("schema") != "luhmOs.manualPluginVirginInstall.v1":
        raise RuntimeError("RED_VIRGIN_INSTALL_SCHEMA")
    if (rebel_studio.get("schema") != "luhmOs.rebelInChatStudio.v1" or
        rebel_studio.get("resourceUri") != UI_RESOURCE_URI or
        rebel_studio.get("tool") != "luhm_open_cockpit" or
        rebel_studio.get("project", {}).get("id") != "rebel" or
        rebel_studio.get("stateBoundary", {}).get("serverWrites") is not False or
        rebel_studio.get("stateBoundary", {}).get("publication") is not False or
        rebel_studio.get("stateBoundary", {}).get("clientMemoryOnly") is not True or
        rebel_studio.get("stateBoundary", {}).get("userInitiatedChatHandoffOnly") is not True or
        rebel_studio.get("crownStatus") != "STOP"):
        raise RuntimeError("RED_REBEL_CHAT_STUDIO_CONTRACT")
    if artist_studio.get("schema") != "luhmOs.artistStudioPlugin.v1" or artist_studio.get("pluginTool") != "luhm_open_cockpit" or artist_studio.get("resourceUri") != UI_RESOURCE_URI:
        raise RuntimeError("RED_ARTIST_STUDIO_CONTRACT")
    if artist_studio.get("stateBoundary", {}).get("serverWrites") is not False or artist_studio.get("stateBoundary", {}).get("publication") is not False:
        raise RuntimeError("RED_ARTIST_STUDIO_PRIVILEGE")
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
        title="LuHm OS Artist Studio",
        description="LuHm artist-first in-chat preproduction studio; local draft editing only, no server mutation or publication.",
        mime_type=APP_MIME_TYPE,
        meta=resource_meta,
    )
    def luhm_cockpit_resource() -> str:
        return _studio_page(harness_root, widget_path.read_text(encoding="utf-8"), widget=True)

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
                    "frameDomains": [godot_frame_origin] if godot_frame_origin else [],
                },
                **({"domain": public_origin} if public_origin else {}),
            },
            "openai/ui": {"availableDisplayModes": ["inline", "fullscreen"]},
            "openai/widgetDescription": "LuHm Godot 4 gameplay viewer; no builds or privileged actions.",
        },
    )
    def luhm_godot_player_resource() -> str:
        page = godot_player_path.read_text(encoding="utf-8")
        staged = _inspect_godot_bundle(godot_root)["ready"]
        if not public_origin or not staged:
            frame = '<p class="pending">Godot Web export not staged on this HTTPS origin. Player is waiting for exact-source CAST proof.</p>'
        else:
            url = html.escape(godot_frame_origin + "/harness/godot-export/index.html", quote=True)
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
        staged = _inspect_godot_bundle(godot_root)["ready"]
        return {
            "schema": "luhmOs.inChatGodotPlayer.v1",
            "resourceUri": GODOT_PLAYER_RESOURCE_URI,
            "state": "WEB_EXPORT_FILES_STAGED" if staged and public_origin else "PENDING_EXPORT_OR_HTTPS_ORIGIN",
            "bundleIntegrity": "SHA256_PASS" if staged else "UNVERIFIED",
            "runtimeVerifiedInChat": False,
            "sourceRef": "EXACT_BUILD_RECEIPT_REQUIRED",
            "readOnly": True,
            "buildAuthority": False,
            "crownStatus": "STOP",
        }

    @server.tool(
        name="luhm_open_cockpit",
        title="Open LuHm OS Artist Studio",
        description="Open the artist-first in-chat storyboard studio with in-session edits and read-only system status. No remote writes or publication.",
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
            "artistStudio": artist_studio,
            "rebelStudio": rebel_studio,
            "embeddedStudio": _studio_contract(root),
            "crownFlow": crown_flow,
            "runtimeReceipt": runtime_receipt,
            "openingDay": opening_day,
            "apiSpine": api_spine,
            "trafficController": traffic_controller,
            "precisionCommands": precision_command,
            "afterHours": after_hours,
            "codingRoleplay": coding_roleplay,
            "virginInstall": virgin_install,
            "betaLanes": beta_lanes,
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
        return Response(
            _studio_page(harness_root, index_path.read_text(encoding="utf-8")),
            media_type="text/html; charset=utf-8",
            headers=_headers(html=True, production=profile_provider() == "production"),
        )

    @server.custom_route("/harness/assets/{asset_path:path}", methods=["GET", "HEAD"])
    async def harness_asset(request: Request) -> Response:
        relative = request.path_params.get("asset_path", "")
        allowed = {"studioDeck.css", "studioDeck.js", "cockpit.css", "cockpit.js", "titan7Cockpit.js", "jquery-3.7.1.min.js", "jquery-ui-1.14.2.min.js", "agent-loading-sprites.json", "agent-roster-v1.png"}
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
                "artistStudio": artist_studio,
                "embeddedStudio": _studio_contract(root),
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
            headers=_headers(dynamic=True),
        )

    @server.custom_route("/harness/pets.json", methods=["GET"])
    async def harness_pets(_: Request) -> Response:
        return JSONResponse(json.loads(pets_path.read_text(encoding="utf-8")), headers=_headers(dynamic=True))

    @server.custom_route("/harness/godot-readiness.json", methods=["GET", "HEAD"])
    async def godot_readiness(_: Request) -> Response:
        result = _inspect_godot_bundle(godot_root)
        return JSONResponse({
            "schema": "luhmOs.godotEmbedReadiness.v1",
            **result,
            "exactOrigin": public_origin or "LOCAL_ONLY",
            "browserRuntimeProven": False,
            "androidDeviceProven": False,
            "privateDonorIncluded": False,
        }, headers=_headers(dynamic=True, production=profile_provider() == "production"))
    @server.custom_route("/harness/godot-export/{asset_path:path}", methods=["GET", "HEAD"])
    async def godot_asset(request: Request) -> Response:
        relative = request.path_params.get("asset_path", "")
        target = _safe_file(godot_root, relative)
        if target is None or not _inspect_godot_bundle(godot_root)["ready"]:
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
