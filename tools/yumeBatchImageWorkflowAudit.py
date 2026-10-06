#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
workflow=json.loads((ROOT/"doctrine/yumeBatchImageWorkflowV1.json").read_text())
template=json.loads((ROOT/"agents/yumeArtOni/templates/batch-image-manifest-v1.template.json").read_text())
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

need(workflow.get("status")=="PROPOSED_SOURCE_ONLY","workflow status drift")
need(workflow.get("creativeLead")=="yume","creative lead drift")
need(workflow.get("factory")=="mediaAssetFactory","factory drift")
need(workflow.get("batchLaw",{}).get("maxConcurrentGenerationJobs")==3,"generation parallelism drift")
need(workflow.get("batchLaw",{}).get("privateDraftOnlyByDefault") is True,"private draft default missing")
need(workflow.get("batchLaw",{}).get("publicGeneratedReplacementArt") is False,"public generated art boundary drift")
need(workflow.get("driveHandoff",{}).get("root")=="20_HYDRA_MEDIA","Drive root drift")
need(workflow.get("driveHandoff",{}).get("driveIsBinaryAuthority") is True,"Drive binary authority drift")
need(template.get("privacyClass")=="privateDraft","template privacy drift")
need(template.get("publicAllowed") is False,"template publicAllowed drift")
need(bool(template.get("jobs")),"template jobs missing")

for path in [
    "agents/yumeArtOni/SKILL.md",
    "agents/mediaAssetFactory/SKILL.md",
    "doctrine/currentSourceTruthV3.json"
]:
    need((ROOT/path).is_file(),f"missing {path}")

if errors:
    print("YUME_BATCH_IMAGE_WORKFLOW=RED")
    for error in errors:
        print("ERROR:",error)
    raise SystemExit(1)

print("YUME_BATCH_IMAGE_WORKFLOW=GREEN_SOURCE_CANDIDATE")
print("mode=skeletonBatchImageWorkflow")
print("maxConcurrentGenerationJobs=3")
print("privateDraftOnly=true")
print("driveHandoff=declaredNotProven")
print("providerExecution=notClaimed")
print("crownStatus=STOP")
