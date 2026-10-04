#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=json.loads((ROOT/"doctrine/currentSourceTruthV3.json").read_text())
lane=json.loads((ROOT/"doctrine/proposedWorkingLaneV1.json").read_text())
yume=json.loads((ROOT/"doctrine/yumeCreativePipelineV1.json").read_text())

checks=[
 ("sourceTopLevelProposed", source.get("status")=="AMBER_PROPOSED_SEAL_OF_TRUTH"),
 ("sourcePromotionFalse", source.get("promotion") is False),
 ("laneProposed", lane.get("status")=="PROPOSED_ONLY"),
 ("laneCrownStop", lane.get("crownStatus")=="STOP"),
 ("workingLaneProposed", source.get("workingDoctrineLane",{}).get("status")=="PROPOSED_ONLY"),
 ("workingLaneNoPromotion", source.get("workingDoctrineLane",{}).get("currentMutationPromotion") is False),
 ("yumeSourceProposed", source.get("yumeCreativePipeline",{}).get("status")=="PROPOSED_YUME_CREATIVE_PIPELINE_SOURCE"),
 ("yumeWorkingLane", source.get("yumeCreativePipeline",{}).get("workingLane")=="PROPOSED_ONLY"),
 ("yumeCrownStop", source.get("yumeCreativePipeline",{}).get("crownStatus")=="STOP"),
 ("yumeContractProposed", yume.get("status")=="PROPOSED_SOURCE_ONLY"),
 ("yumeContractPromotionFalse", yume.get("promotion") is False),
 ("yumeContractCrownStop", yume.get("crownStatus")=="STOP"),
]

failed=[name for name,ok in checks if not ok]
for name,ok in checks:
    print(f"{name}={'GREEN' if ok else 'RED'}")
if failed:
    print("PROPOSED_WORKING_LANE=RED")
    raise SystemExit(1)

print("PROPOSED_WORKING_LANE=GREEN")
print("scope=current mutable doctrine/source-truth state only")
print("historical receipts are excluded from mutation")
