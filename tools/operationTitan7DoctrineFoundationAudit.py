#!/usr/bin/env python3
import json, subprocess
from pathlib import Path

root=Path(".")
errors=[]
checks={}

def load(path):
    try:
        return json.loads((root/path).read_text())
    except Exception as e:
        errors.append(f"{path}: {e}")
        return {}

def check(name, ok):
    checks[name]=bool(ok)
    if not ok: errors.append(name)

seal=load("doctrine/finalDoctrineFoundationSealV1.json")
ticket=load("doctrine/operations/operationTitan7FinalDoctrineFoundationSealV1.json")
inv=load("doctrine/operationTitan7InvocationV1.json")
esc=load("doctrine/operationTitan7EscalationV1.json")
ff=load("doctrine/operationTitan7FinalFormV1.json")
plugins=load("doctrine/workflowPluginRegistryV1.json")
boss=load("doctrine/aiApiBossCapabilitySpineV1.json")
goal=load("doctrine/finalGoalMutationDirectorV1.json")
mil=load("doctrine/projectHydraFinalAuditMilestoneV1.json")
tour=load("doctrine/tourniquetWorkflowV1.json")
role=load("doctrine/codingRoleplayDirectorV1.json")
art=load("doctrine/artOniMasterCharacterWorkflowV1.json")
chars=load("game/canon/CHARACTER_DESIGN_SEAL_REGISTRY_V1.json")

check("professorAuthority", all(x.get("authority")=="Professor" for x in [seal,inv,esc,ff,plugins,boss,goal,mil,tour,role,art,chars]))
check("sealMilestone", seal.get("milestone")=="finalDoctrineFoundationSeal" and seal.get("tier")=="finalForm")
check("sealApprovedIntent", seal.get("claims",{}).get("foundationDesignApprovedByProfessor") is True)
check("sealNoMergeCastLeak", seal.get("claims",{}).get("mergeApproved") is False and seal.get("claims",{}).get("castApproved") is False)
check("ticketExplicit", ticket.get("operation")=="operationTitan7" and ticket.get("tier")=="finalForm" and ticket.get("explicitInvocation") is True)
check("normalMeshDefault", inv.get("defaultWorkflow") is False and inv.get("normalWorkflow")=="luhmAgentMesh" and plugins.get("defaultRuntime")=="luhmAgentMesh")
check("pluginEntry", plugins.get("plugins",{}).get("operationTitan7",{}).get("entryPoint")=="$.operationTitan7")
check("pluginEscalationBinding", plugins.get("plugins",{}).get("operationTitan7",{}).get("escalationContract")=="doctrine/operationTitan7EscalationV1.json")

tiers=esc.get("tiers",{})
ffs=tiers.get("ffs",{})
sc=tiers.get("scorchedEarth",{})
fin=tiers.get("finalForm",{})
check("ffsTier", ffs.get("booleanPhrase")=="For Fuck Sake!" and ffs.get("hardPasses")==25 and ffs.get("mode")=="sanestApproachFirstTierEscalatedAudit")
check("scorchedTier", sc.get("hardPasses")==50 and sc.get("mode")=="sanestApproachSecondTierEscalation" and sc.get("autoDestructive") is False)
check("finalFormTier", fin.get("hardPasses") is None and fin.get("mode")=="absoluteRipOutAndReplaceAudit")
check("finalFormReplacementLaw", ff.get("replacementLaw",{}).get("candidateLaneOnly") is True and ff.get("replacementLaw",{}).get("rollbackPlanRequired") is True and ff.get("replacementLaw",{}).get("preserveUnsatisfiedGoals") is True)
check("tierPassOwnership", inv.get("passPolicy",{}).get("tierOwnsPassCount") is True and inv.get("passPolicy",{}).get("passCountMayNotBeClaimedFromConfigurationAlone") is True)

check("bossCapabilitySpine", boss.get("boss")=="Lum" and boss.get("architecture",{}).get("pattern")=="bossCapabilityBroker")
check("oniUseBoss", boss.get("routingLaw",{}).get("oniRequestsCapabilityThroughBoss") is True and boss.get("routingLaw",{}).get("pluginRequestsCapabilityThroughBoss") is True)
check("vendorsNoCrown", boss.get("routingLaw",{}).get("providerCannotSelfApprove") is True and boss.get("routingLaw",{}).get("providerResultIsNotGreen") is True)

deep=plugins.get("plugins",{}).get("deepDungeon",{})
check("deepDungeonOni", deep.get("agentMode")=="oniMiniAgentOnly" and deep.get("oniSkill")=="agents/deepDungeon/SKILL.md" and deep.get("capabilityBroker")=="aiApiBoss")
check("deepDungeonHumanTrigger", deep.get("humanCenteredTrigger",{}).get("naturalLanguageFirst") is True and deep.get("humanCenteredTrigger",{}).get("targetRequired") is True)

check("roleplayTruthBoundary", role.get("bubbleLaw",{}).get("bubbleCannotEstablishGreen") is True and role.get("bubbleLaw",{}).get("roleplayCannotRewriteEvidence") is True and role.get("bubbleLaw",{}).get("roleplayCannotAdvanceGoalState") is True)
check("professorGateSeparate", role.get("goalPresentation",{}).get("professorGateCannotAutoAdvance") is True and role.get("goalPresentation",{}).get("castRequiresProfessorCrown") is True)

check("artOniBossBroker", art.get("capabilityBroker")=="aiApiBoss" and art.get("artOni")=="Yume" and art.get("provenanceOni")=="Sumi")
check("artPromotionBoundary", "protectedReference" in art.get("promotionLaw","") and "runtimeImportProven" in art.get("promotionLaw",""))
check("characterDesignNotRuntime", chars.get("truthLaw",{}).get("designSealIsRuntimeProof") is False and chars.get("truthLaw",{}).get("runtimeRequiresExactHashAndImportReceipt") is True)

check("tourniquetFailClosed", tour.get("limits",{}).get("selfApproval") is False and tour.get("limits",{}).get("unknownToGreen") is False and tour.get("limits",{}).get("weakenEvidenceToPass") is False)
check("tourniquetCrown", tour.get("consequentialPromotion")=="ProfessorCrownOnly")

check("physicalPostCast", goal.get("truthLaw",{}).get("physicalInstallIsPostCastDeploymentProof") is True and "smX400PhysicalInstallReceipt" in mil.get("postCastProof",[]))
check("physicalNotSoftwareCastGate", "smX400PhysicalInstallReceipt" not in mil.get("remainingProof",[]))
check("historicalGreenBounded", mil.get("claims",{}).get("historicalGreenForFinalAudit") is True and mil.get("claims",{}).get("currentCandidateGreenForFinalAudit") is False)

shared=(root/"agents/shared/ONI_PROTOCOL_V2.md").read_text()
check("sharedCrownLaw","Professor holds Crown" in shared)
check("sharedEvidenceLaw","Historical GREEN is evidence for its exact historical source only." in shared)
check("noRecursiveRecruitment","do not recursively recruit" in shared)

finalWorkflow=(root/".github/workflows/operation-titan7-final-form.yml").read_text()
watchWorkflow=(root/".github/workflows/operation-titan7-watch-fleet.yml").read_text()
check("finalFormNoOrdinaryPr","pull_request:" not in finalWorkflow and "schedule:" not in finalWorkflow)
check("watchFleetNoOrdinaryPr","pull_request:" not in watchWorkflow and "schedule:" not in watchWorkflow)
check("explicitTicketTrigger","operationTitan7FinalDoctrineFoundationSealV1.json" in finalWorkflow)

required=[
 "tools/operationTitan7FfsTwentyFivePassAudit.py",
 "tools/operationTitan7FiftyPassAudit.py",
 "tools/operationTitan7FinalFormAudit.py",
 "tools/workflowPluginRegistryAudit.py",
 "tools/finalGoalMutationAudit.py",
 "agents/deepDungeon/SKILL.md",
 "agents/yumeArtOni/MASTER_CHARACTER_PROOF_SKILL.md"
]
check("requiredFoundationFiles", all((root/p).is_file() for p in required))

head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
report={
  "schema":"luhmOs.operationTitan7DoctrineFoundationAudit.v1",
  "sourceCommit":head,
  "milestone":"finalDoctrineFoundationSeal",
  "tier":"finalForm",
  "mode":"absoluteRipOutAndReplaceAudit",
  "checks":checks,
  "errors":errors,
  "foundationSealEligible":not errors,
  "professorDoctrineSealApproved":seal.get("claims",{}).get("foundationDesignApprovedByProfessor") is True,
  "mergeApproved":False,
  "castApproved":False,
  "physicalInstallProven":False
}
out=root/"build/operation-titan7-doctrine-foundation"
out.mkdir(parents=True,exist_ok=True)
(out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"checks":len(checks),"errors":errors,"foundationSealEligible":not errors,"sourceCommit":head}))
raise SystemExit(1 if errors else 0)
