"""Additive animation antenna tools; no device, provider or execution authority."""
import importlib.util
import os
from pathlib import Path
from typing import Any

URI = "ui://luhm-os/antenna-v1.html"
MAX_WIDGET_BYTES = 262144


def antenna_status(root):
    import json
    canon = json.loads((Path(root) / "doctrine/samsungAntennaV1.json").read_text())
    if canon.get("schema") != "luhmOs.samsungAntenna.v1":
        raise ValueError("Invalid antenna source contract")
    labels = {"termux": "Termux control plane", "termuxX11": "Local X11 display",
              "shizuku": "Permission-gated Android bridge", "usb": "USB diagnostics",
              "bluetooth": "Bluetooth diagnostics", "media": "VLC / HTML5 media",
              "wifi": "Wi-Fi diagnostics", "cellular": "Cellular connectivity diagnostics",
              "ai": "Edge / local AI adapters", "animation": "Godot / Babylon animation"}
    return {"schema": "luhmOs.antennaStatus.v1", "sourceRef": os.environ.get("RENDER_GIT_COMMIT", "UNKNOWN"),
            "executionEnabled": False, "gameWork": "onHold", "focus": "characterAnimation",
            "services": [{"id": key, "label": label, "status": "SOURCE_BOUNDARY_RUNTIME_UNVERIFIED"}
                         for key, label in labels.items()],
            "sourceContract": "doctrine/samsungAntennaV1.json",
            "phoneConnectionProven": False, "animationRuntimeProven": False}


def register_antenna(server, *, root, annotations):
    root = Path(root)
    spec = importlib.util.spec_from_file_location("luhmAntennaPlanner", root / "tools/kai9000Antenna.py")
    planner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(planner)

    @server.resource(URI, name="luhm-animation-antenna", title="LuHm Animation Antenna",
                     mime_type="text/html;profile=mcp-app",
                     meta={"ui": {"prefersBorder": True, "csp": {"connectDomains": [], "resourceDomains": [], "frameDomains": []}}})
    def antenna_resource():
        bundle = root / "frontEnd/prototypes/glassWorld/dist/antennaWidget.html"
        if not bundle.is_file():
            return "<!doctype html><html lang='en'><meta charset='utf-8'><p>Animation antenna build pending. Source status remains available through the tool.</p></html>"
        if bundle.is_symlink() or not 0 < bundle.stat().st_size <= MAX_WIDGET_BYTES:
            raise ValueError("Widget build violates budget")
        return bundle.read_text(encoding="utf-8")

    @server.tool(name="luhm_open_antenna", title="Open Animation Antenna",
                 description="Inspect source-backed antenna services; not a phone connection or runtime proof.",
                 annotations=annotations,
                 meta={"ui": {"resourceUri": URI, "visibility": ["model", "app"]}, "openai/outputTemplate": URI})
    def open_antenna() -> dict[str, Any]:
        return antenna_status(root)

    @server.tool(name="luhm_plan_antenna_creation", title="Prepare Animation Creation Plan",
                 description="Prepare an offline typed creative plan. Does not generate media, execute tools or call AI providers.",
                 annotations=annotations, meta={"ui": {"visibility": ["model", "app"]}})
    def plan_creation(recipe: str, target: str, brief: str) -> dict[str, Any]:
        return planner.creation_plan({"schema": "luhmOs.creationRequest.v1", "recipe": recipe,
                                      "target": target, "brief": brief})
