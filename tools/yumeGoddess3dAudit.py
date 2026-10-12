#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine" / "yumeGoddess3dProductionV1.json"
MATRIX = ROOT / "media" / "goddess3d-production-matrix-v1.json"

errors = []

def need(ok, message):
    if not ok:
        errors.append(message)

d = json.loads(DOCTRINE.read_text(encoding="utf-8"))
m = json.loads(MATRIX.read_text(encoding="utf-8"))

need(d.get("schema") == "luhmOs.yumeGoddess3dProduction.v1", "schema drift")
need(d.get("authority") == "Professor", "Professor authority missing")
need(d.get("boss") == "lum", "Lum boss drift")
need(d.get("artDirection") == "yume", "Yume ownership drift")
need(d.get("productionLaw", {}).get("runtimeInterchange") == "glTF 2.0 binary (.glb)", "GLB interchange drift")
need(d.get("productionLaw", {}).get("secondaryMotion", {}).get("engineNativeFirst") == "SpringBoneSimulator3D", "secondary-motion architecture drift")
need(d.get("productionLaw", {}).get("secondaryMotion", {}).get("uncontrolledPhysics") is False, "uncontrolled physics must remain forbidden")
need(d.get("productionLaw", {}).get("topology", {}).get("automaticRetopoIsCandidateOnly") is True, "automatic retopo cannot self-promote")
need(d.get("productionLaw", {}).get("identityFirewall", {}).get("noGenericGothConvergence") is True, "identity firewall missing")
need(d.get("currentTruth", {}).get("lum", {}).get("baseGlbSha256") == "06bdfcc196e147c4cb92c7c5489110a8feb30ee8a8f362fac585802eced33b69", "Lum base GLB hash drift")
need(d.get("currentTruth", {}).get("lum", {}).get("knownRigFacts", {}).get("joints") == 24, "Lum donor joint count drift")
need(d.get("crownStatus") == "STOP", "Crown must remain STOP")
need(d.get("promotion") is False, "candidate must not self-promote")

ids = [x.get("id") for x in m.get("characters", [])]
need(ids == ["lum", "urd", "belldandy", "skuld"], "character work queue drift")
need(m.get("crownStatus") == "STOP", "matrix Crown must remain STOP")

# Proposed Yume doctrine cannot silently promote source/gallery/runtime evidence.
GALLERY = ROOT / "media" / "yumeReferenceGalleryV1.json"
GALLERY_RECEIPT = ROOT / "receipts" / "yumeReferenceGallery-20261008.json"
YUME_SKILL = ROOT / "agents" / "yumeArtOni" / "SKILL.md"
gallery = json.loads(GALLERY.read_text(encoding="utf-8"))
receipt = json.loads(GALLERY_RECEIPT.read_text(encoding="utf-8"))
skill = YUME_SKILL.read_text(encoding="utf-8")
privacy = d.get("sourcePrivacy", {})
reference = d.get("referenceGalleryGate", {})
ladder = d.get("proofLadder", {})
switch = d.get("characterSwitchSafety", {})
review = d.get("reviewBoundary", {})
need(d.get("workingLane") == "PROPOSED_ONLY", "Yume 3D source must remain proposed")
need(privacy.get("publicDriveIdsAllowed") is False, "public Drive IDs must be forbidden")
need(privacy.get("existingGitHistory", "").startswith("Removing IDs"), "history disclosure warning missing")
need(set(privacy.get("prohibitedPublicKeys", [])) >= {"driveSourceId", "driveApprovedArtFolder", "driveCandidateReviewFolder"}, "private key ban incomplete")
for character in ("lum", "urd", "belldandy", "skuld"):
    record = d.get("currentTruth", {}).get(character, {})
    need(not (set(record) & set(privacy.get("prohibitedPublicKeys", []))), f"private locator exposed: {character}")
    keys = [record.get("privateAssetRef", "")] if character == "lum" else list(record.get("privateAssetRefs", {}).values())
    need(bool(keys) and all(isinstance(x, str) and x.startswith("privateDrive:") for x in keys), f"logical private locator missing: {character}")
need(reference.get("referenceOnly") is True, "gallery must remain reference only")
need(reference.get("sourceLinkedCardMinimum", 0) >= 24, "gallery card minimum missing")
need(reference.get("catalogSourceChecksAreNotLiveBrowserProof") is True, "browser evidence boundary missing")
need(reference.get("previewsAreNotImportProof") is True, "preview/import firewall missing")
need(reference.get("noModBinaryDownloadWithoutLicenseReceipt") is True, "binary license firewall missing")
need(reference.get("thirdPartyGameCharacterAssetsExcludedFromOriginalRuntime") is True, "franchise asset firewall missing")
need(reference.get("noUnverifiedNexusRssClaims") is True, "Nexus RSS truth rule missing")
need(ladder.get("noSelfPromotion") is True and ladder.get("CIStaticSourceAuditNotGodotExecution") is True, "proof ladder must fail closed")
need(switch.get("requiredBodyAbsentMustNotDisplayStalePreviousCharacter") is True, "stale body switch safety missing")
need(switch.get("proofRequires", "").startswith("Godot 4.7"), "runtime proof target missing")
need(review.get("canonicalAuthority") == "Professor" and review.get("crownStatus") == "STOP", "review Crown boundary missing")
need(all(review.get(x) is False for x in ("buildAuthority","mergeAuthority","deploymentAuthority","publicationAuthority")), "unexpected Yume runtime authority")
need(gallery.get("schema") == "luhmOs.yumeReferenceGallery.v1", "gallery schema drift")
cards = gallery.get("cards", [])
need(len(cards) >= 24 and len({c.get("id") for c in cards}) == len(cards), "catalog size or identity drift")
need({"Fallout 4", "Resident Evil 2 (2019)", "Resident Evil 3 (2020)", "Resident Evil Village"}.issubset({c.get("game") for c in cards}), "four-world gallery coverage missing")
need(receipt.get("referenceOnly") is True and receipt.get("assetApproval") is False, "gallery receipt cannot approve asset")
need(receipt.get("promotion") is False and receipt.get("crownStatus") == "STOP", "gallery receipt cannot promote")
need(receipt.get("verification", {}).get("mobileVisualPreview") == "NOT_PROVEN", "historical mobile evidence unexpectedly rewritten")
need("doctrine/yumeGoddess3dProductionV1.json" in skill, "Yume skill missing proposed doctrine link")
need("must not display a stale previous body" in skill, "Yume skill missing stale character safety")

if errors:
    print("YUME_GODDESS_3D_AUDIT=FAIL")
    for e in errors:
        print("ERROR=" + e)
    raise SystemExit(2)

print("YUME_GODDESS_3D_AUDIT=PASS")
print("LUM_3D=PROVEN_CANDIDATE")
print("URD_3D=MISSING_RECONCILED_BODY")
print("BELLDANDY_3D=MISSING_RECONCILED_BODY")
print("SKULD_3D=MISSING_RECONCILED_BODY")
print("CROWN_STATUS=STOP")
