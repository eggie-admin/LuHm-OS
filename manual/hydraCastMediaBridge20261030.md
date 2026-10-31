# Project Hydra / CAST Bridge: rotoscope, mocap, vector and dating-sim studio
**State:** Draft PR #463 source-only. No engine builds, recording, provider calls, asset uploads or promotion. Crown STOP.

## Architecture and escalation
1. **Light OS / Samsung:** opt-in microphone + phone + tablet + up to six webcams, typed capture sheet, clap/timecode sync, original recordings kept private. Hardware synchronization is unproven; use visual/audio clap and measured frame offsets, never claim synchronized six-camera triangulation.
2. **FFmpeg:** preserve originals. Generate a separate B/W luma matte with lutyuv (threshold), or a distinct chromakey preview for green/blue. Save grayscale PNG frames with deterministic FPS, SHA-pinned inputs and explicit non-overwrite command. Do not confuse B/W visualization with true transparency. Artist then combines grayscale matte with color plate and checks edge alpha.
3. **Blender:** animated Bezier masks, tracking markers, feathered vector roto, keyframe cleanups, camera calibration, lens distortion cleanup, retopology, facial/body retarget and editable .blend masters in approved private storage. Never auto-execute imported scripts.
4. **Motion capture:** establish coordinate system, calibrated cameras, lens parameters, frame rate, clap offsets, bone/face maps and rest-pose correction. Monocular webcam/phone capture is a 2D/estimated-pose input, NOT validated precision 3D mocap. Validate foot plants, hand contact, face privacy and drift before exporting.
5. **Engines:** keep Godot existing playable/Android spine; Unity optional reviewable export; Unreal final baked high-fidelity destination with MetaHuman Animator/Live Link as opt-in native alternatives when hardware/license proven. Only one engine owns a given build. No triple runtime packaging, no Unreal-on-tablet claim.
6. **Dating sim:** the engine-neutral `game/datingSimPilotV1.json` defines one four-node first-encounter branching rehearsal with adult, original/approved character proxies, bounded affinity, no untrusted dynamic script evaluation. Prove Godot dialogue and input first, then Unreal parity and only build a Unity adapter when a genuine requirement exists.
7. **AI/remote:** OpenAI and Google Gemini are optional bounded review of consented asset derivatives / shot metadata. Default local deterministic; require account-bound API permissions, cost budget, prompt-injection containment, structured schema checking, privacy/retention approval and signed human review before any cloud media transfer. Existing `doctrine/googleAiDeveloperEntitlementsV1.json` blocks unproven cloud execution; Vertex legacy route stays off. Google Drive private control plane currently ACL-held, therefore do not ingest or upload private source art there until reverified secure.

## Play the lightweight dating-sim slice
The authored `game/datingSimPilotV1.json` is also directly playable as a small **offline text game** with no extra packages, network access or AI calls. It has two first-encounter routes, bounded affinity and a shared rehearsal ending:
```sh
python3 -m tools.datingSimPilot --demo  # deterministic smoke check
python3 -m tools.datingSimPilot --play  # interactive terminal choices
```
This is an actual text-level vertical slice, **not** a built Godot, Unity or Unreal game. The script evaluates no dialogue as code; characters and all artwork are still proxy/unapproved.

## Blocking Unreal EULA / GPL-3.0 review
Root `LICENSE` on the current primary LuHm-OS repository is GPL-3.0. Epic's current Unreal EULA section 6(c) identifies GPL as a potentially non-compatible license for combining with Unreal Licensed Technology. Keep Unreal engine code, proprietary plugins, generated engine modules, and binaries **outside the GPL-3.0 runtime/linking boundary** pending a qualified rights/license review; do not assume that moving files to another directory alone solves compatibility. Share original, rights-cleared, engine-neutral media formats or data contracts only when the actual permissions permit. Epic's MetaHuman/engine assets cannot be used for prohibited model training. Mark Unreal release LEGAL_HOLD until reviewed; no public or private Unreal package claims yet.

## Same-source proof
```sh
python3 -m unittest tests.testHydraCastMediaBridge -v
python3 tools/hydraCastMediaBridge.py --source-ref "$(git rev-parse HEAD)" --output /tmp/hydra-cast-source-receipt.json
# Optional plan only with owner-created private capture manifest:
python3 tools/hydraCastMediaBridge.py --source-ref "$(git rev-parse HEAD)" --output /tmp/hydra-shot-plan.json --shot /private/capture-shot.json
```
The shot CLI produces an FFmpeg argv **proposal only**, never executes it. The artifact must stay private if its shot contains sensitive local filenames. The example tests use synthetic placeholder hashes. Exact source SHA audit is CI-safe and does not test camera hardware, codec throughput, emotional narrative quality, or the target Unreal game.

## Vendor docs
- FFmpeg lumakey and lutyuv: https://ffmpeg.org/ffmpeg-filters.html
- Blender animated masks: https://docs.blender.org/manual/en/latest/movie_clip/masking/introduction.html
- Epic MetaHuman from mono webcam: https://dev.epicgames.com/documentation/metahuman/metahuman-animator-in-unreal-engine
- Epic Live Link: https://dev.epicgames.com/documentation/unreal-engine/live-link-in-unreal-engine
- Godot AnimationTree: https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html
- Google Gemini video API: https://ai.google.dev/gemini-api/docs/video-understanding

**CAST:** source pass => private asset fixture => actual Blender/FFmpeg/Godot proof => Unreal/Unity optional adapter proof => Professor human private beta approval. Never auto-merges or publish.
