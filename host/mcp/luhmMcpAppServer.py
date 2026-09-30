#!/usr/bin/env python3
"""LuHm MCP Apps entrypoint with the read-only Oni Pet Dock UI.

This wraps the existing hardened MCP server. The added UI is presentation-only:
it does not execute helpers, mutate source, request Shizuku permission, or gain Crown authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import luhmMcpServer as base

PET_URI = "ui://luhm/oni-pet-dock-v1.html"
PET_HTML = Path(__file__).with_name("ui").joinpath("oniPetDock.html")


@base.server.resource(
    PET_URI,
    name="luhm-oni-pet-dock",
    title="LuHm Oni Pet Dock",
    description="Read-only Lum/Oni activity card for ChatGPT MCP Apps hosts.",
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"prefersBorder": True}},
)
def oni_pet_dock_resource() -> str:
    return PET_HTML.read_text(encoding="utf-8")


def _helper_packet(worker: str, kind: str) -> dict[str, Any]:
    labels = {
        "Kiri": "context",
        "Tetsu": "build",
        "Kaji": "clean build",
        "Momo": "research",
        "Shiori": "critic",
        "Kugi": "tool plan",
        "DrNao": "verify",
        "Fumi": "records",
        "Sumi": "assets",
        "Koe": "dictation",
        "Yume": "art/media",
    }
    return {
        "id": worker,
        "role": labels.get(worker, kind),
        "state": "QUEUED",
        "label": labels.get(worker, kind),
    }


@base.server.tool(
    name="show_oni_pet_dock",
    title="Show LuHm Oni Pet Dock",
    description=(
        "Render Lum plus up to three Oni from a deterministic LuHm task route. "
        "This is display-only; QUEUED means selected by the router, not proven running. "
        "For patch/build/release routes, provide explicit taskId, sourceRef, and scopeId."
    ),
    annotations=base.READ_ONLY_INTERNAL,
    meta={
        "ui": {"resourceUri": PET_URI, "visibility": ["model", "app"]},
        "openai/outputTemplate": PET_URI,
        "openai/toolInvocation/invoking": "Calling the Oni to the dock…",
        "openai/toolInvocation/invoked": "Oni dock ready.",
    },
)
def show_oni_pet_dock(
    kind: str = "direct",
    taskId: str = "UNKNOWN",
    sourceRef: str = "UNKNOWN",
    scopeId: str = "UNKNOWN",
) -> dict[str, Any]:
    if kind not in base.ROUTE_KINDS:
        raise ValueError(f"unsupported task kind: {kind}")

    route = base.luhm_route_task(
        kind=kind,
        taskId=taskId,
        sourceRef=sourceRef,
        scopeId=scopeId,
    )
    workers = [name for name in route.get("workers", []) if name not in {"Lum", "ProfessorCrown"}]
    helpers = [_helper_packet(name, kind) for name in workers[:3]]
    hidden = max(0, len(workers) - len(helpers))
    phase = "CROWN_STOP" if route.get("requiresProfessorCrown") else "ROUTE"

    return {
        "schema": "luhm-os.oni-pet-chatgpt.v1",
        "boss": {"id": "Lum", "role": "boss", "state": "WAITING" if phase == "CROWN_STOP" else "ACTIVE", "label": "orchestrating"},
        "helpers": helpers,
        "hiddenRoutedOniCount": hidden,
        "maxVisibleHelpers": 3,
        "taskId": taskId,
        "sourceRef": sourceRef,
        "phase": phase,
        "evidenceState": "UNKNOWN",
        "route": {
            "kind": kind,
            "greenAuthority": False,
            "mutationAuthority": False,
            "requiresProfessorCrown": bool(route.get("requiresProfessorCrown", False)),
        },
        "androidCapabilities": {
            "shizuku": {
                "mode": "DETECT_ONLY",
                "liveState": "DEVICE_LOCAL_ONLY",
                "permissionRequestedByMcp": False,
                "genericShell": False,
                "secureFolderBypass": False,
                "mutationAuthority": False,
            }
        },
        "uiAuthority": False,
        "greenAuthority": False,
        "crownAuthority": False,
    }


def main() -> int:
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
