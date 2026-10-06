#!/usr/bin/env python3
"""Create a deterministic Yume -> Godot asset preparation plan.

This tool is intentionally read-only. It validates one candidate manifest and
prints the exact checks/targets required before an asset may be called
Godot-ready. It does not copy assets, import into Godot, mutate source, or
promote canon.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", help="candidate asset JSON manifest")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = (ROOT / manifest_path).resolve()
    manifest = load_json(manifest_path)
    toolbox = load_json(ROOT / "doctrine/yumeGodotArtToolboxV1.json")
    lane = load_json(ROOT / "doctrine/contentLaneDoctrineV1.json")

    required = [
        "assetId", "characterId", "assetType", "contentLane", "sourcePath",
        "sourceSha256", "provenance", "canonStatus", "publicAllowed"
    ]
    missing = [k for k in required if k not in manifest]
    errors = []
    if missing:
        errors.append("missing:" + ",".join(missing))

    lane_id = manifest.get("contentLane")
    if lane_id not in lane.get("lanes", {}):
        errors.append("unknownContentLane")

    source = None
    if manifest.get("sourcePath"):
        source = (ROOT / manifest["sourcePath"]).resolve()
        try:
            source.relative_to(ROOT)
        except ValueError:
            errors.append("sourceOutsideRepository")
        if not source.is_file():
            errors.append("sourceMissing")
        elif manifest.get("sourceSha256") != sha256(source):
            errors.append("sourceHashMismatch")

    if manifest.get("publicAllowed") and lane_id != "cathedralPublic":
        errors.append("publicAllowedRequiresCathedralPublic")
    if lane_id == "cathedralPublic" and manifest.get("publicAllowed") is not True:
        errors.append("cathedralPublicRequiresPublicAllowed")

    profile = manifest.get("godotProfile")
    profiles = toolbox.get("profiles", {})
    if profile not in profiles:
        errors.append("unknownGodotProfile")

    maturity = manifest.get("maturity", "UNKNOWN")
    if maturity == "UNKNOWN":
        errors.append("unknownMaturity")
    if manifest.get("sexualizedPresentation") is True and manifest.get("adultRosterRequired") is not True:
        errors.append("adultLockMissing")

    result = {
        "schema": "luhmOs.yumeGodotAssetPrepReceipt.v1",
        "status": "RED" if errors else "GREEN_PLAN_ONLY",
        "assetId": manifest.get("assetId"),
        "contentLane": lane_id,
        "godotProfile": profile,
        "sourcePath": manifest.get("sourcePath"),
        "sourceSha256": manifest.get("sourceSha256"),
        "errors": errors,
        "nextChecks": toolbox.get("modelingAndImportChecks", []),
        "truth": [
            "planIsNotGodotImportProof",
            "godotImportIsNotRuntimeProof",
            "runtimeSmokeIsNotPhysicalDeviceProof",
            "ProfessorRetainsCrown"
        ]
    }
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if errors else 0)

if __name__ == "__main__":
    main()
