#!/usr/bin/env python3
import json, pathlib, subprocess, sys

root = pathlib.Path(__file__).resolve().parents[1]
errors = []

def load(path):
    try:
        return json.loads((root / path).read_text())
    except Exception as exc:
        errors.append(f"{path}: {exc}")
        return {}

ff = load("doctrine/operationTitan7FinalFormV1.json")
milestone = load("doctrine/projectHydraFinalAuditMilestoneV1.json")
fleet = load("doctrine/OPERATION_TITAN7_WATCH_FLEET_V1.json")
execution = load("doctrine/operationTitan7ExecutionSchemaV1.json")
trigger = load("doctrine/operationTitan7ChatTriggerV2.json")
eighth = load("doctrine/eighthNoteAgentScopeV1.json")
naming = load("doctrine/namingNamespaceCanonV1.json")
source_architecture = load("doctrine/modularSourceArchitectureV1.json")
cast_workflow = load("doctrine/castCommandWorkflowV1.json")

required_files = [
    "agents/lum/SKILL.md",
    "agents/urdMutationOni/SKILL.md",
    "agents/goddessSharedSystemsPractice/SKILL.md",
    "agents/witchingHourCoding/SKILL.md",
    "tools/titan7WatchFleet.py",
    "tools/fullSourceTruthAudit.py",
    ".github/workflows/operation-titan7-watch-fleet.yml",
    ".github/workflows/full-source-truth-audit.yml",
]
for path in required_files:
    if not (root / path).is_file():
        errors.append("missing " + path)

if ff.get("authority") != "Professor":
    errors.append("final form authority")
if ff.get("crownStatus") != "STOP":
    errors.append("candidate must stop at Crown")
if ff.get("greenClaim") is not False:
    errors.append("candidate may not self-green")
if len(fleet.get("watches", [])) < 20:
    errors.append("Titan7 fleet below 20 watches")
if milestone.get("auditProtocol", {}).get("harness") != "operationTitan7":
    errors.append("final milestone not bound to Titan7")
if ff.get("executionSchema") != "doctrine/operationTitan7ExecutionSchemaV1.json":
    errors.append("final form execution schema binding")
if ff.get("executionModes") != ["system", "apply", "test", "all"]:
    errors.append("execution mode grammar drift")
if ff.get("milestoneConditionRequired") is not True:
    errors.append("milestone condition not required")
if list(execution.get("modes", {}).keys()) != ["system", "apply", "test", "all"]:
    errors.append("execution schema modes")
if execution.get("milestoneCondition", {}).get("required") is not True:
    errors.append("execution milestone condition disabled")
if execution.get("modes", {}).get("all", {}).get("sequence") != ["system", "apply", "test"]:
    errors.append("all mode sequence drift")
if execution.get("crownStatus") != "STOP" or execution.get("greenClaim") is not False:
    errors.append("execution schema authority drift")

wh_path = root / "agents/witchingHourCoding/SKILL.md"
if wh_path.is_file():
    wh = wh_path.read_text()
    for term in ["exact sourceRef", "urdDoctorGoddess", "belldandySecretary",
                 "skuldResearch", "Shiori", "Kugi", "nearest evidence-backed known-good"]:
        if term not in wh:
            errors.append("witching hour missing " + term)

wh_contract = ff.get("witchingHour", {})
if wh_contract.get("requiresUrdDoctorDiagnosis") is not True:
    errors.append("Urd doctor diagnosis gate missing")
if wh_contract.get("requiresBelldandySecretaryStateAudit") is not True:
    errors.append("Belldandy secretary state gate missing")
if wh_contract.get("requiresSkuldResearchCompatibility") is not True:
    errors.append("Skuld research compatibility gate missing")

if trigger.get("entryPoint") != "LuHmOS.fn.operationTitan":
    errors.append("Operation Titan function name drift")
if trigger.get("buildVersion") != 7:
    errors.append("Operation Titan build version drift")
if naming.get("namespaceEscalation", {}).get("operationTitanBinding", {}).get("functionRef") != trigger.get("entryPoint"):
    errors.append("Operation Titan namespace binding drift")
if naming.get("namespaceEscalation", {}).get("operationTitanBinding", {}).get("buildVersion") != trigger.get("buildVersion"):
    errors.append("Operation Titan build binding drift")
if ff.get("functionRef") != "LuHmOS.fn.operationTitan" or ff.get("buildVersion") != 7:
    errors.append("Final Form function/version binding drift")
if "finalBoss" in ff or "finalBoss" in trigger:
    errors.append("personal/session authority token must not be encoded in doctrine")
if execution.get("terminalEscalation") or execution.get("finalBossDelegation"):
    errors.append("execution schema must not grant authority")

if eighth.get("meter", {}).get("notesPerMeasure") != 8 or len(eighth.get("notes", [])) != 8:
    errors.append("eighth-note agent scope must contain eight notes")
if eighth.get("workflowChain") != ["vendorAiProvider", "focusedMiniAgents", "goddessAuditors", "lumCustomAgentBoss"]:
    errors.append("eighth-note workflow chain drift")
if eighth.get("scopeContract", {}).get("noAuthorityFromWorkflow") is not True:
    errors.append("workflow must not create authority")
if "finalBossDelegation" in eighth:
    errors.append("personal/session authority token must not be encoded in doctrine")

modules = source_architecture.get("sourceModules", [])
if [m.get("id") for m in modules] != ["kernelVendorPlatform", "linuxBuildEssentials", "python3ControlPlane", "godot4Game"]:
    errors.append("modular source architecture order drift")
if modules and modules[0].get("canonicalChangePolicy") != "securityUpdatesOnly":
    errors.append("canonical kernel security-only policy drift")
if modules and modules[0].get("capsule") != "luhm-samsung-dev-core":
    errors.append("kernel/vendor capsule name drift")
if len(modules) > 1 and modules[1].get("status") != "sourceInPlace":
    errors.append("Linux build essentials source status drift")
if len(modules) > 2 and modules[2].get("runtime") != "Python 3":
    errors.append("Python control-plane runtime drift")
if len(modules) > 3 and modules[3].get("runtime") != "Godot 4":
    errors.append("Godot game runtime drift")
if source_architecture.get("escalation", {}).get("tierMap") != {
    0: "defaultFastPath", 1: "forFuckSake", 2: "scorchedEarth", 3: "finalForm"
}:
    errors.append("modular source escalation tier map drift")
if "separationLaw" not in source_architecture.get("escalation", {}):
    errors.append("module boundaries and operational escalation are not separated")
if ff.get("modularSourceArchitecture") != "doctrine/modularSourceArchitectureV1.json":
    errors.append("Final Form source architecture binding drift")
if execution.get("modularSourceArchitecture") != "doctrine/modularSourceArchitectureV1.json":
    errors.append("execution schema source architecture binding drift")

expected_cast_verbs = ["create", "install", "run", "update", "upgrade"]
cast_commands = cast_workflow.get("commandSurface", {})
package_identity = cast_workflow.get("packageIdentity", {})
actual_cast_verbs = [item.get("name") for item in cast_commands.get("verbs", [])]
if cast_workflow.get("schema") != "luhmOs.castCommandWorkflow.v1":
    errors.append("CAST command workflow schema drift")
if cast_workflow.get("status") != "PROPOSED_SOURCE_ONLY":
    errors.append("CAST command workflow must remain proposed")
if actual_cast_verbs != expected_cast_verbs:
    errors.append("CAST command verb order or set drift")
if cast_commands.get("helpAliases") != ["-h", "--help"]:
    errors.append("CAST help aliases drift")
if cast_commands.get("executable") != "LuHmOS":
    errors.append("CAST executable must use the LuHmOS package name")
if "luhm" not in cast_commands.get("aliases", []) or package_identity.get("aliasResolvesToPackage") != "LuHmOS":
    errors.append("legacy CLI alias must resolve to LuHmOS")
if package_identity.get("packageName") != "LuHmOS":
    errors.append("CAST package identity drift")
if package_identity.get("packageNamespace") != "art.eggiebagelface.LuHmOS.cast":
    errors.append("CAST package namespace drift")
if package_identity.get("lumAgentIdentity") != "lum" or package_identity.get("agentAndPackageAreDistinctIdentities") is not True:
    errors.append("Lum agent identity must remain distinct from the LuHmOS package")
if package_identity.get("projectOwnedJqueryDerivedNamesResolveTo") != "LuHmOS":
    errors.append("jQuery-derived project package names must resolve to LuHmOS")
if package_identity.get("jqueryStyleAlias") != "$.LuHmOS.cast":
    errors.append("jQuery-style compatibility namespace drift")
if any(not item.get("syntax", "").startswith("LuHmOS cast ") for item in cast_commands.get("verbs", [])):
    errors.append("CAST verb syntax must use the LuHmOS package executable")
if ff.get("castCommandWorkflow") != "doctrine/castCommandWorkflowV1.json":
    errors.append("Final Form CAST command workflow binding drift")
cast_authority = cast_workflow.get("authorityBoundary", {})
for key in ["packageStyleCommandsAreCandidateOperations", "cliVerbMayDispatchProfessorCastBridge",
            "cliVerbMayGrantProfessorApproval", "cliVerbMayMergePublishDeployOrPromote"]:
    expected = key == "packageStyleCommandsAreCandidateOperations"
    if cast_authority.get(key) is not expected:
        errors.append("CAST command authority boundary drift: " + key)
if cast_authority.get("packageOrBuildArtifactIsFinalCast") is not False:
    errors.append("CAST package must not be final CAST")
if cast_commands.get("unknownVerb", {}).get("behavior") != "Return canonical help and suggestions; execute nothing.":
    errors.append("CAST unknown verb must be non-executing")
if cast_workflow.get("escalation", {}).get("auditDepthGrantsAuthority") is not False:
    errors.append("CAST escalation must not grant authority")

head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
report = {
    "schema": "luhmOs.operationTitan7FinalFormAudit.v1",
    "sourceCommit": head,
    "status": "GREEN_STAGED_OPERATION_TITAN7_FINAL_FORM" if not errors else "RED_OPERATION_TITAN7_FINAL_FORM",
    "contractErrors": errors,
    "stagedOnly": True,
    "physicalDeviceProof": False,
    "crownStatus": "STOP",
}
out = root / "build/operation-titan7-final-form"
out.mkdir(parents=True, exist_ok=True)
(out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
sys.exit(1 if errors else 0)
