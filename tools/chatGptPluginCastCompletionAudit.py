#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
errors = []

def need(ok, msg):
    if not ok:
        errors.append(msg)

contract = json.loads((root / "doctrine/chatGptPluginCastCompletionV1.json").read_text())

need(contract.get("schema") == "luhmOs.chatGptPluginCastCompletion.v1", "completion schema drift")
need(contract.get("authority") == "Professor", "Professor authority drift")
need(contract.get("boss") == "lum", "Lum boss drift")
need(contract.get("command") == "CAST", "CAST command drift")
need(contract.get("status") == "ACTIVE_FAIL_CLOSED", "completion contract must fail closed")

sequence = contract.get("requiredSequence", [])
need(sequence == [
    "bindExactCurrentMain",
    "buildDeterministicPluginPackage",
    "verifyPackageShaAndReceipt",
    "installPluginInChatGptHost",
    "invokePluginInCurrentConversation",
    "observeLuhmOpenCockpitRuntimeReceipt",
    "declareCastGreen"
], "CAST completion sequence drift")

package = contract.get("substeps", {}).get("publicPluginPackage", {})
need(package.get("completion") == "PACKAGE_READY", "package substep completion drift")
never = set(package.get("neverEquals", []))
for forbidden in (
    "CHATGPT_INSTALLED",
    "CURRENT_CHAT_ATTACHED",
    "CURRENT_CHAT_INVOKED",
    "CAST_GREEN",
    "PUBLIC_DIRECTORY_PUBLISHED",
):
    need(forbidden in never, f"package may be confused with forbidden final state: {forbidden}")

host = contract.get("chatGptHost", {})
need(host.get("preferredInstaller") == "Plugin Creator", "host installer drift")
need(host.get("requiredRuntimeTool") == "luhm_open_cockpit", "runtime tool drift")
need(host.get("githubMayNotForgeHostProof") is True, "GitHub host-proof forgery guard missing")

law = contract.get("automationLaw", {})
need(law.get("fastPath") is True, "FAST_PATH drift")
need(law.get("automaticUntilExternalHostBoundary") is True, "automatic boundary drift")
need(law.get("whenChatGptHostInstallerCapabilityExists") == "use it automatically after package verification", "host automation drift")
need(law.get("whenChatGptHostInstallerCapabilityIsUnavailable") == "STOP_AT_HOST_INSTALL_BOUNDARY_WITHOUT_CAST_GREEN", "missing fail-closed host boundary")
need(law.get("packageSuccessMustNotBeReportedAsFinalCast") is True, "package/final CAST conflation guard missing")
need(law.get("unknownNeverBecomesGreen") is True, "UNKNOWN may not become GREEN")

success = contract.get("success", {})
required = set(success.get("castGreenRequiresAll", []))
for key in (
    "exactCurrentMainBound",
    "packageReceiptGreen",
    "chatGptHostInstallProved",
    "currentConversationInvocationProved",
    "luhmOpenCockpitRuntimeProved",
):
    need(key in required, f"CAST GREEN missing requirement: {key}")

need(success.get("crownAuthority") is False, "CAST must not grant Crown")
need(contract.get("publicDirectoryTrack", {}).get("separateFromCurrentChatCast") is True, "directory lane must stay separate")
need(contract.get("crownStatus") == "STOP", "Crown must remain STOP")

print(json.dumps({
    "schema": "luhmOs.chatGptPluginCastCompletionAudit.v1",
    "status": "GREEN_CAST_COMPLETION_SOURCE" if not errors else "RED_CAST_COMPLETION_SOURCE",
    "errors": errors,
    "crownStatus": "STOP",
}, indent=2))
raise SystemExit(1 if errors else 0)
