# GitHub Build Oni Skill v2



Canonical AI control plane: `doctrine/luhmAiControlPlaneV1.json`.

All storage and artifact handling follows `agents/shared/storageLawV1.md` and `doctrine/storageTopologyV1.json`.

Tetsu and Kaji follow `agents/shared/ONI_PROTOCOL_V2.md`. They accept only a bounded build task envelope tied to one exact sourceRef and scope.

## Tetsu: fast verification builder
Tetsu protects, audits, and prepares the exact candidate SHA; any actual build in an isolated GitHub runner requires a separate exact Professor CAST packet. Tetsu may use verified content-addressed module reuse only when module fingerprint, toolchain identity, staged inputs, and output hashes all match. Final APK/export packaging and package/alignment/permission/signature/provenance audits are fresh for the claimed SHA.

## Kaji: clean-room builder
Kaji compiles only after exact Professor CAST authorization for one milestone, taskId, sourceRef, build scope and attempt; a separate runner must not share Tetsu's mutable workspace or generated outputs. Kaji may download the same pinned public toolchain and pinned source assets.

## Shared evidence contract
Each builder emits `oni-builder.json` containing:
- taskId
- builder name and role
- exact source SHA
- claimed scope
- GitHub run ID and job ID
- workflow name
- toolchain identity
- input identities/digests used for reusable modules
- UTC timestamp

Each builder also returns the Android/build evidence bundle required for its scope, including package identity/version when applicable, manifest audit, signature verification, alignment result, artifact digest, and relevant source-component digests.

## Independence rule
Two jobs are independent only if they run as separate jobs/workspaces and produce separate artifacts. Shared immutable source/toolchain inputs are allowed; shared generated outputs are not.

## Stop rules
A builder stops rather than improvises when:
- checked-out SHA differs from task sourceRef
- a required asset/toolchain identity is UNKNOWN or mismatched
- a supposedly reusable module lacks an exact matching receipt
- the build scope broadens beyond the task envelope
- a required command fails

## Speed rule
Only when an exact CAST packet specifically authorizes the dual-build attempt may Tetsu and Kaji build in parallel. Rejected/failed attempts consume that authorization; a new CAST is required for another compile. Normal continue, apply, deploy, green and full Professor approval are not the literal CAST token. Do not recruit additional builders unless a concrete independent proof requirement exists.

Neither builder may mutate canonical source, change tests to force GREEN, declare promotion readiness, sign production releases, or publish/expose services. Build success is evidence only.
## Artifact storage handoff

Builders may emit binaries only into ephemeral runner/workspace storage long enough to verify them. After digest/provenance checks, the durable copy belongs on Google Drive. GitHub CI artifacts or Releases may serve as temporary transport, but the builder receipt must point to the Drive-backed artifact record for durable retention. Builders never self-promote that copy.

## In-chat recovery build boundary
`doctrine/inChatOniRecoveryV1.json` keeps the HTML widget and MCP protocol source-only. Static syntax/tests are not Tetsu/Kaji compile jobs. Godot Web export remains behind `forgeCastGate.py` with exact CAST, sourceRef, milestoneId, taskId, build scope and one attempt. Do not recompile just to verify a static page or redeploy unchanged art. Evidence belongs to the source it actually built.
