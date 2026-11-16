#!/usr/bin/env python3
"""LuHm Machine Forge: offline architecture matrix, typed hex keys and IPS introspection.

Never opens hardware/firmware, downloads BIOS/ROMs, flashes, executes patches,
loads AI models, runs an emulator, or creates virtual machines.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/machineFourArchitectureForgeV1.json"
QUARANTINE = ROOT / "doctrine/companyWideOperationalQuarantineV1.json"
CANON = ROOT / "doctrine/castIdentityHexRegistryV1.json"
TYPED = ROOT / "doctrine/typedFourLaneSqlV1.json"
LANES = ("numericStream", "textStream", "booleanStream", "aiManifestStream")
ARCH = ("x86_64", "aarch64", "riscv64", "ppc64le")
LAYERS = ("isaCpu", "firmwareBoot", "memoryIo", "acceleratorAi")
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
IDENT = re.compile(r"[a-z][A-Za-z0-9]{0,79}\Z")
HEX = re.compile(r"[0-9a-f]+\Z")
SAFE_KINDS = ("usbVendorId", "usbProductId", "pciVendorId", "pciDeviceId",
              "cpuidLeaf", "ipsOffset", "uefiGuid", "sourceRef", "artifactSha256")
MAX_RAM_BYTES = (1 << 63) - 1


def _read(path: Path) -> dict[str, Any]:
    v = json.loads(path.read_text(encoding="utf8"))
    if not isinstance(v, dict):
        raise ValueError("RED_MACHINE_JSON")
    return v


def source_audit() -> dict[str, Any]:
    p = _read(POLICY)
    issues: list[str] = []
    if p.get("schema") != "luhmOs.machineFourArchitectureForge.v1":
        issues.append("RED_MACHINE_SCHEMA")
    if p.get("repo") != "eggie-admin/LuHm-OS":
        issues.append("RED_MACHINE_GITHUB_AUTHORITY")
    arch = p.get("fourArchitectureFamilies", [])
    layers = p.get("fourMachineLayers", [])
    if ([r.get("id") for r in arch] != list(ARCH) or
            [r.get("id") for r in layers] != list(LAYERS)):
        issues.append("RED_MACHINE_4X4_AXES")
    matrix = p.get("matrix4x4", [])
    count = 0
    if not isinstance(matrix, list) or len(matrix) != 4:
        issues.append("RED_MACHINE_4X4_ROWS")
    else:
        for i, row in enumerate(matrix):
            cells = row.get("cells", [])
            if row.get("architecture") != ARCH[i] or len(cells) != 4:
                issues.append("RED_MACHINE_4X4_ROW")
                continue
            for j, cell in enumerate(cells):
                count += 1
                if (cell.get("id") != ARCH[i] + "." + LAYERS[j] or
                        cell.get("layer") != LAYERS[j] or
                        any(cell.get(k) is not False for k in (
                            "hardwareObserved", "flashed", "modelPerformanceMeasured",
                            "licenseCleared"))):
                    issues.append("RED_MACHINE_PROOF_FABRICATED")
    if count != 16:
        issues.append("RED_MACHINE_16_CELLS")
    anchors = p.get("canon", [])
    if (not isinstance(anchors, list) or len(anchors) != 11 or any(
            type(path) is not str or Path(path).is_absolute() or
            ".." in Path(path).parts or not (ROOT / path).is_file() or
            not (ROOT / path).resolve().is_relative_to(ROOT.resolve())
            for path in anchors)):
        issues.append("RED_MACHINE_SOURCE_ANCHORS")
    if (p.get("typedDataLanes") != list(LANES) or
            [r.get("id") for r in _read(TYPED).get("lanes", [])] != list(LANES) or
            _read(CANON).get("typedSqlLanes") != list(LANES)):
        issues.append("RED_MACHINE_TYPED_LANES")
    sort = p.get("sort", {})
    widths = sort.get("fixedHexNormalization", {})
    expected = {"usbVendorId":4, "usbProductId":4, "pciVendorId":4,
                "pciDeviceId":4, "cpuidLeaf":8, "ipsOffset":6, "uefiGuid":32,
                "sourceRef":40, "artifactSha256":64}
    if set(widths) != set(expected) or any(
            widths[k].get("digits") != n or widths[k].get("bits") != n * 4
            for k, n in expected.items()):
        issues.append("RED_MACHINE_HEX_WIDTHS")
    if (sort.get("machineLayerOrdinal") != list(LAYERS) or
            sort.get("architectureOrdinal") != list(ARCH) or
            sort.get("compareOnlySameBusAndWidth") is not True or
            sort.get("untrustedSelfClaimsAlwaysUnverified") is not True or
            sort.get("memorySizesCanonicalDecimalByteIntegers") is not True):
        issues.append("RED_MACHINE_SORT_AUTHORITY")
    if (sort.get("numericProofWeights") != {
            "verifiedCurrentExactSource":16,"licenseAndArtifactProven":8,
            "deviceMatchVerified":4,"runtimeReceiptVerified":2,
            "rollbackVerified":1}):
        issues.append("RED_MACHINE_WEIGHT_DRIFT")
    rules = p.get("firmwareRules", {})
    for name in ("noRomOrOemBiosDownload", "noFirmwareExtractionOrPatching",
                 "noFlash", "noBootloaderUnlock", "noSecureBootBypass",
                 "noMicrocodeMutation", "noImplicitOemUpdates",
                 "sourceAvailabilityNotModificationLicense"):
        if rules.get(name) is not True:
            issues.append("RED_MACHINE_FIRMWARE_BYPASS")
            break
    patch = p.get("patchLane", {})
    if (patch.get("formats") != ["IPS","BPS","PPF"] or
            patch.get("activeImplementation") != "SYNTHETIC_IPS_INSPECT_ONLY"
            or patch.get("maxInputBytes") != 16384 or
            patch.get("maxRecords") != 32 or
            patch.get("offsetWidthBits") != 24 or
            patch.get("noRealPatchApplication") is not True or
            patch.get("noBiosOrProprietaryRomPayload") is not True):
        issues.append("RED_MACHINE_IPS_RIGHTS")
    if not isinstance(p.get("sourceReferences"), list) or len(p["sourceReferences"]) != 14 or any(
            not x.get("url", "").startswith("https://") or
            not x.get("license") or x.get("action") in ("AUTO_FLASH", "AUTO_IMPORT")
            for x in p["sourceReferences"]):
        issues.append("RED_MACHINE_VENDOR_PROVENANCE")
    release = p.get("release", {})
    if (any(release.get(k) is not True for k in (
            "candidateOnly", "existingMainUnmodified", "noAgentActivation",
            "noPaidCompute", "noAutoMerge", "noAutoDeploy", "noPublicROMPatch",
            "noRealHwAttached")) or any(release.get(k) is not False for k in (
            "productionBootProof", "deviceFirmwareRightsProof",
            "realAIInferenceProof", "realHpcProof"))
            or p.get("crownStatus") != "STOP"):
        issues.append("RED_MACHINE_RELEASE_AUTHORITY")
    q = _read(QUARANTINE)
    if q.get("state") != "QUARANTINED" or q.get("activeTaskWorkersAllowed") is not False:
        issues.append("RED_MACHINE_QUARANTINE")
    if ("GNU GENERAL PUBLIC LICENSE" not in (ROOT / "LICENSE").read_text()[:120]
            or p.get("legal", {}).get("rootActual") != "GPL-3.0"):
        issues.append("RED_MACHINE_LICENSE")
    return {
        "schema": "luhmOs.machineFourArchitectureAudit.v1",
        "state": "SOURCE_CANDIDATE_ONLY" if not issues else "RED_SOURCE_DRIFT",
        "issues": sorted(set(issues)), "architectureFamilies": len(arch),
        "machineLayers": len(layers), "matrixCells": count,
        "typedDataLanes": list(LANES), "candidateUpstreams": len(p.get("sourceReferences", [])),
        "hardwareDiscovered": 0, "firmwareFlashes": 0, "ipsPatchesApplied": 0,
        "vendorBinaryDownloaded": False, "aiAcceleratorBenchmarked": False,
        "hpcBuildTested": False, "greenAuthority": False, "crownAuthority": False,
    }


def fixed_hex(kind: str, value: str | int) -> dict[str, Any]:
    """One bus/type with fixed hex width. GUID is semantic 128-bit text, not wire bytes."""
    registry = _read(POLICY)["sort"]["fixedHexNormalization"]
    if type(kind) is not str or kind not in SAFE_KINDS:
        raise ValueError("RED_HEX_UNKNOWN_NAMESPACE")
    digits = registry[kind]["digits"]
    if type(value) is int:
        if value < 0 or value >= (1 << (4 * digits)):
            raise ValueError("RED_HEX_RANGE")
        num = value
    elif type(value) is str:
        if not value or len(value) > digits or HEX.fullmatch(value) is None:
            raise ValueError("RED_HEX_SHAPE_OR_CASE")
        if kind in ("sourceRef", "artifactSha256") and len(value) != digits:
            raise ValueError("RED_HEX_EXACT_DIGEST_WIDTH")
        num = int(value, 16)
    else:
        raise ValueError("RED_HEX_TYPE")
    canonical = f"{num:0{digits}x}"
    return {
        "kind": kind, "valueHex": canonical,
        "sortKey": kind + ":" + canonical, "numericValue": num if digits <= 8 else None,
        "widthBits": digits * 4, "byteOrder": registry[kind]["byteOrder"],
        "trustedHardwareIdentity": False, "permissionGranted": False,
    }


def machine_plan(task_id: str, source_ref: str, scope_id: str,
                 architecture: str, layer: str, ram_bytes: int,
                 bus_kind: str = "usbVendorId", bus_hex: str = "0000") -> dict[str, Any]:
    if any(type(v) is not str or IDENT.fullmatch(v) is None for v in (task_id, scope_id)):
        raise ValueError("RED_MACHINE_TASK_SCOPE")
    if type(source_ref) is not str or SHA40.fullmatch(source_ref) is None:
        raise ValueError("RED_MACHINE_SOURCE_REF")
    if architecture not in ARCH or layer not in LAYERS:
        raise ValueError("RED_MACHINE_ARCH_LAYER")
    if type(ram_bytes) is not int or not 0 <= ram_bytes <= MAX_RAM_BYTES:
        raise ValueError("RED_MACHINE_RAM_BYTES")
    hex_id = fixed_hex(bus_kind, bus_hex)
    if bus_kind not in ("usbVendorId","usbProductId","pciVendorId","pciDeviceId"):
        raise ValueError("RED_MACHINE_BUS_IDENTIFIER")
    s = source_audit()
    if s["issues"]:
        return {"state": "STOP_CANON_DRIFT", "issues": s["issues"]}
    return {
        "schema": "luhmOs.machinePlan.v1",
        "taskId": task_id, "sourceRef": source_ref, "scopeId": scope_id,
        "architecture": architecture, "layer": layer,
        "machineSortOrdinal": ARCH.index(architecture) * 4 + LAYERS.index(layer),
        "ramBytesDecimal": ram_bytes, "deviceId": hex_id,
        "modelProven": False, "memoryMeasured": False,
        "actualFirmwareInspected": False, "runtimeAcceleratorProven": False,
        "state": "HOLD_REAL_BOARD_HARDWARE_AND_RIGHTS_RECEIPT",
        "sourceHeadIndependentlyObserved": False, "physicalDeviceConnected": False,
        "permissionToFlash": False, "licenseApproved": False,
        "publicReleaseApproved": False,
    }


def inspect_synthetic_ips(raw: bytes, *, asset_class: str = "syntheticHomebrew",
                          rights: str = "homebrewOwned") -> dict[str, Any]:
    """Read IPS offsets/counts only; no ROM payload return, file access or patching."""
    if (type(asset_class) is not str or asset_class != "syntheticHomebrew"
            or type(rights) is not str or rights != "homebrewOwned"):
        raise ValueError("RED_IPS_SOURCE_RIGHTS")
    if type(raw) is not bytes or not 8 <= len(raw) <= 16384 or raw[:5] != b"PATCH":
        raise ValueError("RED_IPS_HEADER_OR_BOUNDS")
    pos = 5
    records = []
    while True:
        if pos + 3 > len(raw):
            raise ValueError("RED_IPS_TRUNCATED")
        if raw[pos:pos + 3] == b"EOF":
            pos += 3
            if pos != len(raw):
                raise ValueError("RED_IPS_TRAILING_DATA")
            break
        if len(records) >= 32:
            raise ValueError("RED_IPS_RECORD_COUNT")
        if pos + 5 > len(raw):
            raise ValueError("RED_IPS_RECORD_SHORT")
        offset = int.from_bytes(raw[pos:pos + 3], "big")
        length = int.from_bytes(raw[pos + 3:pos + 5], "big")
        pos += 5
        rle = length == 0
        if rle:
            if pos + 3 > len(raw):
                raise ValueError("RED_IPS_RLE_TRUNCATED")
            size = int.from_bytes(raw[pos:pos + 2], "big")
            pos += 3
        else:
            size = length
            if pos + size > len(raw):
                raise ValueError("RED_IPS_PAYLOAD_TRUNCATED")
            pos += size
        if not 1 <= size <= 4096 or offset + size > 0x1000000:
            raise ValueError("RED_IPS_OFFSET_OR_SIZE")
        for old in records:
            start = int(old["offsetHex"], 16)
            if offset < start + old["size"] and start < offset + size:
                raise ValueError("RED_IPS_OVERLAP")
        records.append({"offsetHex": f"0x{offset:06x}", "size": size, "rle": rle})
    return {
        "state": "SYNTHETIC_PATCH_METADATA_INSPECTED_NOT_APPLIED",
        "format": "IPS", "sourceClass": asset_class,
        "recordCount": len(records), "records": records,
        "patchSha256": hashlib.sha256(raw).hexdigest(),
        "patchBytesReturned": False, "romOpened": False,
        "firmwareImageOpened": False, "patchApplied": False,
        "redistributionAuthorized": False, "greenAuthority": False,
    }


if __name__ == "__main__":
    print(json.dumps(source_audit(), indent=2))
