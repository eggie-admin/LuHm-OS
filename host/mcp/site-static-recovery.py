"""Drop-in static MCP Apps recovery for the EXISTING Project Hydra Site backend.

This does not execute by landing in GitHub. To activate, install this function
in the owner-controlled Site server, REPLACING the Site's existing cockpit
registrations (never register duplicate tool names); redeploy that same Site.

The Site editor is not accessible via the current Project Hydra read-only tools.
No provider keys, remote networking, mutation or public distribution.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

APP_MIME = "text/html;profile=mcp-app"
RESOURCES = {
    "luhm_open_cockpit": "ui://luhm-os/cockpit-site-v4.html",
    "luhm_open_mobile_cockpit": "ui://luhm-os/mobile-cockpit-v2.html",
}
TEMPLATE = Path(__file__).resolve().parents[1] / "harness" / "site-static-recovery.html"
CSP = {"connectDomains": [], "resourceDomains": [], "frameDomains": []}


def static_html(template: Path = TEMPLATE) -> str:
    """Return the entire browser-readable resource without remote assets."""
    page = template.read_text(encoding="utf-8")
    if (len(page.encode("utf-8")) > 12_000
            or not page.lstrip().lower().startswith("<!doctype html")
            or 'method:"ui/initialize"' not in page
            or 'method:"ui/notifications/initialized"' not in page
            or "<script src=" in page
            or "https://" in page
            or "fetch(" in page):
        raise ValueError("RED_STATIC_CAST_RESOURCE")
    return page


def register_site_static_recovery(
    server: Any, *,
    status_provider: Callable[[], dict[str, Any]] | None = None,
    template: Path = TEMPLATE,
    annotations: Any = None,
) -> None:
    """Call ONLY from the authorized existing Site MCP server initialization.

    Do not combine with already-registered names. All resources and tools must
    be present on the SAME Site endpoint. The revised versioned URIs avoid
    stale iframe/template caches and preserve old assets for rollback.
    """
    page = static_html(template)
    for tool_name, uri in RESOURCES.items():
        @server.resource(
            uri,
            name="luhm-static-" + tool_name.replace("_", "-"),
            title="LuHm OS Static CAST Recovery",
            description="Inline static recovery card; no server mutations or remote media.",
            mime_type=APP_MIME,
            meta={"ui": {"prefersBorder": True, "csp": dict(CSP)},
                  "openai/widgetDescription": "Minimal Project Hydra mobile/static recovery."},
        )
        def _html_resource(_page=page) -> str:
            return _page

        @server.tool(
            name=tool_name,
            title="Open LuHm OS Static CAST",
            description="Return read-only source status and mount the simple local HTML cockpit.",
            annotations=annotations,
            meta={
                "ui": {"resourceUri": uri, "visibility": ["model", "app"]},
                "openai/outputTemplate": uri,
                "openai/toolInvocation/invoking": "Opening LuHm static cockpit...",
                "openai/toolInvocation/invoked": "LuHm status delivered; visual mount needs owner proof.",
            },
        )
        def _open_cockpit() -> dict[str, Any]:
            status = status_provider() if status_provider is not None else {}
            if not isinstance(status, dict):
                status = {}
            return {
                "schema": "luhmOs.siteStaticRecovery.v1",
                "surface": "mcp-app",
                "sourceRef": str(status.get("sourceRef", "UNVERIFIED"))[:80],
                "sourceTruth": str(status.get("sourceTruthStatus", "UNKNOWN"))[:80],
                "status": "HTML_RESOURCE_REGISTERED_CLIENT_MOUNT_UNVERIFIED",
                "readOnly": True,
                "agentExecution": False,
                "publication": False,
                "crown": "STOP",
                "message": "Static cockpit returned. Tap its Test touch button if the HTML card appears.",
            }
