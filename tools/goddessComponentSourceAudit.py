#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "game" / "assets" / "GODDESS_COMPONENT_CONTRACT_V1.json"
ASSEMBLER = ROOT / "scripts" / "game" / "characterComponentAssembler.gd"
AVATAR = ROOT / "scripts" / "game" / "goddessAvatar.gd"
SCENE = ROOT / "scenes" / "GoddessAvatar.tscn"

errors = []

def need(ok, message):
    if not ok:
        errors.append(message)

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
assembler = ASSEMBLER.read_text(encoding="utf-8")
avatar = AVATAR.read_text(encoding="utf-8")
scene = SCENE.read_text(encoding="utf-8")

need(contract.get("schema") == "luhmOs.goddessComponentContract.v1", "contract schema drift")
need(contract.get("authority") == "Professor", "Professor authority missing")
need(contract.get("crownStatus") == "STOP", "Crown must STOP")
need(set(contract.get("characters", {}).keys()) == {"lum","urd","belldandy","skuld"}, "character set drift")
need(contract.get("characters", {}).get("lum", {}).get("body") == "res://assets/lum/luhm.glb", "Lum body donor path drift")
need(contract.get("runtimeLaw", {}).get("externalThirdPartyRuntimeAsset") is False, "third-party runtime firewall missing")
need(contract.get("runtimeLaw", {}).get("componentSwapDoesNotGrantCanon") is True, "component swap promotion guard missing")

for token in ["assemble_character", "mount_component", "ResourceLoader.exists", "PackedScene", "_path_allowed", "canonPromoted"]:
    need(token in assembler, f"assembler token missing: {token}")

for socket in ["BodySocket","HeadSocket","HairSocket","OutfitSocket","AccessorySocket","MaterialSocket","PhysicsSocket"]:
    need(socket in scene, f"socket missing: {socket}")

for token in ["characterMorphController.gd", "characterComponentAssembler.gd", "runtime_summary", "crownAuthority"]:
    need(token in avatar, f"avatar token missing: {token}")

if errors:
    print("GODDESS_COMPONENT_SOURCE_AUDIT=FAIL")
    for error in errors:
        print("ERROR=" + error)
    raise SystemExit(2)

print("GODDESS_COMPONENT_SOURCE_AUDIT=PASS")
print("SLOTS=body,head,hair,outfit,accessories,materialOverlays,physicsChains")
print("LUM_BODY_PATH=STAGED")
print("URD_BODY=UNASSIGNED")
print("BELLDANDY_BODY=UNASSIGNED")
print("SKULD_BODY=UNASSIGNED")
print("RUNTIME_EXECUTION=NOT_CLAIMED")
print("CROWN_STATUS=STOP")
