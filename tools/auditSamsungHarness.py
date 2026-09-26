#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "android" / "samsung-harness-source-audit.json"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


manifest = json.loads(read("doctrine/s24feCanaryAdminHarness-20260926.json"))
webview = read("native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/KAIWebView.kt")
profile = read("native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/SamsungSystemProfile.kt")
android_manifest = read("native/kaiwebview/kaiwebview/src/main/AndroidManifest.xml")
export = read("export_presets.cfg")

passes: list[dict[str, str]] = []


def green(name: str, detail: str) -> None:
    passes.append({"pass": str(len(passes) + 1), "name": name, "status": "GREEN", "detail": detail})


require(manifest["authority"] == "Professor", "authority drift")
require(manifest["sourceLaw"].startswith("AI proposes."), "source law missing")
green("source_authority", "Professor Crown and source law pinned")

require(manifest["target"]["baseline"].startswith("Samsung S24 FE"), "target baseline drift")
require(manifest["target"]["sideBySide"] is True, "harness must remain side-by-side")
green("project_scope", "S24 FE-class Samsung harness isolated from production identity")

require(manifest["donor_policy"]["strategy"].startswith("selective transplant"), "donor policy too broad")
require(len(manifest["donor_policy"]["sources"]) >= 3, "donor receipts incomplete")
green("donor_provenance", "legacy donors are reference/selective-transplant only")

for package in (
    "com.chrome.canary",
    "com.google.android.webview.canary",
    "com.google.android.webview",
):
    require(package in android_manifest, f"missing package visibility query: {package}")
require("WebView.getCurrentWebViewPackage" in profile, "current WebView provider probe missing")
green("canary_provider_matrix", "Chrome/WebView channels are detected without replacing the OS provider")

require("WebViewAssetLoader" in webview, "WebViewAssetLoader missing")
require("WEB_MESSAGE_LISTENER" in webview, "typed WebMessage listener missing")
require("appassets.androidplatform.net" in webview, "local asset origin missing")
for forbidden in (
    "addJavascriptInterface",
    "MIXED_CONTENT_ALWAYS_ALLOW",
    "allowUniversalAccessFromFileURLs",
    "allowFileAccessFromFileURLs",
):
    require(forbidden not in webview, f"unsafe WebView primitive present: {forbidden}")
green("webview_origin_boundary", "packaged appassets origin and typed bridge only")

require("isManagedProfile" in profile, "managed-profile detection missing")
require("isDeviceOwnerApp" in profile and "isProfileOwnerApp" in profile, "owner-state detection missing")
require(manifest["capability_ladder"][1]["description"].find("no cross-profile bypass") >= 0, "Secure Folder/profile bypass rule missing")
green("profile_and_secure_folder_boundary", "profile isolation is observed, never bypassed")

require(manifest["capability_ladder"][2]["silentProvisioning"] is False, "silent admin provisioning forbidden")
require(manifest["capability_ladder"][2]["gameApkSelfPromotesToOwner"] is False, "game APK cannot self-promote")
require(manifest["termux_admin_model"]["termuxCannotBecomeAndroidAdminByLogin"] is True, "Termux admin-login myth reintroduced")
green("admin_rights_boundary", "Android Enterprise owner state is explicit and externally provisioned")

combined = "\n".join((webview, profile, android_manifest, json.dumps(manifest)))
for forbidden in (
    "Runtime.getRuntime().exec",
    "ProcessBuilder(",
    "setenforce 0",
    "supersu",
    "magisk --",
    "android.permission.INSTALL_PACKAGES",
    "android.permission.MANAGE_EXTERNAL_STORAGE",
    "android.permission.REQUEST_INSTALL_PACKAGES",
):
    require(forbidden not in combined, f"privilege expansion found: {forbidden}")
require(manifest["capability_ladder"][3]["webviewBridgeToRoot"] is False, "root bridge must remain disabled")
green("root_and_privilege_boundary", "root is lab-only; no su/SELinux/admin bypass exists in APK")

require("permissions/internet=false" in export, "APK internet permission must remain disabled")
require(manifest["hardening"]["publicListener"] is False, "public listener forbidden")
green("network_and_secret_boundary", "no Internet permission or public service lane in the APK")

require(manifest["green_gate"]["apkBuild"] == "REQUIRED", "APK build proof not required")
require(manifest["green_gate"]["apkSignature"] == "REQUIRED", "signature proof not required")
require(manifest["green_gate"]["zipalign"] == "REQUIRED", "zipalign proof not required")
green("receipt_and_release_gate", "runtime GREEN requires deterministic APK and device receipts")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(
    json.dumps(
        {
            "schema": "luhm-os.samsung-canary-admin-harness-audit.v1",
            "status": "GREEN_SOURCE",
            "passes": passes,
            "runtime": "DEVICE_PROOF_PENDING"
        },
        indent=2,
    ) + "\n",
    encoding="utf-8",
)
print("SAMSUNG HARNESS 10-PASS SOURCE AUDIT GREEN")
