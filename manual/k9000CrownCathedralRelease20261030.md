# Crown Cathedral release acceptance | source candidate

This is **not** a public F-Droid release or a signed APK. Upstream package: `art.eggiebagelface.luhmos.cathedral` (separate from all existing testing/beta package identities). App: **LuHm-OS: Crown Cathedral**. Internal K9000 cockpit remains **offline-first** and does not bundle a Google AI Edge Gallery app or any AI model.

## Hardware → system → WebView → published APK
1. Linux Mint studio kernel: preserve a supported distribution kernel and proprietary driver compatibility. Run `python3 tools/k9000HostReadiness.py` locally before deciding on kernel/sysctl changes. Do not claim security values without host evidence. GParted is an **operator-only GUI tool**, never a WebView, unattended libparted, elevated API, or APK dependency.
2. Development layer: Godot 4.7.2, pinned Android SDK 36, pinned Gradle toolchain, JDK 17, Python 3. Camera and scanner packages are host opt-ins. Installation never occurs from an app feature screen.
3. Android: preserve GKI/KMI, locked vendor boot chain, local `WebViewAssetLoader`, typed exact-origin bridge and denial of arbitrary URL and shell commands. Second-screen status may enumerate Android-attached displays; Tab A8 is a distinct remote companion and requires separate consent-based pairing or an owner-approved wired display.
4. Edge AI: Google Edge Gallery and LiteRT-LM are Apache-2.0 upstream components, **but a model is not implicitly free software**. No model, proprietary accelerator, or APK-to-APK headless API is bundled or assumed. Native integration requires source/libraries/license checks and real memory/thermal tests before enabling.
5. Public F-Droid: GPL-3.0 source, all library+engine+plugin licenses, source rebuild recipe, deterministic/icon artwork provenance, clean-room public assets, upstream tag, fastlane text+icon+screenshots, tested application ID/versionCode, signing strategy, and real device smoke are required. No publish until all gates receive evidence. F-Droid maintainers must accept an upstream submission or metadata MR.

### Open blockers (must not be hidden)
- No Android build for this candidate SHA yet, and macOS DMG not yet built/notarized.
- Existing public source tree contains references to historical/private content and unverified art provenance. An explicit **release-asset whitelist and license ledger** is required before public compilation.
- F-Droid build reproducibility, release keystore continuity, real Samsung install/update proof, icon raster, accessibility/screenshots, and any model/backend integrations are pending.
- Existing company-wide quarantine and Crown STOP remain in force. No automated signing, upload, unquarantine or mainline promotion.
- Private canonical hardware document ACL has an unrestricted editor permission; source cannot cure this. Owner ACL repair remains a separate security action.

## Current safe developer commands
`python3 tools/k9000HostReadiness.py` (on the studio Linux host, reads only)
`python3 tools/k9000PublicReadiness.py` (source snapshot, no devices/network)
`python3 tools/k9000CandidateAudit.py` (K9000 static controls)
`LUHM_SOURCE_REF="$(git rev-parse HEAD)" python3 tools/hardSystemAudit200.py` (200 core source controls)

F-Droid background: https://fdroid.gitlab.io/jekyll-fdroid/docs/Submitting_to_F-Droid_Quick_Start_Guide/
