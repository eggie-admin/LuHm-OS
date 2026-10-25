#!/usr/bin/env python3
"""Offline artist-credit integrity gate for LuHm OS.

Reference catalogs are studies, not proof of asset use, collaboration, endorsement,
Creative Commons grant, or redistribution. This tool never contacts the artist,
downloads media, grants permissions, or publishes a release.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SHA256 = re.compile(r"^[a-f0-9]{64}$")
REQUIRED = (
    "assetId", "assetTitle", "creatorDisplayName", "sourcePlatform",
    "sourceUrl", "sourceRevisionOrVersion", "license", "licenseEvidenceUrl",
    "exactFilePermissionSource", "attributionText", "sourceHash",
    "contentLane", "reviewState",
)
TRUE_TO_PUBLISH = (
    "originalCreatorVerified", "specificFileLicenseAndPermissionsReviewed",
    "actualRuntimeUseVerified", "publicAllowed", "professorArtApproval",
    "redistributionAllowed", "commercialUseAllowed",
)


def safe_link(url):
    if not isinstance(url, str):
        return False
    link = urlsplit(url)
    return (link.scheme == "https" and bool(link.hostname)
            and not link.username and not link.password and not link.port
            and not any(ord(char) < 32 for char in url))


def validate(used, references):
    """Return (errors, public credits); fail closed, including on correction holds."""
    issues, public = [], []
    if used.get("schema") != "luhmOs.artistCreditsApproved.v1":
        issues.append("INVALID_USED_SCHEMA")
    if used.get("sourceType") != "actualRuntimeAssetUsageOnly":
        issues.append("INVALID_USED_SOURCE_TYPE")
    if references.get("scope") != "referenceCatalogOnly":
        issues.append("REFERENCE_SCOPE_MISMATCH")
    cards = references.get("cards", [])
    if not isinstance(cards, list):
        issues.append("REFERENCE_CARDS_INVALID")
        cards = []
    seen_refs = set()
    for index, item in enumerate(cards):
        if not isinstance(item, dict):
            issues.append("REFERENCE_RECORD_INVALID")
            continue
        key = item.get("id")
        if not isinstance(key, str) or not key.strip() or key in seen_refs:
            issues.append("REFERENCE_ID_INVALID_OR_DUPLICATE")
        seen_refs.add(key)
        if item.get("usedInRuntime") is True or item.get("approvedGameCredit") is True:
            issues.append("REFERENCE_CANNOT_CLAIM_GAME_USE")
    assets = used.get("approvedAssets", [])
    if not isinstance(assets, list):
        return issues + ["APPROVED_ASSETS_NOT_ARRAY"], []
    holds = used.get("correctionHoldAssetIds", [])
    if not isinstance(holds, list) or any(not isinstance(x, str) for x in holds):
        issues.append("CORRECTION_HOLDS_INVALID")
        holds = []
    if len(set(holds)) != len(holds):
        issues.append("CORRECTION_HOLDS_DUPLICATE")
    known = set()
    for item in assets:
        if not isinstance(item, dict):
            issues.append("ASSET_RECORD_INVALID")
            continue
        asset_id = item.get("assetId")
        if not isinstance(asset_id, str) or not asset_id.strip() or asset_id in known:
            issues.append("ASSET_ID_INVALID_OR_DUPLICATE")
            continue
        known.add(asset_id)
        errors_for_asset = []
        if asset_id in holds or item.get("creatorCorrectionPending") is True:
            errors_for_asset.append("CREATOR_CORRECTION_HOLD")
        for key in REQUIRED:
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors_for_asset.append("MISSING_" + key)
        for key in TRUE_TO_PUBLISH:
            if item.get(key) is not True:
                errors_for_asset.append("NOT_VERIFIED_" + key)
        if item.get("reviewState") != "approvedArt":
            errors_for_asset.append("NOT_APPROVED_ART")
        if item.get("contentLane") not in ("betaAfterDark", "cathedralPublic"):
            errors_for_asset.append("WRONG_PUBLIC_CONTENT_LANE")
        if not SHA256.fullmatch(str(item.get("sourceHash", ""))):
            errors_for_asset.append("SOURCE_HASH_INVALID")
        for key in ("sourceUrl", "licenseEvidenceUrl", "exactFilePermissionSource"):
            if not safe_link(item.get(key)):
                errors_for_asset.append("UNSAFE_OR_MISSING_" + key)
        if item.get("license", "").strip().lower() in ("", "unknown", "free", "cc", "creative commons"):
            errors_for_asset.append("LICENSE_NOT_SPECIFIC")
        if item.get("derivativeCreated") is True and item.get("modificationAllowed") is not True:
            errors_for_asset.append("DERIVATIVE_PERMISSION_MISSING")
        if item.get("creatorAskedToRemoveAttribution") is True:
            errors_for_asset.append("CREDIT_REMOVAL_REQUEST_NEEDS_REVIEW")
        if errors_for_asset:
            issues.extend(asset_id + ":" + error for error in errors_for_asset)
            continue
        public.append({
            "assetId": asset_id,
            "assetTitle": item["assetTitle"],
            "creatorDisplayName": item["creatorDisplayName"],
            "sourcePlatform": item["sourcePlatform"],
            "sourceUrl": item["sourceUrl"],
            "license": item["license"],
            "licenseEvidenceUrl": item["licenseEvidenceUrl"],
            "attributionText": item["attributionText"],
            "role": "verifiedUsedAsset",
            "endorsedByCreator": False,
        })
    if any(key not in known for key in holds):
        issues.append("CORRECTION_HOLD_UNKNOWN_ASSET")
    # Do not emit a partial public index when one purportedly approved asset fails.
    if issues:
        return issues, []
    return [], sorted(public, key=lambda x: x["assetId"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--used", type=Path, default=ROOT / "media/artistCreditsApprovedV1.json")
    parser.add_argument("--references", type=Path, default=ROOT / "media/yumeReferenceGalleryV1.json")
    args = parser.parse_args()
    issues, credits = validate(
        json.loads(args.used.read_text(encoding="utf-8")),
        json.loads(args.references.read_text(encoding="utf-8")),
    )
    print(json.dumps({
        "schema": "luhmOs.artistCreditIntegrity.v1",
        "status": "SOURCE_GATE_CLEAR" if not issues else "BLOCKED",
        "verifiedPublicUsedAssetCredits": len(credits),
        "credits": credits,
        "issues": issues,
        "referenceMaterialPromoted": False,
        "creatorEndorsementInferred": False,
        "rightsGrantedByAudit": False,
        "publicationAuthorized": False,
        "externalApiRequests": 0,
    }, indent=2, ensure_ascii=False))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
