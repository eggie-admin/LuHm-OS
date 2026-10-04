#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine" / "operationTitan7V1.json"
LAYERS = ROOT / "doctrine" / "luhmCompatibilityLayersV1.json"
WIDGET = ROOT / "host" / "harness" / "widget-v2.html"
SERVER = ROOT / "host" / "mcp" / "luhmMcpServer.py"
PLUGIN = ROOT / "frontEnd" / "jquery" / "operationTitan7.js"
MAX_FINAL_FORM_COMMITS = 50
MAX_AUDIT_PASSES = 100


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, timeout=10).strip()


def load(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def one_pass(contract: dict, layers: dict) -> tuple[dict[str, bool], list[str]]:
    checks: dict[str, bool] = {}
    checks["canonicalName"] = contract.get("canonicalName") == "operationTitan7"
    checks["jqueryEntryPoint"] = contract.get("entryPoints", {}).get("jquery") == "jQuery.fn.operationTitan7"
    checks["defaultMode"] = contract.get("defaultMode") == "saneApproach"
    checks["finalFormCeiling"] = contract.get("escalation", {}).get("finalForm", {}).get("commitWindowMax") == MAX_FINAL_FORM_COMMITS
    checks["noAutoDeploy"] = contract.get("forbidden", []).count("autoDeploy") == 1
    checks["noScheduledRuns"] = contract.get("invocationLaw", {}).get("scheduledBackgroundRunsForbidden") is True
    checks["noPermanentFleet"] = contract.get("invocationLaw", {}).get("permanentWatchFleetForbidden") is True
    checks["fleetRunnerAbsent"] = not (ROOT / "tools" / "titan7WatchFleet.py").exists()
    checks["fleetManifestAbsent"] = not (ROOT / "doctrine" / "OPERATION_TITAN7_WATCH_FLEET_V1.json").exists()
    checks["fleetWorkflowAbsent"] = not (ROOT / ".github" / "workflows" / "operation-titan7-watch-fleet.yml").exists()
    titan_workflows = [p for p in (ROOT / ".github" / "workflows").glob("*titan7*") if p.is_file()]
    checks["noScheduledTitan7Workflow"] = all("schedule:" not in p.read_text(encoding="utf-8") for p in titan_workflows)
    checks["compatibilityLayerOne"] = layers.get("layerOne", {}).get("id") == "openAiCompatibilityLayer"
    checks["compatibilityLayerTwo"] = layers.get("layerTwo", {}).get("id") == "githubCompatibilityLayer"
    checks["providerResultsReturnToLum"] = layers.get("layerTwo", {}).get("allProviderResultsReturnTo") == "lum"
    checks["jqueryPluginEmitsInvocation"] = 'const pluginName = "operationTitan7"' in PLUGIN.read_text(encoding="utf-8") and "luhm:operationTitan7:invoke" in PLUGIN.read_text(encoding="utf-8")
    widget = WIDGET.read_text(encoding="utf-8")
    server = SERVER.read_text(encoding="utf-8")
    devcontainer = load(ROOT / ".devcontainer" / "devcontainer.json")
    checks["chatWidgetCallsTitan7Tool"] = 'name:"luhmOperationTitan7"' in widget
    checks["mcpToolIsReadOnly"] = '@server.tool(annotations=READ_ONLY_INTERNAL)\ndef luhmOperationTitan7(' in server
    checks["repoCodingEnvironment"] = (
        "python" in devcontainer.get("image", "").lower()
        and devcontainer.get("features", {}).get("ghcr.io/devcontainers/features/node:1", {}).get("version") == "22"
        and "host/mcp/requirements.txt" in devcontainer.get("postCreateCommand", "")
        and "npm install --prefix frontEnd" in devcontainer.get("postCreateCommand", "")
    )
    return checks, [name for name, passed in checks.items() if not passed]


def audit(command: str, escalation: str, requested_passes: int | None) -> dict:
    contract = load(CONTRACT)
    layers = load(LAYERS)
    errors: list[str] = []
    escalation_spec = contract.get("escalation", {}).get(escalation, {})
    commit_limit = escalation_spec.get("commitWindowMax", MAX_FINAL_FORM_COMMITS)
    if not isinstance(commit_limit, int) or commit_limit < 1:
        commit_limit = MAX_FINAL_FORM_COMMITS
        errors.append("commitWindowMax")
    commit_limit = min(commit_limit, MAX_FINAL_FORM_COMMITS)

    if requested_passes is None:
        tier_passes = escalation_spec.get("auditPasses", 1)
        passes = tier_passes if isinstance(tier_passes, int) else 1
    else:
        passes = requested_passes
    if not isinstance(passes, int) or not 1 <= passes <= MAX_AUDIT_PASSES:
        errors.append("auditPassesOutOfRange")
        passes = min(max(passes if isinstance(passes, int) else 1, 1), MAX_AUDIT_PASSES)

    # Each pass independently reloads the source contracts and reevaluates every
    # control. The receipt distinguishes repeated pass count from unique controls.
    pass_failures: list[str] = []
    final_checks: dict[str, bool] = {}
    for pass_number in range(1, passes + 1):
        current_contract = load(CONTRACT)
        current_layers = load(LAYERS)
        final_checks, failed = one_pass(current_contract, current_layers)
        pass_failures.extend(f"pass{pass_number}:{name}" for name in failed)

    if pass_failures:
        errors.extend(pass_failures)
    commits = git("log", f"-n{commit_limit}", "--pretty=%H").splitlines()
    source_ref = git("rev-parse", "HEAD")
    supported = command in {"saneApproach", "dryRun"}
    if command in {"exit", "quit"}:
        status = "STOPPED"
    elif errors:
        status = "RED_OPERATION_TITAN7"
    elif not supported:
        status = "NOT_IMPLEMENTED_OPERATION_TITAN7"
        errors.append("commandNotImplemented")
    else:
        status = "READ_ONLY_AUDIT_PASS"

    return {
        "schema": "luhmOs.operationTitan7Receipt.v1",
        "status": status,
        "command": command,
        "escalation": escalation,
        "entryPoint": "jQuery.fn.operationTitan7",
        "sourceRef": source_ref,
        "commitWindowExamined": len(commits),
        "commitWindowMax": commit_limit,
        "auditPassesRequested": passes,
        "auditPassesCompleted": passes,
        "uniqueControlsPerPass": len(final_checks),
        "controlEvaluations": passes * len(final_checks),
        "checks": final_checks,
        "contractErrors": errors,
        "mutationAuthority": False,
        "mergeAuthority": False,
        "deployAuthority": False,
        "crownStatus": "STOP",
        "inspiredMutation": {
            "finalMilestoneProduced": "chatGptOperationTitan7ReadOnlyAudit",
            "nextInspiredMutation": "deployIsolatedCandidateAfterExactSourceCi"
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(prog="operationTitan7")
    parser.add_argument("command", choices=["saneApproach", "dryRun", "update", "upgrade", "distro", "apply", "continue", "continueAll", "exit", "quit"])
    parser.add_argument("--escalation", choices=["forFuckSake", "scorchedEarth", "finalForm"], default="forFuckSake")
    parser.add_argument("--passes", type=int, default=None, help="number of complete doctrine audit passes (maximum 100)")
    parser.add_argument("--json", dest="json_path", default="build/operationTitan7/receipt.json")
    args = parser.parse_args()
    try:
        receipt = audit(args.command, args.escalation, args.passes)
    except Exception as exc:
        print(json.dumps({"schema":"luhmOs.operationTitan7Receipt.v1","status":"RED_OPERATION_TITAN7","error":type(exc).__name__,"mutationAuthority":False,"crownStatus":"STOP"}, indent=2))
        return 1
    output = json.dumps(receipt, indent=2)
    if args.json_path != "-":
        out = ROOT / args.json_path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 1 if receipt["contractErrors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
