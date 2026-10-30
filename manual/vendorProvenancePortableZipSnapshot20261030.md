# Vendor-by-vendor hardening: provenance, portable ZIP and release evidence | 2026-10-30

**Scope:** source-only proposal stacked above CAST exit-development candidate #458. No GitHub APPROVED reviews were present on #452–#458 when checked; the branch uses #458 as the most recent integration tip, **not** as an approved production baseline. Main remains protected and untouched. Crown STOP.

## What changed

- The previous vendor census already distinguished GPL, MPL, BSD, AOSP, proprietary products and studio dependencies, but a source-level vendor class is not file-by-file redistribution provenance. This pass adds `doctrine/vendorProvenanceBoundaryV1.json` with **16 distinct vendor families**, upstream references, explicit unverified file-level provenance and no source copy/bundling claim.
- The current root `LICENSE` and declared LuHm plugin/npm license remain **GPL-3.0-only**. Three first-party **candidate** modules are recorded separately as potentially eligible for future Apache-2.0 licensing only after ownership, external contribution, derivative and counsel review. Current eligibility: **zero**. No notice or SPDX field changed.
- Python DEV ZIP and Java 17 Gradle-source reader now reject Windows reserved device names, alternate-data-stream syntax, nonportable names, trailing dots and case-insensitive aliases. Both retain ZIP_DEFLATED, size limits and exact archive SHA. The Java reader verifies archive SHA-256 and per-entry CRC, **not** independent per-entry SHA-256; the Python receipt computes each member SHA-256. Neither implementation extracts or installs the archive.
- Added adversarial Python tests and Java exact-digest hostile ZIP controls. Existing signed APK/AAR installation is **not** implied by compiling a Java source file from the Android Gradle module.
- New `tools/vendorProvenanceBoundaryAudit.py` binds its receipt to `git rev-parse HEAD`, refuses mismatched `LUHM_SOURCE_REF`, reuses the original GPL/vendor/npm census, and fails on false Apache readiness, third-party copying, runtime claims, Cloudflare changes, Base44 encoding claims or active Lum agents.

## Vendor ladder and license obligations

| Vendor or runtime | Current legal interpretation | Integration role |
| --- | --- | --- |
| Raspberry Pi OS Lite / Debian / Ubuntu | Mixed distro packages, GPL Linux kernel; exact package licenses and image SBOM govern | Optional headless edge; **no actual Pi/VM proof** |
| Firefox / GeckoView | MPL 2.0 and additional third-party notices; GeckoView has Stable/Beta/Nightly and Java 17 requirements | Optional Android browser engine; **not bundled** |
| Chromium | BSD-style upstream with substantial third-party licenses | Browser compatibility target |
| Samsung Internet | Proprietary Samsung browser based on Chromium technology | Browser compatibility only |
| Safari / WebKit | Safari proprietary; WebKit BSD and LGPL portions | Safari/iOS HTML5 compatibility only |
| ChromiumOS vs ChromeOS | Open-source OS versus proprietary OEM product/binary services; per-device license credits | OS compatibility targets, not redistributable images |
| Samsung One UI / AOSP | Samsung proprietary layers; AOSP predominantly Apache 2.0 with GPLv2 kernel and other exceptions | Stock Android system and WebView only |
| Apple iOS/macOS | Proprietary OS and signing toolchain, open components under their own licenses | WKWebView/Safari/DMG/iOS adapter candidate |
| CPython / Java 17 / Gradle | PSF and OpenJDK GPLv2 with Classpath Exception; Gradle/build dependencies have independent terms | DEV ZIP and APK/AAR source pipeline |
| Blender / FFmpeg / Godot 4 | GPL family; FFmpeg LGPL/GPL depending on build flags; Godot MIT plus third-party notices | Studio tools, not Apache-only imports |
| AI model/API vendors | Model-specific weights licenses, service terms and user data policies | Optional typed adapters; no model copied or cloud call |

## Device and proxy readiness

- Samsung Tab S10 Lite stock OS/build, browser version, USB/Bluetooth antenna and K9000 physical benchmark remain **UNVERIFIED**. Its UI is DeX-inspired, not native DeX. S24 FE antenna proxy and Tab A8 companion remain **UNVERIFIED**.
- Raspberry Pi model, power budget, network interface, Bluetooth controller, headless services and Debian 13 Trixie image remain **UNVERIFIED**. Raspberry Pi's official download page lists Oct 6, 2026 Debian 13 images, and a legacy Debian 12 stream. A downloadable image is not proof of installation.
- Remote VM running state, TLS certificate, Cloudflare Access/WAF/Tunnel, Netplan, Certbot and network topology remain **UNVERIFIED**. Existing Render direct managed-TLS path stays unchanged. No keys or DNS mutation.
- Base64url JSON is a bounded encoding envelope (45,056 decoded bytes), not encryption or authentication. Base44 is a separate external service, not a base-N encoding. Signed receipts require independent authenticated provenance.
- Lum coordinator remains a proposal with six role *views* and independent Urd review mapped onto the existing 15 quarantined roles. **Zero** agents activated. Do not infer rights to run shell, install software or approve one's own output.

## Reproducible archive contract

1. Sort and allowlist exact source paths, canonical ASCII names, fixed DOS ZIP timestamp (1980-01-01), fixed permissions, ZIP_DEFLATED only. No encrypted members, duplicate entries, symlinks, casefold aliases, Windows reserved names or path traversal.
2. Maximum 96 entries, 2 MB uncompressed per member, 6 MB total uncompressed and 6 MB archive, expansion ratio <= 200. Stream-read bounded chunks; never use untrusted `extractall` or `zipfile.Path` without name validation.
3. Bind the archive SHA-256 and per-file Python SHA-256 receipt to the reviewed exact Git SHA. The Java reader verifies whole-archive SHA and CRC; do not claim it verifies each file's SHA-256 independently.
4. Reproducibility means two builds with the same allowlist, source, timestamps, compression implementation and flags produce matching bytes. It is not guaranteed across different Python/zlib versions; verify in CI with exact pinned toolchains.

## Actual versus missing evidence

**Source (observed CI):** vendor provenance checks passed; 16 vendor families recorded; **61 npm transitive package entries had license metadata and zero lacked that metadata**. This is only manifest metadata, not verification of source license files, authorship, binary notices, or redistribution rights. Python ran 11 new provenance tests, 16 ZIP negative/positive tests and 12 existing package-train tests. Java 17 verified a real Python-generated 15-entry DEV ZIP against its correct archive SHA-256 and rejected four hostile archives even when their whole-archive SHA-256 was supplied correctly. No actual binary license closure, physical Android install, live antenna proxy, Pi boot, remote VM, signed AAR/APK or user-authorized Lum execution is proved.

**Next smallest safe action:** on the candidate exact commit, run the expanded vendor/ZIP workflow and capture its receipt; then inventory actual npm source license files and copyright holders by exact package version, without copying external code or changing the root GPL license. Only after owner-approved device testing should the Samsung Lite and antenna proxy become a runtime gate.

## Official primary sources reviewed October 30, 2026

- Raspberry Pi OS images (Oct 6, 2026): https://www.raspberrypi.com/software/operating-systems/
- Raspberry Pi OS documentation: https://www.raspberrypi.com/documentation/computers/os.html
- Mozilla MPL 2.0: https://www.mozilla.org/en-US/MPL/2.0/
- GeckoView integration: https://firefox-source-docs.mozilla.org/mobile/android/geckoview/consumer/geckoview-quick-start.html
- ChromiumOS licensing and per-device credits: https://www.chromium.org/chromium-os/licensing/
- ChromiumOS/ChromeOS distinction: https://www.chromium.org/chromium-os/chromium-os-faq/
- WebKit license file inheritance: https://docs.webkit.org/Other/Licensing.html
- AOSP license exceptions: https://source.android.com/docs/setup/contribute/licenses
- Python ZIP path safety: https://docs.python.org/3/library/zipfile.html
- FFmpeg legal and build flags: https://ffmpeg.org/legal.html
