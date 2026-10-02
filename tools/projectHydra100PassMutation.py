#!/usr/bin/env python3
import json, pathlib, subprocess, sys
root=pathlib.Path(__file__).resolve().parents[1]
policy=json.loads((root/"doctrine/projectHydraContinuousBuildV1.json").read_text())
assert policy["systemScope"]["name"]=="wholeLuHmOsProjectHydra"
cfg=policy["mutationPass"]; max_passes=int(cfg["maxPasses"])
receipts=[]

def run_audit():
    commands=[[sys.executable,str(root/"tools/projectHydraHard20PassAudit.py")],[sys.executable,str(root/"tools/fullSourceTruthAudit.py"),"--output",str(root/"build/full-source-truth/readiness.json")],[sys.executable,str(root/"tools/operationTitan7FinalFormAudit.py")],[sys.executable,str(root/"tools/namingPathSealAudit.py")],[sys.executable,str(root/"tools/artOniCamelHumpAudit.py")],[sys.executable,str(root/"tools/goddessTrustSealAudit.py")]]
    logs=[]; rc=0
    for command in commands:
        q=subprocess.run(command,cwd=root,text=True,capture_output=True)
        logs.append(q.stdout+q.stderr); rc=max(rc,q.returncode)
    p=type("AuditResult",(),{"returncode":rc,"stdout":"\n".join(logs),"stderr":""})()
    receipt_path=root/"build/projectHydraHard20Pass/receipt.json"
    receipt=json.loads(receipt_path.read_text()) if receipt_path.exists() else None
    return p.returncode,receipt,(p.stdout+p.stderr)[-6000:]

for n in range(1,max_passes+1):
    source=subprocess.run(["git","rev-parse","HEAD"],cwd=root,text=True,capture_output=True,check=True).stdout.strip()
    dirty=subprocess.run(["git","status","--porcelain"],cwd=root,text=True,capture_output=True,check=True).stdout.strip()
    sanity=bool(source) and not dirty
    if not sanity:
        receipts.append({"pass":n,"sourceRef":source or None,"state":"red","reason":"sanityCheckFailed"})
        break
    code,audit,log=run_audit()
    if audit is None:
        receipts.append({"pass":n,"sourceRef":source,"state":"red","reason":"auditNull","logTail":log})
        break
    required=[x for x in audit.get("results",[]) if x.get("state")!="green"]
    entry={"pass":n,"sourceRef":source,"auditPasses":audit.get("passes"),"auditGreen":audit.get("green"),"gaps":[x.get("pass") for x in required]}
    if code==0 and audit.get("green") and audit.get("passes")==20:
        entry.update({"state":"green","milestoneSatisfied":True,"action":"earlyStopNoMutationRequired"})
        receipts.append(entry)
        break
    entry.update({"state":"red","milestoneSatisfied":False,"action":"boundedMutationRequired","reason":"deterministicGap"})
    receipts.append(entry)
    # CI audit runner diagnoses gaps but never invents or self-approves source mutations.
    # A bounded mutation is performed by the authorized tool lane, then this loop is rerun.
    break

out={"schema":"luhmOs.projectHydra100PassMutationReceipt.v1","maxPasses":max_passes,"executedPasses":len(receipts),"earlyStop":bool(receipts and receipts[-1].get("milestoneSatisfied")),"receipts":receipts}
path=root/"build/projectHydra100Pass"; path.mkdir(parents=True,exist_ok=True)
(path/"receipt.json").write_text(json.dumps(out,indent=2)+"\n")
for x in receipts: print(json.dumps(x,sort_keys=True))
print("mutationPass:", "green" if out["earlyStop"] else "red")
sys.exit(0 if out["earlyStop"] else 1)
