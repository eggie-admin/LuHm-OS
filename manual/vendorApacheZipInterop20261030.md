# LuHm-OS vendor-first Apache readiness and Python/Java ZIP interoperability

**Research/source candidate, October 30, 2026.** No blanket relicensing; no package release, device proxy, signing, new OAuth, VM deployment or agent resumption. Crown STOP.

## The license boundary is not negotiable by changing a label

The present root LICENSE contains GPL-3.0 text. Both LuHm plugin manifests and the private npm tarball manifest explicitly declare GPL-3.0-only. Do NOT replace LICENSE or swap package SPDX fields to Apache-2.0 before copyright ownership, external contributions, generated code provenance and derivative works have been checked. Apache-2.0 code is usable in some GPLv3 projects, but the reverse direction cannot automatically be Apache-only. See https://www.apache.org/licenses/GPL-compatibility .

**Recommended approach:** an Apache-2.0-compatible *new first-party module* may be separated only when all authors and license obligations permit. Keep existing GPL game/runtime/plugin materials under their current terms until evidence and explicit approval. Retain unmodified third-party notices, license files and source obligations. Treat the browser and operating system as compatibility targets, not code to bundle, copy, or relicense. A public release needs an independently reviewed source and binary license closure.

## Vendor / operating-system ladder

- **Debian, Ubuntu, Raspberry Pi OS Lite:** open-source Debian-derived environments but mixed-package licenses and a Linux GPL-family kernel. Current official Raspberry Pi OS Lite is Debian 13-based, no desktop; 64-bit image and actual board/storage/firmware need verification. AOSP mostly uses Apache-2.0, yet includes GPLv2 Linux kernel sources and third-party components. Cannot make a whole OS Apache-only.
- **Firefox/GeckoView:** Mozilla engine and browser under MPL-2.0 and dependencies, not Apache-only. Compatibility first, do not bundle GeckoView without performance, APK size and notices review. Android WebView is already the first-party cockpit adapter.
- **Chromium:** open-source BSD-3 core with third-party bundled licenses. Google Chrome product differs from Chromium; browser must not be copied into K9000 binaries.
- **ChromiumOS / ChromeOS:** ChromiumOS is the open project; Google ChromeOS devices include Google/OEM integration. No presumption of portable 3D engine, native browser Java/USB access, or end-to-end Linux kernel replacement.
- **Samsung Internet / Samsung One UI:** proprietary vendor applications using Chromium/AOSP-related technology. Test standard web APIs and responsive UI only; do not modify Samsung system applications or vendor kernel. Tab S10 Lite desktop presentation must be DeX-inspired, not native DeX.
- **Safari / iOS / macOS:** proprietary user-facing Apple platforms; underlying WebKit contains LGPL-licensed and BSD components. The product can target Safari via HTML5 without bundling Apple's code. DMG/iOS signing and notarization are distinct owner gates.
- **Godot, Blender, FFmpeg, Python, OpenJDK:** Godot is generally MIT plus third-party notices; Blender GPL-family and FFmpeg builds may be LGPL/GPL; CPython uses PSF licensing; OpenJDK uses GPLv2 plus Classpath Exception. Keep heavyweight studio tools optional and host-side. Exact version, build flags and third-party dependencies must be recorded before distribution.
- **AI providers and model weights:** services are independent of bundled binaries. Model licenses, data rights, user entitlements and telemetry need per-adapter review. Preserve agent quarantine.

The machine-readable vendor ledger is at doctrine/vendorApacheReadinessV1.json. Every row is currently marked runtime installation UNVERIFIED, not falsely detected or preinstalled.

## Python ZIP → Java 17 / Gradle 8.13.2

Python zipfile on 3.14 adds ZIP_ZSTANDARD; Java/Android's standard ZipFile/ZipInputStream may not support that method. Use ZIP_DEFLATED with fixed UTC-safe ZIP date tuple, bounded file count, per-member size and ratio, no symbolic links or traversal, fixed permissions and a sorted first-party source allowlist. Do not extract archives with extractall or assume Base64url transport gives integrity. The ZIP and each entry need SHA-256, independent source commit identity and explicit application/content rights checks.

Now implemented:
1. Python ZIP generation: tools/fourPackageTrain.py build-dev produces a deterministic private DEV ZIP and receipt.
2. Python verification: tools/zipInteropAudit.py enforces size, timestamp, compression, member paths, count, duplicate names, anti-bomb ratio, non-symlink and per-file SHA-256 without extraction.
3. Android-side source: androidWeb3Plugin/plugin/src/main/java/art/eggiebagelface/luhmos/web3/ZipInteropInspector.java is a pure Java 17 ZipFile reader placed **inside the existing Gradle Android module source set**. It verifies an exact archive digest, canonical member prefix, deflate method, bounds and CRC without extracting or installing it. A GitHub runner compiles this Java file with javac and checks the actual Python ZIP. It is not an enabled WebView bridge or proof of an APK with an installed archive.
4. Existing Android build: AndroidWeb3Cockpit Gradle plugin retains Godot, Android WebKit, owner signing and exact-SHA CAST gates. Add a native UI file selector only after permission, storage-scope and lifecycle tests, with **no arbitrary ZIP execution**.

## Samsung Lite, antenna and proxies

The existing four-source cockpit contract is the user interface for Samsung and other supported platforms. A network proxy should be a capability-bound, authenticated HTTPS/MCP client for approved methods, not a raw local SQL daemon, exposed ADB, Bluetooth or unrestricted shell. The Linux host/Raspberry Pi can be a separately authorized camera/peripheral bridge only after camera enumeration, bandwidth/power receipts and access-control tests. Android host permissions, Shizuku grants, Apple browser sandboxes and Linux hardware interfaces remain separate.

## One Lum agent, many goddess roles

The desired combined agent should first be **one supervised request router** with bounded role labels (Lum coordinator, Skuld research, Urd security, Yume art, Belldandy provenance), not 15 autonomous background workers. Read-only source/capability probe first, then separate explicit authorization for any mutation, provider call or paid resource. Reuse canonical taskId/sourceRef/scopeId and the already-tested JSON + Base64url envelope with a decoded size limit; Base44 is an external app-building service, **not** a second encoding or encryption format. Persist only limited typed SQLite receipts; do not expose raw SQL or provider secrets in JavaScript. The entire 15-agent fleet stays QUARANTINED and Crown STOP.

## Verification

```bash
python3 tools/vendorApacheAudit.py
python3 -m unittest tests/testVendorZipInterop.py -v
python3 tools/fourPackageTrain.py build-dev
javac -d build/java-zip androidWeb3Plugin/plugin/src/main/java/art/eggiebagelface/luhmos/web3/ZipInteropInspector.java
```

The canonical GitHub workflow runs an actual Java reader against the generated ZIP, plus an intentional bad-digest test. This does not execute an Android/Gradle SDK app build or guarantee physical Samsung Lite OS / antenna communication.

Primary references:
- https://www.apache.org/licenses/GPL-compatibility
- https://source.android.com/docs/setup/contribute/licenses
- https://www.raspberrypi.com/software/operating-systems/
- https://www.mozilla.org/en-US/MPL/
- https://webkit.org/licensing-webkit/
- https://github.com/chromium/chromium/blob/main/LICENSE
- https://www.chromium.org/chromium-os/chromium-os-faq/
- https://docs.python.org/3/library/zipfile.html
- https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/zip/ZipInputStream.html
- https://developer.android.com/build/build-variants
