# LuHm OS: virgin-install debugging entry point

This lane reuses existing Godot, Android WebView, jQuery, plugin, release-boundary,
and exact-installed-APK checks. It does not compile another APK or change production
signing. It is a first-run debugger, not a migration or publication process.

## 100. Diagnose checkout (Linux/Codespaces)

From the repository root:

```bash
python3 tests/test-debug-readiness.py
python3 tools/debug-readiness.py
```

The latter writes `build/debug-readiness/receipt.json`. Python 3, Node.js and
a git checkout are required. Nonzero exit marks failed checks. Read
`failedChecks`, `failureKind`, and the relevant existing audit directly.
The aggregate packet hashes command output but never uploads raw process logs.

## 200. Obtain exact build evidence

Use the existing owner-authorized Android CAST flow (see
`manual/finalGoalAndroidInChat.md`). Use the **same** GitHub Actions
artifact's complete 40-character source SHA and 64-character APK SHA-256,
not a historical manifest SHA. Check the APK locally before installation.
A CI success is not an installed-device receipt.

## 300. Debug one USB-connected Samsung

Install Android platform-tools and enable developer USB debugging.
Authorize this workstation on the device. Connect exactly one device.
If an APK already exists, preserve app data until you decide otherwise.
Run from the exact source checkout corresponding to the APK:

```bash
python3 tools/debug-readiness.py --source-ref FULL_40_CHAR_SOURCE_SHA --device --expected-apk-sha FULL_64_CHAR_APK_SHA256 --launch
```

The existing read-only collector examines `pm path`, installed `base.apk`
SHA-256, package version and Android API; it requests a launcher start only
after the installed APK matches. Results are saved under
`build/debug-readiness/`. No root, uninstall, app-data deletion, or
device settings mutation. A mismatched disposable debug certificate needs
a deliberate decision before reinstalling, not an automatic wipe.

## 400. Reproduce and repair

- **Source check RED:** run the named tool directly, repair the exact failure, rerun the aggregator.
- **No ADB device:** check USB permission, phone authorization and `adb devices`.
- **APK mismatch:** verify downloaded artifact/checksum, inspect package identity and debug signer.
- **Launch accepted but blank UI:** capture a limited local `adb logcat` trace
  using your workstation; review it before sharing, because logs can contain secrets.
- **WebView failure:** inspect `androidWeb3Plugin`, `frontEnd/`, jQuery smoke, and JS console.
- **Godot scene failure:** reproduce with `tools/runGodotSmoke.py` and the existing Godot CI lanes.
- **ChatGPT cockpit failure:** distinguish reachable Render MCP from actual ChatGPT host tool discovery.

The CI artifact is a source diagnostic packet only. An installed APK still
requires actual visual and touch evidence. Beta, public release and Crown
remain separate milestones.
