# LuHm-OS Creator Studio / Nightglass Crossroads

**Working scope:** optional source candidate, not a replacement for the existing First Night Circuit. The display product remains `LuHm-OS`; package namespace remains `LuHmOS` as already defined by the four-layer Canon. External language models are optional suggestion providers, not another product called LLMOS.

## Inspirations, not donated runtime

ScummVM (https://github.com/scummvm/scummvm) is a reference for scene-state, clue-led narrative, tools and dialogue staging. Wine (https://github.com/wine-mirror/wine) is a **host-only** compatibility option for Linux desktop authoring, never an Android/Godot runtime dependency. BodySlide & Outfit Studio (https://github.com/ousnius/BodySlide-and-Outfit-Studio) informs semantic sliders and outfit-conform QA. Vortex (https://github.com/Nexus-Mods/Vortex) informs source manifests, dependency/conflict checks and reversible intake. Never ship source game data, borrowed voice/music, licensed character textures, community mods or disassemblies just because a GitHub repository is open. No mass forks are authorized or needed.

## Four-layer composition

0. `coreLibrary`: content schemas, hashing, semantic IDs, deterministic scene/dialogue checking, source identity.
1. `pluginExtension`: procedural bar/shore, companion affinity, additive morph and component adapters. No engine core fork.
2. `classWidgetOrganization`: editable Creator Studio, character bench, world map, dialogue/quest graph, art reference shelf.
3. `stubAdapterBoundary`: Godot reads reviewed JSON; local Python writes explicitly selected SQLite and JSON; optional future host-only Wine tool, source-only GitHub connector, private Google Drive master pointers. No database ports or remote code execution.

**Database layers are separate:** existing `host/api/typedLanesV1.sql` keeps task/receipt events; additive `host/api/creatorStudioV1.sql` stores worlds/scenes/characters/dialogue/morph candidates. Both are local-only. Godot consumes a validated exported JSON snapshot, not privileged SQL. Image and GLB bytes stay out of SQL and out of unreviewed public commits.

## Studio loop

1. Open this original `game/studio/nightglassHubV1.json` manuscript or edit locally through `tools/creatorStudio.py`.
2. Write a branch of dialogue, scene connection, original companion or morph preset.
3. Validate allowed camelHump IDs, dialogue references, character speakers, bounds and rights declarations.
4. Preview the source-only procedural scenes at `res://scenes/NightglassHub.tscn`. This is an optional scene, no change to `res://scenes/Main.tscn`.
5. AI can propose *draft dialogue JSON*, subject to the existing `doctrine/jrpgAiProposal.schema.json`. Named LuHm-OS roles remain logical presentation roles while quarantine is active. No autonomous provider call.
6. Review exact diff and receipts. Publish/sign/device install remain closed pending separate CAST.

## Current limitations

This is a bounded original **bar + shore dialogue proof** with procedural placeholder props and simple branching, not the finished Chrono Cross-like world, Code Vein characters, commercial Blade Runner engine, full BodySlide outfit conform, API-backed authoring, SQL server or installed APK. Existing morph controller only applies present Godot blend shapes; missing rig/assets must show blockers instead of claiming successful fitting. No third-party art files are added.

## Local authoring commands

```sh
python3 tools/creatorStudio.py validate game/studio/nightglassHubV1.json
python3 tools/creatorStudio.py importWorld --db /tmp/luhmCreatorStudio.sqlite --source-ref <40-lowercase-hex-SHA> game/studio/nightglassHubV1.json
python3 tools/creatorStudio.py listWorlds --db /tmp/luhmCreatorStudio.sqlite
python3 tools/creatorStudio.py exportWorld --db /tmp/luhmCreatorStudio.sqlite nightglassCrossroads /tmp/nightglassExport.json
python3 -m unittest discover -s tests -p 'test_creatorStudio.py'
```
The export contains only the validated manuscript; runtime Godot still uses the tracked source file unless a human explicitly reviews and replaces it. Existing signed release and Crown laws unchanged.
