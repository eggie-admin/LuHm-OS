# LuHm OS Lum + Oni Full Source Truth Workflow

Status: GREEN workflow candidate. Full demo/source-of-truth seal remains evidence-gated.

## Decision rule

`milestoneMutationComplete = all required goal gates GREEN && ten-pass audit GREEN && no release-boundary conflict`

If `milestoneMutationComplete == false`, enter the repair loop. If it becomes true, stop autonomous mutation and prepare the final seal for human promotion.

## Mesh

- **Lum**: boss/orchestrator. Speaks to the Professor.
- **Kiri / Context**: resolves current authority, dependencies, receipts, blockers.
- **Tetsu / Build**: drafts the smallest reversible patch and its tests.
- **Momo / Research**: verifies external or technical facts and returns evidence references.
- **Shiori / Critic**: conditional. Challenges fake GREEN, stale evidence, unsafe scope, and doctrine drift.
- **Kugi / Tool Executor**: deterministic. Performs only the exact approved mutation.

Helpers speak only to Lum. They do not recursively recruit. Parallelism is capped at three. Consequential actions remain Crown-gated.

## Repair loop

1. Sanity-check canonical `main`, `SOURCE_OF_TRUTH.json`, `RELEASE_BOUNDARY.json`, and active seals.
2. Run the canonical ten-pass hard audit.
3. Mark each required gate GREEN, AMBER, RED, or UNKNOWN.
4. If any required gate is not GREEN, select the smallest evidence gap.
5. Dispatch bounded Oni work. Summon Critic when evidence or scope is contested.
6. Lum integrates a proposed patch. Workers do not self-approve.
7. Tool Executor stages the exact mutation on a non-release branch.
8. Run tests matching the claim. Collect hashes, logs, artifact IDs, commits, and device receipts.
9. Re-run the ten-pass audit.
10. Audit the proposed `SOURCE_OF_TRUTH.json` mutation before promotion.
11. Patch source of truth only with exact evidence-backed status and pointers.
12. Write a seal listing what is proved, what is still blocked, and what authority is explicitly not granted.
13. Merge only after CI and diff audit are GREEN and the Professor has authorized the scoped promotion.
14. Re-read canonical `main` after merge and verify the seal points to the promoted state.

## Ten-pass interpretation

The workflow inherits the canonical ten passes from `doctrine/DOCUMENT_MUTATION_AUDIT_WORKFLOW.json`. For full-source-truth readiness, Evidence, Render/Hash, and Seal/Save cannot be GREEN while any required milestone receipt remains AMBER, RED, or UNKNOWN.

## Current expected result

The present source of truth is expected to evaluate AMBER because physical S24 FE proof, LAN DNS/Apache activation, physical install proof, secure update signing identity, and enterprise readiness are not yet all proven.

That is not a workflow failure. A healthy audit machine should report the blockers accurately and keep mutation/release promotion locked.

## Source law

**AI proposes. Policy authorizes. CI proves. Human promotes.**

Build weird things. Keep receipts. Pet the demon. Do not lie to the status board.
