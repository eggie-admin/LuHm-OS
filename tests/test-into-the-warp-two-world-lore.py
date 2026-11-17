"""Two-layer Into the Warp military/MMORPG continuity; source-only audit."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
lore = json.loads((root / "media/pirate-daddy-film/into-the-warp-two-world-lore-v1.json").read_text())
armor = json.loads((root / "media/pirate-daddy-film/into-the-warp-armor-incident-canon-v1.json").read_text())

assert lore["schema"] == "luhmOs.intoTheWarpTwoWorldLore.v1"
assert lore["originalApprovedScreenplay"]["modify"] is False
assert lore["fictionDisclaimer"]["separateFromRealTimeline"] is True
assert lore["fictionDisclaimer"]["worldOfWarcraftMilitaryAccess"] == "FICTIONAL_CLASSIFIED_EARLY_ACCESS_OR_WARP_ANOMALY"
assert lore["fictionDisclaimer"]["antiDaddyGoogleRole"] == "FICTIONAL_ALTERNATE_UNIVERSE_COMPANY_BOSS"
assert lore["fictionDisclaimer"]["attributionRule"].startswith("Use fictional narrator")
assert [x["id"] for x in lore["universe"]["layers"]] == ["physicalWorld", "toonWorld"]
assert lore["characters"]["bigDaddy"]["military"]["callsign"] == "Mr. Buttons"
assert lore["characters"]["bigDaddy"]["military"]["backpackPatch"]["lower"] == "MR. BUTTONS"
assert lore["characters"]["bigDaddy"]["toonWorldMode"]["hairColor"] == "NOT_YET_PINNED_EXCEPT_NON_GRAY"
assert lore["characters"]["antiDaddy"]["militaryPast"]["sameUnitAsBigDaddy"]
assert lore["characters"]["antiDaddy"]["currentHair"]["style"] == "longObsessivelyMaintainedPonytail"
assert lore["characters"]["antiDaddy"]["civilianGrunge"]["redFlannel"]
assert lore["characters"]["antiDaddy"]["civilianGrunge"]["blackJeans"]
assert "Demon Jazz" in lore["characters"]["lum"]["meeting"]
assert lore["climax"]["exactPunchline"] == "HOW DARE YOU DO THIS IN FRONT OF MY ALEX?!"
assert lore["climax"]["oldArmorVsEpicLoot"].startswith("Physical armor")
assert lore["production"]["named3dBodiesBuiltByThisRecord"] is False
assert lore["production"]["publicRightToBlizzardGoogleAssets"] is False
assert lore["production"]["publicReleaseApproved"] is False
assert armor["twoWorldContinuity"]["source"] == "media/pirate-daddy-film/into-the-warp-two-world-lore-v1.json"
assert armor["twoWorldContinuity"]["physicalMilitaryArmorAndGameLootAreDistinct"]
print("GREEN: two-world fictional lore and continuity contract, without false historical/runtime claims")
