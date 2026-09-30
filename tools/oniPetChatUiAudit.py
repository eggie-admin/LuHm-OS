#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine" / "ONI_PET_CHAT_UI_V1.json"
WRAPPER = ROOT / "host" / "mcp" / "luhmMcpAppServer.py"
HTML = ROOT / "host" / "mcp" / "ui" / "oniPetDock.html"
KAI = ROOT / "native" / "kaiwebview" / "kaiwebview" / "src" / "main" / "java" / "art" / "eggiebagelface" / "luhmos" / "kaiwebview" / "KAIWebView.kt"
SHIZUKU = KAI.with_name("ShizukuCapabilityProbe.kt")
GRADLE = ROOT / "native" / "kaiwebview" / "kaiwebview" / "build.gradle.kts"
RENDER = ROOT / "render.yaml"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit("RED_ONI_PET_CHAT_UI: " + message)


def main() -> int:
    for path in (DOCTRINE, WRAPPER, HTML, KAI, SHIZUKU, GRADLE, RENDER):
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    doctrine = json.loads(DOCTRINE.read_text(encoding="utf-8"))
    require(doctrine["status"] == "CANDIDATE_SOURCE_NOT_RUNTIME_PROVEN", "status overclaims runtime proof")
    require(doctrine["chatgpt"]["maxVisibleHelpers"] == 3, "visible helper cap drift")
    require(doctrine["chatgpt"]["toolReadOnly"] is True, "pet tool is not read-only")
    require(doctrine["chatgpt"]["widgetOwnsAuthority"] is False, "widget gained authority")
    require(doctrine["android"]["mode"] == "DETECT_ONLY", "Shizuku mode is not detect-only")
    for key in ("permissionRequest", "genericShell", "secureFolderBypass", "silentInstall", "mutationAuthority"):
        require(doctrine["android"][key] is False, f"Shizuku authority creep: {key}")

    wrapper = WRAPPER.read_text(encoding="utf-8")
    require('PET_URI = "ui://luhm/oni-pet-dock-v1.html"' in wrapper, "MCP Apps resource URI missing")
    require('"resourceUri": PET_URI' in wrapper, "tool is not bound to UI resource")
    require('"visibility": ["model", "app"]' in wrapper, "UI visibility contract missing")
    require('"evidenceState": "UNKNOWN"' in wrapper, "widget route may invent evidence state")
    require('"mutationAuthority": False' in wrapper, "MCP pet route mutation boundary missing")
    require('workers[:3]' in wrapper, "visible helper cap not enforced in server")

    html = HTML.read_text(encoding="utf-8")
    require("ui/notifications/tool-result" in html, "MCP Apps tool-result bridge missing")
    require("sendFollowUpMessage" in html and "ui/message" in html, "follow-up message bridge missing")
    require("prefers-reduced-motion" in html, "reduced-motion handling missing")
    require("tools/call" not in html, "pet UI should not call arbitrary tools")

    probe = SHIZUKU.read_text(encoding="utf-8")
    require("Shizuku.pingBinder()" in probe, "binder probe missing")
    require("Shizuku.checkSelfPermission()" in probe, "permission-state probe missing")
    for forbidden in ("requestPermission", "newProcess", "bindUserService", "Runtime.getRuntime", "ProcessBuilder"):
        require(forbidden not in probe, f"forbidden Shizuku action present: {forbidden}")

    kai = KAI.read_text(encoding="utf-8")
    require('fun shizukuCapabilityStatus()' in kai, "Godot-visible Shizuku status method missing")
    require('.put("shizuku", ShizukuCapabilityProbe.snapshot())' in kai, "WebGlass status does not include Shizuku probe")

    gradle = GRADLE.read_text(encoding="utf-8")
    require('val shizukuVersion = "13.1.5"' in gradle, "Shizuku version pin drift")
    require('implementation("dev.rikka.shizuku:api:$shizukuVersion")' in gradle, "Shizuku API dependency missing")
    require('implementation("dev.rikka.shizuku:provider:$shizukuVersion")' in gradle, "Shizuku provider dependency missing")

    render = RENDER.read_text(encoding="utf-8")
    require("luhmMcpAppServer.py --check" in render, "app server source check missing")
    require("startCommand: python host/mcp/luhmMcpAppServer.py streamable-http" in render, "Render does not start Apps entrypoint")

    print("ONI_PET_CHAT_UI_SOURCE_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
