# Godot 4 plugin and creation-tool census — 2026-09-30

**Purpose:** evidence snapshot for the T0 research gate and later T1/T2/T3 integration decisions. This is not an installation, endorsement, compatibility certification, or change to LuHm OS runtime policy. No plugin, dependency, project setting, engine setting, or remote service was changed.

## How to read this census

- The companion [`godot4PluginCensus-20260930.json`](godot4PluginCensus-20260930.json) is the field-complete matrix. Each candidate entry has the same required fields; missing evidence is written as `UNKNOWN`.
- Upstream GitHub repositories and their release pages take precedence over copied catalog descriptions. The official [Godot Asset Library](https://godotengine.org/asset-library/) backend repository describes the library as being in maintenance mode and says the future Godot Foundation asset store is expected to deprecate it. The official library host did not resolve from this research environment, so individual catalog entries and direct asset IDs could not be independently checked. An Asset Library URL is supplied only when verified; otherwise it is `UNKNOWN`, not a claim that no listing exists.
- Godot 4.7.2 is the requested target. “4.7”, “4.6+”, a compatible major version, or a project being built with Godot does **not** establish 4.7.2 compatibility. Only upstream claims are recorded; this research did not install or test candidates.
- Release tags are included where an upstream release page exposed one. Exact release dates were not consistently available in the retrieved source pages and are explicitly `UNKNOWN` in the matrix rather than estimated.
- `CANDIDATE` means worth considering for an isolated, gated future evaluation; it is not selected, approved, installed, or production-ready. `REFERENCE_ONLY` means useful as a pattern or external workflow, not a proposed project dependency. `REJECT` is limited to evidence of a direct mismatch for the target. `UNKNOWN` means the available evidence is insufficient.

## AI-assisted creation and editor automation

### What can actually mutate the project?

| Tool/workflow | Assistant role | Direct project/editor mutation | Model locality/provider |
| --- | --- | --- | --- |
| [Coding-Solo Godot MCP](https://github.com/Coding-Solo/godot-mcp) | An MCP **server**, not a model. Its README advertises launching the editor/project, capturing debug output, inspecting project structure, and scene operations. | **Yes.** Documented operations include creating scenes, adding nodes/properties, loading sprites, saving scenes, exporting a MeshLibrary, and updating UIDs. It also starts/stops projects and launches Godot. This crosses from suggestions to direct filesystem/scene/editor actions. | The server is model/provider-neutral. Its README documents MCP clients (Claude Code, Cline, Cursor); cloud use, credentials, retention, and telemetry are controlled by the selected client/model provider. No direct Ollama endpoint is documented by the server. |
| MCP server + a local Ollama-capable MCP host | Conditional local-model route, not a verified dedicated Godot Ollama plugin. The MCP server supplies Godot tools; the separate host/model supplies proposals and tool calls. | Potentially the same direct mutation surface as above **if** the host can invoke MCP tools and the local model produces accepted tool calls. No specific host/model pairing or 4.7.2 workflow was validated here. | Local inference is conditional on a compatible host and local model. Ollama compatibility for the Godot server itself is `UNKNOWN`; “supports MCP” alone is not proof the particular Ollama client can call it. |
| Cloud MCP client/model (for example, clients named in the MCP README) | Cloud model can suggest code/content and can request available MCP tools. | With Godot MCP enabled, can perform the server’s documented project/editor operations. Without a mutation-capable tool, code assistance is suggestions or user-mediated edits. | Cloud-provider identity, API key/subscription, data retention, and egress depend on the client/provider; these are not established by the server README. Treat project prompts, source, scenes, assets, logs, and secrets as potentially transmitted when a cloud model is used. |
| [Godot Tools for VS Code](https://github.com/godotengine/godot-vscode-plugin) | IDE language/debugging support (GDScript completion, navigation, formatting, breakpoints, resource navigation); it is not an AI model/plugin. | It edits files only through ordinary IDE editing. No autonomous scene-generation or AI feature was verified in its upstream README. | No model or provider is inherent to this extension. A separately installed coding assistant changes the data-egress and mutation model. |

The key distinction for later decisions is **assistant proposal versus delegated execution**. Godot MCP explicitly exposes scene and project operations; it is not “read-only” merely because an AI agent is the caller. The README even shows an `autoApprove` configuration that can approve mutation operations. Do not use auto-approval for file/scene writes or process launch. Pin the server package, inspect the exact tool schema, run on a disposable copy, review diffs, and require human confirmation. Its `npx` setup and Node.js runtime add a package-supply-chain and local-process dependency.

No upstream evidence retrieved for this census establishes a dedicated, maintained Godot 4.7.2 Ollama assistant that safely edits all requested artifact types. In particular, there is no verified direct AI authoring path here for textures, sprites, animations, rigging, audio, or builds. Those are not implied by a tool that can add a node or write a script. The JSON matrix distinguishes native server operations from model-host capabilities and leaves unproven claims `UNKNOWN`.

### AI creation surface: verified versus not established

| Artifact/task | Evidence-based conclusion |
| --- | --- |
| Scenes, nodes, simple sprite node setup, project inspection, run/debug loop | Godot MCP README explicitly advertises scene creation/node insertion, sprite loading, project inspection, editor/project launch and debug output. The scope is broad enough to mutate a project; safeguards are required. |
| Scripts, GDScript, C#, shaders, materials, tests, docs, build/export configuration | An external coding assistant can propose or edit text if given ordinary filesystem/IDE access, but this is not equivalent to a Godot-aware integrated authoring feature. The retrieved MCP README does not claim purpose-built generation for every one of these artifact types. Mark direct MCP support `UNKNOWN` unless a specific operation is documented. |
| Dialogue, quests, levels, textures, sprites, animations, meshes, facial/blend-shapes, audio/voice, UI | The surveyed authoring add-ons/tools provide human-facing authoring workflows. AI-generation or autonomous editing support was not evidenced for these candidates. Do not infer it from an editor plugin or MCP support. |
| Build configuration and Android/export | Godot’s export workflow is distinct from project-content generation. No candidate was verified here as an AI build/release authority. Publishing, signing, or remote command execution are out of scope. |

## Categorized survey

The entries below cover the requested categories. The field-complete JSON matrix provides operational/security notes, release and license details, evidence links, and an explicit LuHm status for each serious candidate. Built-in engine features and standalone applications are included for comparison but are not misrepresented as installable add-ons.

| # | Category | Upstream-grounded options and assessment |
| ---: | --- | --- |
| 1 | EditorPlugin / editor productivity | Godot Tools for VS Code provides GDScript/resource language features and debugger support. Godot MCP provides editor/project control with a much larger mutation and command surface. Treat the former as IDE support, the latter as privileged automation. |
| 2 | Runtime add-ons | [Phantom Camera](https://github.com/ramokz/phantom-camera) supplies Camera2D/Camera3D behavior and states Godot 4.3+; Dialogic and Dialogue Manager also combine editor authoring with game runtime behavior. Check each plug-in’s project/resource changes separately. |
| 3 | GDExtension / native modules | [Terrain3D](https://github.com/TokisanGames/Terrain3D) is a C++ GDExtension terrain system; [LimboAI](https://github.com/limbonaut/limboai) is a C++ behavior-tree/state-machine plugin. Native code raises engine ABI, binary, renderer, Android, and headless-CI gates. Neither has verified 4.7.2 evidence in the retrieved sources. |
| 4 | MCP / editor-control bridges / agent tooling | Godot MCP is a model-neutral MCP server with documented editor/project launch, debug and scene operations. This is the strongest verified project-mutating AI bridge in the survey, and consequently carries the highest local filesystem/process risk. |
| 5 | Local LLM / Ollama assistants | A local Ollama model could only be used through a separate MCP-capable client that supports that local model and invokes Godot MCP tools. The direct Godot-server/Ollama pairing, supported host, local-only guarantee, and telemetry behavior remain `UNKNOWN`; no dedicated Ollama Godot plug-in was verified. |
| 6 | Cloud-model assistants | The Godot MCP README names cloud-capable MCP clients, but the MCP server is not itself a cloud assistant. Provider/API-key/subscription and data-egress behavior belong to the client and model. Keep this lane separate from local-only execution and do not send project secrets. |
| 7 | GDScript / C# / shader / code assistance | VS Code Godot Tools provides GDScript completion, formatting, navigation and debugging, not an AI model. Godot-native shader/editor tools are authoring interfaces, not evidence of AI generation. External coding agents require their own provider/security review. |
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
| 18 | Testing / debugging / profiling / telemetry | [GUT](https://github.com/bitwes/Gut) 9.7.0 explicitly notes compatibility changes for Godot 4.7 and is the strongest test-framework candidate. This is not 4.7.2 certification. Godot MCP can retrieve debug output; no telemetry service or test integration is implied. |
| 19 | Git / version control / collaboration | Godot’s native VCS interface and external Git are baseline references. The [Godot Git Plugin](https://github.com/godotengine/godot-git-plugin) release page retrieved for this survey describes Godot 3.2–3.4 compatibility, so reject that release line for a Godot 4.7.2 integration unless a newer upstream version explicitly supersedes it. |
| 20 | Android / export / build / release | Godot’s standard export templates and Android export process are the baseline, not an add-on candidate. No surveyed AI tool was verified as a safe Android build, signing, or publishing authority. Signing credentials and release permissions remain outside this census’s integration scope. |
| 21 | Networking / multiplayer | Godot’s built-in multiplayer/ENet is the no-extra-dependency baseline. GodotSteam’s former GitHub repository states that it moved to Codeberg, so the GitHub copy is not treated as canonical current evidence. No third-party networking extension was advanced without current upstream/version proof. |
| 22 | Documentation / devtools | Godot Tools for VS Code exposes language/debugging features; GUT has its own upstream documentation; official Godot docs remain the authoritative engine reference. MCP offers project inspection, not verified automatic documentation generation. |

## TOP_CANDIDATES

These are grouped by use, not ranked against one another. All remain subject to exact-version, license, platform, privacy, and isolated-project validation.

- **Dialogue/narrative:** Dialogue Manager (4.1.0; Godot 4.6+ statement) and Dialogic (2.0-alpha-20; Godot 4.5+, recommends 4.6; alpha risk).
- **Testing/CI:** GUT 9.7.0 (explicit Godot 4.7 compatibility statement; 4.7.2 still unverified).
- **Code productivity:** Godot Tools for VS Code (language/debugger workflow, not AI).
- **Editor automation research reference:** Godot MCP (directly mutating capabilities; reference-only until its local permissions and MCP host are constrained and reviewed).
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
- [Godot Asset Library backend status and API](https://github.com/godotengine/godot-asset-library) · [API documentation](https://github.com/godotengine/godot-asset-library/blob/master/API.md)
- [Godot Tools for VS Code](https://github.com/godotengine/godot-vscode-plugin)
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
