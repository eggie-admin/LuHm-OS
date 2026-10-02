#!/usr/bin/env python3
import json, pathlib, subprocess, sys
root=pathlib.Path(__file__).resolve().parents[1]
errors=[]
def load(p):
    try:return json.loads((root/p).read_text())
    except Exception as e: errors.append(f"{p}: {e}"); return {}
ff=load("doctrine/operationTitan7FinalFormV1.json")
mil=load("doctrine/projectHydraFinalAuditMilestoneV1.json")
fleet=load("doctrine/OPERATION_TITAN7_WATCH_FLEET_V1.json")
for p in ["agents/lum/SKILL.md","agents/urdMutationOni/SKILL.md","agents/goddessSharedSystemsPractice/SKILL.md","agents/witchingHourCoding/SKILL.md","tools/titan7WatchFleet.py","tools/fullSourceTruthAudit.py",".github/workflows/operation-titan7-watch-fleet.yml",".github/workflows/full-source-truth-audit.yml"]:
    if not (root/p).is_file(): errors.append("missing "+p)
if ff.get("authority")!="Professor": errors.append("final form authority")
if ff.get("crownStatus")!="STOP": errors.append("candidate must stop at Crown")
if ff.get("greenClaim") is not False: errors.append("candidate may not self-green")
if len(fleet.get("watches",[]))<20: errors.append("Titan7 fleet below 20 watches")
if mil.get("auditProtocol",{}).get("harness")!="operationTitan7": errors.append("final milestone not bound to Titan7")
wh=(root/"agents/witchingHourCoding/SKILL.md").read_text()
for term in ["exact sourceRef","Urd","Belldandy","Shiori","Kugi","nearest evidence-backed known-good"]:
    if term not in wh: errors.append("witching hour missing "+term)
head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
report={"schema":"luhmOs.operationTitan7FinalFormAudit.v1","sourceCommit":head,"status":"GREEN_STAGED_OPERATION_TITAN7_FINAL_FORM" if not errors else "RED_OPERATION_TITAN7_FINAL_FORM","contractErrors":errors,"stagedOnly":True,"physicalDeviceProof":False,"crownStatus":"STOP"}
out=root/"build/operation-titan7-final-form";out.mkdir(parents=True,exist_ok=True);(out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
sys.exit(1 if errors else 0)
