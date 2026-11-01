# Project Premonition · First Night Pocket

**Status:** independent HTML5 source prototype. **Platform:** mobile Chrome/Samsung, desktop browser, compatible iOS Safari for local file viewing. **Build requirements:** none.

Open `index.html` locally in a browser. It is a **single offline file** with HTML5, CSS and JavaScript. No CDN, account, microphone, cloud AI, network request or localStorage. Quest and scene notes remain in page memory until the tab is closed. **Export scene JSON** creates a local draft, not a canon asset.

## Four layers, minimum vertical slice

| Layer | Present proof | What remains |
| --- | --- | --- |
| **0 Machine** | One HTML asset, no driver/firmware changes or new native libraries | Physical Samsung frame timing and device proof |
| **1 Application** | Semantic HTML5 controls, reduced motion, responsive CSS vector scene and JS state machine | Physical touch/keyboard/accessibility test |
| **2 Creative studio** | Three original procedural vector locations, palette/stars, private director note, JSON export | Rights-reviewed backdrop/character replacement and Godot/Blender |
| **3 Human workflow** | Five canon quest beats, restart and manual review/export | Artist approval and reusable storyboard importer |

**Canon:** `game/story/firstNightQuest.json`, quest `firstNightCircuit`. Event order: `talkLumRiverwalk`, `collectSignalShard`, `collectCoffee`, `clearStaticWisp`, `sealFirstNight`. This pocket sketch is a simplified linear browser visualization, **not** the actual 3D proximity/game-gate implementation in Godot.

**Assets:** `artAssets/README.md` and the sprite/backdrop manifests state publicApproved=false. The existing starter pack is private. Nothing from it is bundled. Three original vector places and a geometric horned silhouette are placeholders, **not approved character body designs**.

No APK signing, Godot web export, live GPU proof, AI workers, publishing or Crown promotion. This is a GitHub draft only.

## Test

From repository root: `node tests/firstNightPocketLogicSmoke.js`.

The test compares the five embedded quest events and completion message with Canon, executes the **actual inline JavaScript** in a mocked DOM, exercises completion, restart, palette, stars and manual export, and checks for external-script/network/autosave drift. It does not claim a physical mobile-browser test.

## Asset graduation

1. Keep this playable vector fallback until an individual approved asset exists.
2. Record creator, rights, provenance, byte size, SHA-256, dimensions/alpha and intended world.
3. Add a reversible optional asset adapter with an explicit fallback; never overwrite artist masters.
4. Measure actual mobile loading, responsiveness and memory usage before selecting optimized image formats.
5. Promote an asset only after the Professor reviews its appearance and rights.

**Goal:** one actually playable small thing first, then gradual hardening rather than adding infrastructure before a demo.
