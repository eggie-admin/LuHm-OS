#!/usr/bin/env python3
import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
required=[
    "doctrine/gameplayVerticalSliceV1.json",
    "doctrine/gameplayVerticalSliceCrownReceiptV1.json",
    "game/story/firstNightQuest.json",
    "scripts/game/questDirector.gd",
    "scripts/game/interactable.gd",
    "scripts/main.gd",
    "scripts/game/gameHud.gd",
    "scripts/game/neonWorld.gd",
    "scripts/game/lumCoffeeHouseScene.gd",
    "scripts/game/cathedralWorld.gd",
    "scripts/game/oniSummonBeacon.gd",
    "scripts/game/oniEchoCompanion.gd",
]
missing=[p for p in required if not (root/p).is_file()]
errors=[]

if not missing:
    contract=json.loads((root/"doctrine/gameplayVerticalSliceV1.json").read_text())
    receipt=json.loads((root/"doctrine/gameplayVerticalSliceCrownReceiptV1.json").read_text())
    quest=json.loads((root/"game/story/firstNightQuest.json").read_text())
    if contract.get("status")!="CANONICAL_GAMEPLAY_SOURCE": errors.append("gameplay contract status drift")
    if contract.get("workingLane")!="CANONICAL_SOURCE": errors.append("gameplay working lane drift")
    if contract.get("promotion") is not True: errors.append("gameplay promotion must be true")
    if contract.get("professorApproval") is not True: errors.append("Professor gameplay approval missing")
    if contract.get("crownStatus")!="CROWNED_SOURCE_MILESTONE": errors.append("gameplay Crown status drift")
    if contract.get("crownReceipt")!="doctrine/gameplayVerticalSliceCrownReceiptV1.json": errors.append("gameplay crown receipt drift")
    if contract.get("installBoundary")!="PARKED": errors.append("install boundary must remain parked")
    if contract.get("releaseAuthority") is not False: errors.append("release authority must remain false")
    if contract.get("publicationAuthority") is not False: errors.append("publication authority must remain false")
    if contract.get("productionSigningAuthority") is not False: errors.append("signing authority must remain false")
    if receipt.get("status")!="crownApprovedCandidate": errors.append("gameplay receipt status drift")
    if receipt.get("authority")!="Professor": errors.append("gameplay receipt authority drift")
    if receipt.get("approvedCandidateSourceRef")!="831368b087b007a00cc7e77563877ed09b9001ef": errors.append("approved candidate source drift")
    if receipt.get("evidence",{}).get("exactHeadGreen") is not True: errors.append("approved candidate proof missing")
    if quest.get("status")!="canonicalGameplay": errors.append("quest status drift")
    if quest.get("professorApproval") is not True: errors.append("quest approval missing")
    if quest.get("crownReceipt")!="doctrine/gameplayVerticalSliceCrownReceiptV1.json": errors.append("quest crown receipt drift")
    steps=quest.get("steps",[])
    expected=["talkLumRiverwalk","collectSignalShard","collectCoffee","clearStaticWisp","sealFirstNight"]
    actual=[s.get("event") for s in steps]
    if actual!=expected: errors.append(f"quest event order drift: {actual}")

    main=(root/"scripts/main.gd").read_text()
    hud=(root/"scripts/game/gameHud.gd").read_text()
    interaction_visual=(root/"scripts/game/interactable.gd").read_text()
    player=(root/"scripts/game/playerController.gd").read_text()
    oni_beacon=(root/"scripts/game/oniSummonBeacon.gd").read_text()
    oni_companion=(root/"scripts/game/oniEchoCompanion.gd").read_text()
    source_truth=json.loads((root/"doctrine/currentSourceTruthV3.json").read_text())
    game_layer=source_truth.get("gameLayer",{})
    if game_layer.get("contract")!="doctrine/gameplayVerticalSliceV1.json": errors.append("current source truth gameLayer contract drift")
    if game_layer.get("workingLane")!="CANONICAL_SOURCE": errors.append("current source truth gameLayer lane drift")
    if game_layer.get("status")!="CANONICAL_GAMEPLAY_SOURCE": errors.append("current source truth gameLayer status drift")
    if game_layer.get("promotion") is not True: errors.append("current source truth gameLayer promotion missing")
    if game_layer.get("crownStatus")!="CROWNED_SOURCE_MILESTONE": errors.append("current source truth gameLayer crown drift")
    if game_layer.get("installBoundary")!="PARKED": errors.append("current source truth install boundary must remain parked")
    if "Titan7MilestoneScript" in main or 'add_child(titan7_milestone)' in main: errors.append("stale Titan7 milestone overlay still active")
    for token in ["QuestDirectorScript","FIRST_NIGHT_QUEST_PATH","_update_interaction_target","interact_requested",'begins_with("travel:")',"set_fast_travel_enabled(false)","set_fast_travel_enabled(true)",'event_name == "clearStaticWisp"',"pulse_effect","OniSummonBeaconScript","_spawn_oni_beacon(name)","OniEchoCompanionScript","_spawn_oni_companion(oni_name)"]:
        if token not in main: errors.append(f"main missing {token}")
    for token in ["signal interact_requested","set_interaction_prompt","set_quest","set_fast_travel_enabled","OniSummonCard","show_oni_request","ROUTING ONLY · NO WORKER STARTED"]:
        if token not in hud: errors.append(f"HUD missing {token}")
    for token in ['android_web3_plugin.hideCockpit()','game_hud.show_world()','game_hud.show_oni_request(name)','player_controller.set_world_active(true)']:
        if token not in main: errors.append(f"Oni summon transition missing {token}")
    for token in ["collectSignalShard","collectCoffee","clearStaticWisp","_build_signal_shard","_build_coffee","_build_static_wisp"]:
        if token not in interaction_visual: errors.append(f"interaction visual missing {token}")
    if "func pulse_effect(" not in player:
        errors.append("player pulse effect missing")
    for token in ["extends Area3D","OniBeaconVisual","TorusMesh","SphereMesh","_accent_for","get_event_name","get_prompt","dismiss","queue_free()"]:
        if token not in oni_beacon: errors.append(f"Oni beacon missing {token}")
    if "agent-roster-v1.png" in oni_beacon:
        errors.append("Oni beacon may not repurpose loading-only roster sprites")
    for token in ['event_name.begins_with("oni:")','echo acknowledged','nearest_interactable.call("dismiss")']:
        if token not in main: errors.append(f"Oni beacon interaction missing {token}")
    if 'return "TOUCH " + oni_name.to_upper() + " ECHO"' not in oni_beacon:
        errors.append("Oni beacon interaction prompt missing")
    for token in ["extends Node3D","OniEchoCompanionVisual","_lifetime := 8.0","target.global_position","global_position.lerp","queue_free()"]:
        if token not in oni_companion: errors.append(f"Oni companion missing {token}")
    if "agent-roster-v1.png" in oni_companion:
        errors.append("Oni companion may not repurpose loading-only roster sprites")
    if "Presence only; still no worker started." not in main:
        errors.append("Oni companion authority disclaimer missing")
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
    "crownStatus":"CROWNED_SOURCE_MILESTONE"
},indent=2))
