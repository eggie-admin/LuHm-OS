# LuHm-OS CAST Bridge | Two-thread 4×4 orchestration and release test

**Status:** staged source-only; two *logical* timelines are not two running agents, ChatGPT conversations, async Python threads, or autonomous jobs. The user continues to talk to Lum in the ordinary chat. A second source-backed orchestration transcript is available as an offline view model, currently without a deployed ChatGPT Site integration. In `publicationSite/castBridgePreview.html`, both appear side-by-side on desktop and stacked on a small phone.

## User language mapped to existing Canon

| Professor's stage | Required canonical guard-rail states | What can be proven right now |
| --- | --- | --- |
| Sanity check | `sanityCheck` | Repo/doc/model shape checks only |
| Hard audit | `audit → ingest` | Exact path and typed receipt audits, source only |
| Adjust / mutation | `mutation` | A reviewed branch diff, not authority for live host effects |
| Build | `test` | GitHub Actions build/test fixture for exact SHA, not signed Android runtime |
| Deploy | `apply → continue → deploy` | Proposed-candidate stage only under current governance |
| CAST Bridge test | Separate `postDeployBridgeSmoke` *after* an approved deployed target | Not run: no exact host/ChatGPT plugin mount proof |

**Do not reorder the canonical eight states to fit conversational shorthand.** A failure in any earlier state means STOP or HOLD. Any source change restarts sanity check at the new Git SHA; no historical GREEN transfers automatically. The current eight-state chain comes from `doctrine/everlastingCovenantV1.json` and the R0–R3 tiers from `doctrine/escalationKernelV1.json`.

## Two visible threads, one authority

**Thread 1, Professor ↔ Lum:** goal intake, scope clarification, current stage, status, smallest next action and Professor approval. The original goal is never persisted into the source-only response; only a deterministic SHA-256 request identity is displayed. Ordinary ChatGPT is still the real user conversation.

**Thread 2, Lum ↔ orchestration:** deterministic handoff to proposed role labels and Urd contradiction/receipt adjudication. In future, separately authorized mini-agents can attach signed or otherwise independently verified receipts, but **zero** are active in this draft. Roles include Lum coordinator, Urd evidence checker, Belldandy records and Skuld compatibility. The original `host/api/luhmCanonOrchestration.py` already implements two **logical** SQLite events in an atomic transaction; it is not a hidden background thread. The new CAST projection is read-only and does not call that ledger's write method.

Both threads use the exact same `taskId + sourceRef + scopeId`. The original eight-note routing remains the owner of agent-role cadence, not a new scheduler. Never allow two concurrent source-mutating agents merely because two visual columns exist.

## Four typed SQL lanes × four escalation tiers

The four machine data lanes are `numericStream`, `textStream`, `booleanStream`, and `aiManifestStream`. They already exist in `host/api/typedLanesV1.sql` with the typed contract `doctrine/typedFourLaneSqlV1.json`. Their contents are respectively bounded numbers/tiers/counts, source + scope + hashes, true/false/UNKNOWN proof, and a bounded candidate task manifest.

Cross each against **R0** default (deterministic local), **R1** coordinated (Lum + focused evidence labels), **R2** specialist (specific domain and rollback research), **R3** closure (exact candidate and human authority). That yields sixteen *planning cells*, not sixteen workers. Each cell starts HOLD.

The workbench should show progress as receipts, not animated pretend agents. `doctrine/castTwoThreadBridgeV1.json` is the machine contract and `host/api/luhmCastTwoThreadBridge.py` exports `source_audit()` and `plan()`. The plan includes a 2-thread transcript, four typed rows, sixteen 4×4 cells, eight ordered state markers, and exact next blocked actions.

## Evidence admission, replay and STOP

A submitted observation is untrusted until independently checked against GitHub CI, the real private host or device, and the matching scoped source. The planner accepts **at most eight** externally claimed receipts. Each must contain **exactly** `taskId`, `sourceRef`, `scopeId`, `stage`, and `evidenceSha256`. A mismatched task/source/scope, skipped stage, duplicate stage, unrecognized stage, malformed digest or hidden extra command field is RED. Even syntactically valid claims are never promoted to proof by this function.

The two source-only threads cannot create another ChatGPT conversation, run any worker, use provider credits, merge Git, install the mobile app, deploy a service, or grant GREEN/Crown. Only a subsequently authorized host adapter with real authenticated evidence can change runtime status.

## Private/API and chat boundaries

The candidate optional private FastAPI adapter exposes authenticated `GET /v1/cast-bridge/status`, `POST /v1/cast-bridge/plan` and `POST /v1/cast-bridge/review`. The `X-LuHm-Control-Token` is configured on a private host only; the API binds localhost by default, the OpenAPI document is disabled, and all new routes reject unauthorized callers and unexpected body fields. No secret goes into HTML, a phone bundle, public GitHub, SQL or a public MCP argument.

The read-only MCP *source definitions* `luhm_cast_two_thread_status` and `luhm_cast_two_thread_plan` are registered in `host/mcp/luhmHarnessServer.py`. Source registration does **not** prove a refreshed private ChatGPT Site plugin mount or actual second conversation.

The unlinked `publicationSite/castBridgePreview.html` is a noindex, offline-only illustrative UI. It displays synthetic labels. It makes no fetch, socket, worker, SQL, browser token, or domain request. The existing public static Render site still points to its own approved deployment branch, not this draft, so this preview is not claimed deployed.

## Fast four-tier CAST loop

1. Bind one task, exact current GitHub commit, scope, target and authority; re-read unexpired receipts.
2. Perform sanity/hard audit, reconcile typed lanes and record an evidence gap list.
3. Choose **the lowest tier** capable of addressing one actual blocker. Reuse deterministic checks, avoid provider sprawl; if an authorized source mutation occurs, change sourceRef and restart at sanity check.
4. Build and test exact SHA under CI. Stop on any RED. Do not mistake test green for live device GREEN.
5. After explicit external target/credentials/backup/owner authorization, a separately permitted executor may deploy an exact candidate. A subsequent CAST smoke probe must report the *observed* plugin/host/feature behavior in the second thread before Lum reports closure in the first.

**Actual next gate:** verify the current draft's exact Git SHA/CI, then physically prove one authenticated ChatGPT Site tool call or one Samsung install receipt. Until that proof exists, keep `castExecuted:false`, active workers zero and source-only status HOLD.

## Local proof

- `python host/api/luhmCastTwoThreadBridge.py`
- `python -m unittest discover -s tests -p 'testCastTwoThreadBridge.py' -v`
- `python -m unittest discover -s tests -p 'testCastTwoThreadFastApi.py' -v`

`.github/workflows/cast-two-thread-source.yml` runs these tests on untrusted PR source without paid API, provider credential or machine access. The existing OpenAI bridge offline suite runs them too. Neither CI report can complete the runtime CAST smoke proof by itself.
