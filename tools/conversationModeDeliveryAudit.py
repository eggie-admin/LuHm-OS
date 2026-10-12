#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

def need(condition, label):
    if not condition:
        errors.append(label)

def load(rel):
    try:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"load:{rel}:{type(exc).__name__}")
        return {}

modes = load("doctrine/conversationModeRouterV1.json")
delivery = load("doctrine/npmPluginApkDeliveryV1.json")
truth = load("doctrine/currentSourceTruthV3.json")
experience = load("doctrine/inChatExperienceV1.json")
package = load("frontEnd/package.json")
lock = load("frontEnd/package-lock.json")
html = (ROOT / "frontEnd/index.html").read_text(encoding="utf-8")
apk_workflow = (ROOT / ".github/workflows/android-testing-build.yml").read_text(encoding="utf-8")

need(modes.get("schema") == "luhmOs.conversationModeRouter.v1", "mode:schema")
need(truth.get("conversationModes", {}).get("contract") == "doctrine/conversationModeRouterV1.json", "mode:sourceTruthPointer")
need(truth.get("conversationModes", {}).get("runtimeWired") is False, "mode:runtimeNotOverclaimed")
need(experience.get("sources", {}).get("conversationModeRouter") == "doctrine/conversationModeRouterV1.json", "mode:inChatContractPointer")
need(truth.get("packageDelivery", {}).get("contract") == "doctrine/npmPluginApkDeliveryV1.json", "delivery:sourceTruthPointer")
need([(x.get("tier"), x.get("id")) for x in modes.get("modes", [])] == [
    (0, "default"), (1, "ic"), (2, "ooc"), (3, "irl")
], "mode:zeroBasedOrder")
need(modes.get("axes", {}).get("orthogonal") is True, "mode:separateFromEscalation")
need(modes.get("transitionLaw", {}).get("icRequiresExplicitEntry") is True, "mode:icExplicit")
need(modes.get("transitionLaw", {}).get("directCorrectionLeavesIcImmediately") is True, "mode:oocExit")
need(modes.get("agentActivity", {}).get("onlyShowWorkerAsActiveWithMatchingTaskEvent") is True, "agents:eventBacked")
need(modes.get("agentActivity", {}).get("hiddenChainOfThought") is False, "agents:noHiddenReasoningClaim")
need(modes.get("providerGate", {}).get("unknownEntitlement") == "STOP_OR_DETERMINISTIC_FALLBACK", "providers:failClosed")
need(modes.get("providerGate", {}).get("credentialsNeverEnterUiOrRepository") is True, "providers:noCredentialLeak")
need(modes.get("uiContract", {}).get("runtime") == "staticHtml", "ui:static")
need(modes.get("uiContract", {}).get("godotInChat") is False, "ui:noGodotInChat")

need(delivery.get("schema") == "luhmOs.npmPluginApkDelivery.v1", "delivery:schema")
need(delivery.get("jquery", {}).get("exactDependency") == "jquery@3.7.1", "npm:jqueryPin")
need(delivery.get("jquery", {}).get("runtimeCdnAllowed") is False, "npm:noRuntimeCdn")
need(delivery.get("jquery", {}).get("arbitraryInstallScriptsAllowed") is False, "npm:noInstallScripts")
need(delivery.get("pluginLifecycle", {}).get("incomingCodeExecutes") is False, "npm:quarantine")
need(delivery.get("pluginLifecycle", {}).get("networkAndCredentialAccessFromPlugin") is False, "npm:pluginBoundary")
need(delivery.get("apkLifecycle", {}).get("npmInstallsApk") is False, "apk:separatePackageType")
need(delivery.get("apkLifecycle", {}).get("workflow") == ".github/workflows/android-testing-build.yml", "apk:workflowBinding")
need(delivery.get("apkLifecycle", {}).get("releaseRequires") and "singleUseCast" in delivery["apkLifecycle"]["releaseRequires"], "apk:castGate")
need(delivery.get("baseline", {}).get("npmLockfileWasMissingAtAudit") is True, "npm:baselineRecorded")
need(delivery.get("crownStatus") == "STOP", "delivery:crownStop")

need(package.get("private") is True, "npm:privatePackage")
need(package.get("dependencies", {}).get("jquery") == "3.7.1", "npm:manifestPin")
need(package.get("scripts", {}).get("ci") == "npm ci --ignore-scripts && npm run stage:jquery && npm run check", "npm:reproducibleCiScript")
need(lock.get("lockfileVersion") == 3, "npm:lockFormat")
need(lock.get("packages", {}).get("node_modules/jquery", {}).get("version") == "3.7.1", "npm:lockPin")
need(lock.get("packages", {}).get("node_modules/jquery", {}).get("integrity") == "sha512-m4avr8yL8kmFN8psrbFFFmB/If14iN5o9nw/NgnnM+kybDJpRsAynV2BsfpTYrTRysYUdADVD7CkUUizgkpLfg==", "npm:lockIntegrity")
need("vendor/jquery-3.7.1.min.js" in html, "jquery:localRuntime")
need("http://" not in html and "https://" not in html, "jquery:noRemoteHtmlScripts")
for rel in ("frontEnd/plugins/incoming/README.md", "frontEnd/plugins/approved/README.md", "frontEnd/plugins/local/README.md"):
    need((ROOT / rel).is_file(), f"pluginBay:{rel}")
need("workflow_dispatch:" in apk_workflow and "sourceRef:" in apk_workflow and "CAST gate" in apk_workflow, "apk:exactCastWorkflow")

report = {
    "schema": "luhmOs.conversationModeDeliveryAudit.v1",
    "status": "AMBER_CANDIDATE" if not errors else "RED_CANDIDATE",
    "modeIds": [x.get("id") for x in modes.get("modes", [])],
    "modeAxisIndependentFromEscalation": modes.get("axes", {}).get("orthogonal") is True,
    "jqueryVersion": lock.get("packages", {}).get("node_modules/jquery", {}).get("version"),
    "npmCi": package.get("scripts", {}).get("ci"),
    "apkBuildWorkflow": delivery.get("apkLifecycle", {}).get("workflow"),
    "providerEntitlementsProven": False,
    "agentProviderDeploymentProven": False,
    "inChatHostInvocationProven": False,
    "crownStatus": "STOP",
    "errors": errors
}
rendered = json.dumps(report, indent=2) + "\n"
parser = argparse.ArgumentParser()
parser.add_argument("--output")
args = parser.parse_args()
if args.output:
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8")
print(rendered, end="")
raise SystemExit(1 if errors else 0)
