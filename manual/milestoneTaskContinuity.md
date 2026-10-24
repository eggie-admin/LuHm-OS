# LuHm OS · ChatGPT Tasks milestone continuity operator

**Professor approval:** 2026-10-24. **Goal:** resume real work instead of losing context after the conversation or app closes. ChatGPT Tasks is the recurring wake-up, not the durable truth database. One task runner, one mutation lane, bounded retries, exact-source evidence.

## Three layers

1. **ChatGPT Tasks trigger.** Reuse one paused LuHm task automation for an hourly conditional watch. It can resume a bounded turn only at its scheduled check; it is not a persistent process and does not automatically carry the old chat transcript. If the account/tool cannot run or lacks a required connector, record that honestly.
2. **GitHub source of truth.** Read current `main` plus `doctrine/milestoneTaskQueueV1.json`, `doctrine/currentSourceTruthV3.json`, `AGENTS.md`, `agents/projectChatBootstrap/SKILL.md`, issue [#310](https://github.com/eggie-admin/LuHm-OS/issues/310), and affected task issue (#388 signing, #389 dependent delivery). Issue comments are sanitized evidence/next-action receipts, never secrets or physical device proof.
3. **Deterministic planner.** `python3 tools/milestoneTaskQueue.py --source <actual-40-character-main-sha> --observations <sanitized-current-observation.json>` returns `nextExecutable`, independent tasks and hard-red nodes. No mutations occur inside this program. The scheduled ChatGPT turn uses currently connected tools for any actual authorized action and records one source-bound checkpoint.

## Tick and retry law

- Re-read main SHA and canonical task status. Refresh actual service/issue/CI status; never trust yesterday's SHA or a historical GREEN.
- Resolve dependencies before actions. If one task requires protected signing, a user's phone, unpublished media rights or unreachable accounts, mark **HARD_RED on that task with a specific evidence-backed reason**; immediately continue independent tasks. Never make a global stop from an unrelated per-lane hard-red.
- **SOFT_RED / AMBER:** diagnose, make a small reversible repair when authorized, run exact-source tests, and continue. If a transient provider failure appears, retry with bounded budget (at most 2 attempts per scheduled tick and at most 3 meaningful retries per identical cause), avoiding duplicate deploys or repeated requests.
- **GREEN:** only advance if the task-specific evidence exists. `CI_SUCCESS` alone is not `DEVICE_TESTED`. A merged PR does not imply a live Render deploy. A valid MCP resource does not imply ChatGPT Android iframe mount. An issue cannot self-close by filing a proposed doctrine.
- **HARD_RED:** unable to proceed without an owner-held key/reviewer action, device touch/installation, art rights, necessary consent, or a true security/feature limitation. Ask the Professor once for exactly the required action, not again for the blanket approval already given.
- **Notification:** report meaningful milestone promotion or newly changed hard-red; suppress unchanged hourly status. If no task is actionable, record precisely which dependencies remain and avoid inventing a background model agent.
- **Crown:** existing Professor approval allows read-only checks, bounded safe source repair, controlled review and already authorized existing free services. Protected release, production signing, APK/F-Droid publication, rights changes, unsafe device action and agent quarantine require their own independent proofs/approval.

## Source checkpoints

Each action binds `taskId`, `checkedAt`, `sourceRef`, `observedStatus`, `evidenceRefs`, `blockedReason`, `lastAttempt`, `nextAction`, `actionScope`, `authority`. Bounded context packets follow `tools/contextTourniquet.py` and always have `executionAuthorized: false`. Never include original media, health/personal information, private Drive links, signing keys, credentials, transcripts, or sensitive device identifiers in public issues.

## First inspection on next tick

Read main service deploy `dep-dbejamhsrm7s73cb0blg` at source `b4215642df7c42f0a6bbe847d40d7c4e42ce309c` as **historical starting reference only**. It last appeared `update_in_progress`; re-check before claiming LIVE. Godot lives on a separate existing free Render service. The physical one-screen UI, playable Godot/touch, music playback, private Lum artwork, and ChatGPT inline mount are independent acceptance gates. Task #388 is signing Canon repair, #389 is dependent Samsung beta delivery. Do not confuse earlier source/Render GREEN with an owner-installed APK.

## Scheduling continuity

A ChatGPT Task automation must be enabled separately from the GitHub merge. Do not create dozens of cloned hourly watchers. The original LuHm automations were found paused. Reuse one existing disabled automation with the approved runner prompt. Older paused watches stay paused to avoid racing over the same repository. If scheduled tools cannot resolve GitHub or Render, report a precise blocker with one minimal reconnect action, and leave the canonical GitHub ledger intact.
