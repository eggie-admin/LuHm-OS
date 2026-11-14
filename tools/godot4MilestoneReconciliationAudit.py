#!/usr/bin/env python3
"""Exact-source static milestone and rights audit. Reports only source facts, never full product GREEN."""
from pathlib import Path
import copy
import json

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"doctrine/godot4MilestoneReconciliation20261114.json"
WORLD=ROOT/"game/world/aramoorArchipelagoV1.json"
SCRIPT=ROOT/"scripts/main.gd"
BUILDER=ROOT/"scripts/world/aramoorArchipelagoBuilder.gd"
HUD=ROOT/"scripts/game/gameHud.gd"
HOTSPOT=ROOT/"scripts/world/aramoorZoneInteractable.gd"
MAIN_TEST=ROOT/"tests/aramoorMainWalkaroundSmoke.gd"
CANON=ROOT/"doctrine/currentSourceTruthV3.json"


def inspect(data):
    errors=[]
    def check(ok,code):
        if not ok: errors.append(code)
    check(data.get("schema")=="luhmOs.godot4MilestoneReconciliation.v1","BAD_SCHEMA")
    check(data.get("status")=="AMBER_RECONCILIATION_IN_PROGRESS","FALSE_STATUS")
    check(data.get("allMilestonesCompleted") is False,"FALSE_FULL_GREEN")
    check(data.get("crown")=="STOP","CROWN_ESCALATION")
    check(data.get("automaticMerge") is False,"AUTO_MERGE")
    check(data.get("automaticPublication") is False,"AUTO_PUBLICATION")
    rows=data.get("milestones",[])
    check(isinstance(rows,list) and len(rows)==20,"COUNT_DRIFT")
    if isinstance(rows,list):
        ids=set()
        for row in rows:
            if not isinstance(row,dict):
                errors.append("NON_RECORD")
                continue
            mid=row.get("id")
            if not isinstance(mid,str) or mid in ids: errors.append("DUPLICATE_MILESTONE")
            ids.add(mid)
            evidence=row.get("evidence","")
            if not isinstance(evidence,str) or evidence.startswith("/") or ".." in evidence or not (ROOT/evidence).is_file():
                errors.append("MISSING_SOURCE_EVIDENCE")
            if not isinstance(row.get("remainingGate"),str) or len(row["remainingGate"]) < 10:
                errors.append("MISSING_GATE")
            if row.get("fullProductGreen") is not False:
                errors.append("FALSE_MILESTONE_GREEN")
    legal=data.get("legalSources",{})
    check(legal.get("destinyChild")=="THIRD_PARTY_PRIVATE_REFERENCE, no redistribution","DESTINY_RIGHTS_ESCALATION")
    check(legal.get("mona")=="STYLE_ONLY_NOT_MODEL_INGEST","MONA_SOURCE_CONFUSION")
    check(legal.get("moriohMoreo")=="IDENTITY_AND_ARCHIVE_UNRESOLVED","MORIOH_UNVERIFIED")
    check(legal.get("eve")=="RIGHTS_PENDING_PRIVATE_DONOR","EVE_RIGHTS_ESCALATION")
    policy=data.get("assetPromotionLaw",{})
    check(policy.get("forbidCopyFromPrivateRef") is True,"PRIVATE_LEAK")
    check(policy.get("forbidMetadataAsRuntimeProof") is True,"METADATA_NOT_RUNTIME")
    check(policy.get("forbidAutomaticWorker") is True,"AGENT_QUARANTINE")
    check(data.get("candidateScope",{}).get("publication") is False,"PUBLICATION_ESCAPE")
    return errors


def main():
    data=json.loads(LEDGER.read_text())
    errors=inspect(data)
    for label,mutate in (
      ("false_green",lambda d:d.update(allMilestonesCompleted=True)),
      ("release",lambda d:d.update(crown="GREEN")),
      ("destiny_public",lambda d:d["legalSources"].update(destinyChild="CLEARED")),
      ("mona_copy",lambda d:d["legalSources"].update(mona="BUNDLED_MODEL")),
      ("morioh_found",lambda d:d["legalSources"].update(moriohMoreo="VERIFIED")),
      ("missing_receipt",lambda d:d["milestones"][0].update(evidence="doesNotExist.json")),
      ("worker_lift",lambda d:d["assetPromotionLaw"].update(forbidAutomaticWorker=False)),
    ):
        m=copy.deepcopy(data)
        mutate(m)
        if not inspect(m): errors.append("NEGATIVE_CONTROL_FAILED_"+label)
    world=json.loads(WORLD.read_text())
    truth=json.loads(CANON.read_text())
    required=dict(
      main=['aramoor_requested.connect(_enter_aramoor_mode)','_toggle_aramoor_tide','aramoor:','switchWorld("aramoorArchipelago")'],
      hud=['signal aramoor_requested','ExploreAramoor','AramoorTideSwitch','set_aramoor_controls'],
      world=['var player_spawn: Vector3','get_interaction_points()','AramoorZoneScript.new()','get_zone_line'],
      spot=['extends Area3D','get_event_name','get_prompt','get_story_line'],
      smoke=['ARAMOOR_MAIN_WALKAROUND_SMOKE_GREEN','First Night returns intact']
    )
    for path,tokens in (
      (SCRIPT,required['main']),(HUD,required['hud']), (BUILDER,required['world']),
      (HOTSPOT,required['spot']),(MAIN_TEST,required['smoke'])):
        content=path.read_text()
        for token in tokens:
            if token not in content:errors.append("MISSING_GAME_INTEGRATION:"+token)
    if world.get("source",{}).get("modulePdfInspected") is not False:
        errors.append("MODULE_PDF_FALSE_PROOF")
    if world.get("artPolicy",{}).get("publicAllowed") is not False:
        errors.append("WORLD_PRIVATE_LEAK")
    if truth.get("status") != "AMBER_PROPOSED_SEAL_OF_TRUTH":
        errors.append("SOURCE_TRUTH_CHANGED_UNEXPECTEDLY")
    if truth.get("crownStatus") != "STOP":
        errors.append("GLOBAL_CROWN_ESCALATION")
    if errors:
        raise SystemExit("RED_GODOT_MILESTONES: "+",".join(errors))
    print("GREEN_GODOT4_MILESTONE_SOURCE_AUDIT")
    print("AUDITED_MILESTONES=20")
    print("NEGATIVE_CONTROLS=7")
    print("PRIVATE_REFERENCE_INGEST=METADATA_ONLY")
    print("ARAMOOR_WALKAROUND=REQUIRES_HEADLESS_SMOKE")
    print("FULL_PRODUCT_CROWN=STOP")


if __name__=="__main__":
    main()
