#!/usr/bin/env python3
import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
required=[
    "doctrine/gameplayVerticalSliceV1.json",
    "game/story/firstNightQuest.json",
    "scripts/game/questDirector.gd",
    "scripts/game/interactable.gd",
    "scripts/main.gd",
    "scripts/game/gameHud.gd",
    "scripts/game/neonWorld.gd",
    "scripts/game/lumCoffeeHouseScene.gd",
    "scripts/game/cathedralWorld.gd",
]
missing=[p for p in required if not (root/p).is_file()]
errors=[]

if not missing:
    contract=json.loads((root/"doctrine/gameplayVerticalSliceV1.json").read_text())
    quest=json.loads((root/"game/story/firstNightQuest.json").read_text())
    if contract.get("status")!="PROPOSED_SOURCE_ONLY": errors.append("gameplay contract must remain proposed")
    if contract.get("workingLane")!="PROPOSED_ONLY": errors.append("working lane drift")
    if contract.get("promotion") is not False: errors.append("promotion must remain false")
    if contract.get("crownStatus")!="STOP": errors.append("Crown must remain STOP")
    if contract.get("installBoundary")!="PARKED": errors.append("install boundary must remain parked")
    if quest.get("status")!="proposedGameplay": errors.append("quest status drift")
    steps=quest.get("steps",[])
    expected=["talkLumRiverwalk","collectSignalShard","collectCoffee","clearStaticWisp","sealFirstNight"]
    actual=[s.get("event") for s in steps]
    if actual!=expected: errors.append(f"quest event order drift: {actual}")

    main=(root/"scripts/main.gd").read_text()
    hud=(root/"scripts/game/gameHud.gd").read_text()
    interaction_visual=(root/"scripts/game/interactable.gd").read_text()
    player=(root/"scripts/game/playerController.gd").read_text()
    source_truth=json.loads((root/"doctrine/currentSourceTruthV3.json").read_text())
    game_layer=source_truth.get("gameLayer",{})
    if game_layer.get("contract")!="doctrine/gameplayVerticalSliceV1.json": errors.append("current source truth gameLayer contract drift")
    if game_layer.get("workingLane")!="PROPOSED_ONLY": errors.append("current source truth gameLayer must remain proposed")
    if game_layer.get("installBoundary")!="PARKED": errors.append("current source truth install boundary must remain parked")
    if "Titan7MilestoneScript" in main or 'add_child(titan7_milestone)' in main: errors.append("stale Titan7 milestone overlay still active")
    for token in ["QuestDirectorScript","FIRST_NIGHT_QUEST_PATH","_update_interaction_target","interact_requested",'begins_with("travel:")',"set_fast_travel_enabled(false)","set_fast_travel_enabled(true)",'event_name == "clearStaticWisp"',"pulse_effect"]:
        if token not in main: errors.append(f"main missing {token}")
    for token in ["signal interact_requested","set_interaction_prompt","set_quest","set_fast_travel_enabled"]:
        if token not in hud: errors.append(f"HUD missing {token}")
    for token in ["collectSignalShard","collectCoffee","clearStaticWisp","_build_signal_shard","_build_coffee","_build_static_wisp"]:
        if token not in interaction_visual: errors.append(f"interaction visual missing {token}")
    if "func pulse_effect(" not in player:
        errors.append("player pulse effect missing")
    travel_tokens = {
        "scripts/game/neonWorld.gd": ["travel:lumCoffeeHouse","travel:cathedral"],
        "scripts/game/lumCoffeeHouseScene.gd": ["travel:neonRiverwalk","travel:cathedral"],
        "scripts/game/cathedralWorld.gd": ["travel:neonRiverwalk","travel:lumCoffeeHouse"],
    }
    for world,tokens in travel_tokens.items():
        world_text=(root/world).read_text()
        for token in tokens:
            if token not in world_text:
                errors.append(f"{world} missing travel gate {token}")

    for world,event in [
        ("scripts/game/neonWorld.gd","talkLumRiverwalk"),
        ("scripts/game/neonWorld.gd","collectSignalShard"),
        ("scripts/game/lumCoffeeHouseScene.gd","collectCoffee"),
        ("scripts/game/cathedralWorld.gd","clearStaticWisp"),
        ("scripts/game/cathedralWorld.gd","sealFirstNight"),
    ]:
        if event not in (root/world).read_text():
            errors.append(f"{world} missing {event}")

if missing or errors:
    print(json.dumps({"status":"RED","missing":missing,"errors":errors},indent=2))
    sys.exit(1)

print(json.dumps({
    "status":"GREEN_GAMEPLAY_VERTICAL_SLICE_SOURCE",
    "scope":"source-only",
    "quest":"firstNightCircuit",
    "steps":5,
    "installBoundary":"PARKED",
    "crownStatus":"STOP"
},indent=2))
