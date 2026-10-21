#!/usr/bin/env python3
"""Read-only, fail-closed Yume -> Godot candidate inspector.

Never opens a source outside the canonical asset root, even if it is referenced
through ../ or a symlink. A GREEN_PLAN_ONLY receipt is not import, runtime,
device, asset-license, AI-execution or publication proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA256 = re.compile(r"^[0-9a-f]{64}$")
IDENTITY = re.compile(r"^[a-z][A-Za-z0-9]{0,79}$")
MAX_GLB_JSON_BYTES = 2 * 1024 * 1024


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def format_error(path: Path, ext: str) -> bool:
    """Small bounded signature/header check, never a full Godot import test."""
    try:
        with path.open("rb") as stream:
            header = stream.read(20)
            if ext == "png":
                return not header.startswith(b"\x89PNG\r\n\x1a\n")
            if ext == "webp":
                return not (header.startswith(b"RIFF") and header[8:12] == b"WEBP")
            if ext == "glb":
                if len(header) < 20 or header[:4] != b"glTF":
                    return True
                version, declared = struct.unpack_from("<II", header, 4)
                first_size, first_kind = struct.unpack_from("<I4s", header, 12)
                if version != 2 or declared != path.stat().st_size or first_kind != b"JSON":
                    return True
                if first_size < 2 or first_size > MAX_GLB_JSON_BYTES or 20 + first_size > declared:
                    return True
                chunk = stream.read(first_size)
                if len(chunk) != first_size:
                    return True
                doc = json.loads(chunk.decode("utf-8").rstrip(" \\t\\r\\n"))
                return not isinstance(doc, dict) or doc.get("asset", {}).get("version") != "2.0"
    except (OSError, UnicodeError, ValueError, TypeError, struct.error, AttributeError):
        return True
    return False


def evaluate_candidate(manifest, root: Path, toolbox: dict, lanes: dict) -> dict:
    """Inspect a manifest and local source with no writes or provider access."""
    if not isinstance(manifest, dict):
        return {"schema": "luhmOs.yumeGodotAssetPrepReceipt.v1", "status": "RED",
                "errors": ["manifestNotObject"], "publicationAuthority": False}

    errors = []
    required = ("assetId", "characterId", "assetType", "contentLane", "sourcePath",
                "sourceSha256", "provenance", "canonStatus", "publicAllowed")
    for key in required:
        if key not in manifest:
            errors.append("missing:" + key)

    for name in ("assetId", "characterId"):
        if not isinstance(manifest.get(name), str) or not IDENTITY.fullmatch(manifest[name]):
            errors.append("invalidIdentity:" + name)

    lane_id = manifest.get("contentLane")
    if not isinstance(lane_id, str) or lane_id not in lanes.get("lanes", {}):
        errors.append("unknownContentLane")
    if not isinstance(manifest.get("assetType"), str) or not manifest["assetType"].strip():
        errors.append("invalidAssetType")

    public_allowed = manifest.get("publicAllowed")
    if type(public_allowed) is not bool:
        errors.append("publicAllowedMustBeBoolean")
    if public_allowed is True and lane_id != "cathedralPublic":
        errors.append("publicAllowedRequiresCathedralPublic")
    if lane_id == "cathedralPublic" and public_allowed is not True:
        errors.append("cathedralPublicRequiresPublicAllowed")

    provenance = manifest.get("provenance")
    if (not isinstance(provenance, (str, dict)) or not provenance
            or isinstance(provenance, str) and provenance.strip().lower() in
            ("", "unknown", "pending", "todo", "tbd")):
        errors.append("provenanceMissingOrUnknown")

    if not isinstance(manifest.get("canonStatus"), str) or not manifest["canonStatus"].strip():
        errors.append("canonStatusMissing")
    maturity = manifest.get("maturity")
    if not isinstance(maturity, str) or maturity.strip().lower() in ("", "unknown", "pending"):
        errors.append("unknownMaturity")
    if manifest.get("sexualizedPresentation") is True:
        if manifest.get("adultRosterRequired") is not True:
            errors.append("adultLockMissing")
        if lane_id == "cathedralPublic":
            errors.append("sexualizedAssetForbiddenPublic")

    profile = manifest.get("godotProfile")
    profiles = toolbox.get("profiles", {})
    if not isinstance(profile, str) or profile not in profiles:
        errors.append("unknownGodotProfile")
        profile_details = {}
    else:
        profile_details = profiles[profile]
        for key in profile_details.get("requires", []):
            if not isinstance(manifest.get(key), str) or not manifest[key].strip():
                errors.append("requiredPolicyMissing:" + key)
        if profile_details.get("requiresFrameMetadata") is True:
            if not isinstance(manifest.get("frameMetadata"), dict) or not manifest["frameMetadata"]:
                errors.append("spriteFrameMetadataMissing")
        if profile_details.get("requiresAlphaDecision") is True:
            if type(manifest.get("alphaRequired")) is not bool:
                errors.append("alphaDecisionMissing")

    if public_allowed is True:
        if manifest.get("generatedWithAi") is True:
            errors.append("publicGeneratedAiArtDefaultDenied")
        if manifest.get("protectedReferenceRefs"):
            errors.append("publicProtectedReferenceForbidden")
        if not isinstance(manifest.get("licenseEvidence"), str) or not manifest["licenseEvidence"].strip():
            errors.append("publicLicenseEvidenceMissing")
        if not isinstance(manifest.get("creatorCredit"), str) or not manifest["creatorCredit"].strip():
            errors.append("publicCreatorCreditMissing")
        approval = manifest.get("professorApproval")
        if not isinstance(approval, dict) or approval.get("approved") is not True or not approval.get("receipt"):
            errors.append("publicProfessorApprovalMissing")

    supplied_digest = manifest.get("sourceSha256")
    if not isinstance(supplied_digest, str) or not SHA256.fullmatch(supplied_digest):
        errors.append("invalidSourceHash")
    root = root.resolve()
    source_path = manifest.get("sourcePath")
    candidate = None
    if (not isinstance(source_path, str) or not source_path.strip()
            or "\\" in source_path or "\x00" in source_path
            or Path(source_path).is_absolute()):
        errors.append("invalidSourcePath")
    else:
        candidate = (root / source_path).resolve()
        if not candidate.is_relative_to(root):
            errors.append("sourceOutsideRepository")
            candidate = None

    if candidate is not None:
        if not candidate.is_file():
            errors.append("sourceMissing")
        else:
            suffix = candidate.suffix.lower().removeprefix(".")
            if profile_details and suffix not in profile_details.get("formats", []):
                errors.append("profileFormatMismatch")
            if suffix in ("png", "webp", "glb") and format_error(candidate, suffix):
                errors.append("sourceFormatInvalid")
            if isinstance(supplied_digest, str) and SHA256.fullmatch(supplied_digest):
                if sha256(candidate) != supplied_digest:
                    errors.append("sourceHashMismatch")

    return {
        "schema": "luhmOs.yumeGodotAssetPrepReceipt.v1",
        "status": "RED" if errors else "GREEN_PLAN_ONLY",
        "assetId": manifest.get("assetId"),
        "contentLane": lane_id,
        "godotProfile": profile,
        "sourcePath": source_path,
        "sourceSha256": supplied_digest,
        "errors": errors,
        "nextChecks": toolbox.get("modelingAndImportChecks", []),
        "publicationAuthority": False,
        "authority": "Professor",
        "truth": ["planIsNotGodotImportProof", "godotImportIsNotRuntimeProof",
                  "runtimeSmokeIsNotPhysicalDeviceProof", "ProfessorRetainsCrown"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", help="candidate asset JSON manifest")
    args = ap.parse_args()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path
    manifest = load_json(manifest_path)
    toolbox = load_json(ROOT / "doctrine/yumeGodotArtToolboxV1.json")
    lanes = load_json(ROOT / "doctrine/contentLaneDoctrineV1.json")
    result = evaluate_candidate(manifest, ROOT, toolbox, lanes)
    print(json.dumps(result, indent=2))
    return 1 if result["status"] == "RED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
