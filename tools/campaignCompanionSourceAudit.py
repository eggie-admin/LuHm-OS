#!/usr/bin/env python3
"""Fast fail-closed source check only; does not verify an actual APK or signing identity."""
from pathlib import Path
from xml.etree import ElementTree as ET
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "androidCampaignCompanion"
APP = "art.eggiebagelface.luhmos.campaignpreview"
checks = {}

def check(name, condition):
    checks[name] = bool(condition)
    print(("PASS " if condition else "FAIL ") + name)

def txt(path):
    return (ROOT / path).read_text(encoding="utf-8")

try:
    gradle = txt("androidCampaignCompanion/app/build.gradle.kts")
    main = txt("androidCampaignCompanion/app/src/main/java/art/eggiebagelface/luhmos/campaignpreview/MainActivity.java")
    manifest = txt("androidCampaignCompanion/app/src/main/AndroidManifest.xml")
    page = txt("publicationSite/index.html")
    guide = txt("androidCampaignCompanion/README.md")
    ET.fromstring(manifest)
    check("packageDistinctFromGodotBeta", gradle.count('applicationId = "' + APP + '"') == 1 and 'applicationId = "art.eggiebagelface.luhmos.beta"' not in gradle)
    check("assetsFromExistingPublicSite", 'rootProject.file("../publicationSite")' in gradle and "<!doctype html>" in page.lower())
    check("androidAssetLoader", "WebViewAssetLoader" in main and "appassets.androidplatform.net" in main and "allowFileAccess(false)" not in main and "setAllowFileAccess(false)" in main)
    check("userGestureMedia", "setMediaPlaybackRequiresUserGesture(true)" in main)
    check("noCleartext", 'android:usesCleartextTraffic="false"' in manifest)
    check("notSignedOrAutoDeployed", "signingConfig" not in gradle and "signingConfigs" not in gradle)
    check("developmentStatusTransparent", "not a signed apk" in guide.lower() and "interim fallback" in guide.lower())
    check("notGodotWorkflow", "samsung-lite-signed-beta" not in gradle)
except (OSError, ET.ParseError, ValueError) as exc:
    check("allInputsReadableAndValid", False)
    print(type(exc).__name__, file=sys.stderr)

print(f"COMPANION_SOURCE_{'PASS' if checks and all(checks.values()) else 'FAIL'}_NOT_SIGNING_OR_DEVICE_PROOF")
raise SystemExit(0 if checks and all(checks.values()) else 1)
