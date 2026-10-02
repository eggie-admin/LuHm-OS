#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(".")
errors=[]
def load(path):
    try:
        return json.loads((root/path).read_text())
    except Exception as e:
        errors.append(f"{path}: {e}")
        return {}

goal=load("doctrine/finalGoalMutationDirectorV1.json")
continuous=load("doctrine/projectHydraContinuousBuildV1.json")
plugins=load("doctrine/workflowPluginRegistryV1.json")
boss=load("doctrine/aiApiBossCapabilitySpineV1.json")
role=load("doctrine/codingRoleplayDirectorV1.json")
final=load("doctrine/projectHydraFinalAuditMilestoneV1.json")
js=(root/"frontEnd/jquery/luhm.codingRoleplay.js").read_text()

checks={}
def check(name, condition):
    checks[name]=bool(condition)
    if not condition: errors.append(name)

check("wholeProjectGoalPreserved", goal.get("goalId")=="wholeLuHmOsProjectHydra" and "entire LuHm OS + Project Hydra" in goal.get("goal",""))
check("continuousGoalPreserved", continuous.get("mutationPass",{}).get("milestone")=="wholeLuHmOsProjectHydra")
check("normalMeshIsDefault", goal.get("defaultWorkflow")=="luhmAgentMesh" and plugins.get("defaultRuntime")=="luhmAgentMesh")
check("titan7IsSpecialCase", goal.get("specialCasePlugins",{}).get("operationTitan7",{}).get("default") is False and plugins.get("plugins",{}).get("operationTitan7",{}).get("purpose")=="hardenedSpecialCaseWorkflow")
check("deepDungeonIsOniMiniAgent", plugins.get("plugins",{}).get("deepDungeon",{}).get("agentMode")=="oniMiniAgentOnly")
check("aiApiBossIsCapabilitySpine", goal.get("capabilitySpine")=="doctrine/aiApiBossCapabilitySpineV1.json" and boss.get("architecture",{}).get("pattern")=="bossCapabilityBroker")
check("vendorsCannotSelfApprove", boss.get("routingLaw",{}).get("providerCannotSelfApprove") is True and boss.get("routingLaw",{}).get("providerResultIsNotGreen") is True)
check("roleplayCannotRewriteTruth", role.get("bubbleLaw",{}).get("roleplayCannotRewriteEvidence") is True and role.get("bubbleLaw",{}).get("roleplayCannotAdvanceGoalState") is True)
check("decorativeGreenForbidden", role.get("bubbleLaw",{}).get("decorativeGreenForbidden") is True)
check("professorGateCannotAutoAdvance", role.get("goalPresentation",{}).get("professorGateCannotAutoAdvance") is True)
check("castRequiresCrown", goal.get("truthLaw",{}).get("professorCrownRequiredForCast") is True and role.get("goalPresentation",{}).get("castRequiresProfessorCrown") is True)
check("physicalProofIsPostCast", goal.get("truthLaw",{}).get("physicalInstallIsPostCastDeploymentProof") is True and "smX400PhysicalInstallReceipt" in final.get("postCastProof",[]))
check("physicalNotRequiredForSoftwareCast", "smX400PhysicalInstallReceipt" not in final.get("remainingProof",[]))
check("finalAuditUsesNormalMesh", final.get("auditProtocol",{}).get("defaultWorkflow")=="luhmAgentMesh")
check("finalAuditTitan7ExplicitOnly", final.get("auditProtocol",{}).get("operationTitan7",{}).get("default") is False and final.get("auditProtocol",{}).get("operationTitan7",{}).get("invocation")=="explicitOnly")
check("historicalGreenBoundToHistory", final.get("claims",{}).get("historicalGreenForFinalAudit") is True and final.get("claims",{}).get("currentCandidateGreenForFinalAudit") is False)
check("roleplayJsGoalStates", "POST_CAST_PHYSICAL_PROOF" in js and "PROFESSOR_GATE" in js)
check("roleplayJsEvidenceSourceRef", "evidence-bearing goal state requires sourceRef" in js)
check("roleplayJsFrozenAfterGoalAttach", "roleplay.goal = Object.freeze" in js and "$.codingRoleplay = Object.freeze(roleplay);" in js)
check("noFrozenObjectLateMutation", "$.codingRoleplay.goal =" not in js)

out=root/"build/final-goal-contract/report.json"
out.parent.mkdir(parents=True,exist_ok=True)
receipt={
    "schema":"luhmOs.finalGoalContractReceipt.v1",
    "sourceCommit":"UNBOUND",
    "checks":checks,
    "errors":errors,
    "result":"PASS" if not errors else "FAIL"
}
try:
    import subprocess
    receipt["sourceCommit"]=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
except Exception:
    pass
out.write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps({"result":receipt["result"],"checks":len(checks),"errors":errors}))
raise SystemExit(1 if errors else 0)
