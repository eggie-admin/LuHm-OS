# LuHm-OS | 4×4 Canon-aligned thin-client skeleton (proposed)

**Scope:** Samsung/Android client source architecture, preserving existing vendor OS and Linux studio contracts. **Status:** `PROPOSED_SOURCE_ONLY`, not installed/verified/crowned.  
**Source baseline:** main `f0cb6ee54066b490c0e80efc2c96200fec76ee2d`. Candidate CI must bind to the proposal's actual head SHA.

## The sanest architecture, kernel upward

| Layer | Source / role | Runtime rule | What remains unproven |
| --- | --- | --- | --- |
| 0. Silicon + boot + vendor firmware | Existing Samsung device, platform drivers and secure boot | **Inherit; do not flash, root, or write firmware** | Physical device state, actual firmware revision and trust chain |
| 1. Kernel + host OS | Samsung Android/Linux GKI/KMI/vendor modules; optional Linux server inherits its own host kernel | **No custom LuHm kernel, no wholesale driver/vendor replacement** | Measured kernel integrity, module ABI, patches and boot |
| 2. Android + native app | `project.godot`, `scenes/Main.tscn`, `export_presets.cfg`, `AndroidWeb3Cockpit` plugin | ARM64, Godot GL Compatibility, System WebView and local assets | Real APK dependency inventory, signer, frame time, device install |
| 3. Minimal cockpit | `frontEnd/index.html`, `frontEnd/app.js`, local jQuery 3.7.1 and CSS | Display and typed messages; no secrets, raw SQL or shell privilege | Physical touch, interaction and lifecycle tests |
| Optional off-device studio | Python 3 stdlib/SQLite headless; heavyweight `.devcontainer/Dockerfile` | Blender/Godot/FFmpeg/GIMP/npm/NGINX/MariaDB **only when a host job requires them** | Job/service permissions and optional live provider connectivity |

The executable shell is **not** a custom BIOS, chipset layer, GRUB replacement, kernel distribution, or emulation host. The source does not build a custom 64-bit kernel. Android owns drivers, signing policy, security updates, process scheduling and memory protection. Godot owns interactive 3D/gameplay; jQuery organizes nonprivileged widgets. Google/Meta/Samsung integrations are separate optional services and **must not become a required proprietary dependency of the offline app**.

## The existing software we actually keep

- **Android:** `art.eggiebagelface.luhmos.testing` is the debug/test source preset; owner-signed `art.eggiebagelface.luhmos.beta` remains a separately gated beta. Do not silently replace package IDs or signing lineage.
- **Native:** Godot 4.7.2 and AndroidX WebKit 1.17.1 are the currently declared direct Android plugin dependencies. They do not prove that a compiled APK includes *only* those transitive libraries.
- **UI:** locally packaged HTML/CSS/JS, locally staged jQuery 3.7.1, Android System WebView through `WebViewAssetLoader`; local URL allowlist, origin-bound messages, blocked remote requests, no Javascript interface privilege or file access.
- **Rendering:** Godot Compatibility renderer for the Android target. Babylon/Vue/Vite is a **separate** experimental/desktop prototype, not an automatically required APK runtime.
- **Control and data:** Python standard library, optional SQLite with bounded job/asset metadata pointers; actual binary art masters stay in owner-controlled Drive. No SQL server, cloud account or Python daemon is required on the tablet.
- **Studio:** heavy Linux artist tools stay in an opt-in host container; they do not need to run on Samsung Android. The current host image is deliberately **not** a stripped production image, so never treat its package count as an Android dependency.
- **Open-source publication:** source root LICENSE is GPLv3 today. License compatibility, copyrighted assets, actual APK permissions and F-Droid anti-feature decisions require later artifact and rights audit. No source-only claim guarantees store acceptance.

## Hex map and 4×4 Canon

`doctrine/thinClientKernelBoundaryV1.json` defines four rows of four **logical check identifiers** `0x00`–`0x0F`: hardware/kernel, OS/runtime, thin client, optional studio. The labels are test/report indexing only, **not** real hardware registers, hexadecimal memory patches, or binary encoding instructions. It references the existing four **source modules** from `modularSourceArchitectureV1` and the separate four **package composition layers** from `luHmOSFourLayerArchitectureV1`; no authority or meaning is transferred between the matrices.

## Exact-source sanity workflow

Run against an actual checkout of this proposal:

```sh
python3 tools/thinClientSkeletonAudit.py
python3 tools/fdroidTabletSourceAudit.py
python3 -m unittest discover -s tests -p 'testVendorReduction.py' -v
```

The first audit performs read-only source checks and **12 deliberate false-GREEN negatives**: fake kernel patch, Internet permission, ARM64 removal, remote UI script, unsafe WebView interface, extra proprietary SDK, unexpected UI dependency, renderer drift, auto-deploy, dropped GKI/vendor ABI protections, broad unfiltered front-end bundling, and injection of prototype assets. The second already runs the Meta/Samsung service-isolation check in this PR and the thin-client audit via the existing GitHub `samsung-lite-public-beta-source` workflow. The vendor-reduction audit is independent.

**Bundle correction in this proposed PR:** \`androidWeb3Plugin/plugin/build.gradle.kts\` no longer uses broad \`assets.srcDir(\"../../frontEnd\")\`. A Gradle \`Sync\` task stages only \`index.html\`, \`styles.css\`, \`app.js\`, four local cockpit jQuery adapters, the pinned jQuery library, and its MIT license. Both owner-CAST Android workflows now run the existing pinned npm stage before compiling an AAR. The staged file set fails closed if missing or extra files are present. This is **source configuration, not a compiled AAR/APK result**.\n\n**What these cannot prove:** no kernel/firmware reads, Android build, APK SBOM or binary packaging scan, stable owner signer, Samsung boot/install/upgrade test, GPU FPS, actual Meta/Google entitlement, app-store/F-Droid approval or public distribution.

## Go/no-go gates

1. **SOURCE:** Exact PR head passes source CI, negative controls and static vendor/dependency scans; this is the only automatically achievable green inside the draft branch.
2. **BUILD:** Exact approved code, locked dependencies and signing boundary produce a real APK, SHA-256, manifest, transitive dependency inventory and rights receipt.
3. **DEVICE:** Owner-controlled Samsung test confirms boot/install, offline launch, local WebView, Godot input, rotation/resume, crashes/performance, same-signer upgrade. Do not erase app data just to bypass a certificate mismatch.
4. **DISTRIBUTE:** Human-approved art, privacy/security, proper source and license metadata, store account and actual publication/upgrade proof. No automatic protected merge, signing, store enrollment, spend or publishing.

**Canonical release law:** `AI proposes. Policy authorizes. Deterministic evidence proves scoped source. Professor promotes.` Crown STOP until explicit review.
