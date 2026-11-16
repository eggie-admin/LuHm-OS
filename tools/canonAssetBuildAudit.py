#!/usr/bin/env python3
"""Validate every public Godot 3D asset against explicit canon, provenance, and SHA-256."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHARACTERS = ("lum", "urd", "belldandy", "skuld")
WORLDS = ("neonRiverwalk", "lumCoffeeHouse", "cathedral")
APPROVED = ("originalApproved", "redistributionApproved")
SHA256 = re.compile(r"[a-f0-9]{64}\Z")
SAFE_ID = re.compile(r"[A-Za-z][A-Za-z0-9]{0,63}\Z")
ALLOWED_STATUSES = {"concept", "candidateReview", "approvedArt", "runtimeImportProven", "parked", "rejected"}
MAX_ASSET_BYTES = 40 * 1024 * 1024
MAX_TOTAL_BYTES = 120 * 1024 * 1024


def validate(root: Path = ROOT) -> dict:
    root = root.resolve()
    manifest = json.loads((root / "game/assets/canonRuntimeAssetsV1.json").read_text("utf-8"))
    canon = json.loads((root / "game/canon/CHARACTER_CANON_V1.json").read_text("utf-8"))
    if manifest.get("schema") != "luhmOs.canonRuntime3dAssetRegistry.v1":
        raise ValueError("INVALID_REGISTRY_SCHEMA")
    if set(manifest.get("characters", {})) != set(CHARACTERS) or set(canon.get("characters", {})) != set(CHARACTERS):
        raise ValueError("CHARACTER_CANON_DRIFT")
    if set(manifest.get("worlds", {})) != set(WORLDS):
        raise ValueError("WORLD_CANON_DRIFT")
    if manifest.get("approvedAssetRoot") != "res://assets/approved3d/":
        raise ValueError("ASSET_ROOT_DRIFT")
    if manifest.get("crownStatus") != "STOP":
        raise ValueError("ASSET_CROWN_GATE_DRIFT")

    asset_root = root / "assets" / "approved3d"
    claimed = set()
    count, total = 0, 0

    def check(entry: dict, asset_id: str) -> None:
        nonlocal count, total
        if not isinstance(entry, dict) or not SAFE_ID.fullmatch(asset_id):
            raise ValueError("INVALID_ASSET_ENTRY")
        status = entry.get("status")
        if status not in ALLOWED_STATUSES:
            raise ValueError("INVALID_ASSET_STATUS")
        path = entry.get("path", "")
        sha = entry.get("sha256", "")
        ready = status == "runtimeImportProven"
        if not ready:
            if path or sha or entry.get("publicAllowed") is not False or entry.get("importProven") is not False:
                raise ValueError("UNAPPROVED_ASSET_MUST_NOT_BE_EXPORTED")
            return
        if entry.get("publicAllowed") is not True or entry.get("importProven") is not True:
            raise ValueError("MISSING_PUBLIC_IMPORT_APPROVAL")
        if entry.get("approvedBy") != "Professor" or entry.get("license") not in APPROVED:
            raise ValueError("MISSING_RIGHTS_OR_HUMAN_APPROVAL")
        if not isinstance(path, str) or not path.startswith("res://assets/approved3d/"):
            raise ValueError("UNSAFE_PUBLIC_RESOURCE_PATH")
        relative = path.removeprefix("res://")
        if "\\" in relative or "//" in relative or "?" in relative or "#" in relative:
            raise ValueError("UNSAFE_RESOURCE_ENCODING")
        resource = (root / relative).resolve()
        if not resource.is_relative_to(asset_root.resolve()) or resource.suffix.lower() not in {".glb", ".tscn"}:
            raise ValueError("RESOURCE_TRAVERSAL_OR_FORMAT")
        if not resource.is_file() or resource.is_symlink():
            raise ValueError("APPROVED_ASSET_MISSING")
        if not isinstance(sha, str) or not SHA256.fullmatch(sha):
            raise ValueError("BAD_ASSET_SHA")
        size = resource.stat().st_size
        if size == 0 or size > MAX_ASSET_BYTES:
            raise ValueError("WEB_MODEL_SIZE_EXCEEDED")
        count += 1
        total += size
        if total > MAX_TOTAL_BYTES:
            raise ValueError("WEB_ASSET_BUDGET_EXCEEDED")
        digest = hashlib.file_digest(resource.open("rb"), "sha256").hexdigest()
        if digest != sha:
            raise ValueError("ASSET_SHA_MISMATCH")
        if resource in claimed:
            raise ValueError("DUPLICATE_ASSET_REFERENCE")
        claimed.add(resource)

    for character_id, entry in manifest["characters"].items():
        check(entry, character_id)
    for world_id, entries in manifest["worlds"].items():
        if not isinstance(entries, list) or len(entries) > 24:
            raise ValueError("WORLD_ASSET_COUNT_INVALID")
        seen = set()
        for entry in entries:
            asset_id = entry.get("id", "") if isinstance(entry, dict) else ""
            if asset_id in seen:
                raise ValueError("DUPLICATE_WORLD_ASSET_ID")
            seen.add(asset_id)
            check(entry, asset_id)

    if asset_root.exists():
        for resource in asset_root.rglob("*"):
            if resource.is_symlink():
                raise ValueError("APPROVED_ASSET_SYMLINK")
            if resource.is_file() and resource.suffix.lower() in {".glb", ".tscn"} and resource.resolve() not in claimed:
                raise ValueError("UNREGISTERED_PUBLIC_3D_BINARY")
    # Godot's default resource export may include unlisted models anywhere in the repo.
    # Do not trust a registry that only scans the designated approved folder.
    forbidden_formats = {".glb", ".gltf", ".fbx", ".obj", ".dae", ".blend"}
    for resource in root.rglob("*"):
        if ".git" in resource.parts or ".godot" in resource.parts:
            continue
        if resource.is_file() and resource.suffix.lower() in forbidden_formats:
            if resource.resolve() not in claimed:
                raise ValueError("UNREGISTERED_3D_SOURCE_IN_PUBLIC_BUILD")
    for forbidden in ("assets/lum/luhm.glb", "assets/lum/luhmRunning.glb"):
        if (root / forbidden).exists():
            raise ValueError("PRIVATE_LUM_DONOR_IN_PUBLIC_SOURCE")

    return {"schema": "luhmOs.canon3dAssetBuildReceipt.v1",
            "state": "GREEN_REGISTRY_GATE", "approvedModels": count,
            "bytesApproved": total, "binaryArtworkPromoted": False,
            "scope": "SOURCE_AND_PUBLIC_BINARY_ELIGIBILITY_ONLY"}


if __name__ == "__main__":
    try:
        print(json.dumps(validate(), indent=2))
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("RED_CANON_3D_ASSET_GATE: " + str(exc), file=sys.stderr)
        sys.exit(1)
