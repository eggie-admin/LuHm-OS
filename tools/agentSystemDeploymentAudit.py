#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

deployment = load("doctrine/agentSystemDeploymentV1.json")
control = load("doctrine/luhmAiControlPlaneV1.json")
training = load("doctrine/agentTrainingSealV1.json")
chat = load("doctrine/projectChatCanonV1.json")
truth = load("doctrine/currentSourceTruthV3.json")
openai = load("doctrine/openAiDeploymentV3.json")

errors: list[str] = []
required = deployment.get("requiredAgents", [])
agents = control.get("agents", {})
resident = deployment.get("residentCore", [])
lazy = deployment.get("globallyAvailableLazyAgents", [])

def need(ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)

need(deployment.get("status") == "PROPOSED_SYSTEM_WIDE_AGENT_DEPLOYMENT", "deployment status drift")
need(deployment.get("workingLane") == "PROPOSED_ONLY", "deployment must remain proposed")
need(deployment.get("promotion") is False, "deployment promotion must remain false")
need(deployment.get("crownStatus") == "STOP", "deployment Crown must remain STOP")
need(deployment.get("requiredAgentCount") == 15, "requiredAgentCount must be 15")
need(len(required) == 15 and len(set(required)) == 15, "required roster must contain 15 unique agents")
need(set(required) == set(agents), "deployment roster must exactly match control-plane roster")
need(set(resident).isdisjoint(set(lazy)), "resident and lazy rosters must not overlap")
need(set(resident) | set(lazy) == set(required), "resident + lazy roster must cover all agents")
need(resident == ["lum", "urdDoctorGoddess", "belldandySecretary", "skuldResearch"], "resident core drift")
activation = deployment.get("activationLaw", {})
need(activation.get("residentCoreBoundToEveryActiveTaskEnvelope") is True, "resident core not bound to active task envelope")
need(activation.get("residentCoreHiddenAsync") is False, "resident core hidden async leak")
need(activation.get("oniDefaultState") == "standby", "Oni default state drift")
need(activation.get("standbyMeansRegisteredNotExecuting") is True, "standby background-execution ambiguity")
model = deployment.get("activationModel", {})
need(model.get("residentGoddessTriplet") == ["urdDoctorGoddess","belldandySecretary","skuldResearch"], "resident goddess triplet drift")
need(model.get("hiddenAsyncExecution") is False, "activation model hidden async leak")
need("yume" in lazy, "Yume must be globally available")
need(all(agent_id in lazy for agent_id in ("kiri","momo","shiori","kugi","tetsu","kaji","fumi","sumi","koe","mediaAssetFactory")), "Oni specialist availability drift")

for agent_id in required:
    role = agents.get(agent_id, {})
    skill_path = role.get("skillPath", "")
    need(bool(skill_path), f"{agent_id}: skillPath missing")
    need(bool(skill_path) and (ROOT / skill_path).is_file(), f"{agent_id}: skill missing: {skill_path}")
    need(role.get("mayRecruit") is False, f"{agent_id}: mayRecruit must be false")
    need(role.get("maySelfApprove") is False, f"{agent_id}: maySelfApprove must be false")

need(training.get("requiredAgents") == required, "training/deployment roster order drift")
need(training.get("expectedAgentCount") == 15, "training count drift")
need(training.get("trainingReadyForPortableDeployment") is True, "training not marked portable-ready")
need(training.get("trainingReadyDoesNotMeanLiveProviderDeployment") is True, "training/live deployment boundary missing")
need(training.get("deploymentContract") == "doctrine/agentSystemDeploymentV1.json", "training deployment contract drift")

system_registry = chat.get("systemAgentRegistry", {})
need(system_registry.get("contract") == "doctrine/agentSystemDeploymentV1.json", "project chat deployment contract drift")
need(system_registry.get("allCanonicalAgentsRegistered") is True, "project chat full roster not registered")
need(system_registry.get("hiddenAsyncExecution") is False, "project chat hidden async leak")
need(chat.get("alwaysLoadedCore", {}).get("agentSystemDeployment") == "doctrine/agentSystemDeploymentV1.json", "project chat deployment registry not always resolved")

agent_layer = truth.get("agentLayer", {})
need(agent_layer.get("deployment") == "doctrine/agentSystemDeploymentV1.json", "source truth agent deployment pointer drift")
need(agent_layer.get("rosterCount") == 15, "source truth roster count drift")
need(agent_layer.get("yumeAvailableSystemWide") is True, "source truth Yume availability drift")
need(agent_layer.get("oniMiniAgentsAvailableSystemWide") is True, "source truth Oni availability drift")
need(agent_layer.get("liveProviderDeploymentProven") is False, "source truth overclaims live provider deployment")
need(agent_layer.get("workingLane") == "PROPOSED_ONLY", "source truth agent layer must remain proposed")
need(agent_layer.get("crownStatus") == "STOP", "source truth agent Crown must remain STOP")

need(openai.get("agentSystemDeployment") == "doctrine/agentSystemDeploymentV1.json", "OpenAI adapter registry drift")
need(openai.get("architecture", {}).get("allCanonicalAgentsPortable") is True, "OpenAI adapter portable roster disabled")
need(openai.get("architecture", {}).get("providerSideWorkersProven") is False, "OpenAI provider workers overclaimed")
need(set(openai.get("architecture", {}).get("activeAgents", [])) == set(required), "OpenAI adapter roster drift")

surfaces = deployment.get("deploymentSurfaces", {})
for surface in ("projectChat","codingAgents","githubCopilot","pluginSkill","localMcp","remoteMcp","openAi","android"):
    need(surface in surfaces, f"deployment surface missing: {surface}")
need(surfaces.get("projectChat", {}).get("status") == "sourceConfigured", "projectChat source adapter not configured")
need(surfaces.get("codingAgents", {}).get("status") == "sourceConfigured", "coding-agent source adapter not configured")
need(surfaces.get("githubCopilot", {}).get("status") == "sourceConfigured", "Copilot source adapter not configured")
need(surfaces.get("pluginSkill", {}).get("status") == "sourceConfigured", "plugin skill source adapter not configured")
need(surfaces.get("localMcp", {}).get("status") == "sourceConfigured", "local MCP source adapter not configured")
need(surfaces.get("remoteMcp", {}).get("status") == "PENDING_LIVE_DEPLOYMENT_RECEIPT", "remote MCP truth boundary drift")
need(surfaces.get("openAi", {}).get("status") == "PENDING_PROVIDER_SIDE_RECEIPT", "OpenAI provider truth boundary drift")
need(surfaces.get("android", {}).get("localPythonAgentRuntime") is False, "Android must not host Python agent control plane")
need(surfaces.get("android", {}).get("providerSecretsInApk") is False, "Android provider secret boundary drift")

for path in (
    "agents/projectChatBootstrap/SKILL.md",
    "AGENTS.md",
    ".github/copilot-instructions.md",
    "plugins/luhm-os/skills/luhm-agent-workflow/SKILL.md",
):
    text = (ROOT / path).read_text(encoding="utf-8")
    need("agentSystemDeploymentV1.json" in text, f"{path}: deployment registry binding missing")

mcp_text = (ROOT / "host/mcp/luhmMcpServer.py").read_text(encoding="utf-8")
need('AGENT_DEPLOYMENT = ROOT / "doctrine" / "agentSystemDeploymentV1.json"' in mcp_text, "MCP deployment source missing")
need("def luhm_agent_deployment()" in mcp_text, "MCP deployment tool missing")
need("RED_AGENT_DEPLOYMENT_ROSTER_DRIFT" in mcp_text, "MCP deployment health gate missing")

router = ROOT / "tools/lumTaskRouter.py"
route_kinds = ["direct","read","records","proof","patch","build","external","diagnose","research","monitor","release","art","media","dictation","asset"]
allowed = set(required) | {"ProfessorCrown"}
routes: dict[str, list[str]] = {}
for kind in route_kinds:
    run = subprocess.run([sys.executable, str(router), kind], cwd=ROOT, check=True, capture_output=True, text=True)
    payload = json.loads(run.stdout)
    workers = payload.get("workers", [])
    routes[kind] = workers
    need(all(worker in allowed for worker in workers), f"{kind}: noncanonical worker in route: {workers}")
need(routes.get("art") == ["lum","yume"], "art route must resolve Lum + Yume")
need(routes.get("monitor") == ["lum","urdDoctorGoddess","belldandySecretary","skuldResearch"], "monitor route cabinet drift")
need({"tetsu","kaji"}.issubset(routes.get("build", [])), "build route missing forge Oni twins")
need("urdDoctorGoddess" in routes.get("proof", []), "proof route missing Urd")
need(routes.get("dictation") == ["lum","belldandySecretary","koe"], "dictation must route through Belldandy continuity before Koe handoff")

training_run = subprocess.run([sys.executable, str(ROOT / "tools/agentTrainingAudit.py")], cwd=ROOT, capture_output=True, text=True)
need(training_run.returncode == 0, "agentTrainingAudit failed")

if errors:
    print("AGENT_SYSTEM_DEPLOYMENT=RED")
    for error in errors:
        print("ERROR:", error)
    raise SystemExit(1)

print("AGENT_SYSTEM_DEPLOYMENT=GREEN_SOURCE_CANDIDATE")
print("registeredAgents=15")
print("residentCore=lum,urdDoctorGoddess,belldandySecretary,skuldResearch")
print("residentGoddessTriplet=urdDoctorGoddess,belldandySecretary,skuldResearch")
print("oniDefaultState=standby")
print("dictationContinuityOwner=belldandySecretary")
print("yume=globallyAvailableLazy")
print("oniMiniAgents=globallyAvailableLazy")
print("projectChat=sourceConfigured")
print("codingAgents=sourceConfigured")
print("githubCopilot=sourceConfigured")
print("pluginSkill=sourceConfigured")
print("localMcp=sourceConfigured")
print("remoteMcp=PENDING_LIVE_DEPLOYMENT_RECEIPT")
print("openAi=PENDING_PROVIDER_SIDE_RECEIPT")
print("android=PENDING_PHYSICAL_RUNTIME_PROOF")
print("modelWeightFineTuning=false")
print("crownStatus=STOP")
