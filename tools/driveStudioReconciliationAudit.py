#!/usr/bin/env python3
"""Fail-closed public-source audit for privately inventoried Drive art.

Never fetches private Drive files in CI. Metadata discovery is not asset approval.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "doctrine/driveStudioReconciliationV1.json"


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def audit(contract, alignment, truth, kiosk):
    failures = []
    def check(ok, label):
        if not ok:
            failures.append(label)

    check(contract.get("schema") == "luhmOs.driveStudioReconciliation.v1", "schema")
    check(contract.get("authority") == "Professor" and contract.get("professorApproved") is True, "humanApproval")
    check(contract.get("scope") == "driveAssetDiscoveryAndDoctrinePromotion", "scope")
    check(contract.get("status") == "CROWNED_SCOPED_SOURCE_RECONCILIATION", "status")
    for key, value in (
        ("rawAssetBytesCopied", False), ("privateDriveIdentifiersInPublicRepo", False),
        ("releaseAuthority", False), ("productionSigningAuthority", False),
        ("spontaneousAgentActivation", False), ("noNewPaidServices", True)
    ):
        check(contract.get(key) is value, "authority:" + key)

    lanes = contract.get("tiers", [])
    keys = [entry.get("key") for entry in lanes]
    check(len(lanes) == 6 and len(set(keys)) == 6, "sixLanes")
    check(keys[:2] == ["lumAnimated", "lumPetSprites"], "firstActualAssets")
    allowed = {
        "lumAnimated", "lumPetSprites", "godotCharacterArt", "yumeMotionTitles",
        "rebelPrivate", "hydraMedia"
    }
    check(set(keys) == allowed, "laneInventory")
    for lane in lanes:
        check(lane.get("assetBytesHashed") is (lane.get("key") == "lumAnimated"), "hashEvidence:" + str(lane.get("key")))
        check(lane.get("artistCanonApproved") is False, "unapprovedArt:" + str(lane.get("key")))
        check(lane.get("formatImportTest") is False, "noImportedAsset:" + str(lane.get("key")))
        check(lane.get("runtime") not in {"APPROVED", "LIVE", "GREEN"}, "falseRuntime:" + str(lane.get("key")))

    first = contract.get("firstVerticalSlice", {})
    check(first.get("id") == "lumPrivateAnimatedPreview", "firstSlice")
    check(first.get("phase") == "SOURCE_GIF_BYTES_DECODED_PREVIEW_PENDING", "importFalsePositive")
    check(first.get("sha256") == "a9df1d2b5c63d5740be8c476b59f389171b99609a14cd02fc8ae7568d27b2aba", "hashFalsePositive")
    check(first.get("publicMediaRelease") is False, "publicDerivativeLeak")
    check(first.get("physicalAndroid") == "PENDING", "physicalFalsePositive")
    check(first.get("preview") == "BROWSER_SOURCE_CANDIDATE_NOT_DEVICE_PROVEN", "previewFalsePositive")

    guards = contract.get("security", {})
    for k in ("doNotExposePrivateDriveIdsOrUrls", "doNotExposeRawFileNames",
              "doNotTransferOrPromoteOnInventoryOnly", "doNotExecuteArchivesOrEmbeddedScripts",
              "doNotBulkImportOrDeduplicateByFilename", "preserveMastersAndPrivateSharing",
              "noPublicRepoBinaryCopy", "noNewPaidResources", "noAgentQuarantineRelease"):
        check(guards.get(k) is True, "security:" + k)
    encoded = json.dumps(contract).lower()
    for forbidden in ("drive.google.com", "docs.google.com", "http://", "https://",
                      "begin private key", ".gif\"",
                      "private_eve_blenderreference"):
        check(forbidden not in encoded, "privateMetadataLeak:" + forbidden)
    check("metadata" in contract.get("observationScope", "").lower(), "inventoryScope")

    ref = "doctrine/driveStudioReconciliationV1.json"
    check(alignment.get("currentAssetReconciliation", {}).get("contract") == ref, "routingLink")
    check(truth.get("creativeLayer", {}).get("driveStudioReconciliation") == ref, "sourceTruthLink")
    check(kiosk.get("driveStudioAssetReconciliation", {}).get("contract") == ref, "canaryLink")
    check(alignment.get("releaseCrownStatus") == "STOP", "releaseGate")
    check(truth.get("releaseAuthority") is False and truth.get("publicationAuthority") is False,
          "globalReleaseGate")
    check(truth.get("promotion") is False, "globalPromotion")
    check(kiosk.get("driveStudioAssetReconciliation", {}).get("publicMediaApproved") is False,
          "kioskMediaGate")
    check(kiosk.get("driveStudioAssetReconciliation", {}).get("driveMediaImportPerformed") is False,
          "kioskMediaImport")
    check(contract.get("crown", {}).get("publicProductRelease") == "NOT_GRANTED_BY_THIS_SCOPE",
          "crownScope")
    return failures


def main():
    contract = read(CONTRACT)
    align = read("doctrine/driveAssetAlignmentV1.json")
    truth = read("doctrine/currentSourceTruthV3.json")
    kiosk = read("doctrine/chromeCanaryKioskMilestonesV1.json")
    errors = audit(contract, align, truth, kiosk)
    assert not errors, errors
    bad = []
    for label, modifier in (
        ("privateBytes", lambda c: c.update(rawAssetBytesCopied=True)),
        ("wrongHash", lambda c: c["firstVerticalSlice"].update(sha256="A" * 64)),
        ("earlyPreview", lambda c: c["firstVerticalSlice"].update(preview="GREEN")),
        ("publicDerivative", lambda c: c["firstVerticalSlice"].update(publicMediaRelease=True)),
        ("rightsAssumed", lambda c: c["tiers"][0].update(artistCanonApproved=True)),
        ("privateUrlLeak", lambda c: c.update(privateLink="https://drive.google.com/file/d/hidden")),
        ("automaticWorkers", lambda c: c["security"].update(noAgentQuarantineRelease=False)),
    ):
        copy_ = copy.deepcopy(contract)
        modifier(copy_)
        if not audit(copy_, align, truth, kiosk):
            bad.append(label)
    assert not bad, "NEGATIVE_CONTROLS_FAILED:" + ",".join(bad)
    print("GREEN_SCOPED_DRIVE_STUDIO_SOURCE_RECONCILIATION_7_NEGATIVE_CONTROLS")
    print("NOT_PROVEN: actual media SHA-256, file-level rights, decode, import, Android playback or public use")


if __name__ == "__main__":
    main()
