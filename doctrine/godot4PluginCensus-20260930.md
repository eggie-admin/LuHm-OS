# Godot 4 plugin and creation-tool census — 2026-09-30

**Purpose:** evidence snapshot for the T0 research gate and later T1/T2/T3 integration decisions. This is not an installation, endorsement, compatibility certification, or change to LuHm OS runtime policy. No plugin, dependency, project setting, engine setting, or remote service was changed.

## How to read this census

- The companion [`godot4PluginCensus-20260930.json`](godot4PluginCensus-20260930.json) is the field-complete matrix. Each candidate entry has the same required fields; missing evidence is written as `UNKNOWN`.
- Upstream GitHub repositories and their release pages take precedence over copied catalog descriptions. The official [Godot Asset Library](https://godotengine.org/asset-library/) backend repository describes the library as being in maintenance mode and says the future Godot Foundation asset store is expected to deprecate it. The official library host did not resolve from this research environment, so individual catalog entries could not be independently checked. A candidate URL appears only when upstream points to it; search-result-only links are explicitly labeled unverified, and other listings are `UNKNOWN`, not presumed absent.
- Godot 4.7.2 is the requested target; the [official archive](https://godotengine.org/download/archive/4.7.2-stable/) dates its stable release to 2026-08-18. “4.7”, “4.6+”, a compatible major version, or a project being built with Godot does **not** establish a plugin's 4.7.2 compatibility. Only upstream claims are recorded; this research did not install or test candidates.
- Release tags are included where an upstream release page exposed one. Exact candidate release dates were not consistently available and are explicitly `UNKNOWN` in the matrix rather than estimated.
- `CANDIDATE` means worth considering for an isolated, gated future evaluation; it is not selected, approved, installed, or production-ready. `REFERENCE_ONLY` means useful as a pattern or external workflow, not a proposed project dependency. `REJECT` is limited to evidence of a direct mismatch for the target. `UNKNOWN` means the available evidence is insufficient.

## AI-assisted creation and editor automation

### What can actually mutate the project?

| Tool/workflow | Assistant role | Direct project/editor mutation | Model locality/provider |
| --- | --- | --- | --- |
| [Coding-Solo Godot MCP](https://github.com/Coding-Solo/godot-mcp) | An MCP **server**, not a model. | **Yes.** README documents editor/project launch, inspection, debug output, scene creation, node insertion, sprite loading, save, UID update, and process start/stop. | Provider-neutral; the MCP host controls model, credentials and egress. |
| [Funplay MCP for Godot](https://github.com/FunplayAI/funplay-godot-mcp) | Editor-only MCP addon; upstream says GDScript-based and supports standard/.NET projects (4.2+ claim). v0.10.0; MIT. | **Yes.** Advertises scene, script, UI, animation, play-mode, input and editor operations; includes `execute_code`. Local bridge defaults to `127.0.0.1:8765`, with per-project token and safety checks on by default. It can also write client configuration and optional project-local skill/AGENTS files. | Cloud/local model choice belongs to MCP client. Treat arbitrary code execution and project-file writes as high-trust actions; do not auto-approve. Godot 4.7.2-specific tests are `UNKNOWN`. |
| [Godot AI MCP](https://github.com/event-horizon-studio/godot-ai-mcp) | Pure-GDScript `@tool` EditorPlugin plus Node.js 18+ MCP process; README says Godot 4.7+. No GitHub release found. | **Yes.** 26 tools include scene/node changes, GDScript read/write/execute, material creation, project settings and viewport capture; local TCP bridge at `127.0.0.1:6505`. Undo/redo is claimed for node/property/signal changes, not a substitute for source review. | MCP client/model supplies inference. No official Asset Library listing or 4.7.2-specific test verified. |
| [Godot-MCP by Ivan Murzak](https://github.com/IvanMurzak/Godot-MCP) | C# EditorPlugin/MCP stack; README advertises Godot 4.3+, .NET 8, NuGet packages and 42 tools. | **Yes.** Reads/creates/updates GDScript and C#; operates scenes, nodes and resources; screenshots and a reflection escape hatch broaden capability. | Defaults to hosted `ai-game.dev` OAuth/cloud route, with self-hosting available. `godot-cli install-plugin` edits project and C# configuration. Provider, credentials and data retention need separate review; exact release/license and 4.7.2 evidence remain `UNKNOWN`. |
| [Ollama Assistant for Godot](https://github.com/TheCronkTM/godot-ollama-assistant) | Godot editor dock/plugin; upstream says Godot 4.4+ and MIT; requires local Ollama/model. | **Code-only by documented scope:** refactor, optimize, explain, complete functions, then apply generated text to the selected script. No scene-tree, shader, or dialogue operation is documented. | Uses `localhost:11434`; README says it works offline after setup/model pull. Model size and exact 4.7.2 test status are `UNKNOWN`. |
| Conditional Ollama model + an MCP-capable host | Architecture pattern, not a verified Ollama/MCP pairing. | If the chosen client can call MCP tools, it may use the scene-mutation capabilities above. Local inference does not narrow tool filesystem/process permissions. | Host tool-call support, telemetry, model download/update behavior and local-only guarantee remain `UNKNOWN`; distinguish this from the script-only Ollama Assistant above. |
| Cloud MCP client/model | Cloud model may suggest code/content and request tools made available by the MCP host. | Can perform connected server operations only when tools are exposed and approved; otherwise assistance is suggestion/user-mediated editing. | Provider, credentials/subscription, retention and egress depend on the selected client. Treat source, scenes, assets, prompts and logs as potentially transmitted. |
| [Godot Tools for VS Code](https://github.com/godotengine/godot-vscode-plugin) | IDE language/debugging support (GDScript completion, navigation, formatting, breakpoints and resource navigation); not an AI model. | Ordinary IDE file editing only; no autonomous scene-generation feature was verified in its README. | No model/provider is inherent; separately installed AI extensions change data egress and mutation risks. |

The key distinction for later decisions is **assistant proposal versus delegated execution**. The MCP servers above expose different scene/project/script operation sets; they are not “read-only” merely because an AI agent is the caller. Funplay documents an auth token and safety checks for `execute_code`; Godot AI MCP describes localhost transport and editor undo/redo; Coding-Solo demonstrates auto-approval configuration; Ivan Murzak documents a cloud backend and reflection escape hatch. None of those mitigations replaces human review. Pin packages, inspect tools and plugin source, use a disposable project, deny auto-approval for writes/execution, and review diffs. Node/npm, NuGet/.NET and cloud service choices add supply-chain and privacy boundaries.

An upstream Ollama Assistant is verified for local GDScript help, but no reviewed source establishes that it edits scenes, shaders, materials, dialogue, textures, sprites, animations, rigging, audio, or builds. Funplay advertises UI/animation/editor operations; Godot AI MCP advertises material creation; the other MCPs document differing scene, resource and script tools. These are not interchangeable asset-authoring guarantees. None of the checked tools has verified 4.7.2 test evidence.

### Discovery-seed disposition

The names/classes supplied as discovery seeds are not endorsements. The census now includes four canonical MCP sources and one Ollama script-assistant source. An Asset Library search surfaced [Godot AI (5050)](https://godotengine.org/asset-library/asset/5050), [Breakpoint MCP (5335)](https://godotengine.org/asset-library/asset/5335), [Godot MCP Pro (4961)](https://godotengine.org/asset-library/asset/4961), [AI Assistant Hub (3427)](https://godotengine.org/asset-library/asset/3427), and [GDMCP (5403)](https://godotengine.org/asset-library/asset/5403); pages and upstream repositories were not retrievable, so their identity, current status and all implementation details remain `UNKNOWN`. These search-result links are leads, not verified endorsements. No standalone prompt-composer/editor-generation product was verified; Funplay's templates/project guidance do not establish a separate product. Godot-specific AI guides not tied to a checked repository remain `UNKNOWN`.

### AI creation surface: verified versus not established

| Artifact/task | Evidence-based conclusion |
| --- | --- |
| Scenes, nodes, project inspection, run/debug loop | Coding-Solo, Funplay, Godot AI MCP and Ivan Murzak all document direct editor/scene/resource operations with differing tool sets; editor/project launch and debug capture are explicit for Coding-Solo. All require review and tool-specific permission checks. |
| Scripts, GDScript and C# | Ollama Assistant applies generated GDScript to a selected file. Funplay, Godot AI MCP and Ivan Murzak document script operations; Ivan explicitly names both `.gd` and `.cs`. Direct script execution is advertised by several MCPs and is high risk. |
| Shaders, materials, sprites, animations, UI and 3D assets | Funplay advertises UI/animation setup and sprite/tool workflows; Godot AI MCP advertises primitive meshes/material creation; Coding-Solo advertises loading sprites. A tool-specific shader authoring, texture/sprite painting, rigging or full 3D asset-generation tool was not verified. |
| Dialogue, quests, levels, tests, docs and build/export configuration | No dedicated AI dialogue/quest authoring, autonomous test authoring, doc generator, or build/release authority was verified. External agents may edit files if separately granted access; that is not a tested Godot-specific feature. |
| Build configuration and Android/export | Godot’s export workflow is distinct from project-content generation. No candidate was verified here as an AI build/release authority. Publishing, signing, or remote command execution are out of scope. |

## Categorized survey

The entries below cover the requested categories. The field-complete JSON matrix provides operational/security notes, release and license details, evidence links, and an explicit LuHm status for each serious candidate. Built-in engine features and standalone applications are included for comparison but are not misrepresented as installable add-ons.

| # | Category | Upstream-grounded options and assessment |
| ---: | --- | --- |
| 1 | EditorPlugin / editor productivity | Godot Tools for VS Code provides GDScript/resource language features and debugger support. Funplay, Godot AI MCP and Ivan Murzak are editor-control MCP plugins; their file/scene/script permissions differ and require separate review. |
| 2 | Runtime add-ons | [Phantom Camera](https://github.com/ramokz/phantom-camera) supplies Camera2D/Camera3D behavior and states Godot 4.3+; Dialogic and Dialogue Manager also combine editor authoring with game runtime behavior. Check each plug-in’s project/resource changes separately. |
| 3 | GDExtension / native modules | [Terrain3D](https://github.com/TokisanGames/Terrain3D) is a C++ GDExtension terrain system; [LimboAI](https://github.com/limbonaut/limboai) is a C++ behavior-tree/state-machine plugin. Native code raises engine ABI, binary, renderer, Android, and headless-CI gates. Neither has verified 4.7.2 evidence in the retrieved sources. |
| 4 | MCP / editor-control bridges / agent tooling | Coding-Solo, Funplay, Godot AI MCP and Ivan Murzak are distinct upstream bridges. Funplay documents local token auth and safety checks; Godot AI MCP describes localhost TCP; Ivan defaults to cloud/self-hostable; Coding-Solo documents project operations. None is pre-approved. |
| 5 | Local LLM / Ollama assistants | Ollama Assistant is a Godot editor dock that applies generated code to a selected script through local Ollama at `localhost:11434`; it is not scene automation. Any local Ollama + MCP combination remains host-dependent and unverified. |
| 6 | Cloud-model assistants | MCP servers are not models; cloud use depends on the client/provider. Ivan Murzak documents hosted `ai-game.dev` OAuth by default and a self-hosted option. Funplay, Godot AI MCP and Coding-Solo are provider-neutral bridges; privacy/credentials depend on the connected client. |
| 7 | GDScript / C# / shader / code assistance | Ollama Assistant documents local GDScript code help; VS Code Godot Tools supplies non-AI language/debugging tools; MCPs expose differing script operations (Ivan says C# and GDScript). No dedicated first-class shader assistant was verified. |
| 8 | Dialogue / narrative / quest authoring | [Dialogue Manager](https://github.com/nathanhoad/godot_dialogue_manager) (upstream describes Godot 4.6+) and [Dialogic](https://github.com/dialogic-godot/dialogic) (2.0-alpha-20, upstream says 4.5+ and recommends 4.6+) are credible narrative candidates. Dialogic’s alpha/breaking-change and updater behavior merit version pinning. No well-evidenced dedicated quest system was verified in this research. |
| 9 | Procedural level / world generation | [Terrain3D](https://github.com/TokisanGames/Terrain3D) supports editable terrain, sculpting, texture painting and foliage; [ProtonScatter](https://github.com/HungryProton/scatter) handles non-destructive scatter/scene dressing; [Voxel Tools](https://github.com/Zylann/godot_voxel) is a higher-complexity voxel option. None is a general guarantee of arbitrary level generation or 4.7.2 compatibility. |
| 10 | 2D sprites / tiles / pixel art / textures | [Pixelorama](https://github.com/Orama-Interactive/Pixelorama) is a standalone sprite/tile/pixel-art editor; upstream says it uses Godot 4.7.2, which is not an add-on compatibility claim. [Aseprite Wizard](https://github.com/viniciusgerevini/godot-aseprite-wizard/tree/godot_4) imports Aseprite animations and tile assets; it writes imported project resources. |
| 11 | 3D mesh / material / texture / world | Blender-to-Godot glTF is the general 3D pipeline baseline (Godot’s official docs could not be fetched in this environment); [Material Maker](https://github.com/RodZill4/material-maker) is a standalone procedural texture/3D painting tool; Terrain3D covers terrain. Standalone tools are not Godot project plugins. |
| 12 | Animation / rigging / retargeting / facial / blend shapes | Blender-to-glTF and Godot’s built-in animation/skeleton workflow are references, not third-party plug-in recommendations. No dedicated, sufficiently evidenced current 4.7.2 retargeting/facial authoring candidate was verified. Check importer behavior on the exact engine version. |
| 13 | Shader / VFX tools | Godot’s built-in shader and particle authoring are the baseline; Material Maker can author procedural textures. A checked GDQuest shader collection warns that it is being ported to Godot 4, so it is not treated as a clean 4.7.2 dependency. |
| 14 | Audio / music / voice | Godot native audio buses are the lower-dependency baseline. [FMOD GDExtension](https://github.com/utopia-rise/fmod-gdextension) is a separate middleware route with native binaries, FMOD SDK/license requirements and mixed upstream version statements; no 4.7.2 claim was found. Dialogue Manager links voice examples, but this is not voice generation. |
| 15 | UI / UX | Godot’s built-in Control/Theme system is the default reference. No separate third-party UI editor with sufficiently clear 4.7.2 evidence was verified. |
| 16 | Terrain / navigation / behavior-tree / gameplay AI | Terrain3D and LimboAI are the notable candidates. Godot’s built-in navigation remains the lower-dependency baseline. LimboAI’s latest release material explicitly targets Godot 4.6; do not silently extend that claim to 4.7.2. |
| 17 | Import / export / interchange (Blender/glTF) | Prefer the engine’s built-in glTF/scene import path as the baseline. The official docs URL is recorded in the JSON; the documentation host was not reachable for this research run, so detailed current version behavior is not asserted. Aseprite Wizard is a separate 2D importer. |
| 18 | Testing / debugging / profiling / telemetry | [GUT](https://github.com/bitwes/Gut) 9.7.0 explicitly notes compatibility changes for Godot 4.7 and is the strongest test-framework candidate. [Debug Draw 3D](https://github.com/DmitriySalnikov/godot_debug_draw_3d) provides C++-backed in-game visualizations and lists Android binaries; its exact Godot 4.7.2/renderer support is unknown. Neither is a telemetry service. |
| 19 | Git / version control / collaboration | Godot’s native VCS interface and external Git are baseline references. The [Godot Git Plugin](https://github.com/godotengine/godot-git-plugin) release page retrieved for this survey describes Godot 3.2–3.4 compatibility, so reject that release line for a Godot 4.7.2 integration unless a newer upstream version explicitly supersedes it. |
| 20 | Android / export / build / release | Godot’s standard export templates and Android export process are the baseline, not an add-on candidate. No surveyed AI tool was verified as a safe Android build, signing, or publishing authority. Signing credentials and release permissions remain outside this census’s integration scope. |
| 21 | Networking / multiplayer | Godot’s built-in multiplayer/ENet is the no-extra-dependency baseline. GodotSteam’s former GitHub repository states that it moved to Codeberg, so the GitHub copy is not treated as canonical current evidence. No third-party networking extension was advanced without current upstream/version proof. |
| 22 | Documentation / devtools | Godot Tools for VS Code exposes language/debugging features; GUT has its own upstream documentation; official Godot docs remain the authoritative engine reference. MCP offers project inspection, not verified automatic documentation generation. |

## TOP_CANDIDATES

These are grouped by use, not ranked against one another. All remain subject to exact-version, license, platform, privacy, and isolated-project validation.

- **Dialogue/narrative:** Dialogue Manager (4.1.0; Godot 4.6+ statement) and Dialogic (2.0-alpha-20; Godot 4.5+, recommends 4.6; alpha risk).
- **Testing/CI:** GUT 9.7.0 (explicit Godot 4.7 compatibility statement; 4.7.2 still unverified).
- **Debug visualization:** Debug Draw 3D (upstream lists Android binaries and Asset Library asset 1766; require exact engine/renderer checks).
- **Code productivity:** Godot Tools for VS Code (language/debugger workflow, not AI).
- **Scene/editor automation:** Funplay MCP (v0.10.0, Godot 4.2+ claim, CANDIDATE with guarded `execute_code`); Coding-Solo Godot MCP (REFERENCE_ONLY); Godot AI MCP (4.7+ claim, REFERENCE_ONLY pending release maturity); Ivan Murzak Godot-MCP (REFERENCE_ONLY pending .NET/cloud review). This is a grouped shortlist, not a winner selection.
- **Local code assistance:** Ollama Assistant for Godot (Godot 4.4+ claim; CANDIDATE for selected-script GDScript help, not scene editing).
- **Terrain/world:** Terrain3D 1.0.2 stable (Godot 4.6 evidence, native extension) and ProtonScatter 4.0 (scene dressing; 4.7.2 unknown). Voxel Tools v1.7 is a higher-complexity alternative with a custom Godot 4.7 build caveat.
- **2D asset authoring:** Pixelorama v1.2.3 (standalone; its own README says Godot 4.7.2) and Aseprite Wizard v9.8.0-4 (Aseprite importer; project resource writes).
- **3D materials/interchange:** Blender-to-glTF plus Material Maker 1.7 as external authoring references; neither is a project add-on.
- **Camera behavior:** Phantom Camera (Godot 4.3+ statement; verify target version and renderer in an isolated project).
- **Audio middleware:** FMOD only if an explicit middleware requirement justifies native SDK/license and build complexity; otherwise start with Godot audio.

## Decision gates for later tiers

1. Keep the plugin census non-authoritative; no plugin installation or engine/project mutation is part of T0.
2. Require an upstream statement or reproducible test on the exact Godot 4.7.2 build. For GDExtension/native tools, require a matching ABI/binary for every target (especially Android) and headless CI import/runtime evidence.
3. Check GL Compatibility separately. Terrain3D's release notes mention Compatibility-renderer support/fixes, but this is not proof that every feature, target, or exact engine patch works. Do not infer Compatibility success from Forward+/Mobile success.
4. Pin exact source commit, release archive, transitive dependencies and checksums; inspect licenses and imported/generated resource diffs. Treat editor scripts and native binaries as privileged code.
5. For AI, separate model policy from tool policy. Explicitly deny unapproved process execution, filesystem traversal, auto-approved scene writes, project-setting changes, network requests, secret reads, signing, and publishing. Local inference reduces external model egress only if the host, logs, extensions and model are actually local.
6. Re-evaluate privacy, network access, telemetry, Android export, reproducibility and offline behavior against upstream source before any future integration. `UNKNOWN` is a gate, not a presumed pass.

## Source index

- [Coding-Solo Godot MCP README and operations](https://github.com/Coding-Solo/godot-mcp)
- [Funplay MCP](https://github.com/FunplayAI/funplay-godot-mcp) · [v0.10.0 releases](https://github.com/FunplayAI/funplay-godot-mcp/releases)
- [Godot AI MCP](https://github.com/event-horizon-studio/godot-ai-mcp)
- [Ollama Assistant for Godot](https://github.com/TheCronkTM/godot-ollama-assistant)
- [Ivan Murzak Godot-MCP](https://github.com/IvanMurzak/Godot-MCP)
- [Godot 4.7.2 stable archive](https://godotengine.org/download/archive/4.7.2-stable/)
- Search-result-only Asset Library leads: [Godot AI](https://godotengine.org/asset-library/asset/5050), [Breakpoint MCP](https://godotengine.org/asset-library/asset/5335), [Godot MCP Pro](https://godotengine.org/asset-library/asset/4961), [AI Assistant Hub](https://godotengine.org/asset-library/asset/3427), [GDMCP](https://godotengine.org/asset-library/asset/5403); not independently verified.
- [Godot Asset Library backend status and API](https://github.com/godotengine/godot-asset-library) · [API documentation](https://github.com/godotengine/godot-asset-library/blob/master/API.md)
- [Godot Tools for VS Code](https://github.com/godotengine/godot-vscode-plugin)
- [Debug Draw 3D](https://github.com/DmitriySalnikov/godot_debug_draw_3d) · [official Asset Library listing](https://godotengine.org/asset-library/asset/1766)
- [GUT releases](https://github.com/bitwes/Gut/releases)
- [Dialogue Manager](https://github.com/nathanhoad/godot_dialogue_manager) · [releases](https://github.com/nathanhoad/godot_dialogue_manager/releases/latest)
- [Dialogic](https://github.com/dialogic-godot/dialogic) · [releases](https://github.com/dialogic-godot/dialogic/releases/latest)
- [LimboAI](https://github.com/limbonaut/limboai) · [v1.6.0](https://github.com/limbonaut/limboai/releases/tag/v1.6.0)
- [Terrain3D](https://github.com/TokisanGames/Terrain3D) · [releases](https://github.com/TokisanGames/Terrain3D/releases)
- [ProtonScatter](https://github.com/HungryProton/scatter)
- [Voxel Tools](https://github.com/Zylann/godot_voxel)
- [Pixelorama](https://github.com/Orama-Interactive/Pixelorama) · [Aseprite Wizard](https://github.com/viniciusgerevini/godot-aseprite-wizard/tree/godot_4)
- [Material Maker](https://github.com/RodZill4/material-maker)
- [Phantom Camera](https://github.com/ramokz/phantom-camera)
- [Godot XR Tools](https://github.com/GodotVR/godot-xr-tools)
- [FMOD GDExtension](https://github.com/utopia-rise/fmod-gdextension)
- [Godot Git Plugin](https://github.com/godotengine/godot-git-plugin)
- Official-doc references (not reachable during this research run): [3D scene import](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/index.html), [Android export](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html), [animation](https://docs.godotengine.org/en/stable/tutorials/animation/index.html), [navigation](https://docs.godotengine.org/en/stable/tutorials/navigation/index.html).
