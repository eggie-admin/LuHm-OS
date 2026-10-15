# LuHm-OS | Artist-first workbench reconciliation | Candidate

**Baseline:** GitHub main `8b507584cdebd9b91ca6ab4c56b478a63a47833a`, 2026-10-15.  
**Authority:** Professor's direction: LuHm-OS is an **art tool**.  
**Canon stage:** proposed candidate; existing scoped seals and creative masters are untouched.

## Architectural correction

**The workstation is the product.** The Android shell, ChatGPT/agent system, Godot play/runtime, hosted harness, GitHub CI and Render deployment are **parts** of the creative workstation, never substitutes for a usable editor.

Artistic source authority and ownership remain with the Professor. Yume guides production and performs bounded assistance. Other agents inspect, log and test. No provider or model can silently replace the original drawings, music, script, creative intent or asset authorship.

## Current implementation, no invented functionality

| Surface | Source verified | Actually proved? |
|---|---|---|
| Chat / companion | `frontEnd/index.html`, `frontEnd/app.js` | Shell candidate only |
| Media asset carousel | `host/harness/index.html`, `host/harness/cockpit.js` | Browser-local inspection design, not durable media editor |
| Factory panel | `frontEnd/index.html` | Static status panel, not an operating render queue |
| Sprite/image toolchain | `tools/renderYumeReferenceGallery.py`, `tools/yumeBatchImageQueue.py` | Source files exist; production alpha and frame-grid proof requires assets |
| 3D toolchain | `project.godot`, `tools/yumeGodotAssetPrep.py`, Yume toolbox doctrine | Model extraction and motion runtime not established for full cast |
| Video render | `host/ai-ffmpeg/ai-ffmpeg.py`, GitHub Actions render tests | Synthetic MP4 proven; persistent worker and final pilot unproved |
| Private storage | `doctrine/storageTopologyV1.json` | Owner-only Audit Vault proved previously; *media tree* remains anyone-with-link-reader RED |
| Canon | `doctrine/yumeArtDirectionCanonV1.json` | Approved scoped art-direction behavior, **not** approved every 3D or film asset |

## Workbench mutations in practical order

**100: Studio first.** Proposed UI navigation makes Studio/Project work central. Preserve the approved Lum companion shell, but expose one genuine artist work surface rather than sending the Professor to GitHub to perform each creative edit. **Gate:** interaction proof on desktop browser and Samsung touch with source identity.

**200: Protected project intake.** Drag/select owner-approved art files into a local or owner-authorized remote workspace. Track original hash, author, revisions, visibility and rights. Never change original bytes or put private assets in public GitHub. **Gate:** lossless readback of one file, owner-only storage verification and provenance receipt.

**300: Layered editable canvas.** Support PNG/WebP/SVG source and layered compositing, transparent layers, transforms, masking and a reversible edit history; keep working masters in GIMP/Blender formats where those are the authoritative editing sources. **Gate:** artist makes an edit, performs Undo, restores it with Redo, and exports an editable source plus derived PNG without losing layers.

**400: Storyboard and animatic timeline.** Author the five Into the Warp sections; build individual shot cards with camera, expressions, set, actor blocking, story beat, per-shot art version and frame count. Add drag/reorder, trim, duration controls, and undo. **Gate:** seven render slots correspond to 23 panel references; the three Witching Hour/crescendo movements and Belldandy Codex reading at Shot 401 remain unchanged. Audio is parked.

**500: FFmpeg batch render console.** Connect an authenticated limited-job adapter to GitHub Actions for finite candidate renders and to Codespaces or a separate authorized private queue for optional interactive sessions. Visual queue must display sourceRef, current job, codec, FFprobe validation, artifact status, hash and cancel/retry state. **Gate:** approved real-media silent 1080x1920 H.264 candidate and Drive readback receipt. Synthetic green never substitutes.

**600: Godot / Blender / sprite preview.** Import only verified assets and original identities; show scene staging and transform controls. Real 3D character movement needs rig/deformation/realtime receipt; concept sheets and animated WebP are not evidence of that. **Gate:** device-appropriate physical/browser playback and source-file round trip.

**700: Review, final export and post templates.** Professor selects accepted shots and approves candidates. Generate short Codex Flash, Pirate Transmission or complete Into the Warp templates without recreating artwork; archive final source, hash and derived MP4. **Gate:** explicit human release and rights approval. No auto-publication to Facebook.

## Film canon held throughout

- Exactly **three approved spoken movements** inside the **five production sections**.
- **Belldandy reads the Anti-Daddy DADDY Codex lore in Movement II, Shot 401.** Eggie interrupts her at “And we raised ourselves…”.
- Section 500 returns to **the same Codex record** for the root-access cliffhanger, without another lookup.
- One Eggie/Big Daddy identity across inventor, Old Guard and Witching Hour; Lum physically follows in the lab. Four monitors keep fixed geography.
- Grayscale/teal/ember and charcoal noir are design choices, not replacements for original art.
- No soundtrack synchronization or public rights proof inferred from a video upload.

## Audit and truthful state

The `doctrine/artist-first-canon-120-checks.json` file lists **120 named controls across 12 domains**. The Python checker produces an exact-source artifact with PASS, GAP or UNVERIFIED for every control. These labels mean:

- **PASS:** source-level artifact or contract assertion only.
- **GAP:** requested source feature missing or source mismatch.
- **UNVERIFIED:** interactive/runtime permission/asset evidence not provided. This is not automatically a failure or a success.
- Any **critical** source mismatch fails GitHub CI.
- Full product GREEN is never inferred from the source count.

**Do not promote the proposed mission contract or release a film solely because this audit passes.** The Professor retains exact-scope approval.
