# LuHm OS | External beta reviewer release lane

**Status:** CANDIDATE ONLY. Not an invite, public publication, deployment or permission grant.

## What is different today

The actual personal ChatGPT Site/App plugin **Project Hydra 1.0.7** is `USER` scoped and `PRIVATE`. Its existing Site binding must not be thrown away to make a beta. The repository-packaged **LuHm OS 0.5.2** is a distinct plugin, with a read-only MCP manifest at `plugins/luhm-os/plugin.json`. Neither artifact's version number proves the other is installed or deployed. Do not silently relabel either.

The current chat has directly invoked the personal Site bridge's `luhmConnectionStatus` and `luhm_open_cockpit` tools. That is not a successful outside-tester install, in-chat 3D playback, or device acceptance.

The requested outside tester is identified privately by the Professor. **Do not place the tester's email address, private invitation token or account identifiers in public GitHub source, issues, actions output, or CI artifacts.**

## Minimal controlled path to a tester

1. **Repository proposal first.** Review a scoped draft PR with exact current-source identity and all focused CI checks. The LuHm-OS repository is public, so viewing the proposal requires no GitHub collaborator invitation. A GitHub username and the minimum suitable repository permission must be confirmed separately if the tester needs to triage or commit. An email address alone is not a verified GitHub account or a permission grant.
2. **Choose an actual ChatGPT distribution channel.** The existing personal `USER`/`PRIVATE` plugin is not automatically shareable to an outside account by email. Confirm that the target account has access through a supported workspace publishing/sharing arrangement **or** submit the independently reconciled read-only plugin through OpenAI's review and publication process. Do not claim that a GitHub invite supplies ChatGPT plugin access. Do not promise targeted public-directory access controls.
3. **Reconcile release identity.** Preserve the personal plugin's Site/App binding. Obtain a real release mapping from package/source hash and host tool name/resource identity, rather than equating 1.0.7 with 0.5.2. Use a clean external installation test; don't uninstall the working private plugin just to claim a virgin install.
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
