# Moonlit Carriage · JRPG Layered 2D Candidate

Status: **AMBER / CROWN STOP / proposal for Professor review only**.

The story here is the small interactive spin-off of the Moonlit Carriage / Cat Goddess conversation. It is **not** a certified Live2D Cubism 5 model, production build, Godot scene, deployed plugin, published character canon or licensed Lum model.

## Source of truth

- `doctrine/SOURCE_OF_TRUTH.json`: canonical repository, Professor authority, no promotion
- `GEMINI.md`: Godot owns actual runtime/save state; AI can stage fiction but cannot make it canon
- `game/demo/relationshipRulesV2.json`: existing bounded relationship contract, read-only in this prototype
- `host/harness/studioDeck.html`: owner-authored layered Lum-inspired SVG portrait, reused here as a small derivative
- `frontEnd/prototypes/companionAtelier/live2dAdapter.mjs`: Cubism not installed; rights clearance needed

Nyx, Lady Morrigan and chapter dialogue are **authored proposals**, not added to approved adult companion roster, and no existing relationship stats or quests are mutated. Narration is deterministic, not model-generated at runtime.

## Run the candidate

From repository root:

```bash
python3 -m http.server 8080 --bind 127.0.0.1
```

Open `http://127.0.0.1:8080/frontEnd/prototypes/moonlitCarriage/`.

Controls: Pet Nyx / Wave / Blink / Pause, and branching dialogue buttons. ArrowLeft goes back, ArrowRight advances the first option while focus is on the stage. Explicit Save stores only bounded story progress in browser localStorage. Reset restarts this session; it does not overwrite a stored save.

## Gates

- Original, owner-authored vector only; no third-party game assets or proprietary Live2D SDK.
- `script-src 'self'`, `connect-src 'self'`, no external network, no tokens or remote writes.
- Read-only Canon check fails closed when schema, repository, authority, STOP or promotion bit doesn't match.
- Limited story IDs, validated local restore, `textContent` DOM insertion, no unsanitized HTML.
- Accessible controls, keyboard movement, touch-scroll preservation, reduced motion support, page-hide pause and timer cleanup.
- No production publish, Android APK, Godot mutation, private art upload or cast seal.

```bash
node --test frontEnd/tests/moonlitCarriageSource.test.mjs
node --check frontEnd/prototypes/moonlitCarriage/scene.mjs
```

## Required future proof

- Browser screenshots and Samsung touchscreen visual test
- Owner visual acceptance and unique provenance receipts for any final art or model
- Licensed Cubism runtime and cleared `.model3.json` if real Live2D is required
- Godot cutscene adapter/state transition tests before any promotion
- Professor review and explicit approval
