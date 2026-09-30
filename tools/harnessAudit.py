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

    widget = (HARNESS / "widget.html").read_text(encoding="utf-8")
    index = (HARNESS / "index.html").read_text(encoding="utf-8")
    script = (HARNESS / "cockpit.js").read_text(encoding="utf-8")
    module = MODULE.read_text(encoding="utf-8")
    presets = PRESETS.read_text(encoding="utf-8")
    libraries = json.loads((HARNESS / "libraryPolicy.json").read_text(encoding="utf-8"))
    pets = json.loads((HARNESS / "pets.json").read_text(encoding="utf-8"))
    donors = json.loads((HARNESS / "donorMutation.json").read_text(encoding="utf-8"))

    require("ui://luhm-os/cockpit-v1.html" in module, "RED_WIDGET_URI")
    require("text/html;profile=mcp-app" in module, "RED_WIDGET_MIME")
    require("luhm_open_cockpit" in module, "RED_RENDER_TOOL")
    require('"greenAuthority": False' in module, "RED_UI_GREEN_AUTHORITY")
    require('"publicationAuthority": False' in module, "RED_UI_PUBLICATION_AUTHORITY")
    require("godotEmbeddingInChat" in module and "False" in module, "RED_NESTED_FRAME_BOUNDARY")

    for text, label in ((widget, "WIDGET"), (index, "INDEX")):
        require(not re.search(r'<script[^>]+src=["\']https?://', text, re.I), f"RED_{label}_REMOTE_SCRIPT")
        require(not re.search(r'<link[^>]+href=["\']https?://', text, re.I), f"RED_{label}_REMOTE_STYLE")

    require(libraries.get("productionPolicy") == "vendored-or-self-hosted-only", "RED_LIBRARY_POLICY")
    require(libraries.get("chatWidgetExternalCdnAllowed") is False, "RED_CHAT_CDN_POLICY")
    require(libraries.get("allowedDevelopmentOrigins") == [], "RED_DEV_CDN_NOT_CLOSED")
    require(pets.get("spritePolicy") == "original-user-controlled-assets-only", "RED_PET_PROVENANCE")
    require(donors.get("mode") == "selective-reimplementation", "RED_DONOR_MODE")
    require(donors.get("serverUploadAuthority") is False, "RED_DONOR_UPLOAD_AUTHORITY")
    require(all(item.get("copyCode") is False for item in donors.get("donors", [])), "RED_DONOR_CODE_COPY")

    require('type="file"' in index and 'application/pdf' in index, "RED_LOCAL_FILE_INTAKE")
    require("URL.createObjectURL" in script and "URL.revokeObjectURL" in script, "RED_BLOB_LIFECYCLE")
    require("requestAnimationFrame" in script and "pointermove" in script, "RED_PARALLAX_REIMPLEMENTATION")
    require("treeBranch" in script and "aria-expanded" in script, "RED_TREE_REIMPLEMENTATION")
    require("imagePreview" in index and "videoPreview" in index and "pdfPreview" in index, "RED_MEDIA_DESK")
    require("FormData" not in script and "XMLHttpRequest" not in script and "sendBeacon" not in script, "RED_NETWORK_UPLOAD_PRIMITIVE")
    require(not re.search(r'fetch\s*\(\s*["\']https?://', script), "RED_REMOTE_FETCH")

    require("host/harness/godot-export/index.html" in presets, "RED_GODOT_EXPORT_TARGET")
    require("variant/thread_support=false" in presets, "RED_GODOT_THREAD_POLICY")
    require("permissions/internet=false" in presets, "RED_ANDROID_NETWORK_POLICY_DRIFT")
    require("/harness/godot-export/index.html" in index, "RED_GODOT_VIEWER_ROUTE")

    print("LUHM_RENDER_CHATGPT_HARNESS_GREEN")
    print("LUHM_ASSET_DESK_DONOR_MUTATION_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
