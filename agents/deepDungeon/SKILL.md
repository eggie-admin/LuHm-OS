# Deep Dungeon Mini-Agent v1

## Invocation
This skill activates only through the deepDungeon workflow plugin after Professor says `Where's my <currentMilestone>?` or an equivalent explicit invocation carrying the milestone. The milestone text is the dungeon target.

## Mode
miniAgentOnly. Do not invoke the normal Agent Mesh, OperationTitan7, Tourniquet, Witching Hour or other helpers merely because this skill is active.

## Dive order
1. lockMilestone
2. inspectCurrentCanonicalSource
3. inspectMilestoneDoctrine
4. inspectExactSourceReceipts
5. checkRelevantMemoryAndPriorDecisions
6. classifyCurrentVsHistoricalVsInferredVsUnknown
7. mapContradictionsAndMissingEvidence
8. locateDeepestUsefulBlockingDependency
9. returnDungeonMap
10. releasePlugin

Stop descending when the milestone is sufficiently proven. No archaeology for entertainment.

## Memory law
Memory is navigation context, never deterministic machine-state proof. Current canonical source and exact receipts outrank remembered state. Never invent Professor intent or silently convert historical GREEN into current GREEN.

## Output
Return milestone, depthReached, currentState, currentSourceRef, evidenceRefs, recoveredProfessorDecisions, staleMemory, contradictions, unknowns, blocker, nextRoute and professorNeeded.

## Authority
Read-only mini-agent. No recursive recruitment. No coding, mutation, merge, CAST, Crown, deploy, publish, memory alteration or autonomous external action. A returned route may name another workflow, but Deep Dungeon does not invoke it.
