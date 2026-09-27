# GitHub Build Oni Skill

## Tetsu: fast verification builder
Tetsu builds the exact candidate SHA in an isolated GitHub runner. Tetsu may use verified content-addressed module reuse when the module fingerprint, toolchain identity, staged inputs, and output hashes all match. Final APK export and its package/alignment/permission/signature/provenance audits are always fresh for the claimed SHA.

## Kaji: clean-room builder
Kaji builds the same exact candidate SHA in a separate runner without sharing Tetsu's mutable workspace. Kaji is the independent second opinion. Kaji may download the same pinned public toolchain and source assets, but may not consume Tetsu's generated build products.

## Shared evidence contract
Each builder emits `oni-builder.json` containing:
- builder name and role
- exact source SHA
- GitHub run ID and job ID
- workflow name
- UTC timestamp

Each builder also returns the existing Android evidence bundle including package identity, version, manifest audit, signature verification, zipalign result, APK digest, and source-component digests.

Neither builder may declare promotion readiness. Their job is to build and report.

## Independence rule
Two jobs are independent only if they run as separate GitHub jobs/workspaces and produce separate artifacts. Identical build logic is acceptable for reproducibility testing; shared generated outputs are not.

## Speed rule
Run Tetsu and Kaji in parallel. Parallel double-build gives roughly one-build wall-clock while preserving an independent proof lane. Use extra agents only when a concrete blocker requires them.
