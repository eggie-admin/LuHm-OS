#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
errors = []

def load(rel):
    try:
        return json.loads((root / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{rel}: {exc}")
        return {}

def need(ok, message):
    if not ok:
        errors.append(message)

stream = load("doctrine/chatGptPluginWorkflowStreamV1.json")
repos = load("doctrine/activeRepositorySetV1.json")
agents = load("doctrine/agentSystemDeploymentV1.json")
final_form = load("doctrine/operationTitan7FinalFormV1.json")

need(stream.get("schema") == "luhmOs.chatGptPluginWorkflowStream.v1", "workflow stream schema drift")
need(stream.get("status") == "STANDBY_CANDIDATE", "workflow stream must remain standby candidate")
need(stream.get("authority") == "Professor", "Professor authority drift")
need(stream.get("boss") == "lum", "Lum boss drift")
need(stream.get("agentMesh") == "doctrine/agentSystemDeploymentV1.json", "agent mesh binding drift")
need(stream.get("repositorySet") == "doctrine/activeRepositorySetV1.json", "repository set binding drift")

activation = stream.get("activation", {})
need(activation.get("canonicalAgentCount") == 15, "workflow must bind 15 canonical agents")
need(activation.get("residentCore") == ["lum","urdDoctorGoddess","belldandySecretary","skuldResearch"], "resident core drift")
need(activation.get("maxParallelSupportWorkers") == 3, "support worker budget drift")
need(activation.get("oneMutableSourceLane") is True, "mutable source lane drift")
need(activation.get("recursiveRecruitment") is False, "recursive recruitment forbidden")
need(activation.get("hiddenAsyncExecution") is False, "hidden async forbidden")
need(activation.get("helpersSpeakTo") == "lum", "helper routing drift")

need(agents.get("requiredAgentCount") == 15, "agent deployment count drift")
need(len(agents.get("requiredAgents", [])) == 15, "agent deployment roster drift")
need(agents.get("activationLaw", {}).get("maxParallelSupportWorkers") == 3, "agent mesh parallelism drift")
need(agents.get("activationLaw", {}).get("oneMutableSourceLane") is True, "agent mesh mutable lane drift")
need(agents.get("activationLaw", {}).get("helpersSpeakTo") == "lum", "agent mesh boss routing drift")

active = repos.get("activeRepositories", [])
need(repos.get("schema") == "luhmOs.activeRepositorySet.v1", "repository set schema drift")
need(len(active) == 3, "active repository count must be three")
need([x.get("repository") for x in active] == [
    "eggie-admin/LuHm-OS",
    "eggie-admin/hydra-shell-android",
    "eggie-admin/vue-headless-cms"
], "active repository identities drift")
need(all(x.get("snapshotRef") for x in active), "active repository snapshot missing")
historical = repos.get("historicalUnavailableRepositories", [])
need(any(x.get("historicalName") == "KAI9000_LuHm_Compatibility" for x in historical), "historical fourth repository migration missing")
need(repos.get("backupLaw", {}).get("historicalUnavailableRepositoryMustNotBeInvented") is True, "missing-repo truth guard drift")

naming = stream.get("mcpToolNamingMigration", {})
need(naming.get("canonicalTool") == "luhmOpenCockpit", "canonical MCP tool name drift")
need(naming.get("legacyExternalAlias") == "luhm_open_cockpit", "legacy compatibility alias drift")
need(naming.get("migrationRequired") is True, "MCP naming migration must remain explicit")
need(naming.get("legacyAliasIsCanonical") is False, "legacy snake alias may not be canonical")
need(naming.get("newProjectOwnedSourceMayIntroduceSnakeCase") is False, "new project-owned snake_case forbidden")

standby = stream.get("standbyGate", {})
for key in (
    "requiresReconciliationMerge",
    "requiresExactMainCiAfterMerge",
    "requiresTitan7FinalFormGreenOnExactHead",
    "requiresAgentMeshGreenOnExactHead",
    "requiresWorkflowStreamAuditGreenOnExactHead",
):
    need(standby.get(key) is True, "standby gate missing: " + key)

deployment = stream.get("deployment", {})
need(deployment.get("renderUsedOnlyWhenGitHubCannotProvideRuntime") is True, "Render boundary drift")
need(deployment.get("automaticDeploy") is False, "automatic deploy forbidden")
need(deployment.get("automaticPublication") is False, "automatic publication forbidden")
need(deployment.get("automaticMerge") is False, "automatic merge forbidden")
need(deployment.get("productionSigningAuthority") is False, "production signing forbidden")

need(final_form.get("agentMesh") == "doctrine/agentSystemDeploymentV1.json", "Final Form agent mesh binding missing")
need(final_form.get("repositorySet") == "doctrine/activeRepositorySetV1.json", "Final Form repository set binding missing")
need(final_form.get("chatGptWorkflowStream") == "doctrine/chatGptPluginWorkflowStreamV1.json", "Final Form workflow stream binding missing")
need(stream.get("crownStatus") == "STOP", "Crown must remain STOP")

report = {
    "schema": "luhmOs.chatGptPluginWorkflowStreamAudit.v1",
    "status": "GREEN_CHATGPT_PLUGIN_WORKFLOW_STANDBY" if not errors else "RED_CHATGPT_PLUGIN_WORKFLOW_STANDBY",
    "registeredAgents": agents.get("requiredAgentCount"),
    "activeRepositories": len(active),
    "legacyMcpToolAlias": naming.get("legacyExternalAlias"),
    "canonicalMcpTool": naming.get("canonicalTool"),
    "errors": errors,
    "crownStatus": "STOP"
}
print(json.dumps(report, indent=2))
raise SystemExit(1 if errors else 0)
