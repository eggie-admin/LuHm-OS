#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "host" / "harness"
SERVER = ROOT / "host" / "mcp" / "luhmHarnessServer.py"
MODULE = ROOT / "host" / "mcp" / "luhmHarness.py"
PRESETS = ROOT / "export_presets.cfg"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def main() -> int:
    required = (
        HARNESS / "index.html",
        HARNESS / "widget.html",
        HARNESS / "widget-v2.html",
        HARNESS / "cockpit.css",
        HARNESS / "cockpit.js",
        HARNESS / "libraryPolicy.json",
        HARNESS / "pets.json",
        HARNESS / "donorMutation.json",
        SERVER,
        MODULE,
        PRESETS,
    )
    for path in required:
        require(path.is_file(), f"RED_HARNESS_MISSING:{path.relative_to(ROOT)}")

    widget = (HARNESS / "widget-v2.html").read_text(encoding="utf-8")
    legacy_widget = (HARNESS / "widget.html").read_text(encoding="utf-8")
    index = (HARNESS / "index.html").read_text(encoding="utf-8")
    script = (HARNESS / "cockpit.js").read_text(encoding="utf-8")
    module = MODULE.read_text(encoding="utf-8")
    presets = PRESETS.read_text(encoding="utf-8")
    libraries = json.loads((HARNESS / "libraryPolicy.json").read_text(encoding="utf-8"))
    pets = json.loads((HARNESS / "pets.json").read_text(encoding="utf-8"))
    donors = json.loads((HARNESS / "donorMutation.json").read_text(encoding="utf-8"))

    require('UI_RESOURCE_URI = "ui://luhm-os/cockpit-v2.html"' in module, "RED_WIDGET_V2_URI")
    require('LEGACY_UI_RESOURCE_URI = "ui://luhm-os/cockpit-v1.html"' in module, "RED_WIDGET_V1_COMPAT_URI")
    require("text/html;profile=mcp-app" in module, "RED_WIDGET_MIME")
    require("luhm_open_cockpit" in module, "RED_RENDER_TOOL")
    require('"openai/ui": {"entrypoints": [{"type": "thread"}]}' in module, "RED_THREAD_ENTRYPOINT")
    require('"greenAuthority": False' in module, "RED_UI_GREEN_AUTHORITY")
    require('"publicationAuthority": False' in module, "RED_UI_PUBLICATION_AUTHORITY")
    require("godotEmbeddingInChat" in module and "False" in module, "RED_NESTED_FRAME_BOUNDARY")

    for text, label in ((widget, "WIDGET_V2"), (legacy_widget, "WIDGET_V1"), (index, "INDEX")):
        require(not re.search(r'<script[^>]+src=["\']https?://', text, re.I), f"RED_{label}_REMOTE_SCRIPT")
        require(not re.search(r'<link[^>]+href=["\']https?://', text, re.I), f"RED_{label}_REMOTE_STYLE")

    for token in ("ui/initialize", "ui/notifications/initialized", "ui/notifications/tool-result", "ui/notifications/host-context-changed", "tools/call", "ui/message", "ui/update-model-context"):
        require(token in widget, f"RED_WIDGET_V2_MCP_APPS:{token}")
    for allowed_tool in ("luhm_status", "luhm_agent_roster"):
        require(f'name:"{allowed_tool}"' in widget, f"RED_WIDGET_V2_TOOL:{allowed_tool}")
    for forbidden in ("fetch(", "XMLHttpRequest", "WebSocket(", "sendBeacon(", "localStorage"):
        require(forbidden not in widget, f"RED_WIDGET_V2_FORBIDDEN:{forbidden}")

    require(libraries.get("productionPolicy") == "vendored-or-self-hosted-only", "RED_LIBRARY_POLICY")
    require(libraries.get("chatWidgetExternalCdnAllowed") is False, "RED_CHAT_CDN_POLICY")
    require(libraries.get("allowedDevelopmentOrigins") == [], "RED_DEV_CDN_NOT_CLOSED")
    require(pets.get("spritePolicy") == "original-user-controlled-assets-only", "RED_PET_PROVENANCE")
    require(donors.get("mode") == "selective-reimplementation", "RED_DONOR_MODE")
    require(donors.get("serverUploadAuthority") is False, "RED_DONOR_UPLOAD_AUTHORITY")
    require(all(item.get("copyCode") is False for item in donors.get("donors", [])), "RED_DONOR_CODE_COPY")

    require('type="file"' in index and 'application/pdf' in index, "RED_LOCAL_FILE_INTAKE")
    require(re.search(r'<iframe id="pdfPreview"[^>]*\bsandbox\b', index) is not None, "RED_PDF_SANDBOX")
    require("URL.createObjectURL" in script and "URL.revokeObjectURL" in script, "RED_BLOB_LIFECYCLE")
    require("requestAnimationFrame" in script and "pointermove" in script, "RED_PARALLAX_REIMPLEMENTATION")
    require("treeBranch" in script and "aria-expanded" in script, "RED_TREE_REIMPLEMENTATION")
    require("imagePreview" in index and "videoPreview" in index and "pdfPreview" in index, "RED_MEDIA_DESK")
    require("FormData" not in script and "XMLHttpRequest" not in script and "sendBeacon" not in script, "RED_NETWORK_UPLOAD_PRIMITIVE")
    require(not re.search(r'fetch\s*\(\s*["\']https?://', script), "RED_REMOTE_FETCH")

    require('h.endsWith(".localhost")' in script, "RED_LOCALHOST_ALIAS")
    require('h.endsWith(".onrender.com")' in script, "RED_RENDER_HOST_CLASSIFICATION")
    require("EXTERNAL / UNVERIFIED" in script, "RED_EXTERNAL_HOST_TRUTH")
    require("Render and IPv4 claims are not assumed" in script, "RED_EXTERNAL_RENDER_ASSUMPTION")

    require("host/harness/godot-export/index.html" in presets, "RED_GODOT_EXPORT_TARGET")
    require("variant/thread_support=false" in presets, "RED_GODOT_THREAD_POLICY")
    require("permissions/internet=false" in presets, "RED_ANDROID_NETWORK_POLICY_DRIFT")
    require("/harness/godot-export/index.html" in index, "RED_GODOT_VIEWER_ROUTE")

    print("LUHM_RENDER_CHATGPT_HARNESS_GREEN")
    print("LUHM_ASSET_DESK_DONOR_MUTATION_GREEN")
    print("LUHM_NETWORK_TRUTH_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
