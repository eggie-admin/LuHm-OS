# LuHm-OS Universal Studio Orchestration | Proposed Lane

Source baseline: `f0cb6ee54066b490c0e80efc2c96200fec76ee2d`
Authority: Professor. Source law: AI proposes. Policy authorizes. CI proves. Human promotes.
State: PROPOSED; Crown STOP for public distribution.

## Single source of truth
- `doctrine/currentSourceTruthV3.json`: source/canon and naming.
- `doctrine/androidDeliveryLanesV1.json`: proposed, beta, release isolation.
- `doctrine/npmPluginApkDeliveryV1.json`: npm web assets, Gradle Android.
- `doctrine/fourTrackReleaseClosureV1.json`: native Samsung, in-chat, Godot Web, distribution.
- `doctrine/googleAiDeveloperEntitlementsV1.json`: external entitlement evidence, fail-closed.
- Never merge, sign, publish, charge a provider, or access private artwork on audit evidence alone.

## Four-by-four promotion matrix
| Layer | Inventory | Harden | Runtime proof | Promotion gate |
| --- | --- | --- | --- | --- |
| Canon | identity, rights, assets | namespace/schema drift | provenance receipt | Professor approval |
| Harness | npm, Python, Gradle, Godot | pinned dependencies, vendor reduction | reproducible headless tests | CI evidence |
| Creative | art ingest, scripts, Blender, FFmpeg | private-asset firewall | import-edit-render-export roundtrip | user review |
| Distribution | MCP/ChatGPT, APK, F-Droid, stores | identity/signing/entitlements | real Samsung install + upgrade | Crown STOP until verified |

## Critical path (do not duplicate existing workflows)
1. Audit current source against candidate PRs, including Art Desk and Blender cockpit. Rebase or reconcile in separate proposed changes; never blindly merge.
2. Validate `frontEnd/package.json` and lockfile with `npm ci --ignore-scripts`; keep npm as orchestration interface, not an APK installer.
3. Run existing Python audits and unit tests; record command, SHA, status, and sanitized logs in evidence ledger.
4. Prove minimal creative loop: import a photo/scan, preserve source, edit layered asset, save editable metadata, storyboard, FFmpeg preview, Blender/Godot interchange, video export.
5. Verify MCP initialize, tools/list, resources/read, actual ChatGPT in-chat mount, and Samsung mobile controls independently.
6. Confirm Android supported ABIs before deciding whether four APK variants are possible; generate one manifest for APK(s) and Play AAB, never four unrelated signing identities.
7. Repair owner-held signing via approved secret store; require exact-source non-debug APK, SHA256, package `art.eggiebagelface.luhmos.beta`, trusted cert fingerprint, monotonically increasing versionCode.
8. Require separately signed F-Droid HTTPS index, real install and same-signer upgrade, brand/privacy review, and Professor final approval before any public distribution.
9. Verify entitlements from authenticated provider receipts, separately for subscriptions, API, IAM, quota, billing, and spend ceilings. Unknown = deny.
10. Use existing scheduled CAST for authorized remote execution; release watcher remains read-only.

## Evidence format
Each check: `{id, sourceSha, layer, target, commandOrProbe, observedAt, result, evidenceRef, blocker, owner, promotionAllowed}`.
Allowed results: VERIFIED, FAILED, BLOCKED, UNTESTED. Historical claims are not current runtime proof.
Deduplicate the proposed 500x500 matrix by control, target, and source SHA. Prioritize blockers before breadth.
No public release, production signing, or paid API calls are authorized by this document.
