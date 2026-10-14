# Samsung Tab S10 Lite (SM-X400) public beta runway

## 100. Fastest distribution path
Use the existing Professor CAST bridge and verified Android build. A public GitHub
prerelease can hold an ARM64 debug APK + SHA256 today, but its generated disposable
debug certificate changes per build. Label such artifacts **developer preview /
first-install only**, not persistent public beta or production release. Existing
GitHub Releases are historical, not current-code or current-device proof.

## 200. Non-root tablet verification
From the exact source checkout on Ubuntu with Python 3, Android platform-tools,
aapt and apksigner installed, connect one SM-X400 via authorized USB debugging.

Run source preflight:
python3 tools/samsung-lite-beta.py

Observe the tablet without installing:
python3 tools/samsung-lite-beta.py --tablet

With the exact locally downloaded and SHA-256-verified debug APK:
python3 tools/samsung-lite-beta.py --source-ref FULL_40_CHAR_SHA --apk ./candidate.apk --expected-sha256 FULL_64_CHAR_SHA

Opt-in install and request launch:
python3 tools/samsung-lite-beta.py --source-ref FULL_40_CHAR_SHA --apk ./candidate.apk --expected-sha256 FULL_64_CHAR_SHA --install

Never use the old rooted installer for public beta devices. This tool does not
uninstall, clear data, use root, change device settings or publish logs.
Certificate mismatch fails instead of erasing app data.

## 300. Public beta (updatable, not disposable)
One owner-held stable **beta** signing identity is needed. Keep keystore material
off Git history and out of ChatGPT. Beta should have a new isolated package ID
or a deliberate first-time migration from the old .testing package. Increment
versionCode per build, verify APK certificate + identity + checksum, install and
update on SM-X400, inspect actual WebView/Godot touch, rotation and app resume.
Only after privacy/art rights review and the Professor's exact artifact approval
should a GitHub Release be labeled as a public beta. GitHub Release downloads
do not automatically update Android apps.

## 400. Follow-on stores
F-Droid and Google Play submission require their own signing, policy, metadata
and approval tracks. Neither is a prerequisite for publishing an honest
GitHub developer preview. A screenshot, CI report, and CAST source build do not
prove the actual installed app or beta upgrade continuity.
