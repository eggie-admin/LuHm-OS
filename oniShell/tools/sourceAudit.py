#!/usr/bin/env python3
"""Dependency-free, fail-closed static checks for ONI SHELL source candidate."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

here = Path(__file__).resolve().parents[1]
root = here.parent
manifest = here / "app/src/main/AndroidManifest.xml"
ns = "{http://schemas.android.com/apk/res/android}"
doc = ET.parse(manifest).getroot()
assert not doc.findall("uses-permission"), "Unexpected Android permission"
app = doc.find("application")
assert app is not None and app.get(ns + "allowBackup") == "false"
assert app.get(ns + "usesCleartextTraffic") == "false"
activities = app.findall("activity")
assert len(activities) == 2
main = next(a for a in activities if a.get(ns + "name") == ".MainActivity")
cockpit = next(a for a in activities if a.get(ns + "name") == ".CockpitActivity")
assert main.get(ns + "exported") == "true"
assert cockpit.get(ns + "exported") == "false"
filters = main.findall("intent-filter")
assert any(any(c.get(ns + "name") == "android.intent.category.HOME"
               for c in item.findall("category")) for item in filters)
assert any(any(c.get(ns + "name") == "android.intent.category.LAUNCHER"
               for c in item.findall("category")) for item in filters)

gradle = (here / "app/build.gradle.kts").read_text()
assert 'applicationId = "art.eggiebagelface.luhmos.onishell"' in gradle
assert "targetSdk = 36" in gradle
assert '"../frontEnd"' in gradle
assert 'include("index.html", "styles.css", "app.js")' in gradle
source = (here / "app/src/main/java/art/eggiebagelface/luhmos/onishell/MainActivity.kt").read_text()
assert "RoleManager.ROLE_HOME" in source and "queryIntentActivities" in source
assert "requestHomeRole()" in source
bridge = (here / "app/src/main/java/art/eggiebagelface/luhmos/onishell/CockpitActivity.kt").read_text()
assert "WebViewAssetLoader" in bridge and "appassets.androidplatform.net" in bridge
assert "settings.allowFileAccess = false" in bridge
assert "settings.allowContentAccess = false" in bridge
assert "shouldOverrideUrlLoading" in bridge
assert not re.search(r"addJavascriptInterface|Runtime\.getRuntime|ProcessBuilder|exec\(", bridge)
assert (root / "frontEnd/index.html").is_file()
assert (root / "frontEnd/styles.css").is_file()
assert (root / "frontEnd/app.js").is_file()
workflow = (root / ".github/workflows/oni-shell-owner-signed.yml").read_text()
assert "workflow_dispatch" in workflow
assert "LUHM_BETA_SIGNING_P12_B64" in workflow
assert "apksigner" in workflow
assert not any(x in workflow for x in ("gh release create", "fdroid update", "fdroid publish",
                                       "git push", "pages: write"))
print("GREEN_ONI_SHELL_SOURCE_ONLY_STATIC_CHECKS")
print("NO_APK_BUILD_NO_SIGNING_NO_FDROID_INDEX_NO_DEVICE_PROOF")
