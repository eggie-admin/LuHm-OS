# LuHm OS | Final APK and full-project proof checklist

Canonical release boundary: `doctrine/finalFormPublicReleaseGateV1.json`.  
Hardening truth: `doctrine/finalGoalHardeningV1.json`.  
Cross-layer source audit: `python3 tools/finalGoalHardeningAudit.py --self-test`.

## Exact-head Android build

Use the existing Professor-authored `/cast androidProposedDebug <currentMain40Sha>` on a LuHm GitHub pull-request discussion or authorized direct workflow dispatch. This creates a **private GitHub Actions debug artifact**. It never signs or publicly releases a stable application.

Retrieve the artifact, verify its archive CRC, `sha256.txt`, `apksigner verify --verbose --print-certs`, `aapt dump badging`/manifest targetSdk, applicationId, version and ARM64 payload. Preserve the full 40-character source SHA and APK SHA-256 in the artifact packet. Every new build changes the expected APK hash; never use an earlier build's SHA-256 to claim the current app is installed.

## Non-root Samsung device artifact proof

On an authorized workstation with ADB and an unlocked, USB-debug-enabled Samsung:

```bash
python3 tools/captureAndroidProof.py --self-test
python3 tools/captureAndroidProof.py --capture --launch --source-ref CURRENT_BUILD_SOURCE_SHA --expected-sha256 SHA256_FROM_THAT_APK
```

Use exact 40/64 hexadecimal strings in place of these two placeholders. The probe reads `pm path`, installed `base.apk` SHA-256, package version, API level, and issues a foreground launch request only when the bytes match. It never captures private screen data, changes device settings, enables root, grants permissions, or proves successful on-screen gameplay. Physical screen and touch proof remain separate receipts.

## Stable public distribution

The `.testing` APK and disposable GitHub signer do **not** form the final production application. Final release requires a separately specified stable application identity, owner-controlled release certificate/keystore, reproducible non-debug build, signed update compatibility, reviewed asset rights/privacy, signed F-Droid index or approved store package, exact APK digest, actual installed Samsung behavior, and Professor's exact-artifact approval.

No release signing secret belongs in GitHub source, ChatGPT prompts, Cloudflare DNS or Android APK assets. `tools/publicDistributionGate.py` is a preflight, not a release or publication command.

## ChatGPT and Godot

The LuHm plugin ZIP can be built in GitHub Actions; it is not ChatGPT-host-installed until the actual current-chat `luhm_open_cockpit` tool call and UI mount are observed. Godot HTML/WASM/PCK exports and Render LIVE receipts prove source hosting and build, not touch gameplay. Each has its own independent final-form gate.

## Canon status

`SOURCE_GATES_GREEN` and `CI_GREEN` never imply `PUBLIC_RELEASE_GREEN`. All 15 registered Oni remain operationally quarantined. Professor retains the Crown. No automatic provider spend, private Tunnel, production signing, store submission, asset publication, or runtime proof fabrication.
