# LuHm OS | External beta reviewer release lane

**Status:** CANDIDATE ONLY. Not an invite, public publication, deployment or permission grant.

## What is different today

The actual personal ChatGPT Site/App plugin **Project Hydra 1.0.8** is `USER` scoped and `PRIVATE`. Its existing Site binding must not be thrown away to make a beta. The repository-packaged **LuHm OS 0.5.2** is a distinct plugin, with a read-only MCP manifest at `plugins/luhm-os/plugin.json`. Neither artifact's version number proves the other is installed or deployed. Do not silently relabel either.

The current chat has directly invoked the personal Site bridge's `luhmConnectionStatus` and `luhm_open_cockpit` tools. That is not a successful outside-tester install, in-chat 3D playback, or device acceptance.

The requested outside tester is identified privately by the Professor. **Do not place the tester's email address, private invitation token or account identifiers in public GitHub source, issues, actions output, or CI artifacts.**

## Minimal controlled path to a tester

1. **Repository proposal first.** Review a scoped draft PR with exact current-source identity and all focused CI checks. The LuHm-OS repository is public, so viewing the proposal requires no GitHub collaborator invitation. A GitHub username and the minimum suitable repository permission must be confirmed separately if the tester needs to triage or commit. An email address alone is not a verified GitHub account or a permission grant.
2. **Choose an actual ChatGPT distribution channel.** The existing personal `USER`/`PRIVATE` plugin is not automatically shareable to an outside account by email. Confirm that the target account has access through a supported workspace publishing/sharing arrangement **or** submit the independently reconciled read-only plugin through OpenAI's review and publication process. Do not claim that a GitHub invite supplies ChatGPT plugin access. Do not promise targeted public-directory access controls.
3. **Reconcile release identity.** Preserve the personal plugin's Site/App binding. Obtain a real release mapping from package/source hash and host tool name/resource identity, rather than equating 1.0.8 with 0.5.2. Use a clean external installation test; don't uninstall the working private plugin just to claim a virgin install.
4. **Gate personal data and assets.** External beta receives no private Google Drive assets, unpublished Rebel/EVE donors, raw conversation logs, provider secrets, or production write tools. The anonymous MCP surface stays read-only. OAuth 2.1 and account-scoped authorization are prerequisites for any future user-private data tool.
5. **Check live evidence.** Verify exact-head CI, Render deployed commit, actual MCP initialization/tool scan, privacy/terms/help URL content, rights review, and outside-tester tool invocation. Independently confirm the actual in-chat GUI on the tester's device.
6. **Approval and rollback.** Show the exact reviewed artifact and access scope to Professor. Obtain approval for each external invitation/publish action. Record separate GitHub and ChatGPT access outcomes, time, and rollback plan in an authorized private channel. No automatic invitation, merger, directory submission, or public deployment.

## Current decision

`SOURCE_POLICY=PROPOSED` until CI checks are observed at the exact candidate head.

`PLUGIN_TESTER_ACCESS=BLOCKED`; `GITHUB_INVITE=NOT_SENT`; `DIRECTORY_PUBLICATION=NOT_SUBMITTED`.

**Source/proof hierarchy:** explicit Professor instruction, exact current GitHub `main`, directly observed provider/host evidence, bounded receipts, earlier conversation. Source contracts are not runtime proof.

## Explicit external publication gates

OpenAI developer guidance: https://developers.openai.com/plugins/deploy/submission

Review requirements: https://developers.openai.com/plugins/deploy/app-review

The intended release is a small supervised **read-only creative cockpit beta**, not automatic enablement of quarantined agents or broad repository write privileges.

## Four-lane beta safety contract

The reviewed source is `doctrine/pluginBetaFourLaneV1.json`, enforced by `tools/pluginBetaFourLaneAudit.py` and hostile-change tests. The four lanes are **testing**, **proposed**, **beta**, and **betaLts**. They share **one Professor approval authority**, not four separate release permissions.

| Lane | Safe use | External tester access | Promotion |
| --- | --- | --- | --- |
| Testing | Rapid local/CI mocks, 390px browser smoke, offline and false-GREEN tests | None | Never automatic |
| Proposed | Review code, rights ledger, exact-head CI, source/rollback receipts | None | Human approval of exact artifact |
| Beta | Supervised first outside tester; clean profile and read-only cockpit tests | Blocked until supported access and consent | Explicit separate approval |
| Beta LTS | Pinned last-known-working binary/source, security/compatibility repairs, rollback rehearsal | No automatic invitation or public listing | Human-approved freeze and update receipt |

Current rollback anchors, independently observed 2026-10-21: cockpit `870661cecc3ac68701ad2e1301b4f1e0a6300f98` and Godot `2b8348a8b83b8176a8b72a79da9726463c10264b`. Recheck Render before using these to actually roll back; source hashes do not prove a tester session. Personal plugin `1.0.8` is owner-private; the historical reconciliation recorded `1.0.7` and remains historical evidence, not a current release. Do not rewrite the historical receipt.

## First outside tester, minimal script

Invite **one person privately only after selecting a supported distribution route**. Never store their account name, email, phone, or token in this public repository. A standalone Render preview link is publicly reachable and **not eligible as the requested first-tester experience**. The Professor explicitly requires ChatGPT in-chat interaction. Do not offer web playback as substitute acceptance.

Give the tester a short opt-in checklist: open on their own device; report whether Lum, cast, pet controls and the 3D link appear; try portrait and landscape; report any blank screen or touch issue; don't upload private photos, medical information, songs, account keys or others' assets. Allow voluntary feedback by a privately agreed channel. Never request the tester's ChatGPT credentials. Log only an anonymous receipt in public CI; private feedback stays in an approved private channel.

**Stop conditions:** an unexpected write tool, sensitive data disclosure, unsupported plugin availability, nonworking exit/feedback flow, unsafe media permissions or unverifiable rollback. No beta promotion, no public plugin listing, no external access until the owner reviews the actual distribution target.

## Professor correction: ChatGPT in-chat beta only

**Primary acceptance is NOT a website or Render demo.** The tester must find and install an authorized Project Hydra/LuHm-OS plugin from the ChatGPT Plugins experience, invoke `luhm_open_cockpit` in their ChatGPT conversation, and see the `ui://luhm-os/cockpit-v2.html` resource with the read-only four-lane beta board. On mobile, confirm the actual interactive card mounts, controls respond, and returning to the conversation is possible. A valid MCP JSON payload is not proof that the host displayed the widget.

**Supported private route when available:** create or publish an eligible *workspace* plugin with permission for the tester, use `Share plugin → Only those invited`, and grant the same tester **viewer access to the underlying ChatGPT Site**. Tester's account must meet both sets of requirements. The existing owner **USER/PRIVATE** plugin does not become shareable just because we copied a link. A personal-only account may not have workspace-specific sharing capabilities. An unreviewed public directory package is not a one-person private invite.

**No website escape:** do not set ChatGPT in-chat widget's `openInAppUrl` to the external Render harness or present a Render website as the beta delivery destination. Keep Godot web exports as a separate optional link for owner troubleshooting; never count them as in-chat gameplay. The invited tester has to experience the chat-native surface.

**Current source evidence:** The owner-only plugin is 1.0.8. The latest owner invocation of `luhm_open_cockpit` returned **cockpit unavailable**, while `luhmConnectionStatus` returned only `bridge=reachable`; this is a live-host issue to resolve before any external invitation. Render LIVE does not override that blocker. Keep `beta` and `betaLts` blocked until an actual ChatGPT tool invocation and UI mount work in the target account.

Official access guides: https://help.openai.com/en/articles/20001256-plugins-in-chatgpt and https://help.openai.com/en/articles/20001339-creating-and-using-chatgpt-sites.
