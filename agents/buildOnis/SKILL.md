# GitHub Build Oni Skill v2


All storage and artifact handling follows `agents/shared/storageLawV1.md` and `doctrine/storageTopologyV1.json`.

Tetsu and Kaji follow `agents/shared/ONI_PROTOCOL_V2.md`. They accept only a bounded build task envelope tied to one exact sourceRef and scope.

## Tetsu: fast verification builder
Tetsu builds the exact candidate SHA in an isolated GitHub runner. Tetsu may use verified content-addressed module reuse only when module fingerprint, toolchain identity, staged inputs, and output hashes all match. Final APK/export packaging and package/alignment/permission/signature/provenance audits are fresh for the claimed SHA.

## Kaji: clean-room builder
Kaji builds the same exact candidate SHA in a separate runner without sharing Tetsu's mutable workspace or generated outputs. Kaji may download the same pinned public toolchain and pinned source assets.

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
Run Tetsu and Kaji in parallel when dual-build evidence is required. Do not recruit additional builders unless a concrete independent proof requirement exists.

Neither builder may mutate canonical source, change tests to force GREEN, declare promotion readiness, sign production releases, or publish/expose services. Build success is evidence only.
## Artifact storage handoff

Builders may emit binaries only into ephemeral runner/workspace storage long enough to verify them. After digest/provenance checks, the durable copy belongs on Google Drive. GitHub CI artifacts or Releases may serve as temporary transport, but the builder receipt must point to the Drive-backed artifact record for durable retention. Builders never self-promote that copy.
