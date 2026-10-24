#!/usr/bin/env python3
"""Validate owner-approved CAST artifact before a GitHub plugin-channel release.

No host installation, app publication, device test, or source mutation implied.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

CHANNELS = ("proposed", "beta", "stable")
SOURCE_SHA = re.compile(r"^[a-f0-9]{40}$")
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
HEX = re.compile(r"^[a-f0-9]{64}$")
APPROVAL_FIELDS = {
    "beta": ("externalChatGptHostInstallReceipt", "mobileDeviceMountReceipt",
             "urdIndependentReviewReceipt", "professorPromotionReceipt"),
    "stable": ("externalChatGptHostInstallReceipt", "mobileDeviceMountReceipt",
               "urdIndependentReviewReceipt", "professorPromotionReceipt",
               "betaAcceptanceReceipt", "rollbackVerificationReceipt",
               "providerPublicationApprovalReceipt"),
}


def inspect(folder: Path, channel: str, source: str, expected_sha: str,
            acceptance: Path | None = None) -> dict:
    failures = []
    def require(ok: bool, why: str) -> None:
        if not ok:
            failures.append(why)
    require(channel in CHANNELS, "invalid channel")
    require(bool(SOURCE_SHA.fullmatch(source)), "source SHA invalid")
    require(bool(HEX.fullmatch(expected_sha)), "expected package digest invalid")
    receipt_file = folder / "publicPluginPackageBuildReceipt.json"
    try:
        outer = json.loads(receipt_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "RED", "errors": ["missing or invalid CAST package receipt"]}
    artifact = outer.get("artifact", {})
    filename = artifact.get("filename", "")
    require(bool(re.fullmatch(r"LuHm-OS-plugin-[0-9]+\.[0-9]+\.[0-9]+-[a-f0-9]{8}\.zip", filename)), "unexpected package name")
    require(outer.get("schema") == "luhmOs.publicPluginPackageBuildReceipt.v2", "receipt schema mismatch")
    require(outer.get("status") == "BUILT_BY_CAST_SCOPE", "not a CAST-built package")
    require(outer.get("sourceRef") == source, "source mismatch")
    require(outer.get("buildScope") == "publicPluginPackage", "build scope mismatch")
    require(outer.get("publicationAuthority") is False and outer.get("releaseAuthority") is False,
            "build receipt gained publication authority")
    require(outer.get("crownAuthority") is False, "build receipt gained Crown authority")
    path = folder / filename
    if not path.is_file() or path.is_symlink():
        require(False, "package file missing or symlinked")
        return {"status": "RED", "errors": failures}
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    require(digest == expected_sha == artifact.get("sha256"), "SHA256 mismatch")
    require(path.stat().st_size == artifact.get("bytes"), "package size mismatch")
    version = filename.removeprefix("LuHm-OS-plugin-").removesuffix("-" + source[:8] + ".zip")
    require(bool(VERSION.fullmatch(version)), "semantic version invalid")
    try:
        with zipfile.ZipFile(path) as z:
            require(z.testzip() is None, "ZIP integrity failed")
            require(len(z.namelist()) == len(set(z.namelist())), "duplicate members")
            require(all(not n.startswith("/") and ".." not in Path(n).parts for n in z.namelist()), "unsafe ZIP names")
            member = json.loads(z.read("BUILD_RECEIPT.json"))
            manifest = json.loads(z.read("plugin.json"))
            require(member.get("sourceRef") == source and member.get("status") == "PACKAGE_READY_ONLY",
                    "embedded receipt mismatch")
            require(member.get("hostInstalled") is False and member.get("inChatToolInvoked") is False,
                    "package claims false host proof")
            require(manifest.get("version") == version and manifest.get("name") == "luhm-os",
                    "manifest identity/version mismatch")
    except (OSError, ValueError, KeyError, zipfile.BadZipFile):
        require(False, "invalid ZIP manifest or embedded receipts")
    evidence = {}
    if channel in APPROVAL_FIELDS:
        if acceptance is None or not acceptance.is_file():
            require(False, "beta/stable acceptance receipt missing")
        else:
            try:
                evidence = json.loads(acceptance.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                require(False, "invalid acceptance receipt")
        require(evidence.get("sourceRef") == source and evidence.get("channel") == channel,
                "acceptance source/channel mismatch")
        require(evidence.get("sha256") == expected_sha, "acceptance digest mismatch")
        require(evidence.get("status") == "PROVED", "acceptance not proved")
        for field in APPROVAL_FIELDS[channel]:
            token = evidence.get(field)
            require(isinstance(token, str) and len(token.strip()) >= 20
                    and not token.startswith(("PENDING", "UNKNOWN", "NONE", "NOT_")),
                    "unproved independent acceptance: " + field)
    return {
        "schema": "luhmOs.pluginReleasePromotionGate.v1",
        "status": "PASS" if not failures else "RED",
        "channel": channel, "version": version, "sourceRef": source,
        "packageSha256": digest, "package": filename,
        "tag": f"luhm-plugin-{channel}-v{version}-s{source[:8]}",
        "errors": failures,
        "hostAndDeviceVerifiedByThisScript": False,
        "crownStatus": "STOP",
    }


def main() -> int:
    a = argparse.ArgumentParser()
    a.add_argument("--folder", type=Path, required=True)
    a.add_argument("--channel", choices=CHANNELS, required=True)
    a.add_argument("--source-ref", required=True)
    a.add_argument("--expected-sha256", required=True)
    a.add_argument("--acceptance", type=Path)
    a.add_argument("--output", type=Path)
    args = a.parse_args()
    report = inspect(args.folder, args.channel, args.source_ref, args.expected_sha256, args.acceptance)
    output = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    print(output)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
