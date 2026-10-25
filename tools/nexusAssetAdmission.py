#!/usr/bin/env python3
"""Offline Nexus asset candidate admission for LuHm Old Magic.

This program DOES NOT download, scrape, infer copyright ownership, grant a
license, modify a scene, access an API, or approve publication. It validates
recorded permission fields before a human performs the rights review.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-zA-Z0-9_-]+$")
MOD_ID = re.compile(r"^[0-9]+$")
STAGES = ("referenceOnly", "permittedPrivatePrototype", "distributionCandidate")
PERMISSION_FIELDS = (
    "fileRightsVerified", "modAuthorOwnsOrCanLicenseContent",
    "upstreamGamePublisherRightsCleared", "nexusSiteTermsForThisUseChecked",
    "offPlatformUseAllowed", "modificationAllowed",
)
PUBLIC_FIELDS = ("redistributionAllowed", "commercialUseAllowed")


def valid_nexus_mod(url):
    if not isinstance(url, str):
        return False
    u = urlsplit(url)
    parts = u.path.strip("/").split("/")
    return (
        u.scheme == "https" and u.hostname == "www.nexusmods.com"
        and not u.username and not u.password and not u.port
        and not u.query and not u.fragment and len(parts) == 3
        and bool(SLUG.fullmatch(parts[0]))
        and parts[1] == "mods" and bool(MOD_ID.fullmatch(parts[2]))
    )


def assess(candidate):
    issues = []
    if not isinstance(candidate, dict):
        return ["INVALID_RECORD"]
    if candidate.get("stage") not in STAGES:
        issues.append("INVALID_STAGE")
    for field in ("candidateId", "assetRole", "author", "sourceUrl"):
        if not isinstance(candidate.get(field), str) or not candidate[field].strip():
            issues.append("MISSING_" + field.upper())
    if not valid_nexus_mod(candidate.get("sourceUrl")):
        issues.append("INVALID_NEXUS_MOD_URL")
    if candidate.get("stage") == "referenceOnly":
        # URLs and author names can be kept as study references.
        # No binary archive is authorized by this classification.
        if candidate.get("includesBinary", False):
            issues.append("REFERENCE_HAS_BINARY")
        return issues
    if candidate.get("includesBinary") is not True:
        issues.append("MISSING_BINARY_SCOPE")
    if not isinstance(candidate.get("fileVersion"), str) or not candidate["fileVersion"].strip():
        issues.append("FILE_VERSION_REQUIRED")
    if not HEX_SHA256.fullmatch(str(candidate.get("sourceSha256", ""))):
        issues.append("FILE_SHA256_REQUIRED")
    evidence = candidate.get("rightsEvidence")
    if not isinstance(evidence, dict):
        return issues + ["RIGHTS_EVIDENCE_REQUIRED"]
    for key in PERMISSION_FIELDS:
        if evidence.get(key) is not True:
            issues.append("RIGHTS_" + key)
    if not isinstance(evidence.get("exactFilePermissionSource"), str) or not evidence["exactFilePermissionSource"].startswith("https://"):
        issues.append("EXACT_PERMISSION_SOURCE_REQUIRED")
    if candidate.get("aiProcessingPlanned") is True and evidence.get("aiProcessingAllowed") is not True:
        issues.append("AI_PROCESSING_RIGHTS_REQUIRED")
    if candidate.get("stage") == "distributionCandidate":
        for key in PUBLIC_FIELDS:
            if evidence.get(key) is not True:
                issues.append("RIGHTS_" + key)
        if candidate.get("professorReviewState") != "approvedForCandidate":
            issues.append("PROFESSOR_REVIEW_REQUIRED")
        if candidate.get("contentLane") not in ("betaAfterDark", "cathedralPublic"):
            issues.append("DISTRIBUTION_LANE_REQUIRED")
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    candidate = json.loads(args.manifest.read_text(encoding="utf-8"))
    issues = assess(candidate)
    status = "STRUCTURAL_CANDIDATE_ONLY_REQUIRES_MANUAL_LICENSE_PROOF" if not issues else "BLOCKED"
    print(json.dumps({"status": status, "stage": candidate.get("stage") if isinstance(candidate, dict) else None,
                      "issues": issues, "downloadAttempted": False, "assetImportAttempted": False,
                      "releaseAuthorized": False}, indent=2))
    return 0 if not issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
