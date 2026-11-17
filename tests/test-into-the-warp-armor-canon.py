"""Source-only guard: Armor Incident must bind Canon character art before generation.

This test does not inspect protected image bytes or prove 3D animation/public release.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "media/pirate-daddy-film/into-the-warp-armor-incident-canon-v1.json").read_text())
game = json.loads((ROOT / "game/canon/CHARACTER_CANON_V1.json").read_text())
art = json.loads((ROOT / "media/public-release-art-ledger.json").read_text())

assert manifest["schema"] == "luhmOs.intoTheWarpArmorIncidentCanon.v1"
assert manifest["state"] == "PROFESSOR_APPROVED_SCOPED_VISUAL_DIRECTION"
assert manifest["originalFilmLock"]["modify"] is False
assert manifest["originalFilmLock"]["sha256"] == "6f6054e86f6f6dd74ffc9355a34f86d2ff4c3822f1c8c4f2d20b8a701b38f9ef"
assert manifest["defaultCanonResolution"]["generatedFacesMayReplaceApprovedIdentity"] is False
assert manifest["defaultCanonResolution"]["genericSubstituteForCanonCharacter"] is False
assert len(manifest["defaultCanonResolution"]["requiredPreflight"]) >= 6
assert manifest["visualApproval"]["originalFourProfessorModesRemainValid"]
assert manifest["visualApproval"]["existingBerserkerTailoredSuitModeNotReplaced"]

bindings = manifest["characterBindings"]
assert {"bigDaddy", "lum", "urd", "belldandy", "skuld", "yume", "alex", "antiDaddy", "mrButtons"} <= bindings.keys()
for character in ("lum", "urd", "belldandy", "skuld"):
    assert character in game["characters"], character
    assert character in art["characters"], character
    assert bindings[character]["referenceFile"], character
    assert re.fullmatch(r"[0-9a-f]{64}", bindings[character]["referenceHash"]), character
    assert bindings[character]["canonPath"] == f"game/canon/CHARACTER_CANON_V1.json#characters/{character}"

assert bindings["lum"]["referenceHash"] == art["characters"]["lum"]["masterProofV2"]["sha256"]
assert bindings["yume"]["inventVisualIdentity"] is False
assert bindings["yume"]["approvedPersonifiedCharacterSheet"] == "NOT_VERIFIED"
assert bindings["alex"]["humanLikenessOrPortraitRequired"] is False

still = manifest["approvedStill"]
assert re.fullmatch(r"[0-9a-f]{64}", still["sha256"])
assert still["publicAllowed"] is False
assert still["durablePrivateDriveCopyProven"] is False
assert still["finalCharacterRigProven"] is False
assert still["allDepictedSupportingFacesApproved"] is False

release = manifest["productionStatus"]
for status in ("actual3dBigDaddyRigProven", "actual3dGoddessBodiesAllProven",
               "completeAnimatedVideoProven", "rightsAndDistributionCleared",
               "automaticPublication", "independentAgentsActivated"):
    assert release[status] is False, status
assert release["publicRelease"] == "STOP"

# Public repository should contain only logical references, not private Drive URLs or IDs.
serialized = json.dumps(manifest)
assert "drive.google.com" not in serialized
assert "docs.google.com" not in serialized
assert "file_000000" not in serialized
print("GREEN: scoped armor design approval + Canon reference-first bindings; no runtime/public claim")
