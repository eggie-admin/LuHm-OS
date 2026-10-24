#!/usr/bin/env python3
"""Deterministic, fail-closed public LuHm OS plugin package assembler."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "luhm-os"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
MEMBERS = (
    "plugin.json",
    "mcp.json",
    "README.md",
    "VIRGIN_INSTALL.md",
    "PRIVACY.md",
    "TERMS.md",
    "review-tests.json",
    "assets/logo.svg",
    "skills/luhm-agent-workflow/SKILL.md",
    "skills/luhm-coding-roleplay/SKILL.md",
    "skills/belldandy-housekeeping/SKILL.md",
    "skills/luhm-glass-module-dock/SKILL.md",
)
REPO_MEMBERS = ("LICENSE",)  # Include the GPLv3 text in distributable fork archives.
GENERATED = ("SOURCE_MAP.json", "BUILD_RECEIPT.json")
PRIVATE_NAMES = ("mcp.local.json", "mcp.private.json", "mcp.remote.example.json")
ENDPOINT = "https://luhm-os-harness-green.onrender.com/mcp"


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def collect(source_ref: str) -> tuple[dict[str, bytes], str]:
    if len(source_ref) != 40 or any(c not in "0123456789abcdef" for c in source_ref):
        raise ValueError("sourceRef must be lowercase 40-character SHA")
    if len(MEMBERS) != len(set(MEMBERS)):
        raise ValueError("duplicate package members")

    payload = {}
    for name in MEMBERS:
        root = PLUGIN.resolve(strict=True)
        file_path = PLUGIN / name
        resolved = file_path.resolve(strict=True)
        if not resolved.is_relative_to(root) or not resolved.is_file() or file_path.is_symlink():
            raise ValueError(f"unsafe package file: {name}")
        if any(part.startswith(".") for part in pathlib.PurePosixPath(name).parts):
            raise ValueError(f"hidden file not allowed: {name}")
        if pathlib.PurePosixPath(name).name in PRIVATE_NAMES:
            raise ValueError(f"private MCP file not allowed: {name}")
        payload[name] = resolved.read_bytes()

    # Reuse the immutable repository license, not an inconsistent package copy.
    # Files under third-party licenses retain their own provenance obligations.
    for name in REPO_MEMBERS:
        license_path = ROOT / name
        if not license_path.is_file() or license_path.is_symlink():
            raise ValueError("missing or symlinked repository license")
        raw = license_path.read_bytes()
        if len(raw) < 1024 or len(raw) > 128 * 1024 or b"GNU GENERAL PUBLIC LICENSE" not in raw:
            raise ValueError("unexpected repository license")
        payload[name] = raw

    manifest = json.loads(payload["plugin.json"].decode("utf-8"))
    mcp = json.loads(payload["mcp.json"].decode("utf-8"))
    if manifest.get("name") != "luhm-os" or not manifest.get("version"):
        raise ValueError("plugin identity malformed")
    if mcp.get("mcpServers", {}).get("luhm", {}).get("url") != ENDPOINT:
        raise ValueError("MCP origin mismatch")
    version = manifest["version"]
    source_map = {
        "schema": "luhmOs.pluginSourceMap.v1",
        "repository": "eggie-admin/LuHm-OS",
        "sourceRef": source_ref,
        "members": {name: sha256(data) for name, data in sorted(payload.items())},
        "excludedProfiles": list(PRIVATE_NAMES),
    }
    payload["SOURCE_MAP.json"] = canonical_bytes(source_map)
    payload["BUILD_RECEIPT.json"] = canonical_bytes({
        "schema": "luhmOs.pluginBuildReceipt.v1",
        "sourceRef": source_ref,
        "version": version,
        "memberCount": len(MEMBERS) + len(REPO_MEMBERS) + len(GENERATED),
        "scope": "publicPluginPackage",
        "status": "PACKAGE_READY_ONLY",
        "hostInstalled": False,
        "inChatToolInvoked": False,
        "crownStatus": "STOP",
    })
    if sorted(payload) != sorted((*MEMBERS, *REPO_MEMBERS, *GENERATED)):
        raise ValueError("payload manifest drift")
    return payload, version


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--out-dir")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    actual = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    if actual != args.source_ref:
        raise SystemExit(f"SOURCE_DRIFT expected={args.source_ref} actual={actual}")
    payload, version = collect(args.source_ref)
    if args.verify_only:
        print(f"GREEN_PLUGIN_SOURCE_MEMBERS count={len(payload)} sourceRef={args.source_ref}")
        return 0
    if not args.out_dir:
        parser.error("--out-dir is required unless --verify-only is used")
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = out_dir / f"LuHm-OS-plugin-{version}-{args.source_ref[:8]}.zip"
    with zipfile.ZipFile(artifact, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, data)
    with zipfile.ZipFile(artifact) as zf:
        if zf.testzip() is not None or sorted(zf.namelist()) != sorted(payload):
            raise ValueError("archive integrity failure")
        if any(zf.read(n) != data for n, data in payload.items()):
            raise ValueError("archive content mismatch")
    outer = {
        "schema": "luhmOs.publicPluginPackageBuildReceipt.v2",
        "status": "BUILT_BY_CAST_SCOPE",
        "sourceRef": args.source_ref,
        "buildScope": "publicPluginPackage",
        "artifact": {"filename": artifact.name, "sha256": sha256(artifact.read_bytes()), "bytes": artifact.stat().st_size},
        "members": sorted(payload),
        "publicationAuthority": False,
        "releaseAuthority": False,
        "crownAuthority": False,
    }
    (out_dir / "publicPluginPackageBuildReceipt.json").write_bytes(canonical_bytes(outer))
    print("PUBLIC_PLUGIN_PACKAGE=BUILT")
    print(f"sourceRef={args.source_ref}")
    print(f"artifact={artifact}")
    print(f"sha256={outer['artifact']['sha256']}")
    print(f"members={len(payload)}")
    print("publicationAuthority=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
