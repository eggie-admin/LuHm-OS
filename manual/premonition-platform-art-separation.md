# LuHm-OS: Project Premonition | Android, Samsung, iOS, Linux asset/compute boundary

**Status: draft source contract, not a physical device build, kernel patch or install.**

## Exact current sources, not a new pretend OS

- Canonical product: **LuHm-OS**; development name **Project Premonition**; legacy name Project Hydra; publisher Eggie Bagelface. Source: `doctrine/organizationBrandRegistryV1.json` and `campaign/brandAndVoiceGuide.md`. Third-party logos and vendor names must not imply sponsorship.
- Existing Android proposal: `project.godot` with GL Compatibility renderer and `export_presets.cfg` with arm64-v8a and Android SDK target 36. An export preset is **not** a signed APK nor physical Samsung test.
- Existing web preview: `frontEnd/prototypes/glassWorld/package.json` includes Babylon/Vue/jQuery, with separate size budget gates. Mobile gets bundled assets and approved runtime, not npm, Python SQL, Blender or a Linux kernel inside the app.
- Existing Lum runtime GLB slot: `assets/lum/README.md` documents `res://assets/lum/luhm.glb` fallback. Its external 56 MB candidate has **zero skins and zero animations** and remains private. Never claim it is rigged or distribute it automatically.
- Existing brand SVG: `publicationSite/logo.svg` is an observed public-site visual variant, **not** proof of one universally approved palette.

## The 4×4 split: platforms across planes

| Runtime row | Kernel/device gate | Vector/UI | 3D/render | Python/SQL metadata |
| --- | --- | --- | --- | --- |
| Android universal | AOSP HAL, GKI KMI, app permissions, device owner kernel | SVG and responsive UI | Godot GLES compatibility / Babylon WebGL as tested | remote/private host API only |
| Samsung Galaxy | OEM model-specific drivers, bootloader, Knox; **do not flash** | tablet scaling, DeX only when supported | ARM64 GPU/thermal benchmark required | no local database server, protected client |
| Apple iOS | XNU architecture studied; signed app sandbox controls actual device | web SVG first | web renderer, native Godot/iOS later | no iOS privileged Python process or raw SQL port |
| Headless Linux VM | Linux kernel on physical host; optional QEMU guest | preview/test vectors | Blender/Godot/FFmpeg on opt-in worker | Python 3 worker and SQLite STRICT; optional private MariaDB |

Source is in `doctrine/premonitionCrossPlatformArtSplitV1.json`. All 16 cells begin **UNKNOWN** for physical runtime and vendor privileges. Android Generic Kernel Image is an example of an actual vendor-neutral kernel boundary, not permission to swap Samsung firmware. Apple's open-source XNU is a research input, not a portable iOS kernel or developer entitlement.

## Finely separated asset bits

1. **Artist-owned editable masters:** SVG, Blender `.blend` and original source art remain versioned and protected.
2. **Portable derivative assets:** use sanitized SVG for vector marks, glTF 2.0/GLB for explicit 3D scene data, PNG/WebP for textures/previews, MP4/WAV for audio/video as rights-approved. Check each candidate's manifest and underlying bytes separately.
3. **Python tools** compute SHA-256, inspect tiny bounded headers, produce known-safe conversion plans, and run format/rights checks. Real Blender/FFmpeg/Godot conversion is a separate opt-in isolated worker; merely reading a `.blend` header does not validate the Blender file.
4. **SQL records** hold the asset ID, task/source/scope identity, format, class, hash, byte count, private logical pointer and rights/provenance metadata. SQLite STRICT handles local development; MariaDB is an optional separately authorized shared receipt store. Never put huge media binaries, shader caches, private video, license keys or scripts in the SQL payload.

The source-only schema `host/api/premonitionAssetLedgerV1.sql` contains `premonitionAssetRecord` and `premonitionTransformRecord`, all default-deny on publication. The Python validator `tools/premonitionPlatformArtAudit.py` verifies the actual source, uses an **in-memory** SQLite instance and rejects dangerous SVG markup, external URI glTF inputs, invalid GLB headers and unauthorized release-state claims. These checks are **not** a replacement for a real sandboxed file parser or glTF validator on untrusted private media.

## Upstream research shortlist

| Upstream source | Our legitimate takeaway | Import / license rule |
| --- | --- | --- |
| Android AOSP GKI / KMI: https://source.android.com/docs/core/architecture/kernel | Generic kernel / vendor-driver interface | architecture reference; do not flash |
| Samsung Open Source Release Center: https://opensource.samsung.com/ | model-dependent upstream OEM components | read-only until exact device/model source and license |
| Apple XNU: https://github.com/apple-oss-distributions/xnu | Darwin/XNU kernel model, platform separation | no unsupported device kernel modification |
| WebKit: https://github.com/WebKit/WebKit | iOS browser portability and rendering | component license review |
| Godot: https://github.com/godotengine/godot | MIT cross-platform scene importer and mobile export design | reuse existing project and preserve third-party notices |
| Google Filament: https://github.com/google/filament | optional PBR and glTF reference for Android/iOS | research only; no redundant renderer without benchmark |
| Khronos glTF validator/spec: https://github.com/KhronosGroup/glTF-Validator and https://registry.khronos.org/glTF/ | glTF semantic/structure compatibility | keep original Blender masters and track extension compatibility |
| W3C SVG2: https://www.w3.org/TR/SVG2/ | vector format portability | safe subset for untrusted input, no scripts/remote resources |

**Popularity is not compatibility proof.** Do not cherry-pick arbitrary community patches into signed Android/iOS builds. Source license, active maintenance, test fixture, platform compatibility, binary provenance and review must all pass first.

## Kernel-to-studio escalation

The next practical ladder is:
- **R1 source:** verify exact commit, model/OS capabilities, brand and license.
- **R2 format:** validate private SVG/GLB bytes and canonical metadata shape.
- **R3 device:** measure real Android/Samsung WebView, GLES/Vulkan and client resource limits; test iOS Safari rendering separately; prove a headless Linux conversion worker independently.
- **R4 promotion:** review responsive artwork, rights, performance, signed build, rollback and Professor approval.

The Android and iOS applications do **not** inherit the Linux VM's root privileges. The existing GitHub repository retains source truth; approved private binary storage holds full editable masters. No new paid service, production merge, signing, bootloader unlock, kernel flash, private donor publication or live autonomous worker is authorized by this draft.
