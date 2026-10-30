# LuHm-OS: ONI SHELL

A reversible, independently installable Android HOME launcher for the Professor's Samsung Galaxy Tab S10 Lite (SM-X400). Native Kotlin/Android UI, magenta/cyan cyber-goth deck, searchable real installed apps, and a local WebView viewer of the **existing** ../frontEnd LuHm cockpit.

**State:** SOURCE-ONLY candidate. No APK has been compiled, signed, published or installed, and no F-Droid repository exists by virtue of this source.

## What works in source

- Real Android Home role (Android 10+) requested on tap, never silently acquired.
- Apps are listed through `ACTION_MAIN` + `CATEGORY_LAUNCHER` and launched through explicit Android intents; scoped `<queries>`, no `QUERY_ALL_PACKAGES`.
- Clock, battery, responsive 4/6-column app grid, text filter, Settings shortcut.
- Local-only cockpit served through AndroidX `WebViewAssetLoader` with host/path checks. No `INTERNET` permission, bridge to Termux, embedded API keys or remote JavaScript.
- Original One UI status bar, recents, lock screen and Quick Settings remain owned by Samsung. This is a **launcher**, not firmware, SystemUI, root overlay or a ROM.
- New package ID `art.eggiebagelface.luhmos.onishell`, separate from both existing `.testing` and `.beta` packages.

## Build / private signed candidate

From the canonical LuHm-OS checkout and a trusted Linux/Android Studio machine, install JDK 17, SDK 36 and Gradle 8.13. Run:

```bash
python3 oniShell/tools/sourceAudit.py
gradle -p oniShell :app:assembleDebug
```

Local debug is only for testing. **Never use a disposable debug-signed build as an updatable F-Droid release.**

For an owner-signed release candidate, after approving and merging source to main, use GitHub Actions workflow `.github/workflows/oni-shell-owner-signed.yml`. It requires explicit manual `cast` and exact main commit SHA and uses the existing `LUHM_BETA_SIGNING_P12_B64`, `LUHM_BETA_SIGNING_PASSWORD`, `LUHM_BETA_SIGNING_ALIAS`, `LUHM_BETA_SIGNER_SHA256` secret names already prescribed by the canonical Samsung owner-signed beta lane. Reusing the same long-lived owner certificate for a **different package ID** is allowed by Android but creates shared key risk. Do not create or rotate keys automatically, and do not proceed if the existing certificate was lost or compromised. The workflow fails closed on missing credentials or signer mismatch. It does not publish an APK.

The exact signed output is an access-controlled GitHub Actions artifact `oni-shell-owner-signed-candidate` containing the APK, hash, signature proof, and a source-bound receipt. Approval of this candidate is **not** automatic production release.

## F-Droid installation

Follow [fdroid/README.md](fdroid/README.md). A valid F-Droid install requires an owner-signed APK, **separately signed F-Droid repository index**, actual HTTPS hosting and verified repository fingerprint. GitHub repository ownership alone never signs apps or F-Droid indexes. The default F-Droid.org catalog is a different distribution process; this project targets a **custom F-Droid client repository**.

After the index exists, add its authenticated HTTPS repo URL to F-Droid on the tablet once, then install/update ONI SHELL from there. Nothing will appear in F-Droid before this setup is complete.

## Default Home / rollback

After installing a reviewed build, open ONI SHELL and tap **SET AS HOME**. Android presents a system-controlled selector. To revert, go to Samsung **Settings → Apps → Choose default apps → Home app → One UI Home**. Do not uninstall or disable One UI Home and do not clear tablet data.

## Future only

Optional notification controls, wallpaper browsing, widgets, Termux service integration, Shizuku, desktop taskbar, Samsung DeX-style windowing and root overlays require separate designs/permissions and device proof. No privileged system execution is implied.

**Proof law:** source staged ≠ APK built ≠ signer verified ≠ index signed ≠ URL live ≠ SM-X400 installed and updated.
