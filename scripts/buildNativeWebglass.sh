#!/usr/bin/env bash
set -euo pipefail
# The caller stages cockpit assets and extracts the pinned Android template first.
if python3 tools/moduleBuild.py restore; then
  exit 0
fi
android/build/gradlew -p native/kaiwebview :kaiwebview:assembleDebug :kaiwebview:assembleRelease --no-daemon
mkdir -p addons/kai_webview/bin
cp native/kaiwebview/kaiwebview/build/outputs/aar/kaiwebview-debug.aar addons/kai_webview/bin/kaiwebview-debug.aar
cp native/kaiwebview/kaiwebview/build/outputs/aar/kaiwebview-release.aar addons/kai_webview/bin/kaiwebview-release.aar
python3 tools/moduleBuild.py save
