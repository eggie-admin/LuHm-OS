"""Fail-closed Anti-Daddy character-design seal; cinematic art is not rig proof."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
p=json.loads((root/"media/pirate-daddy-film/into-the-warp-anti-daddy-character-seal-v1.json").read_text())
lore=json.loads((root/"media/pirate-daddy-film/into-the-warp-two-world-lore-v1.json").read_text())
assert p["schema"]=="luhmOs.antiDaddyCharacterSeal.v1"
assert p["sealDate"]=="2026-11-17"
assert p["approvalScope"]["identityAndSilhouette"]
assert p["approvalScope"]["neutralStudioInsteadOfCave"]
assert p["approvalScope"]["actualFinal3dLikeness"] is False
assert p["referenceArt"][-1]["sha256"]=="8c19b63e180dec2651a3a6dfa477952ee9dcc0bc7097c3897ba5d698706cc1a1"
assert p["referenceArt"][-1]["caveRemoved"]
assert all(x["publicAllowed"] is False for x in p["referenceArt"])
assert len(p["outfitModes"])==5
assert {x["id"] for x in p["outfitModes"]}=={"militaryShaved","grungeCoder","corporateSuave","finalBossCombat","toonWorldJrpg"}
assert p["actual3dProof"]["sha256"]=="9f5f6a26fb827933502953f6c4a2e49f4b06a681cb52845892a08584df4e7627"
assert p["actual3dProof"]["joints"]==22
assert p["actual3dProof"]["realGodot47ImportTested"] is False
assert p["actual3dProof"]["fullFacialVisemesBuilt"] is False
assert p["actual3dProof"]["actualBlendkitDonorAssetUsed"] is False
assert p["constraints"]["originalFilmScriptUnchanged"]
assert p["constraints"]["protectPrivateReferencePixels"]
assert p["nextMilestone"]["state"]=="QUEUED"
assert lore["characters"]["antiDaddy"]["militaryPast"]["sameUnitAsBigDaddy"]
assert lore["fictionDisclaimer"]["antiDaddyGoogleRole"]=="FICTIONAL_ALTERNATE_UNIVERSE_COMPANY_BOSS"
print("GREEN: cave-free Anti-Daddy character-design seal, actual 3D blockout scope, and Big Daddy handoff")
