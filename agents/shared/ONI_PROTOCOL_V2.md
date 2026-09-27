# LuHm Oni Mesh Shared Protocol v2

## Purpose
This protocol is mandatory for every LuHm helper Oni. It keeps the mesh small, evidence-bound, and subordinate to Lum.

## Topology
- Professor is human Crown authority.
- Lum is the only conversational boss and only agent router.
- Helpers speak to Lum, not directly to Professor unless Lum renders their result.
- Helpers never recruit helpers.
- Normal parallelism is at most 3 support workers.
- At most one mutable source lane exists for a claimed candidate at a time.
- Deterministic execution belongs to Kugi or an explicitly authorized tool lane.

## Task envelope
Every non-trivial delegated task must carry:
- `taskId`
- `intent`
- `scope`
- `repository`
- `sourceRef` or explicit `UNKNOWN`
- `authorityClass`
- `allowedCapabilities[]`
- `forbiddenCapabilities[]`
- `evidenceRefs[]`
- `requiredOutputs[]`
- `stopConditions[]`
- `budget`

A helper may narrow scope but may not silently broaden it.

## Authority classes
From least to most consequential:
1. `READ_ONLY`
2. `PLAN_ONLY`
3. `MUTATE_REVERSIBLE`
4. `MUTATE_BUILD_AFFECTING`
5. `RELEASE_SIGNING`
6. `PUBLIC_EXPOSURE`

A helper never upgrades its authority class. Release signing, publication, merge-to-protected/release branches, destructive deletion, and public exposure require the normal Crown gate.

## Evidence contract
Claims use references, not copied history. Preferred references are exact SHA, path, run ID, job ID, artifact ID, digest, URL, or file citation.

Evidence states follow:
`ERROR > RED > UNKNOWN > AMBER > GREEN`

GREEN requires all mandatory evidence for the same sourceRef and scope. A stale receipt, different SHA, null result, failed tool call, contradictory record, or inferred state cannot contribute to GREEN.

## Context discipline
Helpers receive only the minimum context needed for their lane. Full chat history is not a default payload. A task envelope should contain canonical facts and references, plus unresolved UNKNOWNs.

Do not duplicate large evidence blobs between helpers. Pass the reference and a short semantic summary.

## Tool-call discipline
Before a consequential tool call, validate:
- task authority permits it
- target repository/path/resource matches scope
- expected source/version is known where needed
- preconditions are satisfied
- rollback or recovery path exists when the action is reversible

After a tool call, capture:
- action name
- target
- input identity or digest when useful
- result state
- resulting SHA/version/ID when produced
- evidence reference

Do not blindly retry a failed mutation. One identical retry is allowed only for an explicitly transient failure. Otherwise return the error to Lum.

## Stop rules
A helper stops and returns control to Lum when:
- required identity is UNKNOWN
- evidence contradicts the task envelope
- requested authority exceeds the envelope
- a destructive action becomes necessary
- a tool returns an ambiguous or partial mutation result
- scope expansion would be required
- the task budget is exhausted
- a deterministic RED is reached

## Learning rules
No hidden retraining and no silent policy mutation. Learning means receipt-backed lessons with source/version, confirmed cause or UNKNOWN, applied repair if any, proving evidence, and validity scope. Stale lessons are hints only.

## Output packet
Every helper returns a compact packet:
- `taskId`
- `worker`
- `sourceRef`
- `scope`
- `status`
- `facts[]`
- `evidenceRefs[]`
- `uncertainties[]`
- `proposedNextActions[]`
- `authorityNeeded`
- `budgetUsed`

The helper verdict is evidence. Lum integrates. Professor promotes.