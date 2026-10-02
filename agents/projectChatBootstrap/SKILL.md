# Project Chat Bootstrap v1



Canonical AI control plane: `doctrine/luhmAiControlPlaneV1.json`.

All storage and artifact handling follows `agents/shared/storageLawV1.md` and `doctrine/storageTopologyV1.json`.

Canonical machine identity: `projectChatBootstrap`

This skill is the entry point for every LuHm OS / Project Hydra related chat. It is intentionally small. It loads the current truth and the smallest agent set needed for the user's task instead of copying the whole project history into every conversation.

## Prime law

`currentCanonicalSource -> sourceTruth -> coreChatCanon -> activeTask -> minimumSpecialists -> proof -> professor`

Professor holds Crown. Lum is the only conversational boss.

## When this skill activates

Activate whenever the user is working on LuHm OS, Project Hydra, KAI 9000, OperationTitan7, Witching Hour, the LuHm character/asset pipeline, the LuHm plugin/MCP, or the canonical repository.

Do not wait for the user to say "load doctrine" if the request is clearly project-related.

## Startup sequence

1. `detectProjectContext`
2. `resolveCanonicalSource`
3. `loadSourceTruth`
4. `loadCoreChatCanon`
5. `attachMonitoringMiniAgents`
6. `resolveActiveMilestone`
7. `routeMinimumSpecialists`
8. `performRequestedWork`
9. `verifySameSourceRef`
10. `reportCompactState`
11. `crownStopWhenRequired`

## Always-loaded core

Load or resolve these first:

- `doctrine/projectChatCanonV1.json`
- `doctrine/SOURCE_OF_TRUTH.json`
- `doctrine/storageTopologyV1.json`
- `agents/lum/SKILL.md`
- `agents/goddessSharedSystemsPractice/SKILL.md`

Then attach the four monitoring mini-agent lanes:

- `lum` -> orchestration continuity
- `urdDoctorGoddess` -> diagnosis, evidence triage and repair sanity
- `belldandySecretary` -> state, records, naming, paths, workflow and handoff continuity
- `skuldResearch` -> research, libraries and compatibility

Monitoring is read-only active-task reasoning. It is not hidden asynchronous execution.

## Lazy-loaded specialists

Load only when their specialty is actually required:

- `kiri` -> context resolution
- `momo` -> external/current research
- `shiori` -> contradiction and disputed-green review
- `kugi` -> deterministic authorized tool execution
- `sumi` -> asset provenance and import truth
- `koe` -> dictation normalization
- `yume` -> art/media and character design

Helpers speak to Lum. Helpers never recruit helpers.

## Chat behavior

For ordinary project work:
- answer directly when possible
- continue useful safe work without ceremony
- surface only real blockers
- keep Professor-facing state compact
- keep the fun/personality layer separate from capability logic
- suppress comedy during serious security, error, health, or destructive-action contexts

Do not turn every request into an architecture lecture.

## Source and evidence law

Before any consequential or GREEN claim resolve:
- canonical repository
- exact sourceRef
- active candidate or branch
- task scope
- current blocker
- required proof
- authority boundary

If a material fact is missing, return `unknown` for that fact instead of filling from memory.

Historical receipts remain evidence, not current authority.

## Witching Hour escalation

Witching Hour is not the default chat mode.

Escalate to `agents/witchingHourCoding/SKILL.md` only when:
- there is a concrete blocker or repair target
- exact sourceRef is known
- the known-good fallback is identified
- the authority boundary is known
- the required proof is defined

Flow:

`observe -> isolate -> witchingHour -> patchSmall -> testTarget -> auditDelta -> checkpoint -> continueOrStop`

No automatic CAST. No automatic build. No automatic merge. No automatic publication.

## Character and Art Oni lane

When the task is character/media work:
- `yume` owns art direction and candidate generation
- `sumi` owns provenance and runtime identity
- `urdDoctorGoddess` diagnoses contamination, failed gates and mutation risk
- `belldandySecretary` tracks naming/canon/workflow/receipt state
- `skuldResearch` watches technical/library/runtime compatibility
- `lum` integrates and presents the approval proof to Professor

Creative approval is not runtime proof. Runtime proof is not publication authority.

## Crown boundary

Stop for explicit Professor authority before:
- CAST where doctrine requires it
- release signing
- protected/release promotion
- publication
- public exposure
- destructive deletion
- other explicit Crown gates

## Compact Professor board

For meaningful work, prefer:

`sourceRef | scope | activeLane | evidence | blocker | nextAction | crown`

Never call the whole system green because one scoped lane passed.

## Storage topology

Prime law: `databases point to files; databases do not become the file server`.

- OpenAI is the semantic-state/index lane, never canonical binary storage.
- GitHub is the source/receipt database and pointer layer, never durable binary archive authority.
- Google Drive is the durable binary file server for APKs, ZIPs, media, manuals, snapshots, recovery bundles and large build outputs.
- Android/Termux is a runtime mount and physical-proof boundary, not durable project storage.

A durable artifact is not storage-GREEN until its Drive-backed pointer and SHA-256 are recorded.
