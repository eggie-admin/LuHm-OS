# K9000 dual-platform candidate | 2026-10-30

**Status: source-only candidate.** One Godot 4.7.2 game/studio tree; Android APK and macOS DMG as **parallel targets**. No APK/DMG install, AI runtime, UVC stream, Apple notarization, or device compatibility is claimed by this change. Existing protected `main`, owner signing, source checks, and human Crown are unchanged.

## Scope order
1. **Jacob Creator:** first MVP, family-safe art/world-making workstation, original or appropriately licensed assets, no mature character pack or automatic cloud upload. Age and permissions are not inferred; use parent-managed storage/sharing defaults.
2. **Professor Studio:** second profile/edition, separate signed package and private rights-cleared adult gothic character assets; never toggle into it from Jacob's install.
3. **Faith & Blocks:** third family-safe independent voxel/creative-themed pack around build, explore, learn, serve and belong. Do not redistribute Minecraft binaries/assets or imply Mojang endorsement. If it becomes a Minecraft mod, distribute only permitted original mod files and follow the Minecraft EULA and usage guidelines.

## Architecture and 'kernel hardening'
- **Mainline kernel means app/orchestration architecture, not patching Samsung's Linux kernel.** Keep the stock signed Android kernel, sandbox, SELinux and OTA update path. No rooting, privileged daemon, shell bridge, unsigned kernel or untrusted drivers.
- Common Godot scene/creative logic is source of truth. Android is one fullscreen local WebView overlay plus explicit allowlisted Godot bridge. macOS is the same Godot project with an initial native K9000 desktop overlay and a DMG export. Visual parity and all device adapters remain open product tasks.
- Native USB inventory is **read-only enumeration**. Camera preview, user USB permissions, Camera2 fallback, AUSBC adapter, audio sync and six-camera USB bandwidth testing are separate milestones. Never silently record.
- Edge Gallery is a reference app, not a proven headless service. Use a self-contained LiteRT-LM adapter only after licensing/model compatibility, RAM, thermals and offline behavior pass actual tests.
- Screens are family-safe by default. Character sigil is a placeholder, not an approved asset or an AI-connected avatar.

## Developer build tracks in parallel
**Android:** reuse the existing Gradle-built `AndroidWeb3Cockpit` plugin and the owner-gated Android source/test/signed-beta workflows. Do not bypass source SHA, signer pin, explicit owner CAST or private-asset firewall to get an APK.

**macOS:** add the `macOS K9000 Candidate` export preset to the existing Godot project and run `tools/buildK9000MacCandidate.sh` on a Mac with Godot **4.7.2** and matching templates. Its output is local **development-only** DMG, not automatically distributed. A public DMG requires Developer ID signing, hardened runtime, notarization/stapling and Mac smoke evidence.

**Audit:** `LUHM_SOURCE_REF=$(git rev-parse HEAD) python3 tools/hardSystemAudit200.py` for the existing 200 controls; `python3 tools/k9000CandidateAudit.py` for K9000-specific source checks. The proposed CI workflow executes read-only checks on the candidate branch; it does not build, sign or release.

## Research decisions and live gaps
- Godot 4.7.2 macOS exports support Universal 2 and DMG **on macOS hosts**: https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_macos.html
- Android Godot plugins require a custom Gradle build: https://developer.android.com/games/engines/godot/godot-export
- Google LiteRT-LM cross-platform inference: https://developers.google.com/edge/litert-lm/overview
- AUSBC Apache-2.0 UVC multi-camera candidate: https://github.com/ernestp/AndroidUSBCamera
- Android external USB camera HAL is device/OEM dependent: https://android.googlesource.com/platform/docs/source.android.com/+/080e50de3cb31822de0ba5b649e11924086b7817/en/devices/camera/external-usb-cameras.md
- Apple Developer ID hardening/notarization: https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution
- Minecraft community usage: https://www.minecraft.net/en-us/usage-guidelines

## Proof plan
1. Static syntax/security smoke + preexisting 200 audit at exact candidate commit.
2. Native Android: WebView local-only navigation; camera inventory on actual Samsung; permissions prompt/denial; USB plug/unplug; 1, 2, then 6 streams; power, thermal, dropped frames.
3. macOS: Godot launch, fullscreen UI parity, USB/AVFoundation discovery, ad-hoc test DMG, original art intake; separate Developer ID signing/notarization.
4. Shared creative: Godot scene launch, asset source restrictions, offline mode, export integrity, parent-managed controls; then per-edition content and regression.
5. Record actual receipts and blockers. Do not count source checks as device/build/release proof.

**Rollback:** revert the candidate commit or switch back to protected main. No release identity or signing credential changes are proposed here.
