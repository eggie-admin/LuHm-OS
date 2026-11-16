#!/usr/bin/env python3
"""Read-only final-three CAST candidate audit. No actual hardware or agent calls."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"doctrine/finalThreeMachineMutationsV1.json"
QUARANTINE=ROOT/"doctrine/companyWideOperationalQuarantineV1.json"


def _module(file:str)->Any:
    path=ROOT/"tools"/file
    spec=importlib.util.spec_from_file_location("luhm_"+file.replace(".","_"),path)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_FINAL_SOURCE_MODULE")
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def audit()->dict[str,Any]:
    contract=json.loads(CONTRACT.read_text(encoding="utf8"))
    quarantine=json.loads(QUARANTINE.read_text(encoding="utf8"))
    issues=[]
    ids=[x.get("id") for x in contract.get("mutations",[])]
    if ids!=["retroTileText","portableOsRecipe","rTuning"]:
        issues.append("RED_FINAL_THREE_ORDER")
    if contract.get("crown")!="STOP" or contract.get("source")!="eggie-admin/LuHm-OS":
        issues.append("RED_FINAL_CROWN_OR_REPO")
    if quarantine.get("state")!="QUARANTINED" or quarantine.get("activeTaskWorkersAllowed") is not False:
        issues.append("RED_FINAL_QUARANTINE")
    a=_module("retroTileTextCodec.py")
    blank=[[0]*64 for _ in range(16)]
    retro=a.original_sheet_receipt(pixels=blank,fmt="nes2bpp",
        tilemap=list(range(16)),text="MOONLIT ARCHIVE",
        rights="originalOwned",source_ref="0"*40)
    if retro["tileCount"]!=16 or retro["romRead"] is not False:
        issues.append("RED_FINAL_RETRO")
    os=_module("portableOsRecipeAudit.py").source_audit()
    if os["issues"] or os["matrixCells"]!=16:
        issues.append("RED_FINAL_OS")
    r=_module("rSyntheticTuningGate.py").source_audit()
    if r["issues"] or r["matrixCells"]!=16:
        issues.append("RED_FINAL_R")
    lanes=[
        {"id":"retroTileText","candidateCells":16,"status":"SOURCE_ONLY"},
        {"id":"portableOsRecipe","candidateCells":16,"status":"SOURCE_ONLY"},
        {"id":"rTuning","candidateCells":16,"status":"SOURCE_ONLY"},
    ]
    return {
      "schema":"luhmOs.finalThreeMachineGate.v1",
      "state":"THREE_SOURCE_CANDIDATES" if not issues else "RED_SOURCE_DRIFT",
      "issues":sorted(set(issues)), "mutations":lanes,"candidateCells":48,
      "realKernelTuned":False,"newBiosProduced":False,
      "androidSystemImageBuilt":False,"retroCommercialDataImported":False,
      "realAiAgentLaunched":False,"rCIExecutionProvenByThisAudit":False,
      "threeSourcePlansValid":not bool(issues),
      "castRuntimeProven":False,"ownerApproval":False,
      "greenAuthority":False,"crownAuthority":False,
    }


if __name__=="__main__":
    print(json.dumps(audit(),indent=2))
