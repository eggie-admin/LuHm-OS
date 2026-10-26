#!/usr/bin/env python3
"""Read-only SHA-256 content and platform-boundary proof for the LuHm packaging matrix.

Never builds, installs, signs, uploads or publishes. A registry/package is not
assumed just because a package format appears in YAML doctrine.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "doctrine/universalPackageMatrixV1.yaml"
REQUIRED = frozenset(("browser", "npm", "python", "deb", "snap", "oci", "android", "chatGpt"))


def audit(config: dict, root: Path = ROOT) -> dict:
    failures: list[str] = []
    def check(condition: bool, name: str):
        if not condition:
            failures.append(name)

    check(config.get("schema") == "luhmOs.universalPackageMatrix.v1", "RED_SCHEMA")
    check(config.get("status") == "SOURCE_CANDIDATE_NOT_BUILT", "RED_STATUS")
    check(config.get("crownStatus") == "STOP", "RED_CROWN")
    outputs = config.get("outputs", {})
    check(isinstance(outputs, dict) and REQUIRED.issubset(outputs), "RED_MISSING_TARGET")
    for target in REQUIRED.intersection(outputs):
        item = outputs[target]
        check(item.get("generated") is False if "generated" in item else
              item.get("distributionEnabled") is False if target == "browser" else
              item.get("publicPublication") is False, "RED_FALSE_BUILD_" + target)
    check(outputs.get("npm", {}).get("currentPackagePrivate") is True, "RED_NPM_PRIVATE")
    check(outputs.get("android", {}).get("signingProven") is False, "RED_ANDROID_SIGNER")
    check(outputs.get("android", {}).get("androidSecureFolderProof") == "NOT_VERIFIED", "RED_SECURE_FOLDER")
    check(outputs.get("chatGpt", {}).get("nativeHostMount") == "RED_PREVIOUS_OWNER_SCREENSHOT", "RED_CHAT_MOUNT")

    arch = config.get("architecture", {})
    check(arch.get("realRuntimeData") == "existingApprovedPrivateSql", "RED_SQL")
    check(arch.get("canonicalVersionAndCapabilities") == "reviewedYaml", "RED_YAML")
    check(arch.get("noPlatformDriversBundledInsideWebPayload") is True, "RED_DRIVER")
    check(arch.get("proprietaryApiAdaptersOnlyServerSideAndOptIn") is True, "RED_VENDOR")
    check(arch.get("neverAssumeDraftAlreadyOnMain") is True, "RED_DRAFT")
    abi = config.get("abis", {})
    check(abi.get("ubuntuAndAndroidShareUserspaceAbi") is False and
          abi.get("linuxGlibcIsAndroidBionic") is False and
          abi.get("osSpecificNativeSharedObjectsMustNotBeCopiedUnchanged") is True, "RED_NATIVE_ABI")
    deployment = config.get("deployment", {})
    check(deployment.get("noExternalCdnAtRuntime") is True and
          deployment.get("keepServerProvidersOutsideApk") is True and
          deployment.get("noFirmwareHexEditorOdinRootOrUnsupportedKernel") is True,
          "RED_RELEASE_BOUNDARY")
    check(deployment.get("requireActualBuildAndDeviceTestsBeforeGreen") is True,
          "RED_DEVICE_EVIDENCE")

    files = arch.get("immutablePayloadComponents", [])
    check(isinstance(files, list) and len(files) >= 6 and
          len(files) == len(set(files)), "RED_SHARED_SOURCE_LIST")
    manifest = []
    for path in files if isinstance(files, list) else []:
        name = Path(path)
        if name.is_absolute() or ".." in name.parts or not path.startswith("frontEnd/"):
            failures.append("RED_PATH_ESCAPE")
            continue
        filename = (root / name).resolve()
        if root.resolve() not in filename.parents or not filename.is_file():
            failures.append("RED_SHARED_FILE_MISSING_" + path)
            continue
        data = filename.read_bytes()
        manifest.append({"path": path, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return {
        "schema": "luhmOs.universalPackageAudit.v1",
        "status": "GREEN_SOURCE_INVENTORY_ONLY" if not failures else "RED_PORTABILITY_SOURCE_GATE",
        "sharedAssets": sorted(manifest, key=lambda e: e["path"]),
        "sharedAssetBytes": sum(e["bytes"] for e in manifest),
        "candidateFormats": sorted(REQUIRED),
        "releaseArtifactGenerated": False,
        "androidSignedOrInstalled": False,
        "productionKioskModified": False,
        "errors": sorted(set(failures)),
    }


def main() -> int:
    policy = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    receipt = audit(policy)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not receipt["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
