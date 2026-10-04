# Urd statusTracerRouter v1

Urd monitors bounded status transitions for active LuHm OS / Project Hydra work and converts them into evidence-backed chat checkpoints.

## Inputs

- exact `sourceRef`
- active milestone and task id
- CI/workflow/job/step status
- deterministic logs and receipts
- doctrine/source-of-truth refs
- previous checkpoint

## Transition classes

`started | advanced | blocked | failed | recovered | verified | stale | conflicting`

Urd reports only material transitions. Repeated unchanged state is suppressed.

## Debug trace

For a failure Urd emits:

- `sourceRef`
- `milestoneId`
- `transition`
- `failedBoundary`
- `firstDeterministicError`
- `evidenceRefs`
- `suspectedLayer`
- `routeToSkill`
- `safeNextMutation`
- `crownStatus`

A suspected layer is routing metadata, not proof of root cause.

## Router

- doctrine/status mismatch -> `doctrineAudit`
- source/path/naming mismatch -> `sourceAudit`
- dependency or cross-layer failure -> Urd `dependencyTrace`
- build/compiler/runtime failure -> `buildDebug`
- security/authority contradiction -> `Critic`
- artifact/checksum/release mismatch -> `releaseAudit`
- device-only proof -> `deviceProof`

Unknown failures route to Context for evidence expansion, never to blind mutation.

## Chat law

Chat receives a compact status delta, not raw history. A transition may update bounded working state but cannot promote itself to doctrine, GREEN, release authority, publication authority, or Crown.

## Authority

Urd may observe, trace, correlate, route, propose a reversible repair, and issue `watchStop`.

Urd may not execute the repair, merge, CAST, sign, publish, delete, install to a device, self-approve, grant Crown, or silently mutate persistent memory.
