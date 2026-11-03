# Crown Cathedral · WebGL four-layer CAST candidate

**Purpose:** turn the existing Babylon + Vue + jQuery glassWorld into an artist-facing 3D environment, not another abstract agent console.

## Canon layers (4×4)

1. **Artist/human:** Professor chooses Cathedral, Riverwalk, Studio, or places props by touch/mouse. Frontend remains unprivileged.
2. **Human↔machine:** typed `scene-state.mjs` controls local props; `crown-cathedral-layout.mjs` is a pure, bounded 3D layout generator. No URL/user scripts or remote asset loading.
3. **Machine/GPU:** existing Babylon WebGL engine renders original procedural geometry; new env is distinct from editable props. Preset switch disposes old meshes/materials. Existing hidden-tab skip, scaling and resize stay intact. No second WebGL engine.
4. **Evidence/Crown:** exact-source Node tests, Python source checks, existing vendor-budget workflow, GitHub receipt. Device/WebView, actual rigged 3D/Live2D character, ChatGPT MCP App mount, owner-signed APK and public deploy need separate proof.

## Actual new behavior

- **Cathedral:** 79 generated geometry pieces, including aisle, arches, columns, stained-glass-colored panels and 3D companion proxy.
- **Riverwalk:** 39 pieces, including lamp posts, river and neon shopfronts.
- **Studio:** 20 pieces, including stage rig, back wall and softbox-like props.
- User can tap an environment preset without altering local 3D prop JSON or uploading master art.
- The 3D figure is a geometric **proxy only** and **not the approved proprietary/third-party Live2D Lum model**, a final character rig, animation, motion capture, or Godot runtime.
- Render proof and image quality still require a real WebGL browser screenshot and Samsung physical test.

## Source policy and tests

Browser loads pinned Babylon 9.x/Vue 3/jQuery from existing npm lock, self-hosted on approved deployment. No CDN or extra server. Existing `doctrine/vendorReductionV1.json` JS/CSS budget applies. Keep WebGL as compatibility floor; WebGPU is not proof without target support. No third-party protected art or private media masters included.

Run from full checkout:
```sh
python3 tools/crownCathedralWebglAudit.py
cd frontEnd/prototypes/glassWorld
npm ci --ignore-scripts --no-audit --no-fund
npm test
npm run build
cd ../../..
python3 tools/vendorReductionAudit.py --dist frontEnd/prototypes/glassWorld/dist --output build/crown-vendor-receipt.json
```

**Dry-run mutation and rollback:** only new layout, new unit tests, one renderer source integration, three HTML controls, one Vue event listener and CSS, with this contract + audit. Revert candidate without touching production, signed APK, private Drive assets or agent quarantine.

**Promotion:** explicit Professor approval applies to this scoped work, but CI must prove exact branch head before any **source merge**. A source merge never establishes WebGL visual acceptance, true Live2D/3D rig fidelity, app deployment or public release. Crown remains STOP.
