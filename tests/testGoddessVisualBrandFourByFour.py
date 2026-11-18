#!/usr/bin/env python3
"""Proof that 4x4 creative branding does not mutate voice, gameplay, family, or build authority."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
def read(p):
    return json.loads((ROOT/p).read_text(encoding="utf-8"))
b=read("doctrine/goddessVisualBrandFourByFourV1.json")
v=read("doctrine/voiceAmbientIntentV1.json")
name=read("doctrine/japaneseNameTriggerLayerV1.json")
matrix=read("doctrine/japaneseVoice64MatrixV1.json")
agents=read("doctrine/luhmAiControlPlaneV1.json")
game=read("game/canon/CHARACTER_CANON_V1.json")
crew=read("doctrine/aliasOnlyProductionCreditsAndMocapV1.json")

def need(ok,msg):
    if not ok: raise AssertionError("RED_VISUAL_BRAND_FOUR_BY_FOUR:"+msg)
need(b["schema"]=="luhmOs.goddessVisualBrandFourByFour.v1","schema")
need(b["status"]=="PROPOSED_VISUAL_DIRECTION_ONLY","candidate must not imply approval")
need(b["axis"]["rows"]==["lum","urd","belldandy","skuld"],"four cabinet identities")
need(b["axis"]["columns"]==["silhouette","fashionCulture","interactiveGame","filmCampaign"],"four visual surfaces")
need(b["axis"]["resultCellCount"]==16,"must have exactly 16 creative cells")
need({b["characters"][key]["canonicalAgentId"] for key in b["axis"]["rows"]}=={"lum","urdDoctorGoddess","belldandySecretary","skuldResearch"},"four machine ids")
need(set(b["characters"])==set(b["axis"]["rows"]),"no invented goddess")
need(set(b["characters"].keys()).issubset({"lum","urd","belldandy","skuld"}),"goddess names only")
need(len(agents["agents"])==15,"15 registered AI ids unchanged")
for key in b["axis"]["rows"]:
    c=b["characters"][key]
    need(c["characterAgeFloorForMatureVariant"]>=30,"adult maturity: "+key)
    for surface in b["axis"]["columns"]:
        need(isinstance(c[surface],str) and len(c[surface])>18, "no blank art cell: "+key+"/"+surface)
need(b["adultPresentation"]["minimumAgeForMatureStyledCharacter"]>=30,"age floor")
need(b["adultPresentation"]["youthfulFranchiseVersionSexualizationForbidden"] is True,"youth/IP separation")
need(b["adultPresentation"]["beautyReferencesMayNotCloneRealActorsOrPerformers"] is True,"no real actor copy")
need("minimumAge" in game["characters"]["skuld"],"legacy age requirement preserved as evidence")
need(game["characters"]["skuld"]["minimumAge"]<=b["characters"]["skuld"]["characterAgeFloorForMatureVariant"],"mature version not younger than game")
need("existingCanonConflict" in b["characters"]["skuld"],"source conflict has explicit gap")
need(b["witchingHour"]["canonicalSkill"]=="agents/witchingHourCoding/SKILL.md","Witching Hour program")
need(b["witchingHour"]["notAnAestheticDepartment"] is True and b["witchingHour"]["notAnAnimeCharacterFamily"] is True,"program/culture firewall")
need(b["japaneseMythology"]["notWitchingHourProgramming"] is True,"folklore stays folklore")
need(b["domainSeparation"]["voiceInputGrid"].startswith("FOUR_BY_FOUR_BY_FOUR=64"),"do not rewrite HEX64")
need(matrix["addressing"]["totalCells"]==64,"voice HEX64 still distinct")
need(name["visualBrandFourByFour"]["source"]=="doctrine/goddessVisualBrandFourByFourV1.json","naming pointer")
need(name["visualBrandFourByFour"]["inventedMamaAliasForbidden"] is True,"no invented Mama")
aliases=v["voiceAliases"]["projectContextAliases"]
need(not ({"Mom","Mum","Mama"} & set(aliases)),"invented Mom/Mum/Mama to Lum mapping")
need(v["voiceAliases"]["disallowedGoddessAliases"]==["Mom","Mum","Mama"],"explicit disallowed alias audit")
need(aliases["Erd"]["canonicalAgentId"]=="urdDoctorGoddess","spoken Urd correction")
need(len(crew["productionDivisions"])==2,"human film and game divisions unchanged")
need(b["deliverableRules"]["originalHumanSketchMasterFirst"] is True,"human art stays master")
need(b["statusGates"]["websitePublication"]=="NOT_APPLIED" and b["statusGates"]["finalCrown"]=="STOP","no false release")
print("GREEN_GODDESS_4X4_SOURCE_ART_DIRECTION_ONLY")
print("matrix=16; voiceHex64=64; AI_roster=15; humanCrew=2; inventedMamaAlias=none; crown=STOP")
