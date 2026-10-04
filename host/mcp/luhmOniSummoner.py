#!/usr/bin/env python3
"""Read-only LuHm Oni Summoner MCP Apps surface.

The UI can inspect every canonical Lum/Oni role and emit a bounded summon request.
A summon request is not execution. Lum remains the only router, and the Professor
retains Crown authority. Activity text is an observed-status summary, never hidden
model chain-of-thought.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

ONI_SUMMONER_UI_RESOURCE_URI = "ui://luhm-os/oni-summoner-v1.html"
APP_MIME_TYPE = "text/html;profile=mcp-app"
_ACTIVITY_STATES = {"PARKED", "QUEUED", "ACTIVE", "WAITING", "VERIFYING", "SUCCESS", "ERROR"}


def _text(value: Any, maximum: int) -> str:
    text = " ".join(str(value if value is not None else "").split())
    return text[:maximum] if text else "UNKNOWN"


def _role_index(roster: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = roster.get("roles", []) if isinstance(roster, dict) else []
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key in ("agentId", "displayName", "name"):
            alias = str(row.get(key, "")).strip()
            if alias:
                out[alias] = row
    return out


def register_oni_summoner(
    server: Any,
    *,
    root: Path,
    annotations: Any,
    status_provider: Callable[[], dict[str, Any]],
    roster_provider: Callable[[], dict[str, Any]],
) -> None:
    widget_path = root / "host" / "harness" / "oni-summoner-widget.html"
    if not widget_path.is_file():
        raise RuntimeError("RED_ONI_SUMMONER_WIDGET_MISSING")

    resource_meta = {
        "ui": {
            "prefersBorder": True,
            "csp": {"connectDomains": [], "resourceDomains": []},
        },
        "openai/ui": {"availableDisplayModes": ["inline", "fullscreen"]},
        "openai/widgetDescription": (
            "LuHm Oni Summoner: inspect canonical Oni roles, request one through Lum, "
            "and display observed workflow activity without granting execution authority."
        ),
    }

    @server.resource(
        ONI_SUMMONER_UI_RESOURCE_URI,
        name="luhm-oni-summoner",
        title="LuHm Oni Summoner",
        description="Read-only Lum/Oni roster, summon-request, skill, and observed-activity cockpit.",
        mime_type=APP_MIME_TYPE,
        meta=resource_meta,
    )
    def luhm_oni_summoner_resource() -> str:
        return widget_path.read_text(encoding="utf-8")

    @server.tool(
        name="luhm_open_oni_summoner",
        title="Open LuHm Oni Summoner",
        description=(
            "Render the read-only Oni Summoner GUI. Use it to inspect canonical roles, skills, "
            "authority, and observed activity. It never starts a worker or grants GREEN/Crown authority."
        ),
        annotations=annotations,
        meta={
            "ui": {
                "resourceUri": ONI_SUMMONER_UI_RESOURCE_URI,
                "visibility": ["model", "app"],
            },
            "openai/outputTemplate": ONI_SUMMONER_UI_RESOURCE_URI,
            "openai/toolInvocation/invoking": "Opening the Oni Summoner…",
            "openai/toolInvocation/invoked": "Oni Summoner ready.",
        },
    )
    def luhm_open_oni_summoner() -> dict[str, Any]:
        roster = roster_provider()
        return {
            "schema": "luhm-os.oni-summoner-view.v1",
            "status": status_provider(),
            "roster": roster,
            "activity": [
                {
                    "oni": "Lum",
                    "state": "PARKED",
                    "summary": "No observed task packet is active. The crew is parked.",
                    "taskId": "UNKNOWN",
                    "sourceRef": "UNKNOWN",
                }
            ],
            "thinkingEcho": "OBSERVED_ACTIVITY_SUMMARY_ONLY_NO_HIDDEN_CHAIN_OF_THOUGHT",
            "authority": {
                "readOnly": True,
                "mutationAuthority": False,
                "greenAuthority": False,
                "publicationAuthority": False,
                "releaseAuthority": False,
                "productionSigningAuthority": False,
                "crownStatus": "STOP",
            },
        }

    @server.tool(
        name="luhm_request_oni",
        title="Request an Oni through Lum",
        description=(
            "Create a bounded read-only summon request for one canonical Oni. This does not start "
            "execution. Lum must still resolve the task and choose the actual worker route."
        ),
        annotations=annotations,
        meta={"ui": {"visibility": ["model", "app"]}},
    )
    def luhm_request_oni(
        name: str,
        intentSummary: str = "UNKNOWN",
        taskId: str = "UNKNOWN",
        sourceRef: str = "UNKNOWN",
        scopeId: str = "oni-summoner-ui",
    ) -> dict[str, Any]:
        roster = roster_provider()
        roles = _role_index(roster)
        requested_name = _text(name, 32)
        role = roles.get(requested_name)
        if role is None:
            raise ValueError("requested Oni is not in the canonical roster")

        activity = [
            {
                "oni": "Lum",
                "state": "QUEUED",
                "summary": f"Summon request received for {requested_name}. Lum must resolve the route before any worker executes.",
                "taskId": _text(taskId, 120),
                "sourceRef": _text(sourceRef, 160),
            },
            {
                "oni": requested_name,
                "state": "WAITING",
                "summary": "Waiting for Lum to issue a bounded task envelope backed by observed source and scope.",
                "taskId": _text(taskId, 120),
                "sourceRef": _text(sourceRef, 160),
            },
        ]
        if not all(item["state"] in _ACTIVITY_STATES for item in activity):
            raise RuntimeError("RED_ONI_ACTIVITY_STATE")

        return {
            "schema": "luhm-os.oni-summon-request.v1",
            "requestedOni": {
                "name": requested_name,
                "kind": role.get("kind", "UNKNOWN"),
                "defaultAuthority": role.get("defaultAuthority", "UNKNOWN"),
                "skillPath": role.get("skillPath", "UNKNOWN"),
                "skillPresent": bool(role.get("skillPresent", False)),
            },
            "intentSummary": _text(intentSummary, 280),
            "requestScope": {
                "taskId": _text(taskId, 120),
                "sourceRef": _text(sourceRef, 160),
                "scopeId": _text(scopeId, 120),
            },
            "boss": roster.get("boss", "Lum"),
            "requiresLumRouting": True,
            "executionStarted": False,
            "activity": activity,
            "thinkingEcho": "OBSERVED_ACTIVITY_SUMMARY_ONLY_NO_HIDDEN_CHAIN_OF_THOUGHT",
            "mutationAuthority": False,
            "greenAuthority": False,
            "crownStatus": "STOP",
        }
