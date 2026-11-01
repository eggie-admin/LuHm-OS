#!/usr/bin/env python3
"""LuHm staged hostile-input 4x4 source audit for device and mod research.

No host environment reads, USB/Bluetooth scans, display/DB calls, mod downloads,
ROM processing, shell, subprocess, provider execution, drivers or permission
changes. Candidate claims NEVER grant third-party rights or runtime authority.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/hostileModForge4x4V1.json"
TRUTH = ROOT / "doctrine/currentSourceTruthV3.json"
QUARANTINE = ROOT / "doctrine/companyWideOperationalQuarantineV1.json"
BRAND = ROOT / "doctrine/organizationBrandRegistryV1.json"

LANES = ("hostDisplay", "deviceDebug", "studioMods", "rightsSource")
PHASES = ("R1", "R2", "R3", "R4")
HEX4 = re.compile(r"[0-9a-f]{4}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX_OFFSET = re.compile(r"0x[0-9a-f]{1,8}\Z")
UUID128 = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z")
IDENT = re.compile(r"[a-z][A-Za-z0-9]{0,79}\Z")
ALLOWED_PATCH_FORMATS = frozenset(("IPS", "BPS", "PPF"))
REVIEWED_LICENSES = frozenset((
    "MIT", "BSD-2-Clause", "BSD-3-Clause", "Zlib", "Apache-2.0",
    "CC0-1.0", "CC-BY-4.0",
))
EXPECTED_UPSTREAMS = (
    "godot", "sdl3", "blender", "gimp", "ffmpeg", "reshade",
    "bodySlide", "nexusMods", "bluez", "libusb", "weston", "gamescope",
    "retroarch", "pcsx2", "duckstation", "ccBy", "cc0",
)


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf8"))
    if not isinstance(data, dict):
        raise ValueError("RED_POLICY_NOT_OBJECT")
    return data


def _safe_path(path: Any) -> bool:
    if (not isinstance(path, str) or not path or len(path) > 180
            or Path(path).is_absolute() or ".." in Path(path).parts
            or "\\" in path):
        return False
    target = (ROOT / path).resolve()
    return target.is_file() and target.is_relative_to(ROOT.resolve())


def audit() -> dict[str, Any]:
    policy = load(POLICY)
    failures: list[str] = []
    if policy.get("schema") != "luhmOs.hostileModForge4x4.v1":
        failures.append("RED_SCHEMA")
    if policy.get("repository") != "eggie-admin/LuHm-OS" or (
            policy.get("approvedBrand") != "LuHm-OS: Project Premonition"):
        failures.append("RED_SOURCE_OR_BRAND")
    if not isinstance(policy.get("roots"), list) or len(policy["roots"]) != 11 or not all(
            _safe_path(path) for path in policy["roots"]):
        failures.append("RED_SOURCE_ANCHORS")
    lane_ids = [x.get("id") for x in policy.get("lanes", [])]
    phase_ids = [x.get("id") for x in policy.get("phases", [])]
    if lane_ids != list(LANES) or phase_ids != list(PHASES):
        failures.append("RED_FOUR_BY_FOUR_ORDER")
    cells: list[str] = []
    rows = policy.get("cells", [])
    if len(rows) != 4:
        failures.append("RED_MATRIX_ROWS")
    else:
        for i, row in enumerate(rows):
            if row.get("lane") != LANES[i] or len(row.get("states", [])) != 4:
                failures.append("RED_MATRIX_CELLS")
                continue
            for j, state in enumerate(row["states"]):
                cells.append(state.get("id"))
                if (state.get("id") != LANES[i] + "." + PHASES[j] or
                        state.get("phase") != PHASES[j] or
                        state.get("proven") is not False or
                        state.get("mutationAuthorized") is not False):
                    failures.append("RED_MATRIX_IMPLIED_RUNTIME")
    if len(cells) != 16 or len(set(cells)) != 16:
        failures.append("RED_MATRIX_CARDINALITY")
    variables = policy.get("env", {})
    allowed = variables.get("permitted", {})
    defaults = variables.get("defaults", {})
    if (not isinstance(allowed, dict) or len(allowed) != 8
            or set(allowed) != set(defaults)
            or any(key not in allowed or defaults.get(key) not in allowed[key]
                   for key in defaults)):
        failures.append("RED_ENV_POLICY")
    if (set(allowed) & set(variables.get("deniedNames", []))
            or variables.get("noEnvInjectionFromModManifest") is not True
            or variables.get("noSecretsReturned") is not True):
        failures.append("RED_ENV_PRIVILEGE")
    display = policy.get("display", {})
    if (display.get("mode") != "NO_X11_DEPENDENCY" or
            display.get("preferred") != ["headless", "wayland"] or
            display.get("mayStartXorg") is not False or
            display.get("maySetDisplayEnv") is not False or
            display.get("noPrivilegedDisplaySocketFromWeb") is not True):
        failures.append("RED_DISPLAY_BACKEND")
    devices = policy.get("devices", {})
    usb, bt, debug = devices.get("usb", {}), devices.get("bluetooth", {}), devices.get("debug", {})
    if (usb.get("serialStorageForbidden") is not True or
            usb.get("driverDetachForbidden") is not True or
            bt.get("rawMacStorageForbidden") is not True or
            bt.get("writePairOrBondForbidden") is not True or
            debug.get("rawCommandExecution") is not False or
            debug.get("neverInPublicMcp") is not True):
        failures.append("RED_DEVICE_DEBUG_PRIVILEGE")
    mods = policy.get("modding", {})
    for key in ("noRemoteBinaryFetch", "noAutoFork", "noAutoPluginInstall",
                "noCopyNexusAssetsToDistribution", "noAbandonwareCopyrightException",
                "noRomBiosOrDiscImagesInSourceOrReceipts",
                "patchContentCannotBeFetchedOrAppliedByRegistry"):
        if mods.get(key) is not True:
            failures.append("RED_MOD_BINARY_BOUNDARY")
            break
    rights = policy.get("licensing", {})
    if (rights.get("actualRoot") != "GPL-3.0" or
            rights.get("noBlanketRelicense") is not True or
            rights.get("codeNeverAutoClassedAsCreativeCommons") is not True or
            rights.get("useApache2ForNewOriginalSourceOnlyAfterOwnerRightsReview") is not True or
            "GNU GENERAL PUBLIC LICENSE" not in
            (ROOT / "LICENSE").read_text(encoding="utf8")[:140]):
        failures.append("RED_LICENSE_RELABEL")
    upstream = policy.get("upstream", [])
    if [r.get("id") for r in upstream] != list(EXPECTED_UPSTREAMS):
        failures.append("RED_UPSTREAM_IDENTITY")
    else:
        for record in upstream:
            if (not str(record.get("url", "")).startswith("https://")
                    or not record.get("license")
                    or record.get("admit") in ("AUTO_IMPORT", "AUTO_FORK", "PUBLIC_COPY")):
                failures.append("RED_UPSTREAM_AUTHORITY")
                break
    quarantine = load(QUARANTINE)
    brand = load(BRAND)
    if (quarantine.get("state") != "QUARANTINED" or
            quarantine.get("activeTaskWorkersAllowed") is not False or
            brand.get("publicBrands", {}).get("luhmOs", {}).get("currentProject") !=
            "Project Premonition"):
        failures.append("RED_QUARANTINE_OR_BRAND")
    admission = policy.get("admission", {})
    for metric in ("networkRequests", "hardwareDevicesConnected", "filesImported",
                   "codeForksCreated", "liveAgentsStarted"):
        if admission.get(metric) != 0:
            failures.append("RED_FAKE_RUNTIME_" + metric)
    for gate in ("requireSourceCommitAndBinaryDigest", "requireExactFileLicense",
                 "requireProvenanceAndAssetPermission", "requireCodeReviewAndSandbox",
                 "requireOwnerBeforeRuntime", "noAutoMerge", "noAutoDeploy",
                 "noNewSpend", "companyQuarantinePreserved"):
        if admission.get(gate) is not True:
            failures.append("RED_EXECUTION_GATE_" + gate)
    if policy.get("crownStatus") != "STOP":
        failures.append("RED_CROWN")
    canonical = json.dumps(
        {"lanes": lane_ids, "phases": phase_ids, "upstreams": [
            r.get("id") for r in upstream]}, sort_keys=True).encode("utf8")
    return {
        "schema": "luhmOs.hostileModForge4x4Audit.v1",
        "status": "SOURCE_CANDIDATE_ONLY" if not failures else "RED_SOURCE_DRIFT",
        "issues": sorted(set(failures)),
        "fourByFourCells": len(cells),
        "upstreamReferenceCount": len(upstream),
        "registryIdentitySha256": hashlib.sha256(canonical).hexdigest(),
        "observedUsbDevices": 0, "observedBluetoothDevices": 0,
        "actualHostEnvironmentRead": False, "vmDisplayProven": False,
        "forksMade": 0, "pluginsInstalled": 0, "patchesApplied": 0,
        "mediaAssetsImported": 0, "networkCalls": 0,
        "greenAuthority": False, "crownAuthority": False,
    }


def environment_plan(proposed: Mapping[str, Any]) -> dict[str, Any]:
    """Never reads os.environ or sets real process environment variables."""
    if not isinstance(proposed, Mapping) or len(proposed) > 8:
        raise ValueError("RED_ENV_SHAPE")
    env = load(POLICY)["env"]
    requested = dict(proposed)
    for key, value in requested.items():
        if (not isinstance(key, str) or key not in env["permitted"]
                or type(value) is not str or value not in env["permitted"][key]):
            raise ValueError("RED_ENV_UNRECOGNIZED_VARIABLE_OR_VALUE")
    values = dict(env["defaults"])
    values.update(requested)
    # Device read-only requests require an explicit user-authorized host
    # adapter. This function never treats the string as that permission.
    pending = []
    for flag in ("LUHM_USB_ENABLED", "LUHM_BLUETOOTH_ENABLED"):
        if values[flag] == "readOnly":
            pending.append(flag + "_NEEDS_OS_PERMISSION_AND_OWNER")
    if values["LUHM_INPUT_MODE"] == "userAuthorized":
        pending.append("INPUT_OWNER_PERMISSION_NOT_PROVEN")
    return {
        "state": "HOLD_OS_PERMISSION_OR_HOST_RUNTIME" if pending else "SOURCE_FLAGS_ONLY",
        "values": values, "blockers": pending,
        "hostEnvironmentRead": False, "hostEnvironmentModified": False,
        "deviceOpened": False, "workerStarted": False,
        "greenAuthority": False, "crownAuthority": False,
    }


def device_metadata(*, transport: str, vendor_id: str = "",
                    product_id: str = "", service_uuid: str = "") -> dict[str, Any]:
    """Identifiers are untrusted labels, NOT authentication or inventory proof."""
    if transport == "usb":
        if not (type(vendor_id) is str and type(product_id) is str and
                HEX4.fullmatch(vendor_id) and HEX4.fullmatch(product_id) and
                not service_uuid):
            raise ValueError("RED_USB_HEX_ID")
        ident = vendor_id + ":" + product_id
    elif transport == "bluetooth":
        if (not isinstance(service_uuid, str) or
                UUID128.fullmatch(service_uuid) is None or vendor_id or product_id):
            raise ValueError("RED_BLUETOOTH_UUID")
        ident = service_uuid
    else:
        raise ValueError("RED_DEVICE_TRANSPORT")
    return {
        "transport": transport, "opaqueHashSha256": hashlib.sha256(
            (transport + "|" + ident).encode("ascii")).hexdigest(),
        "rawSerialOrMacStored": False, "realDevicePresent": False,
        "permissionGranted": False, "mutationAllowed": False,
        "status": "UNTRUSTED_IDENTIFIER_ONLY",
    }


def community_candidate(*, source_id: str, claimed_license: str,
                        claimed_sha256: str) -> dict[str, Any]:
    """Strict admission for *claims* without automated cloning or forking."""
    policy = load(POLICY)
    sources = {x["id"]: x for x in policy["upstream"]}
    if type(source_id) is not str or source_id not in sources:
        raise ValueError("RED_UNREGISTERED_UPSTREAM")
    if (type(claimed_license) is not str or len(claimed_license) > 64 or
            type(claimed_sha256) is not str or
            HEX64.fullmatch(claimed_sha256) is None):
        raise ValueError("RED_UNTRUSTED_COMPONENT_CLAIM")
    source = sources[source_id]
    return {
        "id": source_id, "declaredLicense": claimed_license,
        "sourcePublishedLicenseHint": source["license"],
        "reportedSha256": claimed_sha256,
        "licenseClaimMatchesResearch": claimed_license == source["license"],
        "possiblePermissiveReview": claimed_license in REVIEWED_LICENSES,
        "actualBinaryVerified": False, "fileRightsVerified": False,
        "status": "HOLD_REVIEW_LICENSE_AUTHOR_PROVENANCE_AND_BINARY",
        "mayFork": False, "mayCopyMedia": False, "mayInstall": False,
        "mayPublish": False, "greenAuthority": False,
    }


def synthetic_patch_plan(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Only read format/size/digests/offsets; never request ROM or patch bytes."""
    required = {"taskId", "sourceRef", "scopeId", "format", "inputSha256",
                "outputSha256", "patchSha256", "offsetHex", "originalRights"}
    if not isinstance(payload, Mapping) or set(payload) != required:
        raise ValueError("RED_PATCH_UNEXPECTED_FIELD")
    if not all(type(payload[k]) is str and IDENT.fullmatch(payload[k])
               for k in ("taskId", "scopeId")):
        raise ValueError("RED_PATCH_TASK_SCOPE")
    if type(payload["sourceRef"]) is not str or HEX40.fullmatch(payload["sourceRef"]) is None:
        raise ValueError("RED_PATCH_SOURCE_ID")
    for key in ("inputSha256", "outputSha256", "patchSha256"):
        if type(payload[key]) is not str or HEX64.fullmatch(payload[key]) is None:
            raise ValueError("RED_PATCH_DIGEST")
    if (payload["format"] not in ALLOWED_PATCH_FORMATS or
            type(payload["offsetHex"]) is not str or
            HEX_OFFSET.fullmatch(payload["offsetHex"]) is None or
            payload["originalRights"] not in ("homebrewOwned", "expresslyLicensed")):
        raise ValueError("RED_PATCH_RIGHTS_FORMAT_OR_OFFSET")
    offset = int(payload["offsetHex"], 16)
    return {
        "schema": "luhmOs.modPatchCandidate.v1",
        "state": "HOLD_LICENSE_AND_USER_SUPPLIED_IMAGE_REVIEW",
        "format": payload["format"], "offsetHex": f"0x{offset:08x}",
        "patchMetadataOnly": True, "originalRomOpened": False,
        "patchApplied": False, "copyProtectionCircumvented": False,
        "filesDownloaded": False, "publicationAuthorized": False,
        "sourceHeadIndependentlyVerified": False,
        "greenAuthority": False, "crownAuthority": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
