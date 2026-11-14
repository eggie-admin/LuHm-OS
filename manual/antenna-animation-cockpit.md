# Phone-first animation cockpit candidate

Current direction: pause game development. Use Godot 4 as a character-animation
stage, Vue as the control surface, Babylon as an optional web preview renderer,
and Blender as the editable high-fidelity rig and motion master. Existing game
source is preserved. This candidate does not replace the seven visual planes,
existing MCP resource identities, private assets, release signing or live host.

## One build, two surfaces, one contract

Run `npm ci --ignore-scripts && npm run check` inside
`frontEnd/prototypes/glassWorld`. The build produces:

| Output | Purpose |
|---|---|
| `dist/antenna.html` | Standalone Vue cockpit with local Python planning |
| `dist/antennaWidget.html` | Self-contained Vue MCP Apps widget; no external assets |
| `dist/luhm-antenna-contracts-0.1.0.tgz` | Private dependency-free npm contract package |
| `dist/antennaWidget.receipt.json` | Widget hash, byte count and explicit project budgets |
| `dist/index.html` | Existing optional Babylon/HTML5 studio |

The npm archive exports `./antenna`, `./animation` and `./widgetBridge`. It includes
data contracts and a restricted MCP Apps bridge; no Vue, Babylon, models or media
dependencies. Vue is bundled into the widget by the owning frontend build.
Nothing is published to the npm registry.

The additive Python module `host/mcp/luhmAntenna.py` registers
`ui://luhm-os/antenna-v1.html`, `luhm_open_antenna` and
`luhm_plan_antenna_creation` through the existing harness server. Build the widget
before starting that candidate server. A missing bundle returns a readable build
diagnostic, never a false working UI claim. Existing cockpit URIs are unchanged.

The widget uses MCP Apps initialization and `tools/call`, with an eight-second
timeout, parent-window verification, a four-request maximum and two allowlisted
tools. The standalone page uses localhost HTTP; neither surface pretends to use
the other's transport. Provider credentials and private assets are not embedded.
Installed ChatGPT plugin identity, visual mount and actual host invocation remain
separate from source/build proof. No live deployment occurs in this candidate.

## Size and memory

No verified source or official page examined established the remembered
“100 megabit” ChatGPT limit. Treat 100 megabits = 12,500,000 bytes as a provisional
project total-build ceiling, not an OpenAI platform guarantee or network bitrate.
The widget has a stricter 262,144-byte build gate. Both apply to uncompressed file
bytes; GPU memory, decoder memory, frame rate and network rate need separate tests.
The total-build receipt excludes only the receipt's own bytes.

No model, texture, audio track, Godot WASM or Base64 asset is embedded in the
antenna widget. Optional 3D must remain user-initiated and outside its initial
download. Large motion/model data stays in approved files with size/hash evidence.

## Animation progression

| Tier | Execution | Preservation / degradation |
|---|---|---|
| Master | Blender on capable workstation | Preserve full mesh, rig, textures, original motion and editable project |
| Animation stage | Native Godot 4 | Imported character, AnimationPlayer, expressions and pose; no game world |
| Web preview | Vue plus Babylon, or a separately loaded Godot Web export | Bake rig constraints/physics; export GLB animation, skinning and morph targets; simplify a derivative |
| Antenna | Chat widget controls | Still/video fallback or remote controls; no resident 3D engine |

Godot Web executes on the browser device; serving an export remotely does not
move rendering to a remote GPU. A true remote-rendered view needs a separately
implemented stream and authenticated control transport. Do not run Babylon and
Godot simultaneously by default or assume transparent frame sharing between them.
Share GLB assets and versioned commands; select one renderer per active view.

`luhmOs.avatarAnimation.v1` defines bounded `play`, `pause`, `seek` requests. The
npm validator and `scripts/avatar-glass.gd` accept imported clip names only; no
scripts, URLs or shell execution. Godot clamps seeking to the imported clip length.
The adapter is source-level until a Godot run proves it on an approved character.
The widget prepares an animation plan; it does not claim to play a character yet.

MMD is the likely remembered Hatsune Miku-era dance workflow. MMD Tools supports
PMX/PMD models, VMD motion and VPD poses. Use it for approved imports and bake the
result in Blender before glTF export. PMX materials, physics and IK are not
assumed to transfer losslessly. Each model, motion and music file needs its own
usage provenance; no third-party character assets are bundled by this change.

Do not rewrite WebGL: use the standard browser graphics API through Babylon or
Godot Compatibility. Preserve full masters; derive lower polygon counts, texture
sizes, bone influences, morph sets and baked motion only after profiling the phone.
No universal polygon or bone limit is asserted without a measured target.

## Source references

- MMD Tools: https://github.com/MMD-Blender/blender_mmd_tools
- Babylon glTF pipeline: https://doc.babylonjs.com/preparingArtForBabylon/dccToGltf
- Godot import formats: https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html
- MCP Apps UI: https://developers.openai.com/plugins/build/chatgpt-ui

## Proof boundary

Run JavaScript policy/bridge tests, Python request/registration tests and the real
pinned MCP integration test. Build output must pass the byte gates. CI uploads the
reviewable bundle. Samsung visual/touch acceptance, deployed plugin invocation,
MMD conversion fidelity and Godot animation runtime remain unverified.

No paid inference, device flashing, DNS mutation, agent activation, merge,
publication, provider reconfiguration or protected release is part of this slice.
