#!/usr/bin/env python3
"""Read-only source audit for the CAST-to-milestone-delivery contract."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


forge = load("doctrine/forgeTwinsV3.json")
delivery = forge["milestoneDelivery"]
cast = forge["castEnvelope"]
escalation = load(delivery["escalationKernel"])
operating = load(delivery["distinctOperatingLayers"])
catalog = load(delivery["knownCreativeRecovery"]["galleryCatalog"])
gallery_receipt = load(delivery["knownCreativeRecovery"]["galleryReceipt"])
matrix = load(delivery["knownCreativeRecovery"]["assetMatrix"])
errors: list[str] = []


def need(condition: bool, reason: str) -> None:
    if not condition:
        errors.append(reason)


need(forge["crownStatus"] == "STOP", "Forge must retain Crown STOP")
need(cast["castWord"] == "cast", "CAST magic word changed")
need(cast["singleUse"] is True and cast["consumedOnAttempt"] is True, "CAST single-use guard lost")
need(cast["persistentAuthorizationAllowed"] is False, "persistent CAST enabled")
need("deployment" in cast["doesNotAuthorize"] and "publication" in cast["doesNotAuthorize"], "CAST release boundary weakened")
need(delivery["status"] == "SOURCE_ONLY_CANDIDATE_NO_INSTALL_OR_RUNTIME_CLAIM", "source-only boundary lost")
need([x["tier"] for x in delivery["escalationTiers"]] == [0, 1, 2, 3], "escalation count/order drift")
need([x["tier"] for x in escalation["tierSemantics"]] == [0, 1, 2, 3], "wrong escalation kernel")
need([x["tier"] for x in operating["tiers"]] == [1, 2, 3, 4], "four presentation layers missing")
need(delivery["packageManagerAnalogy"]["cast"].startswith("single-use build attempt"), "CAST broadened beyond single build")
need("Professor" in delivery["packageManagerAnalogy"]["install"], "install lacks Professor gate")
need(delivery["sequence"][-1] == "recordFinalReceiptOrBlocker", "milestone prematurely terminates at CAST")
needed = {"milestoneId", "taskId", "sourceRef", "scopeId", "expectedVisibleResult", "deliveryTarget", "artifactLocatorOrBlocker", "evidenceRefs"}
need(needed.issubset(delivery["requiredMilestoneFields"]), "milestone handoff insufficient")
for gate in ("castAuthorizedIsNotBuilt", "builtIsNotInstalled", "sourceGalleryIsNotRuntimeProof", "unverifiedMustNotBeLabeledGreen", "showReviewableLinkWhenAvailable"):
    need(delivery["evidenceRules"].get(gate) is True, f"missing truth guard: {gate}")
for gate in ("oneUseCastStillRequired", "installIsNotAuthorizedByCast", "installNeedsExactTargetAndSeparateProfessorApproval", "releaseAndPublicationRemainForbiddenWithoutTheirOwnCrown"):
    need(delivery["authorityGuards"].get(gate) is True, f"missing Crown guard: {gate}")
for path in delivery["knownCreativeRecovery"].values():
    if isinstance(path, str) and (path.startswith("media/") or path.startswith("doctrine/") or path.startswith("frontEnd/") or path.startswith("receipts/") or path.startswith("manual/")):
        need((ROOT / path).is_file(), f"missing recovered source: {path}")
need(len(catalog["cards"]) == gallery_receipt["cardCount"] == 29, "Yume gallery count/receipt mismatch")
need(gallery_receipt["referenceOnly"] is True and gallery_receipt["promotion"] is False, "gallery falsely promoted")
need(matrix["proofStage"]["otherThreeBodies"] == "UNASSIGNED", "other goddess bodies falsely promoted")
need(delivery["knownCreativeRecovery"]["originalArtPrivateDriveFolder"] == "Character Reference Sheets", "private art location lost")
need("private" in delivery["knownCreativeRecovery"]["rightsRule"].lower() or "reference-only" in delivery["knownCreativeRecovery"]["rightsRule"].lower(), "art rights firewall missing")
need((ROOT / "tools/forgeCastGate.py").is_file(), "original CAST tool missing")
need((ROOT / "manual/castMilestoneRecovery20261012.md").is_file(), "human-readable recovery ledger missing")

if errors:
    print("CAST_MILESTONE_SOURCE_AUDIT=RED")
    for err in errors:
        print("ERROR:", err)
    raise SystemExit(1)

print("CAST_MILESTONE_SOURCE_AUDIT=GREEN_SOURCE_ONLY")
print("castIsStillSingleUse=true")
print("installRequiresSeparateProfessorTargetApproval=true")
print("existingYumeGalleryCards=29")
print("privateCharacterSheets=2_nameOnly")
print("finishedGoddessBodies=NOT_PROVEN_FOR_THREE")
print("liveArtPresentation=UNVERIFIED")
print("crownStatus=STOP")
