#!/usr/bin/env python3
"""LuHm R tuning sidecar: exact bounded synthetic grid and independent receipt gate.

No R execution from Python. The R program runs separately in CI only, with a
fixed fixture. Never reads host/kernel/credentials or requests an AI worker.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"doctrine/finalThreeMachineMutationsV1.json"
SCRIPT=ROOT/"tools/rSyntheticTuning.R"
LANES=("numericStream","textStream","booleanStream","aiManifestStream")
PHASES=("sourceIdentity","boundedSearch","crossLanguageReceipt","ownerApproval")
SAFE_OUT={
 "schema":"luhmOs.syntheticRTune.v1",
 "best":"2",
 "trials":"5",
 "state":"SYNTHETIC_ONLY_NOT_REAL_KERNEL_OR_AGENT_TUNING",
 "runtimeRights":"HOLD",
}


def _source()->dict[str,Any]:
    p=json.loads(POLICY.read_text(encoding="utf8"))
    if not isinstance(p,dict):
        raise ValueError("RED_R_CANON")
    return p


def source_audit()->dict[str,Any]:
    p=_source()
    m=next((x for x in p.get("mutations",[]) if x.get("id")=="rTuning"),{})
    issues=[]
    if (p.get("schema")!="luhmOs.finalThreeMachineMutations.v1"
        or m.get("axes")!=list(LANES) or m.get("checks")!=list(PHASES)
        or m.get("maxTrials")!=16):
        issues.append("RED_R_SCHEMA_OR_GRID")
    conf=p.get("math",{})
    if any(conf.get(k) is not True for k in
        ("notPasswordCracking","notAdversarialCredentialBruteForce",
         "noRealKernelTuning","noAiModelClaim","noSelfApproval",
         "noUnboundedLoops","noSideEffects","runtimeEvidenceNeedsCI")):
        issues.append("RED_R_SECURITY_POLICY")
    if not SCRIPT.is_file() or not SCRIPT.read_text(encoding="utf8").startswith("#!/usr/bin/env Rscript"):
        issues.append("RED_R_SCRIPT_MISSING")
    if p.get("crown")!="STOP":
        issues.append("RED_R_CROWN")
    return {
      "schema":"luhmOs.rTuningSourceAudit.v1",
      "state":"SOURCE_ONLY" if not issues else "RED_SOURCE_DRIFT",
      "issues":issues,"lanes":len(LANES),"phases":len(PHASES),
      "matrixCells":16,"maxTrials":16,
      "scriptSha256":hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
          if SCRIPT.is_file() else None,
      "rInterpreterExecutedByPython":False,"realKernelBenchmark":False,
      "agentActivated":False,"trainingRunCompleted":False,
      "greenAuthority":False,
    }


def plan(*,target:int,candidates:list[int])->dict[str,Any]:
    if type(target) is not int or not 0<=target<=10:
        raise ValueError("RED_R_TARGET")
    if (type(candidates) is not list or not 1<=len(candidates)<=16
        or any(type(v) is not int or not 0<=v<=15 for v in candidates)
        or len(set(candidates))!=len(candidates)):
        raise ValueError("RED_R_CANDIDATES")
    if source_audit()["issues"]:
        return {"state":"STOP_SOURCE_DRIFT"}
    pairs=sorted(
        (((n-target)**2+0.1*n*n,n) for n in candidates),
        key=lambda item:(item[0],item[1]))
    best=pairs[0][1]
    return {
      "schema":"luhmOs.syntheticRTune.v1",
      "best":best,"trials":len(candidates),
      "objective":"(parameter-target)^2 + 0.1*parameter^2",
      "state":"SYNTHETIC_ONLY_NOT_REAL_KERNEL_OR_AGENT_TUNING",
      "modelTrained":False,"hardwareMeasured":False,
      "credentialsTested":False,"kernelVariablesChanged":False,
      "rExecutedByPython":False,"approvalGranted":False,
    }


def verify_r_fixture(stdout:str)->dict[str,Any]:
    if type(stdout) is not str or len(stdout)>500 or "\r" in stdout:
        raise ValueError("RED_R_RECEIPT_BYTES")
    rows=stdout.splitlines()
    if len(rows)!=5:
        raise ValueError("RED_R_RECEIPT_ROWS")
    observed={}
    for line in rows:
        if "=" not in line:
            raise ValueError("RED_R_RECEIPT_SHAPE")
        key,value=line.split("=",1)
        if key in observed or not re.fullmatch(r"[A-Za-z]+",key):
            raise ValueError("RED_R_RECEIPT_DUPLICATE")
        observed[key]=value
    expected=plan(target=2,candidates=[0,1,2,3,4])
    if (observed!=SAFE_OUT or int(observed["best"])!=expected["best"]
        or int(observed["trials"])!=expected["trials"]):
        raise ValueError("RED_R_CROSS_LANGUAGE_DRIFT")
    return {
       "status":"R_SYNTHETIC_OUTPUT_MATCHED_PYTHON_FIXTURE",
       "rOracleCompared":True,"candidateTrials":5,
       "realKernelTuned":False,"agentAuthorized":False,
       "productionCastProven":False,
    }


if __name__=="__main__":
    if sys.argv[1:]==["--verify-stdin"]:
        print(json.dumps(verify_r_fixture(sys.stdin.read()),indent=2))
    elif sys.argv[1:]==["--audit"]:
        print(json.dumps(source_audit(),indent=2))
    else:
        raise SystemExit("use --audit or --verify-stdin")
