#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

def require(ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)

def read(rel: str) -> str:
    path = ROOT / rel
    require(path.is_file(), f"missing required file: {rel}")
    return path.read_text(encoding="utf-8") if path.is_file() else ""

def load_json(rel: str) -> dict:
    text = read(rel)
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception as exc:
        errors.append(f"invalid JSON {rel}: {exc}")
        return {}

installer = read("tools/termuxVirginInstall.sh")
orchestrator = read("tools/termuxCastReleaseInstall.sh")
workflow = read(".github/workflows/android-testing-build.yml")
source = load_json("doctrine/SOURCE_OF_TRUTH.json")
release_boundary = load_json("doctrine/RELEASE_BOUNDARY.json")
install_contract = load_json("doctrine/ROOTED_TERMUX_GITHUB_RELEASE_INSTALL_V1.json")

aw3 = source.get("androidWeb3Cockpit", {})
require(aw3.get("delivery") == "GITHUB_PRERELEASE_TO_ROOTED_TERMUX",
        "source truth delivery must be GitHub prerelease -> rooted Termux")
require(aw3.get("releaseInstallContract") == "doctrine/ROOTED_TERMUX_GITHUB_RELEASE_INSTALL_V1.json",
        "source truth rooted install contract missing")
require(aw3.get("rootedTermuxInstaller") == "tools/termuxVirginInstall.sh",
        "source truth Termux installer drift")
require(aw3.get("legacyLanPortal") == "HISTORICAL_ONLY_FOR_THIS_MILESTONE",
        "legacy LAN portal must remain historical for this milestone")

require(install_contract.get("package") == "art.eggiebagelface.luhmos.testing",
        "rooted install package drift")
safety = install_contract.get("safety", {})
require(safety.get("checksumRequired") is True, "checksum must be required")
require(safety.get("rootRequired") is True, "root must be required")
require(safety.get("broadStorageDeletion") is False, "broad storage deletion must remain false")
require(safety.get("arbitraryPackageRemoval") is False, "arbitrary package removal must remain false")
require(safety.get("packageFixedToLuHm") is True, "package must remain fixed to LuHm")
require(install_contract.get("priorLanPortal", {}).get("status") == "HISTORICAL_ONLY_FOR_THIS_MILESTONE",
        "install contract must retire LAN portal for this milestone")

for token in (
    'REPO="eggie-admin/LuHm-OS"',
    'PACKAGE="art.eggiebagelface.luhmos.testing"',
    'su -c id',
    'sha256sum -c "$SHA_NAME"',
    'pm clear',
    'pm uninstall',
    '/data/local/tmp/$APK_NAME',
    'pm install -t',
    'cmd package resolve-activity --brief',
    'getprop ro.product.model',
    'getprop ro.product.device',
    'getprop ro.build.version.release',
    'getprop ro.build.version.sdk',
    'getprop ro.build.fingerprint',
):
    require(token in installer, f"Termux virgin installer missing: {token}")

require("/tmp/luhm-" not in installer, "Termux installer must not assume desktop /tmp")
require('"/sdcard/Android/data/$PACKAGE"' in installer, "scoped Android/data cleanup missing")
require('"/sdcard/Android/obb/$PACKAGE"' in installer, "scoped Android/obb cleanup missing")
require("rm -rf /" not in installer, "broad root filesystem deletion is forbidden")
require("rm -rf -- '$p'" in installer, "external cleanup must stay scoped to enumerated LuHm paths")
require(installer.index('sha256sum -c "$SHA_NAME"') < installer.index('pm uninstall'),
        "checksum verification must occur before uninstall")
require(installer.index('pm uninstall') < installer.index('pm install -t'),
        "old LuHm package must be removed before fresh install")

for token in (
    '[ "$CAST_WORD" = "cast" ]',
    'gh auth status',
    'repos/$REPO/branches/main',
    'gh workflow run "$WORKFLOW"',
    '--ref main',
    '-f cast=cast',
    '-f sourceRef="$SOURCE_REF"',
    '-f releaseTag="$TAG"',
    '-f publishPrerelease=true',
    'gh run watch "$RUN_ID"',
    'gh release view "$TAG"',
    'exec bash "$SCRIPT_DIR/termuxVirginInstall.sh" "$TAG"',
):
    require(token in orchestrator, f"Termux CAST/release helper missing: {token}")
require("rerun" not in orchestrator.lower(), "helper may not substitute rerun for a fresh CAST dispatch")
require("DISPATCH_AFTER=" in orchestrator and ".createdAt >= " in orchestrator,
        "helper must bind run lookup to the dispatch window")

scope = release_boundary.get("androidWeb3Prerelease", {})
require(scope.get("authorizedBy") == "Professor", "prerelease authority drift")
require(scope.get("sourceMustEqualCastSource") is True, "prerelease source must equal CAST source")
require(scope.get("overwriteExistingTag") is False, "release tags must be immutable")
require(scope.get("stableReleaseAuthority") is False, "stable release authority must remain false")
require(scope.get("productionSigningAuthority") is False, "production signing authority must remain false")
require(scope.get("crownAuthority") is False, "Crown authority must remain false")

for token in (
    "workflow_dispatch:",
    "releaseTag:",
    "publishPrerelease:",
    "Prepare GitHub Release assets",
    "LuHmOS-AndroidWeb3-",
    "arm64-v8a.apk",
    'sha256sum "$NAME" > "$NAME.sha256"',
    "actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093",
    "publish-prerelease:",
    "contents: write",
    'gh release create "$RELEASE_TAG"',
    '--target "$SOURCE_REF"',
    "--prerelease",
    "release tag already exists; refusing overwrite",
):
    require(token in workflow, f"GitHub prerelease workflow missing: {token}")

require("pull_request:" not in workflow, "release/build workflow must not auto-run on pull requests")
require("Stage private LAN install bundle" not in workflow,
        "Android Web3 release workflow must not stage legacy LAN install bundle")
require("luhm-os-s24fe-lan-install" not in workflow,
        "Android Web3 release workflow must not upload legacy LAN artifact")
require(workflow.count("contents: write") == 1,
        "write permission must be scoped to the single prerelease publication job")
require("forgeCastGate.py" in workflow, "build workflow must invoke Forge CAST gate")
require("inputs.sourceRef" in workflow, "workflow must bind exact sourceRef input")

status = "GREEN_ROOTED_TERMUX_GITHUB_PRERELEASE_SOURCE_READY" if not errors else "RED_ROOTED_TERMUX_GITHUB_PRERELEASE"
print(json.dumps({
    "schema": "luhm-os.rooted-termux-github-prerelease-audit.v1",
    "status": status,
    "errors": errors,
    "build": "PENDING_FRESH_CAST",
    "githubPrerelease": "PENDING_FRESH_CAST",
    "rootedVirginInstall": "PENDING_DEVICE",
    "crownStatus": "STOP"
}, indent=2))
sys.exit(0 if not errors else 2)
