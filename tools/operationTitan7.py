#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine" / "operationTitan7V1.json"
LAYERS = ROOT / "doctrine" / "luhmCompatibilityLayersV1.json"

def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

def load(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser=argparse.ArgumentParser(prog="operationTitan7")
    parser.add_argument("command", choices=["saneApproach","dryRun","update","upgrade","distro","apply","continue","continueAll","exit","quit"])
    parser.add_argument("--escalation", choices=["forFuckSake","scorchedEarth","finalForm"], default="forFuckSake")
    parser.add_argument("--json", dest="json_path", default="build/operationTitan7/receipt.json")
    args=parser.parse_args()

    contract=load(CONTRACT)
    layers=load(LAYERS)
    errors=[]
    if contract.get("canonicalName")!="operationTitan7": errors.append("canonicalName")
    if contract.get("notAProject") is not True: errors.append("notAProject")
    if contract.get("notAlwaysRunning") is not True: errors.append("notAlwaysRunning")
    if contract.get("invocationLaw",{}).get("scheduledBackgroundRunsForbidden") is not True: errors.append("scheduledBackgroundRunsForbidden")
    if layers.get("layerOne",{}).get("id")!="openAiCompatibilityLayer": errors.append("layerOne")
    if layers.get("layerTwo",{}).get("id")!="githubCompatibilityLayer": errors.append("layerTwo")
    if layers.get("layerTwo",{}).get("allProviderResultsReturnTo")!="lum": errors.append("lumReconciliation")
    if layers.get("wireProtocol",{}).get("javascriptAdapter",{}).get("authority") is not False: errors.append("minifierAuthority")

    escalation=contract["escalation"][args.escalation]
    commit_limit=escalation["commitWindowMax"]
    commits=git("log",f"-n{commit_limit}","--pretty=%H").splitlines()
    source_ref=git("rev-parse","HEAD")

    if args.command in {"exit","quit"}:
        status="STOPPED"
    elif args.command=="apply":
        status="WAIT_EXECUTOR"
    elif errors:
        status="RED_OPERATION_TITAN7"
    else:
        status="GREEN_OPERATION_TITAN7_DRYRUN" if args.command=="dryRun" else "READY_OPERATION_TITAN7"

    receipt={
      "schema":"luhmOs.operationTitan7Receipt.v1",
      "status":status,
      "command":args.command,
      "escalation":args.escalation,
      "sourceRef":source_ref,
      "commitWindowExamined":len(commits),
      "commitWindowMax":commit_limit,
      "contractErrors":errors,
      "mutationAuthority":False,
      "mergeAuthority":False,
      "deployAuthority":False,
      "crownStatus":"STOP",
      "inspiredMutation":{
        "finalMilestoneProduced":"twoLayerCompatibilityPlusCallableTitan7Candidate",
        "nextInspiredMutation":"bind remote provider adapters only after exact connector/deployment evidence"
      }
    }
    out=ROOT/args.json_path
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2))
    return 1 if errors else 0

if __name__=="__main__":
    raise SystemExit(main())
