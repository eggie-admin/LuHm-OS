#!/usr/bin/env python3
"""Static tests only. Never builds, signs, notarizes or publishes a Mac package."""
from pathlib import Path
import subprocess
import re

root = Path(__file__).resolve().parents[1]
script = root / "tools/mac-companion-release.sh"
text = script.read_text(encoding="utf-8")
checks = [
    "RED_REQUIRES_MACOS",
    "RED_DIRTY_SOURCE",
    "RED_HEAD_DRIFT",
    'git archive "$sourceRef"',
    'art.eggiebagelface.luhmos.companion',
    "RED_PRIVATE_ASSET_SOURCE",
    'codesign --verify --deep --strict',
    'xcrun notarytool submit',
    'xcrun stapler validate',
    'RED_NOTARIZATION_NOT_ACCEPTED',
    '"publicDistribution":False',
    '"deviceLaunchProven":False',
    '"crownStatus":"STOP"',
    'luhm-os-companion.dmg',
    'luhm-os-companion.app',
]
# Repository artifact slugs are lowercase kebab-case. Machine names are camelHump.
# Status sentinels and external platform-required environment variables are DRAGONTAIL.
assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*\\.dmg", "luhm-os-companion.dmg")
if 'LuHm-OS-Companion.dmg' in text or 'LuHm OS Companion.app' in text:
    raise SystemExit("RED_NONKEBAB_ARTIFACT_NAMESPACE")
if re.search(r"\\b(source_ref|godot_bin)\\b", text):
    raise SystemExit("RED_NONCAMEL_MACHINE_NAMESPACE")
missing = [term for term in checks if term not in text]
if missing:
    raise SystemExit("RED_MAC_COMPANION_GUARD_MISSING:" + ",".join(missing))
for forbidden in ("gh release create", "git push", "fdroid publish", "curl --upload"):
    if forbidden in text:
        raise SystemExit("RED_UNAUTHORIZED_UPLOAD:" + forbidden)
subprocess.run(["bash", "-n", str(script)], check=True)
subprocess.run(["bash", str(script), "--self-test"], check=True)
bad = subprocess.run(["bash", str(script), "nope", "/tmp"],
                     capture_output=True, text=True)
if bad.returncode == 0 or "RED_SOURCE_SHA" not in bad.stderr:
    raise SystemExit("RED_FAIL_OPEN_SOURCE_REF")
print("MAC_COMPANION_SOURCE_AUDIT=GREEN; MAC_DMG=NOT_BUILT")
