#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

lane = load("doctrine/contentLaneDoctrineV1.json")
matrix = load("doctrine/assetEligibilityMatrixV1.json")
truth = load("doctrine/SOURCE_OF_TRUTH.json")
yume = load("doctrine/yumeCreativePipelineV1.json")
media = load("doctrine/mediaAssetFactoryV1.json")

checks = [
    ("lane.schema", lane.get("schema") == "luhmOs.contentLaneDoctrine.v1"),
    ("lane.proposed", lane.get("status") == "PROPOSED_CANON_LAW"),
    ("lane.professor", lane.get("authority") == "Professor"),
    ("lane.lumBoss", lane.get("boss") == "lum"),
    ("lane.oneCanon", lane.get("canonLaw", {}).get("oneCharacterCanon") is True),
    ("lane.noSplitCanon", lane.get("canonLaw", {}).get("separateCharacterCanonsPerLane") is False),
    ("lane.privateExists", "privateMutation" in lane.get("lanes", {})),
    ("lane.betaExists", "betaAfterDark" in lane.get("lanes", {})),
    ("lane.publicExists", "cathedralPublic" in lane.get("lanes", {})),
    ("lane.privateNoPublic", lane["lanes"]["privateMutation"].get("publicDistributionAllowed") is False),
    ("lane.betaNoPublic", lane["lanes"]["betaAfterDark"].get("publicDistributionAllowed") is False),
    ("lane.publicFamily", lane["lanes"]["cathedralPublic"].get("maturityCeiling") == "familySafe"),
    ("lane.publicNoSexualized", lane["lanes"]["cathedralPublic"].get("sexualizedPresentationAllowed") is False),
    ("lane.adultLock", lane.get("adultLock", {}).get("allSexualizedPresentationRequiresAdultCharacter") is True),
    ("lane.noAmbiguousSexualization", lane.get("adultLock", {}).get("ageAmbiguousCharacterSexualizationForbidden") is True),
    ("lane.noYoungCodedSexualization", lane.get("adultLock", {}).get("youngCodedCharacterSexualizationForbidden") is True),
    ("lane.promotionOrder", lane.get("promotionFlow") == ["privateMutation", "betaAfterDark", "cathedralPublic"]),
    ("lane.noReleaseAuthority", lane.get("releaseAuthority") is False),
    ("lane.noPublicationAuthority", lane.get("publicationAuthority") is False),
    ("lane.crownStop", lane.get("crownStatus") == "STOP"),
    ("matrix.schema", matrix.get("schema") == "luhmOs.assetEligibilityMatrix.v1"),
    ("matrix.bound", matrix.get("contentLaneContract") == "doctrine/contentLaneDoctrineV1.json"),
    ("matrix.privateFailClosed", matrix.get("fallbackLaw", {}).get("missingLaneMetadata") == "failClosed"),
    ("matrix.unknownMaturityFailClosed", matrix.get("fallbackLaw", {}).get("unknownMaturity") == "failClosed"),
    ("matrix.publicFallback", "ApprovedPublicSafeFallbackOrFailClosed" in matrix.get("fallbackLaw", {}).get("privateAdultOrMatureAssetInPublicBuild", "")),
    ("matrix.noAiPromotion", matrix.get("crossLaneRules", {}).get("aiCannotPromoteAsset") is True),
    ("matrix.noProviderPromotion", matrix.get("crossLaneRules", {}).get("providerCannotPromoteAsset") is True),
    ("truth.bound", truth.get("contentLanes", {}).get("contract") == "doctrine/contentLaneDoctrineV1.json"),
    ("yume.bound", yume.get("contentLaneDoctrine") == "doctrine/contentLaneDoctrineV1.json"),
    ("media.bound", media.get("contentLaneDoctrine") == "doctrine/contentLaneDoctrineV1.json"),
]

failed = [name for name, ok in checks if not ok]
for idx, (name, ok) in enumerate(checks, 1):
    print(f"{'PASS' if ok else 'FAIL'} {idx:02d}/{len(checks)} {name}")
if failed:
    raise SystemExit("CONTENT_LANE_AUDIT=RED failed=" + ",".join(failed))
print("CONTENT_LANE_AUDIT=GREEN")
print(f"passes={len(checks)}/{len(checks)}")
print("lane=PROPOSED_ONLY")
print("crown=STOP")
