#!/usr/bin/env python3
"""Read-only managed-path checks; no certificate or private-key contents read."""
import argparse
import json
import re
from pathlib import Path


def inspectPaths(certName, configRoot=Path("/etc/letsencrypt")):
    resultValue = {"schema": "luhmOs.certbotWorkspaceSymlinkAudit.v1", "status": "VERIFY_CERTBOT_RUNTIME_STATE", "certName": certName or "UNSET", "secretValuesRead": False, "mutationAuthority": False, "certificateValidityProven": False, "renewalProven": False, "serviceReadinessProven": False, "checks": {}, "crownStatus": "STOP"}
    if not certName:
        resultValue["status"] = "VERIFY_CERT_NAME_REQUIRED"
        return resultValue, 2
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,252}", certName) is None:
        resultValue["status"] = "RED_CERT_NAME_INVALID"
        return resultValue, 2
    try:
        liveBase = configRoot / "live"
        archiveBase = configRoot / "archive"
        renewalBase = configRoot / "renewal"
        livePath = liveBase / certName
        archivePath = archiveBase / certName
        checksDoc = resultValue["checks"]
        checksDoc["managedRootsAreDirectories"] = all(pathValue.is_dir() and not pathValue.is_symlink() for pathValue in (configRoot, liveBase, archiveBase, renewalBase))
        checksDoc["liveRootExists"] = livePath.is_dir() and not livePath.is_symlink()
        checksDoc["archiveRootExists"] = archivePath.is_dir() and not archivePath.is_symlink()
        renewalPath = renewalBase / (certName + ".conf")
        checksDoc["renewalConfigExists"] = renewalPath.is_file() and not renewalPath.is_symlink()
        versionList = []
        for prefixValue, filenameValue in (("fullchain", "fullchain.pem"), ("privkey", "privkey.pem")):
            pathValue = livePath / filenameValue
            checksDoc[prefixValue + "IsSymlink"] = pathValue.is_symlink()
            resolvedPath = pathValue.resolve(strict=True)
            checksDoc[prefixValue + "Exists"] = resolvedPath.is_file()
            nameMatch = re.fullmatch(prefixValue + r"([1-9][0-9]*)\.pem", resolvedPath.name)
            checksDoc[prefixValue + "ManagedTarget"] = resolvedPath.parent == archivePath.resolve(strict=True) and nameMatch is not None
            versionList.append(nameMatch.group(1) if nameMatch else None)
        checksDoc["matchingArchiveVersions"] = versionList[0] is not None and versionList[0] == versionList[1]
        if all(checksDoc.values()):
            resultValue["status"] = "GREEN_CERTBOT_LIVE_PATH_PRESENT"
            return resultValue, 0
    except (OSError, RuntimeError, ValueError):
        resultValue["status"] = "VERIFY_CERTBOT_RUNTIME_STATE"
        resultValue["checks"]["filesystemInspectionCompleted"] = False
    return resultValue, 3


def main():
    parserValue = argparse.ArgumentParser(description=__doc__)
    parserValue.add_argument("--cert-name", dest="certName", default="")
    parserValue.add_argument("--runtime", action="store_true")
    argsValue = parserValue.parse_args()
    if argsValue.runtime:
        resultValue, exitCode = inspectPaths(argsValue.certName)
    else:
        resultValue = {"schema": "luhmOs.certbotWorkspaceSymlinkAudit.v1", "status": "SOURCE_CONTRACT_ONLY", "certName": argsValue.certName or "UNSET", "secretValuesRead": False, "mutationAuthority": False, "checks": {}, "certificateValidityProven": False, "renewalProven": False, "serviceReadinessProven": False, "crownStatus": "STOP"}
        exitCode = 0
    print(json.dumps(resultValue, indent=2))
    return exitCode


if __name__ == "__main__":
    raise SystemExit(main())

