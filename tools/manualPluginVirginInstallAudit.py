#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

rootPath = Path(__file__).resolve().parents[1]
errors = []

def need(conditionValue, messageValue):
    if conditionValue is False:
        errors.append(messageValue)

installDoc = json.loads((rootPath / "doctrine/manualPluginVirginInstallV1.json").read_text(encoding="utf-8"))
roleplayDoc = json.loads((rootPath / "doctrine/codingRoleplayDirectorV2.json").read_text(encoding="utf-8"))
pluginDoc = json.loads((rootPath / "plugins/luhm-os/plugin.json").read_text(encoding="utf-8"))
reviewDoc = json.loads((rootPath / "plugins/luhm-os/review-tests.json").read_text(encoding="utf-8"))
mcpDoc = json.loads((rootPath / "plugins/luhm-os/mcp.json").read_text(encoding="utf-8"))
roleplaySkill = (rootPath / "plugins/luhm-os/skills/luhm-coding-roleplay/SKILL.md").read_text(encoding="utf-8")
roleplayJs = (rootPath / "frontEnd/jquery/luhm.codingRoleplay.js").read_text(encoding="utf-8")
harness = (rootPath / "host/mcp/luhmHarness.py").read_text(encoding="utf-8")

need(installDoc.get("schema") == "luhmOs.manualPluginVirginInstall.v1", "virgin-install doctrine schema drift")
need(installDoc.get("installModel", {}).get("mode") == "virginInstall", "install mode drift")
need(installDoc.get("installModel", {}).get("oldPluginStateRequired") is False, "old plugin state became required")
need(installDoc.get("installModel", {}).get("migrationRequired") is False, "migration unexpectedly required")
need(installDoc.get("firstBoot", {}).get("defaultMode") == "normalChat", "first boot must default to normal chat")
need(installDoc.get("firstBoot", {}).get("oocAndIrlForcePlainConversation") is True, "OOC/IRL clean boundary missing")
need(pluginDoc.get("version") == "0.5.0", "plugin version drift")
need(pluginDoc.get("extensions", {}).get("com.openai", {}).get("interface", {}).get("capabilities") == ["Read"], "plugin lost read-only capability")
need(mcpDoc.get("mcpServers", {}).get("luhm", {}).get("url") == "https://luhm-os-harness-green.onrender.com/mcp", "manual package MCP endpoint drift")

need(roleplayDoc.get("sources", {}).get("sourceTruth") == "doctrine/currentSourceTruthV3.json", "roleplay no longer binds source truth")
need(roleplayDoc.get("sources", {}).get("chatCanon") == "doctrine/projectChatCanonV1.json", "roleplay no longer binds chat canon")
need(roleplayDoc.get("sources", {}).get("virginInstall") == "doctrine/manualPluginVirginInstallV1.json", "roleplay virgin-install binding missing")
need(roleplayDoc.get("modeRouting", {}).get("defaultMode") == "normalChat", "roleplay default mode drift")
need(roleplayDoc.get("modeRouting", {}).get("directTaskCorrectionForcesPlainConversation") is True, "direct-task correction boundary missing")
need(roleplayDoc.get("portablePlugin", {}).get("priorPluginStateRequired") is False, "portable roleplay requires prior plugin state")

for phrase in (
    "Normal ChatGPT is the default mode.",
    "OOC, IRL",
    "Unknown single-letter commands",
    "Virgin install law",
    "presentation only",
):
    need(phrase in roleplaySkill, f"portable roleplay skill missing: {phrase}")

for phrase in (
    "function configure(contract, sourceRef)",
    "luhm:roleplay:configure",
    'defaultMode !== "normalChat"',
    'authority: "presentationOnly"',
    "doctrineConfigured",
):
    need(phrase in roleplayJs, f"jQuery roleplay mutation missing: {phrase}")

for phrase in (
    'coding_roleplay_path = root / "doctrine" / "codingRoleplayDirectorV2.json"',
    'virgin_install_path = root / "doctrine" / "manualPluginVirginInstallV1.json"',
    '"codingRoleplay": coding_roleplay',
    '"virginInstall": virgin_install',
):
    need(phrase in harness, f"MCP virgin roleplay payload missing: {phrase}")

need(len(reviewDoc.get("positive", [])) == 5, "review positives must remain exactly five")
need(len(reviewDoc.get("negative", [])) == 3, "review negatives must remain exactly three")
need(any("coding roleplay" in row.get("prompt", "").lower() for row in reviewDoc.get("positive", [])), "review suite lacks coding roleplay test")

builder = subprocess.run([sys.executable, str(rootPath / "tools/buildManualPluginPackage.py")], cwd=rootPath, capture_output=True, text=True)
need(builder.returncode == 0, "manual plugin package builder failed")

archivePath = rootPath / "build/manual-plugin/luhm-os-manual-upload-0.5.0.zip"
need(archivePath.is_file(), "manual upload ZIP missing")

if archivePath.is_file():
    with zipfile.ZipFile(archivePath) as archive:
        names = set(archive.namelist())
        for required in (
            "plugin.json",
            "mcp.json",
            "README.md",
            "VIRGIN_INSTALL.md",
            "PRIVACY.md",
            "TERMS.md",
            "review-tests.json",
            "BUILD_RECEIPT.json",
            "SOURCE_MAP.json",
            "assets/logo.svg",
            "skills/luhm-agent-workflow/SKILL.md",
            "skills/belldandy-housekeeping/SKILL.md",
            "skills/luhm-coding-roleplay/SKILL.md",
        ):
            need(required in names, f"manual ZIP missing: {required}")
        for forbidden in (
            "mcp.local.json",
            "mcp.private.json",
            "mcp.remote.example.json",
            "DEPLOYMENT.md",
            "PUBLIC_SUBMISSION_DRAFT.md",
        ):
            need(forbidden not in names, f"manual ZIP leaked developer/private file: {forbidden}")
        need(all(name.startswith("luhm-os/") is False for name in names), "ZIP has an extra top-level luhm-os directory")
        combined = b"".join(archive.read(name) for name in names if name.endswith((".json",".md",".txt",".svg")))
        need(b"-----BEGIN PRIVATE KEY-----" not in combined, "private key material found in manual ZIP")
        need(b"127.0.0.1:8788" not in combined, "local MCP endpoint leaked into manual ZIP")

print(json.dumps({
    "schema": "luhmOs.manualPluginVirginInstallAudit.v1",
    "status": "GREEN_MANUAL_PLUGIN_VIRGIN_INSTALL" if not errors else "RED_MANUAL_PLUGIN_VIRGIN_INSTALL",
    "pluginVersion": pluginDoc.get("version"),
    "archive": "build/manual-plugin/luhm-os-manual-upload-0.5.0.zip",
    "errors": errors,
    "publicationAuthority": False,
    "mutationAuthority": False,
    "crownStatus": "STOP",
}, indent=2))
raise SystemExit(1 if errors else 0)
