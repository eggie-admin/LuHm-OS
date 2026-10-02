#!/usr/bin/env python3
import json, pathlib, subprocess, sys
root=pathlib.Path(__file__).resolve().parents[1]
errors=[]
def load(p):
    try:return json.loads((root/p).read_text())
    except Exception as e: errors.append(f"{p}: {e}"); return {}

ff=load("doctrine/operationTitan7FinalFormV1.json")
inv=load("doctrine/operationTitan7InvocationV1.json")
esc=load("doctrine/operationTitan7EscalationV1.json")
mil=load("doctrine/projectHydraFinalAuditMilestoneV1.json")
plugins=load("doctrine/workflowPluginRegistryV1.json")
tour=load("doctrine/tourniquetWorkflowV1.json")

required=[
 "agents/shared/ONI_PROTOCOL_V2.md",
 "agents/lum/SKILL.md",
 "agents/urdMutationOni/SKILL.md",
 "agents/belldandyQualityOni/SKILL.md",
 "agents/goddessSharedSystemsPractice/SKILL.md",
 "agents/witchingHourCoding/SKILL.md",
 "agents/tourniquetWorkflow/SKILL.md",
 "agents/shioriCriticOni/SKILL.md",
 "agents/kugiToolOni/SKILL.md",
 "tools/operationTitan7FfsTwentyFivePassAudit.py",
 "tools/operationTitan7FiftyPassAudit.py",
 "tools/fullSourceTruthAudit.py",
 ".github/workflows/operation-titan7-final-form.yml"
]
for p in required:
    if not (root/p).is_file(): errors.append("missing "+p)

if ff.get("authority")!="Professor": errors.append("final form authority")
if ff.get("crownStatus")!="STOP": errors.append("candidate must stop at Crown")
if ff.get("greenClaim") is not False: errors.append("candidate may not self-green")
if ff.get("tier")!="finalForm": errors.append("final form tier identity")
if ff.get("mode")!="absoluteRipOutAndReplaceAudit": errors.append("final form mode")
if ff.get("escalationContract")!="doctrine/operationTitan7EscalationV1.json": errors.append("final form escalation contract")
if inv.get("defaultWorkflow") is not False: errors.append("Titan7 became default")
if inv.get("normalWorkflow")!="luhmAgentMesh": errors.append("normal mesh drift")
if inv.get("passPolicy",{}).get("tierOwnsPassCount") is not True: errors.append("tier pass ownership drift")

tiers=esc.get("tiers",{})
ffs=tiers.get("ffs",{})
sc=tiers.get("scorchedEarth",{})
fin=tiers.get("finalForm",{})
if ffs.get("booleanPhrase")!="For Fuck Sake!" or ffs.get("hardPasses")!=25: errors.append("FFS tier drift")
if ffs.get("mode")!="sanestApproachFirstTierEscalatedAudit": errors.append("FFS mode drift")
if sc.get("hardPasses")!=50 or sc.get("mode")!="sanestApproachSecondTierEscalation": errors.append("Scorched Earth tier drift")
if fin.get("mode")!="absoluteRipOutAndReplaceAudit": errors.append("Final Form escalation drift")
if fin.get("hardPasses") is not None: errors.append("Final Form may not masquerade as fixed pass count")

op=plugins.get("plugins",{}).get("operationTitan7",{})
if op.get("entryPoint")!="$.operationTitan7": errors.append("Titan7 plugin entry drift")
if op.get("escalationContract")!="doctrine/operationTitan7EscalationV1.json": errors.append("plugin escalation binding drift")
if plugins.get("defaultRuntime")!="luhmAgentMesh": errors.append("plugin registry default runtime drift")

milOp=mil.get("auditProtocol",{}).get("operationTitan7",{})
if milOp.get("default") is not False or milOp.get("invocation")!="explicitOnly": errors.append("final milestone Titan7 invocation drift")

binding=ff.get("tourniquet",{})
if binding.get("required") is not True: errors.append("Titan7 Tourniquet not required")
if binding.get("path")!="doctrine/tourniquetWorkflowV1.json": errors.append("Titan7 Tourniquet path drift")
if binding.get("skill")!="agents/tourniquetWorkflow/SKILL.md": errors.append("Titan7 Tourniquet skill drift")
if tour.get("authority")!="Professor": errors.append("Tourniquet authority drift")
if tour.get("greenAction")!="reingestCurrentTruthAndContinue": errors.append("Tourniquet green continuation drift")
if tour.get("redAction")!="rollbackOrNearestEvidenceBackedKnownGood": errors.append("Tourniquet red fallback drift")

law=ff.get("replacementLaw",{})
for k in ["candidateLaneOnly","reversibleUntilProfessorPromotion","exactSourceRefRequired","rollbackPlanRequired","knownGoodFallbackRequired","preserveUnsatisfiedGoals","mayNotRewriteHistory","mayNotDeleteGateToPass","mayNotConvertRedToUnknown"]:
    if law.get(k) is not True: errors.append("replacement law "+k)

workflow=(root/".github/workflows/operation-titan7-final-form.yml").read_text()
if "pull_request:" in workflow: errors.append("Final Form must not auto-run on ordinary PR")
if "schedule:" in workflow: errors.append("Final Form must not auto-run on schedule")

head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
report={
 "schema":"luhmOs.operationTitan7FinalFormAudit.v2",
 "sourceCommit":head,
 "tier":"finalForm",
 "mode":"absoluteRipOutAndReplaceAudit",
 "status":"GREEN_STAGED_OPERATION_TITAN7_FINAL_FORM" if not errors else "RED_OPERATION_TITAN7_FINAL_FORM",
 "contractErrors":errors,
 "stagedOnly":True,
 "physicalDeviceProof":False,
 "crownStatus":"STOP"
}
out=root/"build/operation-titan7-final-form"
out.mkdir(parents=True,exist_ok=True)
(out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
sys.exit(1 if errors else 0)
