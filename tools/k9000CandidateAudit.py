#!/usr/bin/env python3
"""K9000 source-only negative-gate audit; not a build, camera, or release receipt."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def audit_files(files):
    html, css, js, kotlin, presets, canon, readme = (files[k] for k in
        ("html", "css", "js", "kotlin", "presets", "canon", "readme"))
    desktop = files["desktop"]
    main = files["main"]
    checks = {
        "cspLocalOnly": "default-src 'none'" in html and "connect-src 'none'" in html,
        "noRemoteScript": 'src="https://' not in html and 'src="http://' not in html,
        "cathedralBrandMark": 'brand/k9000-cathedral-mark.svg' in html,
        "screensPanel": 'data-panel="screens"' in html and 'data-screen-probe' in html,
        "screenReadOnly": '"screen_probe_requested" -> setOf("type")' in kotlin and 'sendDisplayInventory()' in kotlin,
        "noMediaProjection": "MediaProjection" not in kotlin,
        "isolatedPublicPackage": 'package/unique_name="art.eggiebagelface.luhmos.cathedral"' in presets,
        "publicPreset": 'name="Android Crown Cathedral Public Candidate"' in presets,
        "testingIdentityPreserved": 'package/unique_name="art.eggiebagelface.luhmos.testing"' in presets,
        "singleUiEntry": '<title>K9000 | LuHm-OS: Crown Cathedral</title>' in html,
        "nativeScript": './k9000.js' in html and './k9000.css' in html,
        "familyFirst": "JACOB CREATOR · FAMILY SAFE" in html,
        "cameraScanLabeled": "USB/UVC discovery is read-only" in html,
        "noAutoCamera": "getUserMedia" not in js and "navigator.mediaDevices" not in js,
        "noFakeCameraCount": "NOT SCANNED" in html and "SCANNING..." in js,
        "noRawInnerHtml": ".innerHTML" not in js,
        "hardwareTab": 'data-panel="hardware"' in html and 'data-hardware-probe' in html,
        "canonPrivate": "COOLPIX B500" not in html and "Perfection V39 II" not in html,
        "hardwareProbeAllowlisted": '"hardware_probe_requested" -> {' in kotlin,
        "hardwareProbeReadOnly": "sendHardwareInventory()" in kotlin and "requestPermission(" not in kotlin,
        "usbNoSerials": "usb.serialNumber" not in kotlin and "getSerialNumber(" not in kotlin,
        "hardwareJsSecureText": 'hardwareList.replaceChildren()' in js and 'p.textContent = vendor' in js,
        "hardwareNoCapture": "getUserMedia" not in js and "scanimage" not in js,
        "nativeAllowlist": '"camera_probe_requested", "hardware_probe_requested" -> setOf("type")' in kotlin,
        "nativeLocalOnly": 'LOCAL_ORIGIN' in kotlin and 'isAllowedLocalUrl' in kotlin,
        "usbInventoryOnly": "USB_CLASS_VIDEO" in kotlin and "requestPermission(" not in kotlin,
        "androidK9000Default": 'k9000.html' in kotlin,
        "godotAndroidExisting": 'name="Android Proposed"' in presets,
        "macExportPreset": 'name="macOS K9000 Candidate"' in presets,
        "macUniqueBundle": 'application/bundle_identifier="art.eggiebagelface.k9000.candidate"' in presets,
        "macDevOnly": 'notarization/notarization=0' in presets,
        "macNativeCockpit": "K9000 macOS native cockpit candidate" in desktop,
        "macNativeWorldSignal": "signal world_requested" in desktop,
        "macMainBound": 'OS.get_name() == "macOS"' in main and 'k9000_desktop_shell.world_requested.connect(enterWorldMode)' in main,
        "canonSourceOnly": canon.get("status") == "PROPOSED_SOURCE_ONLY",
        "canonSourceAuthority": canon.get("sourceRepository") == "eggie-admin/LuHm-OS",
        "sharedGodot": canon.get("sharedEngine") == "Godot 4.7.2",
        "stockAndroidKernel": canon.get("kernel", {}).get("rootRequired") is False,
        "noAgentRelease": canon.get("gate", {}).get("crownStatus") == "STOP",
        "noAutoBuildRelease": canon.get("gate", {}).get("noAutomaticSign") is True,
        "familyNoAdultAssets": canon.get("profiles", {}).get("jacobCreator", {}).get("adultAssets") is False,
        "adultSeparate": canon.get("profiles", {}).get("professorStudio", {}).get("notBundledInJacob") is True,
        "minecraftUnbundled": canon.get("profiles", {}).get("faithVoxel", {}).get("minecraftAssets") == "NOT_BUNDLED",
        "edgeNotProven": canon.get("providers", {}).get("edgeGallery", {}).get("headlessServiceProven") is False,
        "uvcNotStreaming": canon.get("cameras", {}).get("streaming") == "NOT_IMPLEMENTED",
        "noFakeBuildProof": "No APK/DMG install" in readme,
        "noRemoteShell": "rootBridgeAllowed" in json.dumps(canon) and canon["kernel"]["rootBridgeAllowed"] is False,
    }
    return [key for key, ok in checks.items() if not ok]

def read_files():
    paths = {
        "html": "frontEnd/k9000.html", "css": "frontEnd/k9000.css",
        "js": "frontEnd/k9000.js",
        "kotlin": "androidWeb3Plugin/plugin/src/main/java/art/eggiebagelface/luhmos/web3/AndroidWeb3CockpitPlugin.kt",
        "presets": "export_presets.cfg", "canon": "doctrine/k9000DualPlatformCanonV1.json",
        "readme": "manual/k9000DualPlatformPlan20261030.md",
        "desktop": "scripts/k9000/k9000DesktopShell.gd",
        "main": "scripts/main.gd",
    }
    data = {k: (ROOT / path).read_text(encoding="utf-8") for k, path in paths.items()}
    data["canon"] = json.loads(data["canon"])
    return data

if __name__ == "__main__":
    failures = audit_files(read_files())
    if failures:
        raise SystemExit("RED_K9000_CANDIDATE_SOURCE " + ",".join(failures))
    print("GREEN_K9000_CANDIDATE_SOURCE 47/47 (SOURCE ONLY, no APK/DMG/device proof)")
