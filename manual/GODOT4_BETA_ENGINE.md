# LuHm OS Godot 4 Beta Engine Lane

Status: **BETA / NOT CROWNED / NOT MAIN**

This lane exists because a build can be CI-green and still look wrong on a real phone. Rendering, assets, character deformation, mod content, and physical-device presentation are separate proof surfaces.

## Renderer stack

### Samsung Mobile Beta
Android moves from the old Compatibility visual target to Godot's **Mobile** renderer. Compatibility remains a fallback, but Mobile is the intended Samsung path.

The beta director enables ACES tonemapping, glow, color adjustment, 4x MSAA plus FXAA on RenderingDevice, debanding, depth/height fog, one primary shadow-casting directional light, shadowless hero/fill lights around Lum, and hooks for reflection probes, decals, particle trails, LightmapGI and imported PBR materials.

Forward+-only effects are not lied about on the phone. SSR, SSIL, SDFGI, volumetric fog and subsurface scattering belong to the workstation ultra profile.

### Workstation Forward+ Ultra
This is the capture/dev-quality lane for TAA/FSR2-ready output, SSAO/SSIL/SSR, SDFGI/VoxelGI-ready lighting, volumetric fog, higher shadow quality/contact shadows and a subsurface-skin path.

## Asset lanes

1. **OWNED**: can be forged and packaged.
2. **PERMISSIVE**: can be packaged only with required attribution/license receipts.
3. **PRIVATE_REFERENCE**: private experiments/mod lane only.
4. **UNKNOWN**: quarantine.

The public repository intentionally does not contain private Google Drive IDs or ChatGPT Library file IDs. The private asset vault is materialized locally, hashed, normalized, and only approved derivatives enter the beta staging tree.

Current indexed sources include the 77 deterministic repository community assets; the private Drive Original vault with the Cathedral cockpit interface and Lum gothic hip/wing animation sheet; Drive community/open-license and third-party-private-reference lanes; the Drive Meshy conversion pipeline; the ChatGPT Library asset-dungeon manifest indexing 28 curated assets; and the pinned/hash-verified Meshy Lum runtime donor.

## PBR / texture forge

`pbrMaterialForge.gd` consumes an explicit sidecar for base color, tangent-space normal/bump, roughness, metallic, AO, optional height and optional emissive maps. No map is guessed from a visually similar character. Identity/UV proof remains mandatory.

Mobile targets are 2K textures by default, with 4K as a hard upper target. Character LOD targets remain roughly 120k / 60k / 25k triangles for LOD0/1/2.

## Face and animation

The facial driver inventories imported blend shapes and reports blink, smile, jaw/talk, brow and core viseme coverage. Animation remains imported `AnimationPlayer` clips plus `AnimationTree` blending.

## Hair, cloth, wings and body secondary motion

Godot 4's `SpringBoneSimulator3D` is the beta secondary-motion engine for hair, cloth, tails, wings and optional adult-character bust bones when those bones actually exist in the authored rig.

Spring-bone simulation is **blocked on a scaled skeleton hierarchy**. The current runtime can presentation-scale Lum, so the beta lane reports a blocker instead of enabling unstable physics. Bake/apply final character scale in Blender/GLB first.

## Private/Nexus-style mod lane

Private mods live under `user://mods`. The engine inventories local ZIP/PCK/GLB/GLTF packs, never downloads mods at runtime, never auto-executes third-party scripts, never silently promotes a private mod into the public APK, and requires a rights/provenance decision before third-party content becomes distributable.

## Promotion gates

`BETA SOURCE -> ASSET RIGHTS AUDIT -> GODOT HEADLESS SMOKE -> APK -> SAMSUNG VISUAL PROOF -> HUMAN CROWN`

No visual GREEN from CI alone.
