#!/usr/bin/env python3
"""Fail-closed public-repo check for private Google Drive / GitHub asset routing."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/driveAssetAlignmentV1.json"

def inspect(data: dict, root: Path = ROOT) -> list[str]:
    errors = []
    expect = lambda okay, name: errors.append(name) if not okay else None
    expect(data.get("schema") == "luhmOs.driveAssetAlignment.v1", "schema")
    expect(data.get("authority") == "Professor", "crownOwner")
    expect(data.get("status") == "CANONICAL_ROUTING_POLICY", "routingStatus")
    expect(data.get("repository") == "eggie-admin/LuHm-OS", "sourceRepo")
    for path in data.get("sourceContracts", []):
        p = root / path
        expect(p.is_file() and p.resolve().is_relative_to(root.resolve()), "contractMissing")
    classes = data.get("assetClasses", {})
    for name, target in {
        "sourceCode":"github", "originalMedia":"googleDrive",
        "codeOrDonorArchives":"googleDrive", "visualReferences":"googleDrive",
        "previewCandidate":"googleDrive", "metadataReceipts":"github",
        "runtimeInstalledApk":"androidDevice",
    }.items():
        expect(classes.get(name, {}).get("canonical") == target, "storageClass:" + name)
    for name in ("rebel","yume","pets","hydra"):
        expect(name in data.get("projects", {}), "project:" + name)
    modes = data.get("knownVisibilityClasses", {})
    expect(modes.get("rebelSharedLegacy") == "ANYONE_WRITER_OBSERVED_BLOCK_PRIVATE_INTAKE", "sharedRebelAccess")
    expect(modes.get("legacyPrivateControl") == "ANYONE_READER_OBSERVED_NOT_PRIVATE", "legacyControlAccess")
    expect(modes.get("legacyPublicWrite") == "ANYONE_WRITER_OBSERVED_UNTRUSTED", "untrustedLegacy")
    law = data.get("securityRules", {})
    for name in ("driveItemsNeverExecuteByListing", "untrustedDriveRootNeverCanonical",
                 "existingPermissionRiskMustBeFixedBeforePrivateIntake", "noPrivateIdsInPublicRepo",
                 "noPrivateMastersInPublicGit", "noAutomaticPublication",
                 "noAutonomousAgentResume", "noDefaultNewSpend"):
        expect(law.get(name) is True, "securityLaw:" + name)
    expect(data.get("releaseCrownStatus") == "STOP", "releaseGate")
    expect(data.get("runtimeClaim") == "SOURCE_ROUTING_ONLY", "runtimeClaim")
    expect(len(data.get("rebelFirstUsableCut", [])) >= 5, "rebelWorkflow")
    encoded = json.dumps(data)
    for forbidden in ("drive.google.com", "docs.google.com", "https://", "BEGIN PRIVATE KEY",
                      "1o4GoxrQDKrxzfbbWY8Yja5SrxGEBZhbk", "1AmQfX8Ha95giDEA9ceNeLJ3VLj7w5rS-"):
        expect(forbidden not in encoded, "privateIdentityLeak")
    return errors

def smoke() -> None:
    base=json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert not inspect(base), inspect(base)
    for key, altered in [
        ("publicAuthority", {"releaseCrownStatus":"GO"}),
        ("untrustedSource", {"knownVisibilityClasses":{**base["knownVisibilityClasses"],"rebelSharedLegacy":"TRUSTED"}}),
        ("hostClaim", {"runtimeClaim":"LIVE"}),
        ("leakedId", {"unapprovedDriveLink":"https://drive.google.com/file/d/not-public"}),
    ]:
        copy_ = copy.deepcopy(base)
        copy_.update(altered)
        assert inspect(copy_), "RED_FALSE_GREEN_ACCEPTED:" + key
    print("GREEN_DRIVE_ASSET_ROUTING_SOURCE_4_NEGATIVE_CONTROLS")
    print("NOT_PROVEN: file permissions remediation, codecs, private asset rights, live Codespace, device, public release")

if __name__ == "__main__":
    smoke()
