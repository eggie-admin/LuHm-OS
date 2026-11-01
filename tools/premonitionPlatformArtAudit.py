#!/usr/bin/env python3
"""LuHm Premonition cross-platform art boundary audit, offline and read-only.

Inspects platform Canon and stages tiny synthetic asset *metadata* in an
in-memory SQLite STRICT database. It does not open real private assets, import
a rig, build an Android/iOS kernel, sign binaries or deploy a worker.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import sqlite3
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/premonitionCrossPlatformArtSplitV1.json"
LEDGER = ROOT / "host/api/premonitionAssetLedgerV1.sql"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
IDENT = re.compile(r"[a-z][A-Za-z0-9]{0,79}\Z")
POINTER = re.compile(r"[a-z][A-Za-z0-9._:/-]{0,159}\Z")
DOMAIN_ORDER = ("kernelDevice", "vectorBrand", "threeD", "dataProcessing")
PLATFORMS = ("universalAndroid", "samsungGalaxy", "appleIos", "linuxVm")
EXTENSIONS = {
    "svg": "vectorBrand",
    "blend": "threeD", "glb": "threeD", "gltf": "threeD",
    "png": "dataProcessing", "webp": "dataProcessing",
    "mp4": "dataProcessing", "wav": "dataProcessing",
}
ALLOWED_SVG = frozenset({
    "svg", "g", "path", "rect", "circle", "ellipse", "line",
    "polygon", "polyline", "defs", "linearGradient", "radialGradient",
    "stop", "clipPath", "title", "desc"
})
MAX_INSPECT_BYTES = 16 * 1024 * 1024


def _load(path: Path) -> dict[str, Any]:
    v = json.loads(path.read_text(encoding="utf8"))
    if not isinstance(v, dict):
        raise ValueError("RED_JSON_SHAPE")
    return v


def _safe_root_path(path: Any) -> bool:
    if not isinstance(path, str) or path.startswith("/") or ".." in Path(path).parts:
        return False
    # No symlinks escaping the source tree.
    resolved = (ROOT / path).resolve()
    return resolved.is_file() and resolved.is_relative_to(ROOT.resolve())


def audit_source() -> dict[str, Any]:
    policy = _load(POLICY)
    issues: list[str] = []
    if policy.get("schema") != "luhmOs.premonitionCrossPlatformArtSplit.v1":
        issues.append("RED_POLICY_SCHEMA")
    if [p.get("id") for p in policy.get("platforms", [])] != list(PLATFORMS):
        issues.append("RED_PLATFORM_ORDER")
    if [d.get("id") for d in policy.get("domains", [])] != list(DOMAIN_ORDER):
        issues.append("RED_DOMAIN_ORDER")
    matrix = policy.get("matrix", [])
    ids = []
    if not isinstance(matrix, list) or len(matrix) != 4:
        issues.append("RED_4X4_ROWS")
    else:
        for i, row in enumerate(matrix):
            if row.get("platform") != PLATFORMS[i]:
                issues.append("RED_4X4_PLATFORM")
            cells = row.get("cells", [])
            if len(cells) != 4:
                issues.append("RED_4X4_COLUMNS")
                continue
            for j, cell in enumerate(cells):
                ids.append(cell.get("id"))
                if (cell.get("id") != PLATFORMS[i] + DOMAIN_ORDER[j] or
                        cell.get("domain") != DOMAIN_ORDER[j] or
                        cell.get("physicalDeviceTest") is not False or
                        cell.get("vendorKernelMutationAllowed") is not False or
                        cell.get("publicMediaPublicationAllowed") is not False):
                    issues.append("RED_4X4_AUTHORITY")
    if len(ids) != 16 or len(set(ids)) != 16:
        issues.append("RED_4X4_UNIQUE")
    anchors = policy.get("sourceAnchors", [])
    if not isinstance(anchors, list) or len(anchors) < 18 or not all(
            _safe_root_path(p) for p in anchors):
        issues.append("RED_CANON_ANCHORS")
    brand = _load(ROOT / "doctrine/organizationBrandRegistryV1.json")
    current = policy.get("product", {})
    if (current.get("name") != "LuHm-OS" or
            current.get("development") != "Project Premonition" or
            current.get("previousDevelopment") != "Project Hydra" or
            brand["publicBrands"]["luhmOs"].get("currentProject") != "Project Premonition" or
            brand["publicBrands"]["luhmOs"].get("displayName") != "LuHm-OS" or
            current.get("noVendorCoBrand") is not True):
        issues.append("RED_PRODUCT_BRAND")
    if policy.get("assetRouting", {}).get("binaryNeverStoredInSql") is not True:
        issues.append("RED_SQL_BINARY_BOUNDARY")
    types = policy.get("assetRouting", {}).get("sourceAssetTypes", {})
    for ext, klass in EXTENSIONS.items():
        if not isinstance(types.get(ext), dict) or klass not in DOMAIN_ORDER:
            issues.append("RED_ASSET_TYPE_MAP")
    if (policy.get("license", {}).get("rootLicense") != "GPL-3.0" or
            policy["license"].get("noAutoRelicense") is not True or
            "GNU GENERAL PUBLIC LICENSE" not in
            (ROOT / "LICENSE").read_text(encoding="utf8")[:140]):
        issues.append("RED_LICENSE_BOUNDARY")
    if policy.get("security", {}).get("mustNotFlashKernel") is not True:
        issues.append("RED_KERNEL_FLASH")
    if any(policy.get("security", {}).get(k) is not True for k in (
            "mustNotInstallIosKernel", "mustNotEmbedPrivateMediaInPublicBuild",
            "companyQuarantinePreserved", "noAutoMerge", "noSigning",
            "noPublication")):
        issues.append("RED_PLATFORM_AUTHORITY")
    q = _load(ROOT / "doctrine/companyWideOperationalQuarantineV1.json")
    if q.get("state") != "QUARANTINED" or q.get("activeTaskWorkersAllowed") is not False:
        issues.append("RED_QUARANTINE_DRIFT")
    godot = (ROOT / "project.godot").read_text(encoding="utf8")
    export = (ROOT / "export_presets.cfg").read_text(encoding="utf8")
    if ("gl_compatibility" not in godot or "target_sdk=\"36\"" not in export
            or "architectures/arm64-v8a=true" not in export):
        issues.append("RED_ACTUAL_ANDROID_SOURCE")
    if "skins: 0" not in (ROOT / "assets/lum/README.md").read_text(encoding="utf8"):
        issues.append("RED_STATIC_AVATAR_PROOF")
    pkg = _load(ROOT / "frontEnd/prototypes/glassWorld/package.json")
    if pkg.get("private") is not True or not pkg.get("dependencies", {}).get("@babylonjs/core"):
        issues.append("RED_ACTUAL_WEB_RUNTIME")
    tables: list[str] = []
    try:
        with sqlite3.connect(":memory:") as conn:
            conn.executescript(LEDGER.read_text(encoding="utf8"))
            rows = conn.execute(
                "SELECT name,sql FROM sqlite_master WHERE type='table'"
            ).fetchall()
            tables = sorted(name for name, _ in rows if name.startswith("premonition"))
            if len(tables) != 2 or any(
                    not definition.strip().endswith("STRICT")
                    for name, definition in rows if name in tables):
                issues.append("RED_SQLITE_STRICT_ASSET_LEDGER")
    except sqlite3.DatabaseError:
        issues.append("RED_SQLITE_DDL")
    return {
        "schema": "luhmOs.premonitionCrossPlatformAudit.v1",
        "status": "SOURCE_CONSISTENT_ONLY" if not issues else "RED_SOURCE_DRIFT",
        "issues": sorted(set(issues)), "candidateMatrixCells": len(ids),
        "sqliteMetadataTables": tables,
        "actualDeviceTests": 0, "kernelImagesBuilt": 0, "iosBuildSigned": False,
        "privateArtImported": False, "binaryStoredInSql": False,
        "networkCalls": 0, "paidCalls": 0,
        "greenAuthority": False, "crownAuthority": False,
    }


def _safe_svg(raw: bytes) -> bool:
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper() or b"<?" in raw:
        return False
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return False
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        return False
    for node in root.iter():
        if node.tag.split("}")[-1] not in ALLOWED_SVG:
            return False
        for k, v in node.attrib.items():
            name = k.split("}")[-1].lower()
            if (name.startswith("on") or name in ("href", "src", "style")
                    or "url(" in v.lower() or "javascript:" in v.lower()):
                return False
    return True


def classify_content(raw: bytes, kind: str) -> bool:
    """Very small header/sanitization gate, not a file parser or render proof."""
    if not isinstance(raw, bytes) or len(raw) > MAX_INSPECT_BYTES:
        return False
    if kind == "svg":
        return _safe_svg(raw)
    if kind == "blend":
        return raw.startswith(b"BLENDER")
    if kind == "glb":
        if len(raw) < 20 or raw[:4] != b"glTF":
            return False
        version, total, first_len, chunk = struct.unpack_from("<III4s", raw, 4)
        if version != 2 or total != len(raw) or chunk != b"JSON":
            return False
        if first_len < 2 or first_len > 2 * 1024 * 1024 or first_len + 20 > total:
            return False
        try:
            obj = json.loads(raw[20:20 + first_len].decode("utf8").rstrip(" \t\r\n"))
        except (ValueError, UnicodeError):
            return False
        return obj.get("asset", {}).get("version") == "2.0"
    if kind == "gltf":
        try:
            obj = json.loads(raw)
        except (UnicodeError, ValueError):
            return False
        if not isinstance(obj, dict) or obj.get("asset", {}).get("version") != "2.0":
            return False
        # External buffers / images need separate sandboxed URI validation.
        return not any(
            isinstance(item, dict) and "uri" in item
            for key in ("buffers", "images") for item in obj.get(key, [])
        )
    if kind == "png":
        return raw.startswith(b"\x89PNG\r\n\x1a\n")
    if kind == "webp":
        return len(raw) >= 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WEBP"
    if kind == "wav":
        return len(raw) >= 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WAVE"
    if kind == "mp4":
        return len(raw) >= 12 and raw[4:8] == b"ftyp"
    return False


def plan_asset(*, asset_id: str, task_id: str, source_ref: str,
               scope_id: str, kind: str, pointer: str,
               payload: bytes, rights_state: str = "PRIVATE_REVIEW") -> dict[str, Any]:
    """Metadata-only proposal; never persists raw art."""
    for ident in (asset_id, task_id, scope_id):
        if type(ident) is not str or IDENT.fullmatch(ident) is None:
            raise ValueError("invalid bounded asset/task/scope identifier")
    if type(source_ref) is not str or SHA40.fullmatch(source_ref) is None:
        raise ValueError("invalid exact GitHub source SHA")
    if kind not in EXTENSIONS:
        raise ValueError("unknown art format")
    if type(pointer) is not str or POINTER.fullmatch(pointer) is None:
        raise ValueError("invalid private logical pointer")
    if rights_state != "PRIVATE_REVIEW":
        raise ValueError("public asset rights cannot be self-approved by planner")
    if not classify_content(payload, kind):
        raise ValueError("asset content header or private SVG policy rejected")
    return {
        "assetId": asset_id, "taskId": task_id, "sourceRef": source_ref,
        "scopeId": scope_id, "assetClass": EXTENSIONS[kind], "format": kind,
        "sha256Hex": hashlib.sha256(payload).hexdigest(),
        "byteCount": len(payload), "logicalPrivatePointer": pointer,
        "rightsState": rights_state, "provenanceState": "UNKNOWN",
        "publicReleaseAuthorized": 0,
        "status": "SOURCE_BYTES_LOCAL_INSPECTED_METADATA_ONLY",
        "actualTargetDeviceVerified": False,
        "binaryBytesReturned": False, "greenAuthority": False,
    }


def receipt_in_memory(proposal: Mapping[str, Any]) -> dict[str, Any]:
    """Test-only SQLite transaction, not a deployment or asset store."""
    if not isinstance(proposal, Mapping) or proposal.get("status") != (
            "SOURCE_BYTES_LOCAL_INSPECTED_METADATA_ONLY"):
        raise ValueError("only validated source proposal accepted")
    fields = ("assetId", "taskId", "sourceRef", "scopeId", "assetClass",
              "format", "sha256Hex", "byteCount", "logicalPrivatePointer",
              "rightsState", "provenanceState", "publicReleaseAuthorized")
    with sqlite3.connect(":memory:") as db:
        db.executescript(LEDGER.read_text(encoding="utf8"))
        values = tuple(proposal[k] for k in fields)
        db.execute(
            "INSERT INTO premonitionAssetRecord (" + ",".join(fields) +
            ") VALUES (" + ",".join("?" for _ in fields) + ")",
            values)
        result = db.execute(
            "SELECT assetId,sha256Hex,assetClass,byteCount,rightsState "
            "FROM premonitionAssetRecord WHERE assetId=?",
            (proposal["assetId"],)).fetchone()
    return {
        "state": "OFFLINE_SQLITE_METADATA_INSERT_VERIFIED",
        "assetId": result[0], "sha256Hex": result[1],
        "assetClass": result[2], "byteCount": result[3],
        "rightsState": result[4], "rawAssetPersisted": False,
        "durableDatabaseCreated": False, "publicationAllowed": False,
        "greenAuthority": False, "crownAuthority": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit_source(), indent=2))
