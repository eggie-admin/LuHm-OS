#!/usr/bin/env python3
import json
import pathlib
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[1]
errors = []

def load(path):
    try:
        return json.loads((root / path).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path}: {exc}")
        return {}

def need(ok, message):
    if not ok:
        errors.append(message)

ff = load("doctrine/operationTitan7FinalFormV1.json")
milestone = load("doctrine/projectHydraFinalAuditMilestoneV1.json")
execution = load("doctrine/operationTitan7ExecutionSchemaV1.json")
trigger = load("doctrine/operationTitan7ChatTriggerV2.json")
eighth = load("doctrine/eighthNoteAgentScopeV1.json")
naming = load("doctrine/namingNamespaceCanonV1.json")
source_architecture = load("doctrine/modularSourceArchitectureV1.json")
cast_workflow = load("doctrine/castCommandWorkflowV1.json")
package_architecture = load("doctrine/luHmOSFourLayerArchitectureV1.json")
deployment = load("doctrine/agentSystemDeploymentV1.json")
repo_set = load("doctrine/activeRepositorySetV1.json")
workflow_stream = load("doctrine/chatGptPluginWorkflowStreamV1.json")

required_files = [
    "doctrine/luHmOSFourLayerArchitectureV1.json",
    "doctrine/agentSystemDeploymentV1.json",
    "doctrine/activeRepositorySetV1.json",
    "doctrine/chatGptPluginWorkflowStreamV1.json",
    "agents/lum/SKILL.md",
    "agents/urdMutationOni/SKILL.md",
    "agents/goddessSharedSystemsPractice/SKILL.md",
    "agents/witchingHourCoding/SKILL.md",
    "tools/fullSourceTruthAudit.py",
    "tools/hardSystemAudit200.py",
    "tools/agentSystemDeploymentAudit.py",
    "tools/chatGptPluginWorkflowStreamAudit.py",
    ".github/workflows/full-source-truth-audit.yml",
    ".github/workflows/titan7-final-form-reconciliation-audit.yml"
]
for path in required_files:
    need((root / path).is_file(), "missing " + path)

need(ff.get("authority") == "Professor", "final form authority")
need(ff.get("crownStatus") == "STOP", "candidate must stop at Crown")
need(ff.get("greenClaim") is False, "candidate may not self-green")
need(ff.get("baseMain") == "c6096b398eb226a2936c2332689dd87d034f39f7", "Final Form baseMain drift")
need(milestone.get("auditProtocol", {}).get("harness") == "operationTitan7", "final milestone not bound to Titan7")
need(milestone.get("auditProtocol", {}).get("retiredWatchFleet") is True, "retired Watch Fleet must remain retired")

need(ff.get("agentMesh") == "doctrine/agentSystemDeploymentV1.json", "Final Form agent mesh binding")
mesh = ff.get("agentMeshExecution", {})
need(mesh.get("canonicalAgentCount") == 15, "Final Form agent count drift")
need(mesh.get("residentCore") == ["lum","urdDoctorGoddess","belldandySecretary","skuldResearch"], "Final Form resident core drift")
need(mesh.get("lazySpecialistCount") == 11, "Final Form lazy specialist count drift")
need(mesh.get("maxParallelSupportWorkers") == 3, "Final Form support budget drift")
need(mesh.get("oneMutableSourceLane") is True, "Final Form mutable lane drift")
need(mesh.get("helpersSpeakTo") == "lum", "Final Form helper routing drift")
need(mesh.get("recursiveRecruitment") is False, "Final Form recursive recruitment forbidden")
need(mesh.get("hiddenAsyncExecution") is False, "Final Form hidden async forbidden")
need(mesh.get("retiredWatchFleet") is True, "Final Form must not revive Watch Fleet")

need(deployment.get("requiredAgentCount") == 15, "canonical deployment count drift")
need(len(deployment.get("requiredAgents", [])) == 15, "canonical deployment roster drift")
activation = deployment.get("activationLaw", {})
need(activation.get("maxParallelSupportWorkers") == 3, "deployment parallelism drift")
need(activation.get("oneMutableSourceLane") is True, "deployment mutable lane drift")
need(activation.get("helpersSpeakTo") == "lum", "deployment helper routing drift")
need(activation.get("recursiveRecruitment") is False, "deployment recursive recruitment drift")
need(activation.get("residentCoreHiddenAsync") is False, "deployment hidden async drift")

need(ff.get("repositorySet") == "doctrine/activeRepositorySetV1.json", "Final Form repository set binding")
need(repo_set.get("schema") == "luhmOs.activeRepositorySet.v1", "repository set schema drift")
need(len(repo_set.get("activeRepositories", [])) == 3, "repository set active count drift")
need(all(x.get("snapshotRef") for x in repo_set.get("activeRepositories", [])), "repository set snapshot missing")
need(any(x.get("historicalName") == "KAI9000_LuHm_Compatibility" for x in repo_set.get("historicalUnavailableRepositories", [])), "historical fourth repository disposition missing")

need(ff.get("chatGptWorkflowStream") == "doctrine/chatGptPluginWorkflowStreamV1.json", "Final Form ChatGPT workflow binding")
need(workflow_stream.get("status") == "STANDBY_CANDIDATE", "ChatGPT workflow must remain standby")
need(workflow_stream.get("agentMesh") == "doctrine/agentSystemDeploymentV1.json", "ChatGPT workflow agent mesh drift")

need(ff.get("executionSchema") == "doctrine/operationTitan7ExecutionSchemaV1.json", "Final Form execution schema binding")
need(ff.get("executionModes") == ["system","apply","test","all"], "execution mode grammar drift")
need(ff.get("milestoneConditionRequired") is True, "milestone condition not required")
need(list(execution.get("modes", {}).keys()) == ["system","apply","test","all"], "execution schema modes")
need(execution.get("milestoneCondition", {}).get("required") is True, "execution milestone condition disabled")
need(execution.get("modes", {}).get("all", {}).get("sequence") == ["system","apply","test"], "all mode sequence drift")
need(execution.get("crownStatus") == "STOP" and execution.get("greenClaim") is False, "execution schema authority drift")

wh_path = root / "agents/witchingHourCoding/SKILL.md"
if wh_path.is_file():
    wh = wh_path.read_text(encoding="utf-8")
    for term in ["exact sourceRef", "urdDoctorGoddess", "belldandySecretary", "skuldResearch", "Shiori", "Kugi", "nearest evidence-backed known-good"]:
        need(term in wh, "witching hour missing " + term)

wh_contract = ff.get("witchingHour", {})
need(wh_contract.get("requiresUrdDoctorDiagnosis") is True, "Urd doctor diagnosis gate missing")
need(wh_contract.get("requiresBelldandySecretaryStateAudit") is True, "Belldandy secretary state gate missing")
need(wh_contract.get("requiresSkuldResearchCompatibility") is True, "Skuld research compatibility gate missing")

need(trigger.get("entryPoint") == "LuHmOS.fn.operationTitan", "Operation Titan function name drift")
need(trigger.get("buildVersion") == 7, "Operation Titan build version drift")
binding = naming.get("namespaceEscalation", {}).get("operationTitanBinding", {})
need(binding.get("functionRef") == trigger.get("entryPoint"), "Operation Titan namespace binding drift")
need(binding.get("buildVersion") == trigger.get("buildVersion"), "Operation Titan build binding drift")
need(ff.get("functionRef") == "LuHmOS.fn.operationTitan" and ff.get("buildVersion") == 7, "Final Form function/version binding drift")
need("finalBoss" not in ff and "finalBoss" not in trigger, "personal/session authority token must not be doctrine")
need(not execution.get("terminalEscalation") and not execution.get("finalBossDelegation"), "execution schema must not grant authority")

need(eighth.get("meter", {}).get("notesPerMeasure") == 8 and len(eighth.get("notes", [])) == 8, "eighth-note scope must contain eight notes")
need(eighth.get("workflowChain") == ["vendorAiProvider","focusedMiniAgents","goddessAuditors","lumCustomAgentBoss"], "eighth-note workflow chain drift")
need(eighth.get("scopeContract", {}).get("noAuthorityFromWorkflow") is True, "workflow must not create authority")

modules = source_architecture.get("sourceModules", [])
need([m.get("id") for m in modules] == ["kernelVendorPlatform","linuxBuildEssentials","python3ControlPlane","godot4Game"], "modular source architecture order drift")
if modules:
    need(modules[0].get("canonicalChangePolicy") == "securityUpdatesOnly", "canonical kernel security-only policy drift")
    need(modules[0].get("capsule") == "luhm-samsung-dev-core", "kernel/vendor capsule name drift")
if len(modules) > 1:
    need(modules[1].get("status") == "sourceInPlace", "Linux build essentials source status drift")
if len(modules) > 2:
    need(modules[2].get("runtime") == "Python 3", "Python control-plane runtime drift")
if len(modules) > 3:
    need(modules[3].get("runtime") == "Godot 4", "Godot game runtime drift")

need(source_architecture.get("references", {}).get("compositionArchitecture") == "doctrine/luHmOSFourLayerArchitectureV1.json", "source architecture composition binding drift")
need(eighth.get("parentArchitecture") == "doctrine/luHmOSFourLayerArchitectureV1.json", "eight-note composition binding drift")
need(package_architecture.get("packageIdentity") == "LuHmOS", "four-layer architecture package identity drift")

cast_commands = cast_workflow.get("commandSurface", {})
package_identity = cast_workflow.get("packageIdentity", {})
need([item.get("name") for item in cast_commands.get("verbs", [])] == ["create","install","run","update","upgrade"], "CAST command verb drift")
need(cast_commands.get("helpAliases") == ["-h","--help"], "CAST help aliases drift")
need(cast_commands.get("executable") == "LuHmOS", "CAST executable drift")
need(package_identity.get("packageName") == "LuHmOS", "CAST package identity drift")
need(package_identity.get("lumAgentIdentity") == "lum", "Lum agent identity drift")
need(package_identity.get("agentAndPackageAreDistinctIdentities") is True, "Lum and LuHmOS identity conflation")
need(package_identity.get("dollarEntryPoint") == "$.LuHmOS.cast", "LuHmOS dollar entrypoint drift")
need(ff.get("castCommandWorkflow") == "doctrine/castCommandWorkflowV1.json", "Final Form CAST workflow binding drift")

head = subprocess.check_output(["git","rev-parse","HEAD"], cwd=root, text=True).strip()
report = {
    "schema": "luhmOs.operationTitan7FinalFormAudit.v2",
    "sourceCommit": head,
    "status": "GREEN_STAGED_OPERATION_TITAN7_FINAL_FORM" if not errors else "RED_OPERATION_TITAN7_FINAL_FORM",
    "canonicalAgentCount": deployment.get("requiredAgentCount"),
    "activeRepositoryCount": len(repo_set.get("activeRepositories", [])),
    "chatGptWorkflow": workflow_stream.get("status"),
    "retiredWatchFleet": True,
    "contractErrors": errors,
    "stagedOnly": True,
    "physicalDeviceProof": False,
    "crownStatus": "STOP"
}
out = root / "build/operation-titan7-final-form"
out.mkdir(parents=True, exist_ok=True)
(out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
raise SystemExit(1 if errors else 0)
