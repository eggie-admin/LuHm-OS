#!/usr/bin/env python3
"""Debug-stage Godot donor triage: read-only, bounded ZIP checks and ranked proposals.

NO network, archive extraction, scripts/plugins execution, writes, public promotion or agent work.
Uses Canon's existing tools.artAssetIntegrity rather than duplicating its ZIP firewall.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from zipfile import BadZipFile
from tools.artAssetIntegrity import inspect_zip, whole_hash

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "game/demo/communityDonorIntakeV1.json"
REQUIRED = {"assetId", "sourceFamily", "sourceUrl", "sourceRevisionOrVersion",
            "license", "licenseUrlOrFile", "sourceHash", "contentLane",
            "publicAllowed", "assetRole", "destinationFamily", "professorReviewState"}
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
EXTERNAL = {"kenney", "quaternius"}
WORLDS = ("cathedral", "neonRiverwalk", "lumCoffeeHouse", "characterBench")


def validate(catalog: dict) -> None:
    if catalog.get("schema") != "luhmOs.demoCommunityDonorIntake.v1":
        raise ValueError("BAD_DONOR_SCHEMA")
    items = catalog.get("candidates", [])
    if not isinstance(items, list) or not (1 <= len(items) <= 24):
        raise ValueError("UNBOUNDED_DONOR_LIST")
    seen = set()
    for item in items:
        if not isinstance(item, dict) or REQUIRED - set(item):
            raise ValueError("MISSING_DONOR_FIELDS")
        ident = item["assetId"]
        if not isinstance(ident, str) or not ident or ident in seen:
            raise ValueError("DUPLICATE_OR_INVALID_ID")
        seen.add(ident)
        if item["publicAllowed"] is not False or item["godotImport"] == "TESTED":
            raise ValueError("FALSE_GAME_READY_PROMOTION")
        if item["sourceFamily"] in EXTERNAL:
            if item["license"] != "CC0_1_0_SOURCE_PAGE_REPORTED":
                raise ValueError("UNVERIFIED_EXTERNAL_LICENSE")
            if item["sourceHash"] is not None or item["downloadVerified"] is not False:
                raise ValueError("UNSUPPORTED_DOWNLOADED_EVIDENCE")
        if item["destinationFamily"] not in WORLDS and item["sourceFamily"] in EXTERNAL:
            raise ValueError("UNKNOWN_SCENE_DESTINATION")
    rules = catalog["escalation"]
    if rules["automaticDownload"] or rules["autoPublish"] or rules["autoDeploy"] or rules["autoMerge"]:
        raise ValueError("UNAUTHORIZED_AUTO_ESCALATION")
    if rules["maxSimultaneousDonorPacks"] > 2 or not rules["noEndlessTaskGeneration"]:
        raise ValueError("UNBOUNDED_DONOR_ESCALATION")


def pick(catalog: dict, scene: str, limit: int = 3) -> list[dict]:
    validate(catalog)
    if scene not in WORLDS or not 1 <= limit <= 3:
        raise ValueError("INVALID_SCENE_OR_LIMIT")
    rows = (r for r in catalog["candidates"] if r["destinationFamily"] == scene)
    return [
        {"assetId": r["assetId"], "priority": r["priority"], "role": r["assetRole"],
         "state": "DISCOVERED_NOT_IMPORTED", "sourceUrl": r["sourceUrl"]}
        for r in sorted(rows, key=lambda r: (r["priority"], r["assetId"]))[:limit]
    ]


def inspect_candidate(catalog: dict, asset_id: str, archive: Path) -> dict:
    validate(catalog)
    rows = [r for r in catalog["candidates"] if r["assetId"] == asset_id]
    if len(rows) != 1:
        raise ValueError("UNKNOWN_DONOR_ASSET")
    record = rows[0]
    if archive.is_symlink() or not archive.is_file() or archive.suffix.lower() != ".zip":
        raise ValueError("UNSUPPORTED_OR_SYMLINK_ARCHIVE")
    size = archive.stat().st_size
    if size <= 0 or size > MAX_ARCHIVE_BYTES:
        raise ValueError("ARCHIVE_SIZE_BOUND")
    try:
        scan = inspect_zip(archive)
    except (BadZipFile, OSError, RuntimeError, ValueError, EOFError) as exc:
        return {"assetId": asset_id, "archiveStatus": "FAIL_QUARANTINE",
                "failure": type(exc).__name__, "publicAllowed": False}
    sha = whole_hash(archive)
    if record["sourceHash"] and record["sourceHash"] != sha:
        return {"assetId": asset_id, "archiveStatus": "HASH_MISMATCH",
                "publicAllowed": False, "observedSha256": sha}
    formats = scan["extensions"]
    three_d = sum(formats.get(ext, 0) for ext in
                  (".glb", ".gltf", ".fbx", ".obj", ".blend"))
    is_safe = scan["integrity"] == "PASS"
    is_code_free = scan["sourceScriptsForReview"] == 0
    return {
        "assetId": asset_id, "archiveStatus": "ZIP_SCAN_PASS" if is_safe else "FAIL_QUARANTINE",
        "observedSha256": sha, "entryCount": scan["entries"],
        "modelFormatEntries": three_d, "extensionCounts": formats,
        "licenseDeclarationInArchive": scan["licenseSignal"],
        "requiresCodeReview": not is_code_free,
        "needsLicenseAndOriginReceipt": True,
        "needsGodotImportTest": True, "needsSceneRuntimeTest": True,
        "extractionPerformed": False, "publicAllowed": False,
        "crownStatus": "STOP"
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--catalog", type=Path, default=DEFAULT)
    p.add_argument("--scene", choices=WORLDS, default="cathedral")
    p.add_argument("--candidate")
    p.add_argument("--archive", type=Path)
    a = p.parse_args()
    catalog = json.loads(a.catalog.read_text(encoding="utf8"))
    validate(catalog)
    if bool(a.candidate) != bool(a.archive):
        p.error("--candidate and --archive must be provided together")
    if a.candidate:
        result = inspect_candidate(catalog, a.candidate, a.archive)
    else:
        result = {
            "schema": "luhmOs.demoDonorSelectionReceipt.v1",
            "scene": a.scene, "candidates": pick(catalog, a.scene),
            "downloadedOrImported": False, "publicAllowed": False,
            "nextProof": "downloadedZipSafetyShaLicenseThenGodotImport",
            "crownStatus": "STOP"
        }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
