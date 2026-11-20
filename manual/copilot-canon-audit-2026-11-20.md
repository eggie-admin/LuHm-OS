# Copilot Canon audit: Project Premonition / legacy Hydra

**Scope:** read-only source, GitHub, and CI audit; proposed reconciliation only.  
**AUDITED_REF:** `eggie-admin/LuHm-OS/main@f2e4be2224dd706d93d2dc660f536431a7d04f34`  
**AUDIT_OBSERVED_AT:** `2026-11-20T22:09:31Z` (UTC)  
**Copilot received this assignment:** YES — this report was prepared from the issue assignment delivered to this Copilot coding-agent session. No separate LuHm worker or provider was invoked.  
**Authority:** Professor retains Crown. No merge, provider access, deployment, signing, publication, spend, agent activation, secret access, device mutation, or destructive operation was performed.

## Executive verdict

**AMBER source / STOP for Crown or release.** Live `main` still resolves to the issue's observed SHA. The highest-level current source truth is `AMBER_PROPOSED_SEAL_OF_TRUTH`, promotion is false, and Crown is STOP. The three-repository source pins and the named PRs can be reconciled without a rewrite, but runtime, current Render health, ChatGPT UI mounting, physical device, rights, and production-signing evidence remain incomplete or stale. The open-PR inventory is large (127 open PRs); this audit reviews the named PRs and directly related network candidates, not every PR or branch.

The smallest safe next action is **STOP all mutations** until the Professor authorizes a specific source-only lane. If that authorization is later given, the narrowest candidate is to rebase the already-open NGINX correction PR #526 onto this audited `main`, review only its delta, and rerun its source tests. Do not merge it or change a live proxy, DNS, Render service, or route as part of that step.

### Claim labels

`PROVEN` = directly observed by a current GitHub/source/CI receipt in this audit; `SOURCE_DERIVED` = what the exact source contract declares; `OBSERVED` = current tool or repository observation; `INFERENCE` = reasoned conclusion; `PROPOSAL` = suggested future work; `UNKNOWN` = no current proof; `CONTRADICTED` = a claim conflicts with current evidence or has been superseded. No `MEMORY_ONLY` claim is used as proof.

## 1. Source, authority, and Canon precedence

- **[PROVEN]** GitHub resolved `main` to `f2e4be2224dd706d93d2dc660f536431a7d04f34`; the local audit branch began at `2db53627d4024f813daab58c6351581eaee4180a` and initially had no source delta from that base.
- **[SOURCE_DERIVED]** `/doctrine/currentSourceTruthV3.json` is the current source-truth contract. It says `AMBER_PROPOSED_SEAL_OF_TRUTH`, `promotion: false`, and global `crownStatus: STOP`. `/doctrine/projectChatCanonV1.json` identifies LuHm-OS as the product, `projectPremonition` as the development identity, and `projectHydra` as the former identity; legacy routes and historical receipts are to be preserved.
- **[SOURCE_DERIVED]** `/doctrine/everlastingCovenantV1.json` defines `sanityCheck → audit → ingest → mutation → test → apply → continue → deploy`; all states bind to the same `taskId + sourceRef + scopeId`, and RED, UNKNOWN, stale, mismatched, missing, or contradictory evidence stops progression. The current lane's deploy is proposal-only.
- **[SOURCE_DERIVED]** The Covenant's `crownedMilestone` status is explicitly scoped to `everlastingCovenantGovernanceMilestone` in current source truth. Likewise, the queue's `CROWNED_SCOPED_CONTINUITY` and the game layer's `CROWNED_SOURCE_MILESTONE` are scoped milestones, not the overall product Crown. The queue itself says `productCrown: NOT_PROVEN_FROM_QUEUE_ONLY`. These scoped labels do not conflict with global Crown STOP when read at their declared scope.
- **[CONTRADICTED / historical only]** The September 30 baseline in issue #67 and its `SOURCE_OF_TRUTH.json` authority claim predate the current `currentSourceTruthV3.json`. `/doctrine/currentSourceTruthV3.json` lists `SOURCE_OF_TRUTH.json` as a prior source-truth artifact under historical compatibility. Do not use #67's old SHA or source-index status as current proof.
- **[SOURCE_DERIVED]** Names are identity-preserving aliases, not migration permission. Keep the product, Project Hydra routes, Site/App identities, plugin IDs, package namespace, and old receipts intact unless each is separately authorized and evidenced. The internal “Llama” title remains an alias; it is not a provider runtime, new product identity, or public-title approval.
- **[SOURCE_DERIVED]** The four tiers in `/doctrine/fourTierOperatingModelV1.json` are operating/workflow tiers. The seven planes in `/doctrine/layeredStageCanonV1.json` are visual compositor planes. The same source explicitly says the seven visual planes are not architecture tiers; neither count should be substituted for the other.
- **[SOURCE_DERIVED / UNKNOWN]** `/game/canon/CHARACTER_CANON_V1.json` is marked `CANDIDATE`, not a sealed rights grant. `/media/public-release-art-ledger.json` marks character public approvals pending and `publicAllowed: false`. The proposed 4×4 art direction itself records an unresolved Skuld age/silhouette conflict with the candidate game sheet. Keep existing sheets and assets unchanged; no public-use or rights approval is inferred.

## 2. Doctrine consistency and conflict ledger

| Source / clause | Authority and severity | Finding | Proposed reconciliation |
|---|---|---|---|
| `/doctrine/currentSourceTruthV3.json`: global `AMBER_PROPOSED_SEAL_OF_TRUTH`, promotion false, Crown STOP | Current source truth; **High** | Consistent global stop. Scoped “Crowned” labels elsewhere are narrower and must not be rolled up into product GREEN. | Keep global status AMBER/STOP; retain each receipt's declared scope and date. |
| `/doctrine/currentSourceTruthV3.json`: plugin layer `PUBLIC_PACKAGE_GREEN_UPLOAD_PENDING`, `renderRuntime: GREEN`, with ChatGPT host AMBER and public invocation pending; `/doctrine/chatGptPluginRuntimeReceiptV1.json` describes a 2026-10-05 deploy at an older commit and leaves host steps pending | Source receipt; **High** | These are old, scoped source/host claims, not fresh proof of the current main's Render deploy or ChatGPT mount. The receipt itself says exact main CI is unproven and host tasks are pending. | Preserve the historical receipt; only update current fields after fresh exact-main provider and host observations. Until then treat current runtime/host as UNKNOWN or AMBER. |
| `/doctrine/milestoneTaskQueueV1.json`: `CROWNED_SCOPED_CONTINUITY` | Queue authority; **Medium** | It describes task-queue continuity, not final product readiness; `productCrown` says it is not proven from the queue alone. | Keep this label scoped; do not relabel the product or close M08 from it. |
| `/doctrine/networkSpineV1.json`: `reverseProxy.preferredHostProxy: apache2`; issue #525's newer direction and draft PR #526 propose NGINX | Professor policy vs current source; **High** | Direct source/policy conflict. PR #526 is only a candidate, based on old `main@69e8d2fc…`; its current checks include an external Workers failure. No live proxy was inspected. | Preserve the current live path. After explicit source-only approval, rebase #526 onto audited `main`, review/test its exact delta, then stop before deployment. |
| `/doctrine/activeRepositorySetV1.json` pins LuHm main to `a795edac…` from 2026-10-22; live main is `f2e4be…` | Current repo inventory; **Medium** | The canonical-main snapshot pin is stale. The two supporting repo pins still match their live heads. No new cross-repo or Drive/local recovery snapshot was created in this read-only audit. | Refresh the canonical main snapshot only in a separately authorized, non-destructive checkpoint. Keep prior snapshot refs as historical recovery evidence. |
| `/game/canon/CHARACTER_CANON_V1.json` candidate vs `/doctrine/goddessVisualBrandFourByFourV1.json` proposed visual direction | Professor-owned character/art sources; **High for publication** | The 4×4 proposal explicitly records a Skuld design/age conflict. The release-art ledger leaves public approvals pending. | Keep both as candidate evidence; resolve the exact character sheet and rights receipt before producing named public assets. |
| `/doctrine/agentSystemDeploymentV1.json` lists 15 roles; `/doctrine/companyWideOperationalQuarantineV1.json` says QUARANTINED and active task workers disallowed | Professor quarantine; **Critical** | Registered roles, in-chat labels, source skills, and UI cards do not establish executing agents. | Preserve all 15 registrations and quarantine. No CAST, hidden worker, provider worker, or self-approval claim. |
| `/doctrine/storageTopologyV1.json` | Professor storage law; **High** | GitHub stores source and sanitized receipts/pointers; Drive stores durable binary masters; SQL stores typed metadata/pointers; ChatGPT is a context/working surface. | Keep private media, Drive IDs, credentials, signing keys, and raw user chat out of public GitHub. Do not apply review-only SQL DDL. |

## 3. Multi-repository matrix

Live SHA was queried directly for all three repositories. Snapshot references below are from `/doctrine/activeRepositorySetV1.json` and `/doctrine/currentCanonSnapshot20261022.json`; a snapshot pin is not a fresh backup or proof of a deploy.

| Repository | Live `main` SHA | Canon snapshot pin | Role / overlap | Disposition |
|---|---|---|---|---|
| `eggie-admin/LuHm-OS` | `f2e4be2224dd706d93d2dc660f536431a7d04f34` | `a795edac042f968e439ecd93293c99d48d40c696` (2026-10-22; differs from live) | Canonical product/source, doctrine, CI and public-safe receipts. | Preserve as sole mutable source lane. Refresh snapshot only through its own approval and exact-hash process. |
| `eggie-admin/hydra-shell-android` | `08644e2dbb032b1804e260c8ece1060597a22ae0` | `08644e2dbb032b1804e260c8ece1060597a22ae0` | README describes an Android orchestration/testing repository and identifies a separate APK-body candidate; its own “testing-only” language does not make it the current LuHm Canon. | Donor/reference only. Inspect one exact file and license at a time; transplant selectively through a reviewed PR. Never merge its history wholesale or delete it. |
| `eggie-admin/vue-headless-cms` | `1d51c5b90266f7beb8236cf07acfb17a085a4134` | `1d51c5b90266f7beb8236cf07acfb17a085a4134` | README describes a Vue 3 / Vite headless CMS that saves to JSON. This is not a second LuHm source of truth. | Reference/donor only. Review exact component provenance, license, JSON/data boundaries, and browser behavior before any selective transplant. |

**[OBSERVED]** The supporting repository pins match the live GitHub heads queried in this audit; LuHm's canonical-main pin does not. **[UNKNOWN]** No commit-count comparison or complete source-tree diff between each donor and LuHm was performed; snapshot equality does not prove component parity. The active set also labels `KAI9000_LuHm_Compatibility` unavailable; do not invent or promote it as a current repository. No wholesale merge or destructive cleanup is proposed.

## 4. GitHub PR and issue disposition

**[PROVEN]** GitHub search returned **127 open PRs**. Only the issue-mandated PRs and their directly related network candidates were assessed here; the remaining open PRs were not individually checked. GitHub list results were capped at 100 on the first page. **[PROPOSAL]** Narrow future review to changed files, current head/base, and exact checks for the relevant candidate lane rather than treating PR count or old issue summaries as a review receipt.

| Item | Exact observed state | Disposition |
|---|---|---|
| PR #584, Lum/Google layered orchestration | Open, not merged; head `55a21cbc…`, base recorded as `4474df15…` (not audited `main`). Google API entitlement/provider execution are explicitly unknown in its body. The PR has one failed external “Workers Builds: luhm-os” check; nine associated GitHub workflow runs show `action_required`. | **Preserve proposal; split/rebase only after review.** Reconcile only the new source delta against `f2e4be…`; no Google call, CI credential, worker activation, merge, or Crown. `action_required` is not PASS. |
| PR #590, Reaper film candidate | Draft, not merged; head `a7fa492b…`, base `f2e4be…`, 12 commits/six changed files. Current check-run list reports 14 success and one failed external Cloudflare Workers build. GitHub log retrieval for that external check returned 404; its provider-side cause is UNKNOWN. Its candidate workflow fetches public stock footage into a short-lived GitHub artifact, so CI success is not a per-file rights receipt. | **Keep draft.** Require exact-head workflow review, source/license/creator receipts for each used file, storage/retention review, and human media approval. Do not treat generated artifacts or the draft's safety claims as public-release authorization. |
| PR #592, this audit | Draft, open; head `2db53627…` began with an empty/no-delta plan commit against `f2e4be…`. Six checks are `action_required`; the Copilot check was in progress at the time queried. | **Keep as the documentation-only audit lane.** This report adds no runtime or doctrine mutation. Do not mark the audit independently signed off or ready to merge. |
| PR #519, Firefox/FQDN/SQL; #520, source audit; #521, delivery/art; #526, NGINX correction | All are open drafts on older `69e8d2…` bases. #526 head is `da859a79…`; its current check list has 11 success and one failed external Workers build. Its GitHub source/audit checks succeed, but that is not a live NGINX deployment receipt. | **Preserve, compare/rebase selectively.** Do not merge stale whole branches. For #526, rebase only with source-only approval and rerun against `f2e4be…`; leave current proxy, DNS, Render and MCP route untouched. #519–521 CI at current heads was not revalidated in this audit. |
| Issue #67, ten-pass audit | September 30 baseline `506e486…`, old `SOURCE_OF_TRUTH.json` framing and prior findings. | **Historical/superseded for current source identity.** Keep as history; do not reuse its baseline or treat its requested Gemini receipt as present-day evidence. |
| Issue #366, FastAPI Cloud | October 21 research/staging proposal; says existing Render services remain and no live main auto-deploy. Current provider account, cost, rollback, and installation state were not queried. | **HOLD.** No FastAPI Cloud connection, service, workflow, provider call, or Render replacement. Reconsider only with current provider-side cost, account, capability, data, and rollback evidence plus explicit Professor approval. |
| Issues #398 and #525 | Historical milestone/Canon checkpoints with dated SHA claims. #525's latest comment requests a review; its older receipts do not prove current host, DNS, device or signing state. | **Retain as history and task context.** Use current `main` plus the current milestone queue for status; never transplant a stale GREEN into this audit. |

## 5. M01–M08 milestone board

The source statuses below are the queue's declared initial/current task states, not fresh runtime receipts. `UNKNOWN` means this audit did not establish the external proof. All acceptance tests must retain the exact task/source/scope identity and restart at `sanityCheck` if source changes.

| ID / goal | Depends on; source status | CI / host / device / rights evidence now | Blocker and next acceptance test |
|---|---|---|---|
| **M01 `mobileMainHost`** — existing main Render/MCP host | None; **WATCH** | **CI:** three observed failures are scheduled public TLS probes on exact main SHA (runs [44704526374](https://github.com/eggie-admin/LuHm-OS/actions/runs/44704526374), [44489783094](https://github.com/eggie-admin/LuHm-OS/actions/runs/44489783094), [44269205482](https://github.com/eggie-admin/LuHm-OS/actions/runs/44269205482)); 22 successes and five skips among the latest 30 returned main runs. **Host:** current Render deploy and health UNKNOWN; queue's deploy ID is historical. | Observe (do not repeat) the existing service's exact deploy ID/commit, then verify HTTPS health and MCP initialization against it. No new service, live-main auto-deploy, or duplicate deploy. |
| **M02 `androidCockpitProof`** — visible browser/Godot touch and glass navigation | M01; **UNKNOWN** | **Source:** queue defines visible first screen, opt-in Godot touch, five-button glass navigation, and no unexpected network. **Device:** current owner-device receipt not available here. Older October 24 scoped browser/MCP observations do not cover the full acceptance set. **Rights:** not an asset-publication gate. | Owner performs a bounded screen/touch/network observation after M01 is current; record exact device/browser, source/deploy, interaction, and negative network checks. Do not infer physical Android proof from desktop CI. |
| **M03 `godotMusicRuntime`** — reachable Godot export, touch input, actual music playback | M01; **SOFT_RED** | **Source:** current truth says Godot playability is not proven and records an invalid music URL in the October 24 scoped snapshot. **CI/host/device:** no current exact-source playable scene, phone touch, or playback receipt in this audit. | Verify dedicated existing Godot export, rendered scene, phone touch, and actual playback; separately record rights/availability for the chosen music. Static export or HTTP 200 is insufficient. |
| **M04 `chatGptInlineMount`** — MCP resource to visible ChatGPT/Android mount | None; **SOFT_RED** | **Source:** plugin receipt/runtime fields leave ChatGPT discovery and invocation pending; current truth says UI mount unverified. **Host/device:** no current host UI or user-clicked Android receipt. | At exact current host/source, verify resource MIME, visible ChatGPT mount, user-clicked interaction on Android, and positive/negative host behavior. Do not equate MCP read success with iframe/app mounting. |
| **M05 `privateLumAndSprites`** — private character animation and pet sprite preview | M01; **AMBER** | **Rights:** `/media/public-release-art-ledger.json` says Lum approval is pending and `publicAllowed: false`; other goddess sheets are candidate/approval pending. **Private binary/device:** no current private-byte hash, rights receipt, or actual Android preview available in this audit. | Owner uses the private original; record its hash, creator/rights approval, and local preview receipt. Keep Drive IDs and master bytes private; do not publish or use an unapproved legacy sheet. |
| **M06 `samsungCanonSigning`** — signing source and protected signer readiness | None; **AMBER** | **Source:** release boundary denies production signing; current truth says debug artifact only, debuggable, physical install pending, release certificate pending. **Protected environment/key/device:** not inspected; no key values requested or exposed. | Require exact PR/workflow source, independent protected-environment review, and owner-held key presence without disclosure. Test only an owner-authorized, isolated signing path; no disposable release key. |
| **M07 `samsungBetaDelivery`** — signed artifact, Samsung upgrade, F-Droid update | M06; **WAIT_DEPENDENCY** | **CI/source:** source and debug APK status are not signed-beta evidence. **Device:** no install/launch/upgrade receipt. **Rights/distribution:** F-Droid acceptance is a separate required proof. | After M06 is independently accepted, record artifact SHA/fingerprint, physical Samsung install/launch/upgrade, and F-Droid update acceptance separately. Never uninstall/clear user data to simulate upgrade proof. |
| **M08 `finalProductCrown`** — final product acceptance | M02, M03, M04, M05, M07; **WAIT_DEPENDENCY** | **Human/release:** full dependency packet, stable signing/publishing authority, and Professor final acceptance are absent. **Global source:** Crown STOP. | Only Professor can assemble/accept the exact-source Crown docket. Do not self-authorize signing, distribution, publication, merge, deployment, or global GREEN. |

## 6. Code, security, and capability review

- **GitHub governance. [OBSERVED]** The GitHub branch listing reports `main` at the audited SHA with `protected: true`. Current detailed ruleset/required-review configuration was not returned by the available read tools; do not infer the contents of branch protection from that boolean. Older issue #67's unprotected-main finding is superseded by this current observation. The repository has many unprotected candidate/snapshot branches; their existence is not permission to merge or delete them.
- **Workflows/dependencies. [OBSERVED]** The inspected TLS workflow declares `contents: read`, uses SHA-pinned checkout/artifact actions, and its failing TLS command writes diagnostics to a short-lived artifact. The job log proves exit code 1, but not the certificate/root cause; the artifact was not opened from its temporary signed download URL. Other candidate branches have separate external Workers checks whose logs are not available through GitHub (the log request returned 404). Do not retry those provider checks or call them source-test failures without logs.
- **Dependency provenance. [OBSERVED / UNKNOWN]** The front-end manifest pins jQuery `3.7.1` and has a `package-lock.json`; the MCP requirements file pins `mcp==2.2.0`. This is not a full dependency/license/vulnerability audit: transitive Python lock/hash provenance, every workflow action, and every Android/Godot dependency were not examined. No dependency was added by this audit.
- **MCP/app host. [SOURCE_DERIVED]** `host/mcp/luhmMcpServer.py` annotates tools read-only and uses bounded scope checks; it calls fixed internal Python/Git commands through `subprocess`. Source review found no execution of provider/model or Crown actions in the inspected tool declarations. An annotation is not server-side authorization proof: current deployed host, authentication enforcement, exact tool discovery, and ChatGPT UI invocation remain unverified. The portable workflow requires OAuth and per-tool authorization before private reads or writes; anonymous public tools remain read-only by contract.
- **SQL. [SOURCE_DERIVED]** `/host/api/typedPostgresReviewV1.sql` is explicitly review-only DDL. Typed/strict local SQLite tests are not proof of a live PostgreSQL or MariaDB deployment. No DDL or database was changed or queried.
- **Network / Zero Trust. [SOURCE_DERIVED / UNKNOWN]** `/doctrine/networkSpineV1.json` marks DNS/runtime unverified, live mutation false, and the proxy preference as `apache2`. Cloudflare/DNS/Tunnel/Access/NGINX runtime and current TLS end-to-end behavior were not inspected through a provider account. Keep the current direct Render MCP route; do not change DNS, install a proxy, or expose private services.
- **Android bridge. [SOURCE_DERIVED]** `/doctrine/androidWeb3BridgeV2.json` is a proposed candidate. It specifies exact-origin/main-frame behavior and denies arbitrary navigation, network fallback, JS interface, shell, and Crown authority; its own runtime evidence says native handoff and private-art picking remain pending/unverified. This contract does not prove the installed WebView implementation or physical Samsung security.
- **Signing/privacy. [SOURCE_DERIVED / UNKNOWN]** `/doctrine/releaseBoundaryV2.json` denies production signing and stable publication; current truth identifies only a debuggable debug artifact with install and release-certificate proof pending. No key value, provider secret, private media, raw user input, or private Drive identifier was accessed. No rights or public-media approval was created.

## 7. Proof integrity and unsupported GREEN claims

These planes are distinct: source present; exact-head CI; merged main; provider deploy; live HTTP/MCP receipt; ChatGPT host mount; physical Samsung behavior; signing/upgrade proof; asset rights; publication. Passing one does not prove another.

- **[PROVEN] Source:** the exact main SHA and declared source contracts above.
- **[OBSERVED] CI:** latest 30 returned main runs contain 22 success, five skipped, and three TLS-watch failures. The TLS job ran `tools/securityTrustCertAudit.py` against public hostnames and exited nonzero; its precise diagnosis remains UNKNOWN. The commit message's historical “14/14 exact-head CI” statement is not a replacement for this current sample.
- **[UNKNOWN] Current runtime:** no current provider-authenticated Render, Cloudflare, Google, OpenAI, Hugging Face, or FastAPI Cloud observation was made. Source files and old issue receipts do not establish current deployment.
- **[UNKNOWN] ChatGPT mount/device:** no host-discovery, UI-mount, Android interaction, music-playback, physical Samsung install, or upgrade receipt was produced in this session.
- **[UNKNOWN] Rights/signing/publication:** source ledger approval fields remain pending; no owner signing or publication authority was inspected.
- **[CONTRADICTED if stated globally]** `GREEN_RUNTIME_DEPLOY_PUBLIC_DIRECTORY_PENDING`, `GREEN_DEBUG_ARTIFACT_ONLY`, and older `GREEN_SCOPED_*` values are limited by their declared scope and dates. They do not prove overall product GREEN or current host/device/publication status. Keep valid historical scoped receipts; report the present external state as UNKNOWN until re-observed.

## 8. AI, provider, and cost reality

- **[SOURCE_DERIVED]** Lum is the product's conversational routing identity, not the LuHm-OS product itself. The 15 canonical role registrations remain source-configured, while operational quarantine forbids task-worker activation. In-chat role labels are presentation/reasoning labels, not independent processes.
- **[SOURCE_DERIVED / UNKNOWN]** `/doctrine/googleAiDeveloperEntitlementsV1.json` sets API invocation to DENY by default and leaves API, IAM, model/quota, billing, and smoke receipt unknown. Consumer AI subscriptions/credits do not prove API entitlement. `/doctrine/lumOrchestraHardeningV1.json` is a candidate hardening contract, not live provider execution. No Google API, Hugging Face inference, or paid provider call was made.
- **[UNKNOWN]** Current OpenAI/Copilot account entitlements, plugin installation, current provider billing, Render state, Hugging Face write permissions, and Cloudflare controls were not independently inspected. Source configuration and Actions checks do not prove them.
- **FastAPI Cloud decision: `HOLD`.** No current account, price/billing, service, rollback, or authenticated endpoint proof was available in this audit. Keep the existing Render services; do not connect `main` to FastAPI auto-deploy, replace Render, or add a new paid service. A future isolated staging proposal requires current provider-side proof, explicit spend cap, tested source pin, data boundary, and rollback before any setup.

## 9. Simplest reconciliation and five bounded proposals

No mutation is authorized by this audit. These are future, reversible proposals only; each requires its stated approval. No proposal means merge, host deployment, production mutation, publication, signing, agent release, or Crown.

| Priority / proposal | Cost / risk | Test and rollback | Approval gate |
|---|---|---|---|
| **1 — safest source candidate:** Rebase the existing #526 NGINX source correction onto `f2e4be…`, review only the three-file delta, and keep it open. | $0 provider cost; low-to-medium source risk because it changes a proxy preference but not the running host. | Run its focused positive/negative source audit at the new exact head; confirm old route fields are unchanged. Roll back by reverting/closing the candidate PR before merge. | Explicit Professor approval for this source-only lane; no proxy/DNS change. |
| **2 — status integrity:** After fresh exact-target host proof, update only the relevant current plugin/Render status fields while preserving old receipts as dated history. | $0; medium risk of either overstating or obscuring a real historical proof. | Require exact commit/deploy ID, health/MCP result, and separate host-mount result; add/keep checks that refuse a current GREEN without the corresponding current receipt. Revert the candidate commit if the data or tests do not match. | Current provider evidence and Professor approval; no live deployment. |
| **3 — snapshot freshness:** In a separate checkpoint, refresh only `/doctrine/activeRepositorySetV1.json`'s canonical-main snapshot to an immutable exact SHA; retain donor pins and old snapshots. | $0; medium data-integrity risk if snapshot refs are mistaken for durable Drive/local backups. | Verify each repo SHA and snapshot read-back; record GitHub, local, and restricted-Drive backups as distinct receipts. Revert the source pointer if any repo or recovery receipt is missing. | Professor checkpoint/backup authorization; no destructive history operations. |
| **4 — selective donor reuse:** If one Android/CMS component is needed, inspect that exact donor file, license and provenance, then transplant only that component via a small reviewed PR. | $0 by default; medium compatibility/licensing risk. | Run the component's deterministic tests and affected LuHm integration smoke; preserve the donor and revert the transplant PR if compatibility/rights evidence fails. | Exact donor SHA/file, rights/license review, and Professor scope approval. |
| **5 — defer cloud expansion:** Keep Google API default DENY and FastAPI Cloud HOLD; do not create service, CI auth, credentials, or billing. Revisit only with a documented isolated-staging proposal. | $0 now; future cost UNKNOWN until provider proof. | If separately approved later, use a throwaway staging target with exact-source health/version test, explicit spend ceiling, no private media, and proven rollback; otherwise do not proceed. | Fresh provider entitlement/billing/rollback proof and explicit Professor approval. |

**Dependency order:** source identity and safe snapshot → resolve the NGINX source conflict → observe existing main host without redeploy → prove chat/device/game/rights/signing lanes independently → only then consider final acceptance. A failure in a human/device lane blocks its dependents, not unrelated source review. No rewrite, replatforming, parallel source-of-truth, redundant queue, or automatic donor-history merge is recommended.

## 10. Adversarial review / stop conditions

1. A `protected: true` branch flag was observed for `main`; the actual branch ruleset/reviewer configuration was not retrieved. Do not assert required checks, independent review, or deployment protection without those exact settings.
2. The open PR count is 127 and this audit did not inspect all open PR diffs/checks. The named PRs are not a proxy for all branches or PRs. Before any merge, inspect the exact current candidate and applicable checks.
3. The current TLS-watch failure cause was not established from the job log; the diagnostic was written to a short-lived artifact. Do not infer certificate expiry, provider outage, or a passing chain check.
4. The Cloudflare Workers failures on #584/#590/#526 are provider-side checks with no GitHub job log available from the check IDs. Their cause is UNKNOWN.
5. No fresh multi-repository/local/Drive backup receipt was created. Snapshot branches are Git recovery pointers, not complete binary/private/restore proof.
6. Rights are not proven by a filename, a sheet hash, public availability, a proposed art grid, or a draft workflow. Keep protected masters private and publicAllowed false until asset-specific review.
7. Physical Android, ChatGPT mount, current Render health, signing key custody, upgrade continuity, Google API eligibility/billing, and external Zero Trust/DNS remain UNKNOWN.
8. Copilot authored this audit and cannot independently review its own work or grant signoff/Crown. An independent human/authorized review remains required.

## Compact checkpoint

```yaml
sourceRef: eggie-admin/LuHm-OS/main@f2e4be2224dd706d93d2dc660f536431a7d04f34
objective: Read-only Canon, orchestration, repository, PR, security, and M01-M08 audit
confirmedFacts:
  - "[PROVEN] live main SHA resolved directly"
  - "[SOURCE_DERIVED] current source truth is AMBER_PROPOSED_SEAL_OF_TRUTH; promotion=false; Crown STOP"
  - "[PROVEN] main branch listing reports protected=true"
  - "[OBSERVED] two support repository heads match their 2026-10-22 pins; canonical main pin is stale"
  - "[SOURCE_DERIVED] all 15 roles remain registered and quarantined from task execution"
  - "[OBSERVED] 127 open PRs; only named/related candidates reviewed here"
evidenceRefs:
  - "doctrine/currentSourceTruthV3.json"
  - "doctrine/everlastingCovenantV1.json"
  - "doctrine/contextTourniquetV1.json"
  - "doctrine/companyWideOperationalQuarantineV1.json"
  - "doctrine/agentSystemDeploymentV1.json"
  - "doctrine/milestoneTaskQueueV1.json"
  - "doctrine/storageTopologyV1.json"
  - "doctrine/activeRepositorySetV1.json"
  - "GitHub PR #584, #590, #592, #519, #520, #521, #526"
  - "GitHub issues #67, #366, #398, #525, #591"
  - "GitHub Actions runs 44704526374, 44489783094, 44269205482"
pendingDecisions:
  - "Professor source-only authorization for any next candidate"
  - "Current host, device, rights, signer, provider, and full open-PR proof"
conflicts:
  - "[CONTRADICTED] networkSpineV1 says apache2; newer requested direction/PR #526 says nginx"
  - "[UNKNOWN] current plugin/runtime GREEN labels lack fresh current-host proof"
  - "[UNKNOWN] M02-M08 external acceptance evidence"
proposedMutations:
  - "Rebase existing #526 and rerun focused source-only checks; do not merge/deploy"
  - "Refresh scoped current status only after exact host receipts"
  - "Refresh active-repository checkpoint separately; retain all history"
  - "Selective donor transplant only with exact SHA/file/license review"
  - "Keep FastAPI Cloud on HOLD"
executionAuthorized: false
```

## Signoff

```text
COPILOT_SIGNOFF=FAIL
AUDITED_REF=f2e4be2224dd706d93d2dc660f536431a7d04f34
TEN_PASS_COMPLETE=false
BLOCKERS=current TLS probe failures unresolved; external Workers checks lack logs; 127 open PRs not fully audited; host/device/rights/signing/provider evidence missing or stale; current main ruleset details unavailable
UNSUPPORTED_GREEN_CLAIMS=current overall/runtime/device/publication GREEN inferred from dated scoped receipts or source labels
SAFE_NEXT_MUTATION=STOP (candidate only after approval: rebase existing PR #526 and rerun exact-head source checks)
```

This is a Copilot self-assessment, **not an independent second review**. Full Crown remains **STOP**.

## Pinned source index

All source references below resolve against the audited commit, not a moving `main` URL:

- [Project chat Canon](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/doctrine/projectChatCanonV1.json)
- [Everlasting Covenant](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/doctrine/everlastingCovenantV1.json)
- [Current source truth](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/doctrine/currentSourceTruthV3.json)
- [Context precedence and checkpoint contract](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/doctrine/contextTourniquetV1.json)
- [Company quarantine](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/doctrine/companyWideOperationalQuarantineV1.json)
- [Agent deployment registry](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/doctrine/agentSystemDeploymentV1.json)
- [Milestone queue](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/doctrine/milestoneTaskQueueV1.json)
- [Storage topology](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/doctrine/storageTopologyV1.json)
- [Active repository set](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/doctrine/activeRepositorySetV1.json)
- [Network spine](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/doctrine/networkSpineV1.json)
- [Four-tier operating model](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/doctrine/fourTierOperatingModelV1.json)
- [Seven visual planes](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/doctrine/layeredStageCanonV1.json)
- [Character Canon candidate](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/game/canon/CHARACTER_CANON_V1.json)
- [Public release art ledger](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/media/public-release-art-ledger.json)
- [Read-only portable agent workflow](https://github.com/eggie-admin/LuHm-OS/blob/f2e4be2224dd706d93d2dc660f536431a7d04f34/plugins/luhm-os/skills/luhm-agent-workflow/SKILL.md)
