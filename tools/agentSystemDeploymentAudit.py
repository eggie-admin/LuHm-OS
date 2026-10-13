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
company_quarantine = load("doctrine/companyWideOperationalQuarantineV1.json")
need(company_quarantine.get("schema") == "luhmOs.companyWideOperationalQuarantine.v1", "company quarantine schema drift")
need(company_quarantine.get("registeredAgents") == required, "company quarantine roster drift")
company_held = company_quarantine.get("state") == "QUARANTINED"
quarantine_path = ROOT / "doctrine/belldandyOperationalQuarantineV1.json"
quarantine = json.loads(quarantine_path.read_text(encoding="utf-8"))
need(quarantine.get("schema") == "luhmOs.belldandyOperationalQuarantine.v1", "quarantine schema drift")
need(quarantine.get("subject") == "belldandySecretary", "quarantine subject drift")
need(quarantine.get("state") in {"QUARANTINED", "CLEARED"}, "quarantine state invalid")
quarantined = quarantine.get("state") == "QUARANTINED"
route_kinds = ["direct","read","records","proof","patch","build","external","diagnose","research","monitor","release","art","media","mediaFactory","dictation","asset"]
allowed = set(required) | {"ProfessorCrown"}
routes: dict[str, list[str]] = {}
for kind in route_kinds:
    run = subprocess.run([sys.executable, str(router), kind], cwd=ROOT, check=True, capture_output=True, text=True)
    payload = json.loads(run.stdout)
    workers = payload.get("workers", [])
    routes[kind] = workers
    need(all(worker in allowed for worker in workers), f"{kind}: noncanonical worker in route: {workers}")
if company_held:
    need(all(not worker_list for worker_list in routes.values()), "company-wide quarantine leaked an active worker")
else:
    need(routes.get("art") == ["lum","yume"], "art route must resolve Lum + Yume")
    need(routes.get("mediaFactory") == ["lum","yume","mediaAssetFactory"], "media factory must remain Lum/Yume candidate-only")
    expected_monitor = ["lum","urdDoctorGoddess","skuldResearch"] if quarantined else ["lum","urdDoctorGoddess","belldandySecretary","skuldResearch"]
    need(routes.get("monitor") == expected_monitor, "monitor route quarantine drift")
    need({"tetsu","kaji"}.issubset(routes.get("build", [])), "build route missing forge Oni twins")
    need("urdDoctorGoddess" in routes.get("proof", []), "proof route missing Urd")
    expected_dictation = ["lum","koe"] if quarantined else ["lum","belldandySecretary","koe"]
    need(routes.get("dictation") == expected_dictation, "dictation route quarantine drift")
    need(routes.get("records") == (["lum","fumi"] if quarantined else ["lum","belldandySecretary","fumi"]), "records route quarantine drift")
    if quarantined:
        need(all("belldandySecretary" not in workers for workers in routes.values()), "quarantined secretary still routed")

# Full 15-agent behavioral/authority matrix. Skills inherit the shared protocol;
# absence of repeated envelope text in a short skill does not remove that contract.
protocol_text = (ROOT / "agents/shared/ONI_PROTOCOL_V2.md").read_text(encoding="utf-8")
for token in ("taskId", "sourceRef", "scopeId", "Lum", "Professor", "UNKNOWN", "crownStop"):
    need(token.lower() in protocol_text.lower(), f"shared reasoning/authority protocol missing: {token}")

for agent_id in required:
    role = agents[agent_id]
    skill_rel = role["skillPath"]
    skill = (ROOT / skill_rel).read_text(encoding="utf-8")
    need(skill_rel.startswith("agents/") and ".." not in Path(skill_rel).parts, f"{agent_id}: unsafe skill path")
    need(len(skill.strip()) >= 250, f"{agent_id}: skill body unexpectedly empty")
    need("doctrine/luhmAiControlPlaneV1.json" in skill, f"{agent_id}: canonical control-plane link missing")
    need(role.get("defaultAuthority") in control.get("authorityClasses", []), f"{agent_id}: unknown authority class")
    need(bool(role.get("capabilities")) and all(isinstance(x, str) and x for x in role.get("capabilities", [])),
         f"{agent_id}: declared capability contract missing")
    need(bool(role.get("forbidden")) and all(isinstance(x, str) and x for x in role.get("forbidden", [])),
         f"{agent_id}: forbidden-capability contract missing")
    need(role.get("speaksTo") == ("Professor" if agent_id == "lum" else "lum"),
         f"{agent_id}: unauthorized conversational authority")
    need(role.get("parallelClass") in {"boss", "support", "executor", "builder", "service"},
         f"{agent_id}: unknown parallel class")

for agent_id in ("urdDoctorGoddess", "belldandySecretary", "skuldResearch"):
    need(agents[agent_id]["defaultAuthority"] == "READ_ONLY", f"{agent_id}: cabinet authority drift")
for agent_id in ("tetsu", "kaji"):
    need(agents[agent_id]["defaultAuthority"] == "BUILD_EPHEMERAL", f"{agent_id}: builder authority drift")
need(agents["kugi"]["defaultAuthority"] == "PLAN_ONLY", "Kugi mutation not allowed by default")
for rel in ("agents/lum/SKILL.md", "agents/kugiToolOni/SKILL.md"):
    skill = (ROOT / rel).read_text(encoding="utf-8")
    need("Dr. Nao" not in skill, f"{rel}: retired adjudicator still owns active workflow")
    need("Urd Doctor Goddess" in skill, f"{rel}: current evidence adjudicator missing")

# A registered specialist must be addressable by at least one deliberate route,
# including the three documented opt-in diagnostic/research flags.
reachable = set(worker for workers in routes.values() for worker in workers)
for flag in ("--contested", "--external-fact", "--asset-review"):
    cp = subprocess.run([sys.executable, str(router), "read", flag], cwd=ROOT, capture_output=True, text=True)
    need(cp.returncode == 0, f"router rejected bounded {flag}")
    if cp.returncode == 0:
        extra = json.loads(cp.stdout)
        reachable.update(extra.get("workers", []))
        need(extra.get("greenAuthority") is False and extra.get("residentCabinetHiddenAsync") is False,
             f"{flag}: runtime-authority or hidden-async leak")
if company_held:
    need(reachable == set(), "company-quarantined workers were activated")
else:
    expected_reachable = set(required) - ({"belldandySecretary"} if quarantined else set())
    need(expected_reachable.issubset(reachable), f"unexpected unreachable active agents: {sorted(expected_reachable - reachable)}")
    if quarantined:
        need("belldandySecretary" not in reachable, "quarantined agent reachable in active route")
need(reachable.issubset(allowed), f"unregistered routing identity: {sorted(reachable - allowed)}")

for kind in route_kinds:
    cp = subprocess.run([sys.executable, str(router), kind], cwd=ROOT, capture_output=True, text=True)
    if cp.returncode == 0:
        payload = json.loads(cp.stdout)
        need(payload.get("greenAuthority") is False, f"{kind}: routing grants GREEN")
        need(payload.get("residentCabinetHiddenAsync") is False, f"{kind}: hidden runtime workers claimed")
        need(payload.get("sourceMutationLanes") in (0, 1), f"{kind}: mutable lane expansion")
        need(payload.get("parallelBuilds") in (0, 2), f"{kind}: unexpected build lane count")
        need(len(payload.get("supportWorkers", [])) <= 3, f"{kind}: support-worker overrun")
if company_held:
    need(routes.get("release") == [], "release route must be frozen")
    release_plan = json.loads(subprocess.run([sys.executable, str(router), "release"], cwd=ROOT, check=True, capture_output=True, text=True).stdout)
    need(release_plan.get("requiresProfessorCrown") is True, "frozen release still requires Professor")
else:
    need(routes.get("release") == ["lum","urdDoctorGoddess","ProfessorCrown"],
         "release must retain explicit Professor gate")
overbudget = subprocess.run(
    [sys.executable, str(router), "build", "--contested", "--external-fact", "--asset-review"],
    cwd=ROOT, capture_output=True, text=True,
)
if company_held:
    need(overbudget.returncode == 0 and json.loads(overbudget.stdout).get("workers") == [], "quarantine must suppress all overloaded work")
else:
    need(overbudget.returncode != 0 and "RED_ROUTER_SUPPORT_PARALLELISM_EXCEEDED" in (overbudget.stderr + overbudget.stdout),
         "parallelism overflow did not fail closed")
need(control.get("aiTaskManifest", {}).get("schema") == truth.get("manifestLaw", {}).get("currentAiTaskSchema")
     == "luhmOs.aiTaskManifest.v2", "agent reasoning input manifest schema drift")
need(control.get("taskManifest", {}).get("mayAuthorizeExecution") is False,
     "legacy manifest may not grant execution authority")

training_run = subprocess.run([sys.executable, str(ROOT / "tools/agentTrainingAudit.py")], cwd=ROOT, capture_output=True, text=True)
need(training_run.returncode == 0, "agentTrainingAudit failed")

if errors:
    print("AGENT_SYSTEM_DEPLOYMENT=RED")
    for error in errors:
        print("ERROR:", error)
    raise SystemExit(1)

print("AGENT_SYSTEM_DEPLOYMENT=GREEN_SOURCE_CANDIDATE")
print("registeredAgents=15")
print("behavioralSkillsAudited=15")
print("routingRegistryCoverage=15/15")
print("activeRouteCoverage=" + ("0/15_COMPANY_QUARANTINE" if company_held else ("14/15_URD_REVIEW_PENDING" if quarantined else "15/15")))
print("retiredAdjudicator=urdDoctorGoddess")
print("reasoningAudit=observableContractOnly")
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
