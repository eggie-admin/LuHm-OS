# Hydra Mod & Avatar / Web HDR | Top-to-bottom CAST source hardening | 2026-10-30

## Practical target
One original, explicitly adult, artist-controlled goth/anime avatar with thoughtful deformation loops, body/face morphs, wardrobe swaps, and a single approved engine-neutral GLB/FBX/USD exchange. The current Godot 4 playable runtime remains intact. Unreal is a separate GPL/EULA-reviewed final destination. Unity is an optional compatibility check, not another mandatory game build. The Samsung light OS is a private capture/control cockpit, not an Unreal Editor.

## Nexus / RE / Fallout donor boundaries
- Read official Nexus Mods API v3 as an authenticated **metadata-only** future adapter. Never scrape pages, auto-download a mod, embed API keys in public Actions, or auto-execute installers. Vortex extensions should use the maintained `@nexusmods/vortex-api` package from Nexus-Mods/Vortex, not the archived separate repo.
- Resident Evil: study praydog/REFramework Lua, object inspection and camera workflows without extracting Capcom character assets into Hydra.
- Fallout: study ousnius/BodySlide-and-Outfit-Studio for outfit sliders, normalization, NIF-to-workflow ideas, and TES5Edit/TES5Edit for conflict detection. The BodySlide Nexus page forbids cross-game conversion of its mod files and other reuse without permission. Source GPL != mod asset permission.
- Adult-rated metadata requires an opt-in, age-gated catalog profile. User choice to view a mod does **not** authorize integrating its textures, meshes, outfits or audio into the published original game. The published game needs original work or independently verified creator and game-publisher clearance.
- These repos are **references only**: no automatic clone, merge, mirror, plugin loader or auto-install; continue source-pin and individual license checks.

## Python choice is task- and license-driven
Keep the stdlib-first deterministic workflow. Evaluate NumPy + SciPy for poses and temporal smoothing; OpenCV for calibrated camera geometry, masks and optical flow; MediaPipe for single-camera landmark candidates; MMPose for heavier whole-body models; scikit-image for mask metrics; trimesh for mesh inspection; Open3D for optional scan alignment. Not all are needed. Preserve a separate constraints/lockfile and SBOM after actual Python environment verification; do not automatically add these dependencies to the Android APK, server or existing python requirements. GPU/CUDA/ROCm availability requires its own host proof.

## Avatar deformation gates
Store editable .blend masters privately. Each export records author, asset rights, SHA256, mesh triangles, UV/normal and skin-weight checks, eyelid/mouth/shoulder/elbow/hip/knee edge-loop review, six face morphs, foot sliding and collision checks. Aim for **initial budget targets** 120k desktop and 20k mobile triangles (not facts about existing models). Test expressions, walking and dance turns at the chosen engine FPS before saying GREEN. Real measurements must come from an actual Blender asset inspection, not a JSON label.

## Web layer / skyboxes
Reuse the existing Babylon glassWorld instead of creating Three.js + Unity WebGL + Unreal Pixel Streaming simultaneously. An HDR/ENV environment provides background and PBR illumination; prefer local approved assets, correct color-space/tone mapping, a capped asset budget, reduced-motion support, and depth/occlusion tests. `tools/hydraModAvatarAudit.py` checks a *reference manifest*, **not** a rendered skybox or a real Babylon runtime.

## 500 × 500 × 500 honesty contract
500 * 500 * 500 = **125,000,000 design combinations**. Our source test emits just **500 deterministic, unique, three-axis planned cases** using two coprime modular permutations, so every axis slot appears once in the sampled plan. Those 500 cases are NOT machine, mod, gameplay, security, artwork, browser, camera, engine, or user tests. The receipt says 0 runtime cases executed. Expand with risk-based pairwise testing and meaningful real fixtures rather than compute theater.

## Exact-head source check (no IO to Nexus or cloud)
```bash
python3 -m unittest tests.testHydraModAvatarAudit -v
python3 tools/hydraModAvatarAudit.py --source-ref "$(git rev-parse HEAD)" --output /tmp/hydra-mod-avatar-proposed.json
```
Crown STOP. No production merge/sign/deploy, adult-content publication, permission uplift, SaaS billing, remote AI, code downloads or agents resumed.

Official sources: https://help.nexusmods.com/article/114-api-acceptable-use-policy ; https://help.nexusmods.com/article/28-file-submission-guidelines ; https://help.nexusmods.com/article/19-adult-content-policy ; https://github.com/Nexus-Mods/Vortex ; https://github.com/praydog/REFramework ; https://github.com/ousnius/BodySlide-and-Outfit-Studio ; https://github.com/TES5Edit/TES5Edit ; https://doc.babylonjs.com/features/featuresDeepDive/environment/skybox/ ; https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/python .
