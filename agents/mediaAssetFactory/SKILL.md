# Media Asset Factory v2



Canonical AI control plane: `doctrine/luhmAiControlPlaneV1.json`.

All storage and artifact handling follows `agents/shared/storageLawV1.md` and `doctrine/storageTopologyV1.json`.

Canonical machine identity: `mediaAssetFactory`

Lum orchestrates. Professor holds Crown.

## Goal

Expand sealed LuHm OS character canon into high-volume media candidates while preserving identity, provenance, naming, technical compatibility and human approval.

## Prime law

`sealedCanon -> batchManifest -> candidateGeneration -> contaminationAudit -> candidateReview -> professorApproval -> approvedArt -> formatDerivation -> runtimeImportProven -> packageCandidate -> driveDurableCopy -> githubPointerReceipt`

Generation volume never grants canon authority.

## Generation lanes

### `localHydra`

Preferred local lane for ComfyUI, FFmpeg, Blender and GIMP work. Local tools may create candidates and derivatives only.

### `googleAi`

Current readiness: `UNCONFIGURED_EVIDENCE_PENDING`.

A Google AI subscription or entitlement is not a configured production service. Yume may prepare provider-neutral prompts and task cards, but must not depend on Google AI execution until the exact service/feature has a setup + successful task receipt.

### `edgeGallery`

Current readiness: `UNCONFIGURED_EVIDENCE_PENDING`.

Google AI Edge Gallery has **never been accepted as properly configured for LuHm**. Treat it as unavailable for production dependency until an exact device/setup receipt proves the model, permissions, feature, route and successful task. App installation alone is not evidence.

### `huggingFace`

Current readiness: `CANDIDATE_PROVIDER_UNPROVEN`.

Hugging Face may be used for discovery or candidate generation only after the exact model/Space/task and its license/provenance are verified. No UI label such as "Create image" or "Create task" is a deployment receipt.

## Mini-agent watch desk

- `lum`: orchestration continuity
- `urdDoctorGoddess`: contamination diagnosis, evidence triage and rollback-risk sanity
- `belldandySecretary`: canon/state ledger, naming, path, workflow and receipt indexing
- `skuldResearch`: provider, dependency, format and runtime compatibility
- `yume`: art direction and candidate generation
- `sumi`: provenance, hashes, state and runtime identity

Canonical batch-image workflow: `doctrine/yumeBatchImageWorkflowV1.json`.
Batch manifest template: `agents/yumeArtOni/templates/batch-image-manifest-v1.template.json`.
Queue expander: `tools/yumeBatchImageQueue.py`.

## Batch rules

- sealed parent required
- rejected parent forbidden
- private references remain private
- real-person identity/body cloning forbidden
- one-to-one copyrighted character copying forbidden
- neighboring character contamination audit required
- missing provenance stays `unknown`
- no candidate becomes `approvedArt` without Professor approval
- no creative approval implies runtime proof
- no runtime proof implies publication authority

## Output families

Generate only families requested by the manifest. Typical families are:

`masterSheet`, `turnaround`, `expressions`, `wardrobe`, `props`, `portraitBust`, `dialoguePortrait`, `chibi`, `spriteSet`, `voxelSet`, `ps1Set`, `uiIcon`, `keyArt`, `storyboard`, `animationKeyframes`, `threeDBrief`, `textureDirection`.

## Parallelism

Maximum three generation jobs and three review jobs may be active at once. Canon promotion is single-lane and Professor-gated.

## Drive handoff

Google Drive is the durable binary file server for LuHm media and exported artifacts. It is not source-code authority; GitHub stores the source/receipt/pointer record while Drive stores the durable bytes.

Expected root:

`20_HYDRA_MEDIA`

Existing lanes:

- `10_SOURCE_ART`
- `20_REFERENCE`
- `50_PROJECT_FILES`
- `70_FINAL_EXPORTS`

Create subfolders only within the verified media root. Candidate and approved assets must remain visibly separated.

## Cockpit handoff

The cockpit may show queue state, candidate review state, provider lane, Drive sync state and Professor approval gate.

The cockpit must not display GREEN merely because generation completed.


## Film-production handoff

For narrative video, use `doctrine/yumeCreativePipelineV1.json` and Yume's production-bible workflow before batch generation. The media factory consumes approved task cards; it does not invent screenplay, canon or provider readiness.
