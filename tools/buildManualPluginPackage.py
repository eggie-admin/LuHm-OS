#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

rootPath = Path(__file__).resolve().parents[1]
pluginRoot = rootPath / "plugins" / "luhm-os"
buildRoot = rootPath / "build" / "manual-plugin"
stageRoot = buildRoot / "stage"
archivePath = buildRoot / "luhm-os-manual-upload-0.5.0.zip"

installDoc = json.loads((rootPath / "doctrine" / "manualPluginVirginInstallV1.json").read_text(encoding="utf-8"))
sourceTruth = json.loads((rootPath / "doctrine" / "currentSourceTruthV3.json").read_text(encoding="utf-8"))
roleplayDoc = json.loads((rootPath / "doctrine" / "codingRoleplayDirectorV2.json").read_text(encoding="utf-8"))
pluginDoc = json.loads((pluginRoot / "plugin.json").read_text(encoding="utf-8"))
mcpDoc = json.loads((pluginRoot / "mcp.json").read_text(encoding="utf-8"))

requiredNames = installDoc["package"]["required"]
excludedNames = set(installDoc["package"]["excluded"])

if pluginDoc.get("version") != installDoc["package"]["packageVersion"]:
    raise SystemExit("plugin version does not match virgin-install doctrine")

if stageRoot.exists():
    shutil.rmtree(stageRoot)
stageRoot.mkdir(parents=True, exist_ok=True)
buildRoot.mkdir(parents=True, exist_ok=True)

for name in requiredNames:
    sourcePath = pluginRoot / name
    if sourcePath.exists() is False:
        raise SystemExit(f"required plugin input missing: {name}")
    targetPath = stageRoot / name
    if sourcePath.is_dir():
        shutil.copytree(sourcePath, targetPath)
    else:
        shutil.copy2(sourcePath, targetPath)

for name in excludedNames:
    if (stageRoot / name).exists():
        raise SystemExit(f"excluded developer/private input entered stage: {name}")

sourceRef = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=rootPath, text=True).strip()
sourceMap = {
    "schema": "luhmOs.manualPluginSourceMap.v1",
    "pluginVersion": pluginDoc["version"],
    "sourceRef": sourceRef,
    "sourceTruthSchema": sourceTruth.get("schema"),
    "sourceTruthStatus": sourceTruth.get("status"),
    "contracts": {
        "chatCanon": "doctrine/projectChatCanonV1.json",
        "codingRoleplay": "doctrine/codingRoleplayDirectorV2.json",
        "semanticDomainHardening": "doctrine/semanticDomainHardeningV1.json",
        "belldandyPkiCorporateSecretary": "doctrine/belldandyPkiCorporateSecretaryV1.json",
        "manualPluginVirginInstall": "doctrine/manualPluginVirginInstallV1.json",
    },
    "roleplaySchema": roleplayDoc.get("schema"),
    "mcpEndpoint": mcpDoc.get("mcpServers", {}).get("luhm", {}).get("url"),
    "authority": {
        "readOnly": True,
        "mutationAuthority": False,
        "greenAuthority": False,
        "crownAuthority": False,
    },
}
(stageRoot / "SOURCE_MAP.json").write_text(json.dumps(sourceMap, indent=2) + "\n", encoding="utf-8")

fileHashes = {}
for path in sorted(p for p in stageRoot.rglob("*") if p.is_file()):
    relative = path.relative_to(stageRoot).as_posix()
    fileHashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()

buildReceipt = {
    "schema": "luhmOs.manualPluginBuildReceipt.v1",
    "status": "PACKAGE_STAGED",
    "pluginVersion": pluginDoc["version"],
    "sourceRef": sourceRef,
    "installMode": "virginInstall",
    "archiveRootEqualsPluginRoot": True,
    "priorPluginStateRequired": False,
    "migrationRequired": False,
    "secretValuesIncluded": False,
    "excludedDeveloperConfigs": sorted(excludedNames),
    "fileHashes": fileHashes,
    "crownStatus": "STOP",
}
(stageRoot / "BUILD_RECEIPT.json").write_text(json.dumps(buildReceipt, indent=2) + "\n", encoding="utf-8")

if archivePath.exists():
    archivePath.unlink()

fixedTime = (2026, 10, 7, 0, 0, 0)
with zipfile.ZipFile(archivePath, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in sorted(p for p in stageRoot.rglob("*") if p.is_file()):
        relative = path.relative_to(stageRoot).as_posix()
        info = zipfile.ZipInfo(relative, fixedTime)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(info, path.read_bytes())

archiveHash = hashlib.sha256(archivePath.read_bytes()).hexdigest()
summary = {
    "schema": "luhmOs.manualPluginArtifactReceipt.v1",
    "status": "PACKAGE_BUILT",
    "artifact": str(archivePath.relative_to(rootPath)),
    "sha256": archiveHash,
    "sourceRef": sourceRef,
    "pluginVersion": pluginDoc["version"],
    "entryCount": len(zipfile.ZipFile(archivePath).namelist()),
    "crownStatus": "STOP",
}
(buildRoot / "artifact-receipt.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
