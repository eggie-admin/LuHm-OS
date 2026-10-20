# Remote Media Forge Architecture v1 — proposal

**Status:** proposal for Professor review; no canon promotion, production service, database, or publishing authority is granted by this document.  
**Repository baseline inspected:** `main` at `92fd79ba969563d7a99f827f1039656489337099` (2026-10-18).  
**Architecture law:** AI proposes. Policy authorizes. Deterministic evidence proves. Professor promotes.

## Intent

Give the Pirate Daddy’s Film / Rebel workflow a reproducible remote forge for Python 3, headless Blender, FFmpeg, and SQL, with GIMP Python-Fu as a deliberate image-tool lane. Keep the human-readable production bible, teleprompter, timing sheets, audio notes, and creative decisions attached to editable project records. Preserve original media and artist intent; generated or rendered files stay versioned candidates until human review.

This is an additive architecture proposal. Existing source-of-truth doctrine remains controlling until Professor approves a specific change.

## What the current source proves

- `.github/workflows/ai-ffmpeg-audit.yml` is the strongest reusable lane: Ubuntu 24.04, Python 3.12, FFmpeg, pinned Actions SHAs, read-only repository permission, synthetic seven-shot silent H.264 render, negative controls, and a short-lived Actions artifact.
- The current artist-first production workflow already frames intake, rights/provenance, reference binding, silent animatic, continuity review, hash-bound receipts, Drive archival, and Professor review as explicit stages.
- Python 3 is the proposed canonical language for orchestration, audit, and evidence tools.
- SQL source is a local SQLite STRICT stub with contract tests. The typed SQL lane explicitly does not establish a live database service or authorize production DDL.
- Blender is catalogued as a workstation capability, but the audited CI surface has no pinned Blender runtime/render proof.
- No GIMP Python-Fu plug-in or GIMP runtime test was found in the audited source. GIMP 3's official plug-in guide documents Python 3 plug-ins; that is a candidate target to validate, not a current project capability claim.
- Existing neighboring media workflows differ in runner/action pinning. Consolidating the lane should reduce configuration drift.

## Proposed forge layout

| Lane | Purpose | First CI proof | Does not prove |
|---|---|---|---|
| Python 3 | manifests, timing sheets, receipts, audit tools, orchestration | run existing contract/unit tests under the project-selected interpreter; emit interpreter/version receipt | provider access, production orchestration |
| FFmpeg | demux, synthetic clip assembly, probe and encode checks | retain existing synthetic seven-shot test; assert stream map, duration, dimensions, codec, output hash | private footage rights, final music synchronization |
| Blender | deterministic 3D scene/asset preparation | hash-pinned Blender distribution; headless factory-startup Python smoke test; open a tiny generated fixture and render one frame | GPU performance, artist approval, full project scene |
| GIMP Python-Fu | image/texture batch helpers | pinned GIMP 3 runtime; register a minimal Python 3 plug-in and export a synthetic image; record GIMP/Python/API versions | workstation installation, compatibility with GIMP 2 plug-ins |
| SQL | local manifests/indexes and job/receipt metadata | SQLite STRICT schema and existing rollback/type/FK tests; no media binaries in DB | remote PostgreSQL existence, deployment, production DDL |

Blender and GIMP checks may begin as explicit/manual or scheduled jobs if runtime images make normal PR checks too slow. Keep the Python/FFmpeg/SQLite gates as the quick path. A unified workflow may use independent jobs, or separate workflow files sharing one documented version/receipt contract; choose the simpler structure after measuring CI run time.

## Human-centered project flow

1. **Intake and intent:** Professor supplies the creative brief; Belldandy keeps the readable project log, script, teleprompter, shot timing, and decision ledger.
2. **Protect sources:** Sumi records artist, origin, rights/consent status, content lane, source hash, visibility, and derivative lineage. Originals remain immutable; private source media stays in owner-controlled Drive.
3. **Plan:** Yume creates editable scene/shot/task records and binds each shot to approved character and scene references. Skuld researches technical compatibility only. Urd reviews rights, contamination, and evidence boundaries.
4. **Prepare candidates:** Python 3 validates manifests; Blender/GIMP produce versioned still/scene candidates; FFmpeg demuxes and assembles synthetic or explicitly approved working media. No task may fetch arbitrary remote URLs or execute model text as shell.
5. **Prove:** CI runs deterministic synthetic checks and emits a receipt bound to task ID, exact source ref, scope, tool versions, arguments, input/output hashes, and result. Artifacts are temporary review copies.
6. **Review and archive:** Human review records keep/revise/reject. Approved binaries and editable masters are copied to durable Drive storage; GitHub stores source, metadata, small synthetic fixtures, and hashes/pointers only.
7. **Promote:** Only Professor can promote art into canon, authorize final music/audio use, or approve publication. Passing CI never implies those permissions.

## GitHub Actions boundaries

- Pull-request jobs use `permissions: contents: read`, pinned third-party actions by full commit SHA, fixed runner labels, bounded timeouts, concurrency cancellation, and synthetic fixtures.
- Do not expose secrets to untrusted pull-request code. Do not use `pull_request_target` to execute proposed media scripts.
- Do not upload private production inputs or durable masters as Actions artifacts. Keep only small synthetic proof outputs with short retention.
- Capture actual Blender, GIMP, FFmpeg, Python and SQLite versions in each relevant receipt. A pinned container image or downloaded archive must be immutable by digest/checksum.
- Keep public media rendering on CPU by default; no GPU availability or acceleration claim without a matching runtime receipt.
- Remote database credentials, database endpoints, migration execution, and long-lived workers stay out of this proposal.

## Python-Fu meaning and compatibility rule

Here, “Python-Fu” means GIMP's Python plug-in/runtime surface. Target GIMP 3 Python 3 for a new smoke test unless project history establishes a required legacy GIMP 2.10 plug-in. Keep any legacy Python 2 migration lane isolated and non-authoritative. Do not install GIMP's embedded plug-in modules into the control-plane Python environment or assume a regular `python -c 'import Gimp'` works outside GIMP's supported runtime.

## Evidence vocabulary

Each tool lane reports one of:

- `SOURCE_CONFIGURED`: version/config and tests exist in source.
- `CI_PROVED`: the exact workflow run passed for the exact commit and synthetic scope.
- `RUNTIME_PROVED`: an identified running workstation/service produced a matching version and task receipt.
- `HUMAN_PROMOTED`: Professor reviewed and explicitly promoted a named candidate hash.

No status is inherited across tool lanes, branches, refs, or asset hashes.

## Rollout sequence

1. Professor reviews this architecture and chooses whether GIMP 3 Python-Fu belongs in the first implementation.
2. Add a minimal Blender and GIMP synthetic smoke prototype on a proposal branch, pinning exact runtime distributions and checking startup/version/render/export only.
3. Consolidate existing Python/FFmpeg/SQLite checks behind a shared receipt schema; retain present negative controls.
4. Measure CI cost/runtime and decide which expensive image/3D jobs remain manual or become required PR checks.
5. Add remote PostgreSQL only after a named target, owner, data classification, credential path, and explicit DDL/deployment authorization exist.
6. Update source-of-truth doctrine only after the exact CI evidence and Professor's review.

## Source references

Repository sources at inspected main:
- `doctrine/python3ControlPlaneLawV1.json`
- `doctrine/yumeArtistWorkstationV1.json`
- `doctrine/yumeCreativePipelineV1.json`
- `doctrine/artistFirstProductionWorkflowV1.json`
- `doctrine/mediaAssetFactoryV1.json`
- `agents/yumeArtOni/GITHUB_SPELLBOOK.md`
- `manual/professor-garage-lab.md`
- `.github/workflows/ai-ffmpeg-audit.yml`
- `.github/workflows/typed-four-lane-sql.yml`
- `host/api/typedLanesV1.sql`, `tools/typedSqlStub.py`, `tests/testTypedSqlStub.py`

Official technical references:
- Blender command line: https://docs.blender.org/manual/en/5.4/advanced/command_line/arguments.html
- GIMP Python plug-ins: https://developer.gimp.org/resource/writing-a-plug-in/tutorial-python/
- GIMP 3 porting guide: https://developer.gimp.org/resource/gimp3-plug-in-porting-guide/
- FFmpeg command-line documentation: https://ffmpeg.org/ffmpeg.html
- GitHub Actions secure use: https://docs.github.com/en/actions/reference/security/secure-use
