# Focused patch builds

The existing Godot world, native Android bridge and release forge remain the architecture.

- Presentation: `scripts/game/lumFocus.gd` owns opening camera framing. Rig/world code remains independent.
- World and rig: scene/model changes still require Godot import, scene smoke and packed-resource proof.
- Native WebGlass: native source, cockpit source/lockfile, plugin descriptors, toolchain contract and module builder produce a content fingerprint. Only matching cached AARs with matching output hashes can be reused. Missing/corrupt entries rebuild. There are no fallback cache keys.
- Host AI: separate host adapter; never packaged as an Android credential path.
- Build and gates: changes require full revalidation. Unknown file paths also require full revalidation.

Run `python3 tools/buildPlan.py --base <verified-base-sha>` to review changed modules after committing. This planner is informational; it does not turn off checks. The Crown workflow automatically restores/saves the native module cache. Its first run is cold; later scene-only changes can reuse the AARs. Other existing workflows remain independent verification lanes.

Every changed Android candidate still exports a fresh APK, signs it, verifies package/permissions/signature/alignment and binds provenance to the new source. Never cache keystores, credentials or a final signed APK as a substitute for new proof. A cache receipt is an integrity/reuse record, not independent release certification. GitHub's cache scope separates untrusted PR caches from the protected/base branch.

This is build-time modular reuse, not runtime hot patching. APK updates still depend on version and signer compatibility. Permanent signing and Samsung visual proof remain pending external gates.

Lum acceptance: opening vertical framing covers 55–90% of viewport height, centered horizontally, with the WebGlass initially reduced to its bubble. Her 1.90m authored scale survives the intro and pulse reset. Projection checks do not establish visual quality or occlusion; Samsung recording remains mandatory.
